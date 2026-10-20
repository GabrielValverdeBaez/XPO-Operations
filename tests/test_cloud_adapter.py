"""Native adapter tests. SQL is real SQLite; JS bindings are doubles, not production D1."""
import asyncio
from copy import deepcopy
import io
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
from urllib.parse import urlparse
import pytest
from fastapi.testclient import TestClient
from cloud_adapter.api import create_cloud_app, MAX_BODY
from cloud_adapter.auth import COOKIE, TTL, issue_session, valid_session, password_matches, key_valid
from cloud_adapter.d1 import D1Store
from loadstudio.engine import render, DEFAULT_RULES, HEADERS, CATALOG
from loadstudio.ingest import parse

KEY='synthetic-only-ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789'
ORIGIN='https://studio.test'
TEXT='''Referencia: DEMO-CLOUD
Cliente: XPO TRANSPORT SOLUTIONS SPAIN SL
Origen: ES 28909 Getafe
Destino: PT 2675-076 Odivelas
Recogida: 20/10/2026 10:00-16:00
Descarga: 21/10/2026 12:00-13:00
Servicio: FTL
Peso: 15 t
Mercancia: Aceite / Oil
Precio cliente: 900'''

class Statement:
    def __init__(self,db,sql,args=()):self.db,self.sql,self.args=db,sql,args
    def bind(self,*args):return Statement(self.db,self.sql,args)
    def execute(self):
        cur=self.db.connection.execute(self.sql,self.args)
        rows=[dict(r) for r in cur.fetchall()] if cur.description else []
        return {'success':True,'results':rows}
    async def all(self):
        result=self.execute()
        self.db.connection.commit()
        return result

class SqliteD1:
    def __init__(self):
        self.connection=sqlite3.connect(':memory:',check_same_thread=False)
        self.connection.row_factory=sqlite3.Row
    def prepare(self,sql):return Statement(self,sql)
    async def batch(self,statements):
        self.connection.execute('BEGIN')
        try:
            values=[s.execute() for s in statements]
            self.connection.commit()
            return values
        except Exception:
            self.connection.rollback()
            raise

class Assets:
    async def fetch(self,url):
        root=Path(__file__).resolve().parents[1]/'dist/cloudflare/public'
        path=root/urlparse(url).path.lstrip('/')
        content=path.read_bytes() if path.exists() else b'Not found'
        class Asset:
            status=200 if path.exists() else 404
            headers={'content-type':'text/html' if path.suffix=='.html' else 'text/plain'}
            async def bytes(self):return content
        return Asset()

class Limiter:
    def __init__(self,limit=5):self.count=0;self.maximum=limit
    async def limit(self,args):
        self.count+=1
        return {'success':self.count<=self.maximum}

@pytest.fixture(scope='module',autouse=True)
def bundle():
    from scripts.build_cloudflare import build
    return build()

@pytest.fixture
def env():return SimpleNamespace(XPO_LOGIN_KEY=KEY,DB=SqliteD1(),ASSETS=Assets(),LOGIN_LIMITER=Limiter())

@pytest.fixture
def client(env):
    database=env.DB
    with TestClient(create_cloud_app(env),base_url=ORIGIN,follow_redirects=False) as c:yield c
    database.connection.close()

def login(client):
    r=client.post('/auth/login',json={'password':KEY},headers={'Origin':ORIGIN})
    assert r.status_code==200,r.text
    return r

def write(client,path,body,method='post'):
    return getattr(client,method)(path,json=body,headers={'Origin':ORIGIN})

def prepared(client):
    parsed=write(client,'/api/parse',{'text':TEXT,'mode':'text'})
    assert parsed.status_code==200,parsed.text
    return {'load':parsed.json()['drafts'][0]['load'],'reviewed':True}

@pytest.mark.parametrize('key',[None,'','short','x'*40,123])
def test_fail_closed_key(key,env):
    env.XPO_LOGIN_KEY=key
    c=TestClient(create_cloud_app(env),base_url=ORIGIN)
    assert c.get('/api/config').status_code==503
    assert c.get('/').status_code==503
    assert not key_valid(key)

def test_auth_cookie_signature_expiry_rotation():
    value=issue_session(KEY,now=1_800_000_000)
    assert valid_session(value,KEY,now=1_800_000_001)
    assert not valid_session(value+'0',KEY,now=1_800_000_001)
    assert not valid_session(value,KEY+'other',now=1_800_000_001)
    assert not valid_session(value,KEY,now=1_800_000_000+TTL)
    assert not valid_session(value,KEY,now=1_799_999_999)
    assert password_matches(KEY,KEY)
    assert not password_matches('bad',KEY)

@pytest.mark.parametrize('path',['/api/config','/api/history','/api/rules','/api/rates','/api/health'])
def test_api_is_private(client,path):assert client.get(path).status_code==401

@pytest.mark.parametrize('path',['/','/index.html','/static/app.js','/static/style.css','/login.html'])
def test_static_has_no_auth_bypass(client,path):
    r=client.get(path)
    assert r.status_code==303
    assert r.headers['location']=='/login'
    assert r.headers['cache-control']=='no-store'

def test_no_insecure_remote_login(env):
    c=TestClient(create_cloud_app(env),base_url='http://studio.test')
    assert c.post('/auth/login',json={'password':KEY},headers={'Origin':'http://studio.test'}).status_code==400

def test_cookie_security_and_logout(client):
    r=login(client)
    cookie=r.headers['set-cookie']
    for part in ['Secure','HttpOnly','SameSite=strict','Path=/','Max-Age=28800']:assert part in cookie
    assert client.get('/api/config').status_code==200
    assert client.get('/').status_code==200
    assert write(client,'/auth/logout',{}).status_code==200
    assert client.get('/api/history').status_code==401

def test_wrong_key_and_rate_limit(client):
    for _ in range(5):assert write(client,'/auth/login',{'password':'wrong'}).status_code==401
    assert write(client,'/auth/login',{'password':KEY}).status_code==429

def test_origin_and_forged_token(client):
    assert client.post('/auth/login',json={'password':KEY}).status_code==403
    assert client.post('/auth/login',json={'password':KEY},headers={'Origin':'https://evil.test'}).status_code==403
    assert client.get('/api/history',headers={'X-XPO-Token':KEY}).status_code==401
    login(client)
    assert client.post('/api/save',json={},headers={'Origin':'https://evil.test'}).status_code==403
    assert client.get('/api/config',headers={'Sec-Fetch-Site':'cross-site'}).status_code==403

def test_no_credentials_in_validation_response(client):
    r=write(client,'/auth/login',{'password':KEY,'unknown':KEY})
    assert r.status_code==422
    assert KEY not in r.text

def test_body_limit(client):
    login(client)
    r=client.post('/api/parse',content=b'{}',headers={'Origin':ORIGIN,'Content-Length':str(MAX_BODY+1)})
    assert r.status_code==413

def test_cloud_local_equivalence_history_versions(client):
    login(client)
    req=prepared(client)
    from loadstudio.models import Load
    cloud=write(client,'/api/render',req).json()
    local=render(Load.model_validate(req['load']),DEFAULT_RULES,[],True)
    for key in ('markdown','plain','html','tsv','load','can_export','market_basis'):assert cloud[key]==local[key]
    assert len(cloud['tsv'].split('\t'))==26
    assert cloud['tsv'].split('\t')[24]==''
    assert cloud['tsv'].split('\t')[6]=='2675'
    first=write(client,'/api/save',req).json();again=write(client,'/api/save',req).json()
    assert first['duplicate'] is False and again['duplicate'] is True
    assert first['id']==again['id']
    req['load']['client_price_eur']='901'
    revision=write(client,'/api/save',req).json()
    assert revision['id']!=first['id'] and revision['related']==[first['id']]
    assert len(client.get('/api/history').json())==2
    assert client.get('/api/history/'+str(first['id'])).json()['tsv']==cloud['tsv']

def test_review_cannot_be_bypassed(client):
    login(client);req=prepared(client);req['reviewed']=False
    assert write(client,'/api/save',req).status_code==422
    assert client.get('/api/history').json()==[]

def test_optimistic_rules_restoration_and_audit(client):
    login(client)
    current=client.get('/api/rules').json()[0]['rules']
    current.update(revision=2,reason='Synthetic cloud test')
    body={'rules':current,'expected_revision':1}
    assert write(client,'/api/rules',body,'put').status_code==200
    assert write(client,'/api/rules',body,'put').status_code==422
    assert write(client,'/api/rules/restore',{'revision':1,'expected_revision':2}).status_code==200
    rows=client.get('/api/rules').json()
    assert [r['revision'] for r in rows]==[3,2,1]
    backup=write(client,'/api/backup',{}).json()['download']
    assert len(backup['tables']['audit'])==3

def test_rates_backup_and_no_secret(client):
    login(client)
    rate={'id':'SYNTHETIC','origin_country':'España','origin_prefix':'28','destination_country':'Portugal','destination_prefix':'26','service':'FTL','vehicle':'Trailer','adr':False,'base_eur':'1000','max_weight_kg':'24000','max_linear_meters':'13.6','valid_from':'2026-01-01','valid_until':'2026-12-31','source':'SYNTHETIC TEST NOT FOR OPERATIONS'}
    assert write(client,'/api/rates',rate,'put').status_code==200
    assert len(client.get('/api/rates').json())==1
    exported=write(client,'/api/backup',{}).json()
    assert exported['download']['format']=='xpo-d1-backup'
    assert 'XPO_LOGIN_KEY' not in json.dumps(exported)
    assert KEY not in json.dumps(exported)
    assert len(exported['download']['tables']['rates'])==1

def test_xlsx_and_ocr_off(client):
    from openpyxl import Workbook
    login(client);w=Workbook();w.active.append(['reference']);w.active.append(['SYNTHETIC'])
    b=io.BytesIO();w.save(b)
    r=client.post('/api/excel/preview',content=b.getvalue(),headers={'Origin':ORIGIN,'Content-Type':'application/octet-stream'})
    assert r.status_code==200,r.text
    assert r.json()['sheets'][0]['rows'][1][0]=='SYNTHETIC'
    assert client.get('/api/config').json()['ocr_available'] is False
    assert write(client,'/api/ocr',{}).status_code==503

def test_missing_d1_fails_closed(client,env):
    login(client);env.DB=None
    assert client.get('/api/config').status_code==503

def test_future_schema_rejected(env):
    db=env.DB
    db.connection.execute('CREATE TABLE xpo_meta(id INTEGER PRIMARY KEY, version INTEGER)')
    db.connection.execute('INSERT INTO xpo_meta VALUES(1,99)');db.connection.commit()
    with pytest.raises(ValueError):asyncio.run(D1Store(db).ensure())
    assert not db.connection.execute("SELECT name FROM sqlite_master WHERE name='snapshots'").fetchall()

def test_allowlisted_bundle_and_catalog_equivalence(bundle):
    root=Path(__file__).resolve().parents[1]
    for path in bundle:
        assert not path.endswith(('.xls','.xlsx','.sqlite3','.token'))
        assert 'template-audit' not in path
    assert len(bundle)==18
    ns={};exec((root/'dist/cloudflare/loadstudio/_catalog.py').read_text(),ns)
    assert ns['AUDIT']['headers']==HEADERS
    catalog={k:[r[0] for r in rows if r and r[0] is not None] for k,rows in ns['AUDIT']['catalogs'].items()}
    assert catalog==CATALOG
    page=(root/'dist/cloudflare/public/index.html').read_text()
    assert 'Datos en tu equipo' not in page
    assert 'content="cloudflare"' in page
    assert 'historial guardado en D1' in page

def test_d1_transaction_rollback(env):
    async def run():
        store=await D1Store(env.DB).ensure()
        with pytest.raises(sqlite3.OperationalError):
            await store.batch([store.statement("INSERT INTO rates VALUES('never','{}')"),store.statement('SELECT * FROM does_not_exist')])
        assert not await store.rows("SELECT * FROM rates WHERE id='never'")
    asyncio.run(run())

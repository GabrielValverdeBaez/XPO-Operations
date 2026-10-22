#!/usr/bin/env python3
"""Private XPO cache. No network calls, public data writes or automated sending."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone, date
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import unicodedata

VERSION = 1
REGIONS = {
 'andalucia': ['andalucia','almeria','cadiz','cordoba','granada','huelva','jaen','malaga','sevilla','algeciras','antequera','lebrija','dos hermanas','alcala de guadaira','jerez','san roque','puerto real','bailen','guarroman','martos','la carolina','lucena','motril','el ejido','adra','huevar','la rinconada','ecija','utrera','carmona','velez malaga','marbella','chiclana','el puerto de santa maria'],
 'galicia': ['galicia','galiza','a coruna','la coruna','coruna','lugo','ourense','orense','pontevedra','vigo','arteixo','culleredo','ledono','o porriño','porriño','oroso','naron','betanzos','santiago de compostela','bergondo','ames','tui','tomino','vilalba','villalba','caldas de reis','carballo','redondela','mos','a estrada','salceda de caselas','outeiro de rei','curtis','padron','lalin'],
}
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+")

def now(): return datetime.now(timezone.utc).isoformat()
def norm(value):
    return ' '.join(re.sub(r'[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFKD',str(value).casefold()) if not unicodedata.combining(c))).split())
def identifier(kind, value): return kind+'-'+hashlib.sha256(value.encode()).hexdigest()[:24]
def emails(value): return list(dict.fromkeys(x.lower() for x in EMAIL.findall(value)))
def regions(text):
    text=' '+norm(text)+' '
    return [key for key, aliases in REGIONS.items() if any(' '+norm(alias)+' ' in text for alias in aliases)]
def money(value):
    if value is None: return None
    try:
        d=Decimal(str(value))
        if not d.is_finite() or d<0 or d.as_tuple().exponent < -2: raise ValueError
        return format(d.quantize(Decimal('.01')),'f')
    except (ValueError,InvalidOperation): raise ValueError('money must be nonnegative exact decimal with at most two decimals')

SCHEMA="""
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, version TEXT NOT NULL, observed_at TEXT NOT NULL, content_hash TEXT NOT NULL, locator TEXT NOT NULL, notes TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS carriers(id TEXT PRIMARY KEY, name TEXT NOT NULL, normalized_name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, carrier_id TEXT NOT NULL REFERENCES carriers(id), source_id TEXT NOT NULL REFERENCES sources(id), source_row TEXT NOT NULL, emails TEXT NOT NULL, routes TEXT NOT NULL, coverage TEXT NOT NULL, observations TEXT NOT NULL, controls TEXT NOT NULL CHECK(controls IN ('unknown','checked','blocked')), checked_at TEXT, raw TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS trips(id TEXT PRIMARY KEY, carrier_id TEXT NOT NULL REFERENCES carriers(id), source_id TEXT NOT NULL REFERENCES sources(id), trip_ref TEXT UNIQUE, order_ref TEXT, pickup TEXT, origin TEXT NOT NULL, destination TEXT NOT NULL, state TEXT NOT NULL, notes TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id), order_ref TEXT NOT NULL, event_date TEXT NOT NULL, origin TEXT NOT NULL, destination TEXT NOT NULL, state TEXT NOT NULL, client_revenue TEXT, carrier_cost TEXT, market_estimate TEXT, currency TEXT NOT NULL, customer TEXT, carrier_name TEXT, observations TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS exclusions(kind TEXT NOT NULL CHECK(kind IN ('email','carrier')), value TEXT NOT NULL, reason TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(id), PRIMARY KEY(kind,value));
CREATE TABLE IF NOT EXISTS observations(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id), subject_kind TEXT NOT NULL, subject_ref TEXT NOT NULL, observed_at TEXT NOT NULL, text TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id TEXT PRIMARY KEY, event_at TEXT NOT NULL, action TEXT NOT NULL, record_id TEXT NOT NULL, source_id TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS records_carrier ON records(carrier_id);
CREATE INDEX IF NOT EXISTS records_source ON records(source_id);
CREATE INDEX IF NOT EXISTS trips_carrier ON trips(carrier_id);
CREATE INDEX IF NOT EXISTS operations_order ON operations(order_ref);
"""
TABLES=('sources','carriers','records','trips','operations','exclusions','observations','audit')

class Cache:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.db=sqlite3.connect(self.path,timeout=20)
        os.chmod(self.path,0o600)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript(SCHEMA)
        version=self.db.execute("SELECT value FROM meta WHERE key='version'").fetchone()
        if version and version[0]!=str(VERSION): raise ValueError('unsupported schema version')
        self.db.execute("INSERT OR IGNORE INTO meta VALUES('version',?)",(str(VERSION),));self.db.commit()
    def close(self): self.db.close()
    def source(self,key,version,locator='',content_hash='',notes=''):
        old=self.db.execute('SELECT version FROM sources WHERE id=?',(key,)).fetchone()
        if old and old[0]!=version:
            self.db.execute('DELETE FROM records WHERE source_id=?',(key,))
        self.db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version, observed_at=excluded.observed_at, content_hash=excluded.content_hash, locator=excluded.locator, notes=excluded.notes',(key,version,now(),content_hash,locator,notes))
    def log(self,action,key,source):
        version=self.db.execute('SELECT version FROM sources WHERE id=?',(source,)).fetchone()[0]
        aid=identifier('audit',action+'|'+key+'|'+source+'|'+version)
        self.db.execute('INSERT OR IGNORE INTO audit VALUES(?,?,?,?,?)',(aid,now(),action,key,source))
    def carrier(self,name):
        key=identifier('carrier',norm(name))
        self.db.execute('INSERT OR IGNORE INTO carriers VALUES(?,?,?)',(key,name,norm(name)))
        return key
    def record(self,source,row,values,controls='unknown',checked_at=None):
        if len(values)!=19: raise ValueError('directory record needs 19 columns')
        if controls not in ('unknown','checked','blocked'): raise ValueError('invalid controls')
        if controls=='checked' and not checked_at: raise ValueError('checked controls require timestamp')
        key=identifier('record',source+'|'+str(row));cid=self.carrier(values[0])
        self.db.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET carrier_id=excluded.carrier_id, emails=excluded.emails, routes=excluded.routes, coverage=excluded.coverage, observations=excluded.observations, controls=excluded.controls, checked_at=excluded.checked_at, raw=excluded.raw',(key,cid,source,str(row),json.dumps(emails(values[12])),values[10],values[9],values[15],controls,checked_at,json.dumps(values,ensure_ascii=False)))
        self.log('directory-upsert',key,source);return cid
    def exclude(self,kind,value,reason,source):
        if kind not in ('email','carrier'): raise ValueError('invalid exclusion kind')
        value=value.lower() if kind=='email' else norm(value)
        self.db.execute('INSERT INTO exclusions VALUES(?,?,?,?) ON CONFLICT(kind,value) DO UPDATE SET reason=excluded.reason,source_id=excluded.source_id',(kind,value,reason,source))
    def trip(self,source,carrier_name,origin,destination,trip_ref=None,order_ref=None,pickup=None,state='recorded',notes=''):
        if state not in {'recorded','assigned','picked','delivered','provisional','cancelled'}: raise ValueError('invalid trip state')
        cid=self.carrier(carrier_name)
        # Without source IDs preserve provisional identity; never promote a screenshot summary to completed trip.
        key=identifier('trip',str(trip_ref)) if trip_ref else identifier('provisional',source+'|'+cid+'|'+str(pickup)+'|'+origin+'|'+destination)
        self.db.execute('INSERT INTO trips VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET source_id=excluded.source_id,state=excluded.state,notes=excluded.notes',(key,cid,source,trip_ref,order_ref,pickup,origin,destination,state,notes))
        self.log('trip-upsert',key,source);return key
    def operation(self,source,order_ref,event_date,origin,destination,state='draft',client_revenue=None,carrier_cost=None,market_estimate=None,currency='EUR',customer=None,carrier_name=None,observations=''):
        if state not in {'draft','available','offered','assigned','picked','delivered','cancelled','invoiced'}: raise ValueError('invalid operation state')
        date.fromisoformat(event_date)
        if not re.fullmatch('[A-Z]{3}',currency): raise ValueError('invalid currency')
        key=identifier('operation',order_ref+'|'+event_date+'|'+state)
        self.db.execute('INSERT INTO operations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET client_revenue=COALESCE(excluded.client_revenue,operations.client_revenue),carrier_cost=COALESCE(excluded.carrier_cost,operations.carrier_cost),market_estimate=COALESCE(excluded.market_estimate,operations.market_estimate),customer=COALESCE(excluded.customer,operations.customer),carrier_name=COALESCE(excluded.carrier_name,operations.carrier_name),observations=CASE WHEN LENGTH(excluded.observations)=0 THEN operations.observations ELSE excluded.observations END',(key,source,order_ref,event_date,origin,destination,state,money(client_revenue),money(carrier_cost),money(market_estimate),currency,customer,carrier_name,observations))
        self.log('operation-upsert',key,source);return key
    def observation(self,source,subject_kind,subject_ref,text,observed_at=None):
        if subject_kind not in {'carrier','operation','route','general'} or not text.strip(): raise ValueError('invalid observation')
        observed_at=observed_at or now()
        key=identifier('note',source+'|'+subject_kind+'|'+subject_ref+'|'+text+'|'+observed_at)
        self.db.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?,?,?,?)',(key,source,subject_kind,subject_ref,observed_at,text))
        return key
    def query(self,region,basis='declared',direction='any',approved_only=False,max_age_hours=24):
        region=norm(region)
        if region not in REGIONS: raise ValueError('supported regions: '+', '.join(REGIONS))
        if basis not in {'declared','history','delivered','coverage','any'}: raise ValueError('invalid basis')
        if direction not in {'any','to','from'}: raise ValueError('invalid direction')
        if direction!='any' and basis in {'declared','coverage','any'}: raise ValueError('direction requires structured history/delivered evidence')
        excluded_emails={r[0] for r in self.db.execute("SELECT value FROM exclusions WHERE kind='email'")}
        excluded_carriers={r[0] for r in self.db.execute("SELECT value FROM exclusions WHERE kind='carrier'")}
        blocked_ids={r[0] for r in self.db.execute("SELECT carrier_id FROM records WHERE controls='blocked'")}
        found=[];out_emails=[];unknown=0
        for carrier in self.db.execute('SELECT * FROM carriers ORDER BY normalized_name'):
            if carrier['normalized_name'] in excluded_carriers or norm(carrier['name'].split(' - ')[0]) in excluded_carriers or carrier['id'] in blocked_ids: continue
            records=[dict(r) for r in self.db.execute('SELECT * FROM records WHERE carrier_id=?',(carrier['id'],))]
            evidence=[]
            if basis in {'declared','any','coverage'}:
                for r in records:
                    field='coverage' if basis=='coverage' else 'routes'
                    if region in regions(r[field]): evidence.append({'kind':'coverage' if field=='coverage' else 'declared_route','text':r[field],'source_id':r['source_id'],'source_row':r['source_row']})
            if basis in {'history','delivered','any'}:
                for trip in self.db.execute('SELECT * FROM trips WHERE carrier_id=?',(carrier['id'],)):
                    if trip['state']=='cancelled' or (basis=='delivered' and trip['state']!='delivered'): continue
                    if trip['state']=='provisional': continue
                    route=trip['destination'] if direction=='to' else trip['origin'] if direction=='from' else trip['origin']+' '+trip['destination']
                    if region in regions(route): evidence.append({'kind':'delivered_trip' if trip['state']=='delivered' else 'recorded_trip','trip_ref':trip['trip_ref'],'state':trip['state'],'text':trip['origin']+' → '+trip['destination'],'source_id':trip['source_id']})
            if not evidence: continue
            if approved_only:
                eligible=[]
                for r in records:
                    try: age=(datetime.now(timezone.utc)-datetime.fromisoformat(r['checked_at'])).total_seconds();fresh=0<=age<=max_age_hours*3600
                    except (TypeError,ValueError): fresh=False
                    if r['controls']=='checked' and fresh: eligible.append(r)
                records=eligible
                if not records: continue
            elif any(r['controls']!='checked' for r in records): unknown+=1
            addresses=list(dict.fromkeys(e for r in records for e in json.loads(r['emails']) if e not in excluded_emails))
            found.append({'carrier':carrier['name'],'emails':addresses,'evidence':evidence,'controls':'checked' if records and all(r['controls']=='checked' for r in records) else 'unverified'})
            out_emails.extend(addresses)
        return {'region':region,'basis':basis,'direction':direction,'approved_only':approved_only,'carriers':found,'emails':list(dict.fromkeys(out_emails)),'unverified_carriers':unknown,'sources':[dict(r) for r in self.db.execute('SELECT * FROM sources')],'scope':'cached documentary lookup; not current availability or approval'}
    def sales(self,region=None,customer=None,completed_only=False):
        if region is not None and norm(region) not in REGIONS: raise ValueError('unsupported region')
        results=[]
        for raw in self.db.execute('SELECT * FROM operations ORDER BY event_date,order_ref,state'):
            row=dict(raw)
            if region and norm(region) not in regions(row['origin']+' '+row['destination']): continue
            if customer and norm(customer) not in norm(row['customer'] or ''): continue
            if completed_only and row['state'] not in {'delivered','invoiced'}: continue
            results.append(row)
        return results
    def snapshot(self,path):
        self.db.commit()
        data={'schema_version':VERSION,'exported_at':now(),'tables':{table:[dict(r) for r in self.db.execute('SELECT * FROM '+table+' ORDER BY 1')] for table in TABLES}}
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd,tmp=tempfile.mkstemp(prefix='snapshot-',dir=path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as out: json.dump(data,out,ensure_ascii=False,indent=2)
            os.chmod(tmp,0o600);os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        return data
    def restore(self,data):
        if data.get('schema_version')!=VERSION or set(data.get('tables',{}))!=set(TABLES): raise ValueError('invalid snapshot schema')
        if any(self.db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in TABLES): raise ValueError('restore requires empty cache; never overwrite existing history')
        with self.db:
            for table in TABLES:
                columns=[r[1] for r in self.db.execute('PRAGMA table_info('+table+')')]
                for row in data['tables'][table]:
                    if set(row)!=set(columns): raise ValueError('invalid columns for '+table)
                    self.db.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in columns)+')',[row[k] for k in columns])
        return self.stats()
    def stats(self): return {t:self.db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in TABLES}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',default=os.environ.get('XPO_CACHE_DB','private/cache/xpo-cache.sqlite3'))
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('stats');sub.add_parser('init')
    sales=sub.add_parser('sales');sales.add_argument('--region');sales.add_argument('--customer');sales.add_argument('--completed-only',action='store_true')
    notes=sub.add_parser('notes');notes.add_argument('--subject')
    query=sub.add_parser('query');query.add_argument('region');query.add_argument('--basis',choices=['declared','history','delivered','coverage','any'],default='declared');query.add_argument('--direction',choices=['any','to','from'],default='any');query.add_argument('--approved-only',action='store_true');query.add_argument('--emails',action='store_true')
    export=sub.add_parser('export');export.add_argument('path')
    restore=sub.add_parser('restore');restore.add_argument('path')
    ingest=sub.add_parser('ingest');ingest.add_argument('path',help='JSON payload with source and records/trips/operations/exclusions')
    args=parser.parse_args();cache=Cache(args.db)
    try:
        if args.action in {'init','stats'}: print(json.dumps(cache.stats()))
        elif args.action=='sales': print(json.dumps(cache.sales(args.region,args.customer,args.completed_only),ensure_ascii=False,indent=2))
        elif args.action=='notes':
            result=[dict(r) for r in cache.db.execute('SELECT * FROM observations ORDER BY observed_at') if not args.subject or args.subject==r['subject_ref']]
            print(json.dumps(result,ensure_ascii=False,indent=2))
        elif args.action=='query':
            result=cache.query(args.region,args.basis,args.direction,args.approved_only)
            if args.emails:
                print('; '.join(result['emails'])+(';' if result['emails'] else ''))
                print(json.dumps({k:result[k] for k in ['basis','direction','approved_only','unverified_carriers','scope']}),file=__import__('sys').stderr)
            else: print(json.dumps(result,ensure_ascii=False,indent=2))
        elif args.action=='export': cache.snapshot(args.path);print('Exported private snapshot')
        elif args.action=='restore': print(json.dumps(cache.restore(json.loads(Path(args.path).read_text()))))
        else:
            data=json.loads(Path(args.path).read_text());source=data['source'];key=source['key']
            with cache.db:
                cache.source(**source)
                for row in data.get('records',[]): cache.record(key,**row)
                for trip in data.get('trips',[]): cache.trip(key,**trip)
                for operation in data.get('operations',[]): cache.operation(key,**operation)
                for observation in data.get('observations',[]): cache.observation(key,**observation)
                for rule in data.get('exclusions',[]): cache.exclude(source=key,**rule)
            print(json.dumps(cache.stats()))
        return 0
    except (ValueError,sqlite3.Error) as exc:
        print(str(exc),file=__import__('sys').stderr);return 1
    finally: cache.close()

if __name__=='__main__': raise SystemExit(main())

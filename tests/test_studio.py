from datetime import date
from decimal import Decimal
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from loadstudio.models import Load, Rules, CorridorRate, Window
from loadstudio.engine import render, DEFAULT_RULES, AUDIT
from loadstudio.ingest import parse, workbook_preview, import_rows
from loadstudio.store import Store
from loadstudio.app import create_app

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validate_wtransnet.py')
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)

def good(**kw):
    data=dict(reference='SYN-001',customer='XPO TRANSPORT SOLUTIONS SPAIN SL',origin={'country':'ES','postcode':'28909','locality':'Getafe'},
              destination={'country':'PT','postcode':'2675-076','locality':'Odivelas'},pickup={'date':'2026-10-20','start':'10:00','end':'16:00'},
              delivery={'date':'2026-10-21','start':'12:00','end':'13:00'},service='FTL',weight_kg='15000',goods_es='Aceite',goods_en='Oil',client_price_eur='900.00')
    data.update(kw);return Load.model_validate(data)

def out(**kw):return render(good(**kw),reviewed=True)

FOTE='''Order # 99000001 GETAFE, 28 ODIVELAS, 11
Pick Up
20 Oct, 2026 10:00-16:00
Delivery
21 Oct, 2026 12:00-13:00
Revenue
900,00 EUR
Cost
1200,00 EUR
General
Order #:
99000001
Equipment Type:
Tautliner standard
Customer Service Type:
T100 (Full Truck Load)
Commodity:
OIL
Weight
15000 kg(s)
15000 kg(s)
Linear Meters
0.000 0.000
Origin
Location:
XPO GETAFE
Address:
CALLE SINTETICA 1
GETAFE, 28 28909
ES
Destination
Location:
DESTINATARIO SINTETICO
Address:
CALLE SINTETICA 2
ODIVELAS, 11 2675-076
PT
Related Orders
No Orders found
Customer
Name:
XPO TRANSPORT SOLUTIONS SPAIN SL
'''
# Synthetic structural fixture, no real order/customer prices or contact details.

@pytest.fixture
def client(tmp_path):
    app=create_app(tmp_path,testing=True)
    with TestClient(app) as c:
        c.headers['X-XPO-Token']=app.state.token
        yield c

def test_audit_primary_manifest():
    assert AUDIT['sha256']=='836b2eb26bf7d33e1ae21bf266416b9ffdc68507db4fb14dc7178c52afe9c1f3'
    assert len(AUDIT['headers'])==26 and len(AUDIT['validations'])==12
    assert len(AUDIT['catalogs']['NombresVehiculos'])==27
    assert AUDIT['nonblank_input_cells_below_header']==0
    assert AUDIT['validations'][0]['ranges']==['N2:W39','Z2:Z39']
    assert next(d for d in AUDIT['validations'] if d['ranges']==['E2:E39'])['allow_blank'] is False
    assert next(d for d in AUDIT['validations'] if d['ranges']==['Y2:Y39'])['formula2']==99999

def test_golden_text():
    x=out();lines=x['markdown'].splitlines()
    assert lines[0]=='**20/10/2026 \u2014 GETAFE \u2192 ODIVELAS \u2014 Ref.: SYN-001**'
    assert lines[1]=='**Origen** / *Origin*: 28909'
    assert lines[2]=='**Destino** / *Destination*: 2675-076'
    assert lines[3]=='**Tipo** / *Type*: FTL \u00b7 Trailer Tautliner \u00b7 15 t \u00b7 13,6 m'
    assert lines[-1]=='**Precio mercado estimado** / *Estimated market price*: Por confirmar / To be confirmed'
    assert '<strong>900' not in x['html'] and '<em>Oil' not in x['html']

def test_tsv_roundtrip():
    x=out();r=x['tsv'].split('\t');assert len(r)==26 and r[24:]==['','']
    assert r[6]=='2675' and r[11]=='15' and r[12]=='13,6'
    assert not validator.errors_for_row(r,1)

def test_review_gate():
    assert render(good())['tsv'] is None
    assert render(Load(),reviewed=True)['tsv'] is None

def test_reference_missing_blocks():assert not out(reference=None)['can_export']
def test_missing_price_not_fabricated():assert 'Por confirmar' in out(client_price_eur=None)['markdown']
def test_unknown_adr_is_empty():assert out()['columns'][13]==''
def test_zero_kept_but_not_valid_for_actual_load():assert not out(weight_kg=0)['can_export']
def test_customer_rate_independence():assert out(client_price_eur='9')['market_basis']==out(client_price_eur='90000')['market_basis']==[]

@pytest.mark.parametrize('customer,note',[('TCL','Indicar matr\u00edculas.'),('Mattel','Indicar matr\u00edculas y nombre del conductor.')])
def test_notes_exact_last(customer,note):
    x=out(customer=customer);assert x['markdown'].splitlines()[-1]=='NOTA: '+note
    assert 'NOTA:' not in x['columns'][23]

def test_seb_center_guard():
    assert 'NOTA:' not in out(customer='Groupe SEB')['markdown']
    assert 'Adelantar' in out(customer='Groupe SEB',origin={'country':'ES','postcode':'45340','locality':'Ontigola','center':'DHL ONTIGOLA'})['markdown']

def test_no_geographic_customer_note():
    assert 'NOTA:' not in out(customer='OTRO',origin={'country':'ES','postcode':'45340','locality':'Ontigola','center':'DHL ONTIGOLA'})['markdown']

@pytest.mark.parametrize('weight,length,expected',[ (None,None,('2000','5')),('4567',None,('4567','5')),(None,'6.3',('2000','6.3')),('4567','6.3',('4567','6.3'))])
def test_lg_fieldwise(weight,length,expected):
    x=out(customer='LX Pantos',service='GROUPAGE',weight_kg=weight,linear_meters=length)['load'];assert (x['weight_kg'],x['linear_meters'])==expected

def test_lg_ftl_not_group_defaults():assert not out(customer='LG',weight_kg=None)['can_export']
def test_actual_centers_win():assert out(origin={'country':'ES','postcode':'28918','locality':'Leganes','center':'XPO LEGANES'})['load']['origin']['postcode']=='28918'

def test_diversey_current_hours():
    x=out(customer='Diversey',origin={'country':'ES','postcode':'45200','locality':'Illescas'});assert x['columns'][13:15]==['S','S'];assert x['load']['pickup']['start']=='10:00:00';assert x['load']['pickup']['end']=='16:00:00'
def test_diversey_false_not_overwritten():
    x=out(customer='Diversey',adr=False,origin={'country':'ES','postcode':'45200','locality':'Illescas'});assert x['columns'][13]=='N';assert any(i['field']=='adr' for i in x['issues'])
def test_multi_stop_not_collapsed():assert not out(stop_count=3)['can_export']

@pytest.mark.parametrize('bad',['=HYPERLINK("bad")','+cmd','@formula','ref\tnew','ref\nnew'])
def test_tsv_injection(bad):assert not out(reference=bad)['can_export']

def test_html_escaping():
    x=out(goods_es='<script>alert(1)</script>');assert '<script>' not in x['html'];assert '&lt;script&gt;' in x['html']
def test_window_invalid():
    with pytest.raises(ValueError):Window(date='2026-10-20',start='19:00',end='08:00')
def test_invalid_date():
    with pytest.raises(ValueError):good(pickup={'date':'2026-02-31'})
def test_no_extra_fields():
    with pytest.raises(ValueError):good(market_price='950')

def test_fote_parser():
    f=FOTE.replace('900,00 EUR','900,00 \u20ac');d=parse(f)[0];x=render(Load.model_validate(d['load']),reviewed=True)
    assert x['can_export'];assert x['load']['reference']=='99000001';assert x['load']['client_price_eur']=='900.00'
    assert x['load']['origin']['postcode']=='28909';assert x['load']['destination']['postcode']=='2675-076'
    assert x['load']['weight_kg']=='15000';assert x['load']['linear_meters']=='13.6'
def test_fote_conflict_not_last_wins():
    d=parse(FOTE.replace('15000 kg(s)','15000 kg(s)',1)+'\n18000 kg(s)')[0]
    assert d['load']['weight_kg'] is None
    assert any(i['field']=='weight_kg' for i in d['issues'])
def test_fote_multiple_orders():assert len(parse(FOTE+'\n'+FOTE.replace('99000001','99000002')))==2

def test_text_parsing():
    d=parse('Referencia: SYN-001\nOrigen: ES 28909 Getafe\nDestino: PT 2675-076 Odivelas\nPeso: 15 t\nRecogida: 20/10/2026 10-16\nDescarga: 21/10/2026 12-13\nServicio: FTL\nMercancia: Aceite / Oil',mode='text')[0]
    assert render(Load.model_validate(d['load']),reviewed=True)['can_export']
def test_missing_year():
    d=parse('Recogida: 20/10 10-16',mode='text')[0];assert d['load']['pickup']['date'] is None and d['issues']
def test_text_no_guess():assert parse('Carga para Portugal ya sabes cual',mode='text')[0]['issues']

def test_excel_preview_and_mapping():
    b=Workbook();s=b.active;s.append(['Referencia','CP origen','Peso']);s.append(['SYN-001','01001',15]);f=io.BytesIO();b.save(f)
    rows=workbook_preview(f.getvalue())[0]['rows'];d=import_rows(rows[1:],{'reference':0,'origin.postcode':1,'weight_t':2})[0]
    assert d['load']['origin']['postcode']=='01001';assert d['load']['weight_kg']=='15000'
def test_excel_formula_and_numeric_postcode_rejected():
    d=import_rows([['=CMD()',1001]],{'reference':0,'origin.postcode':1})[0];assert len(d['issues'])==2

def test_history_dedup_different_inputs(tmp_path):
    s=Store(tmp_path/'test.sqlite3');a=s.save(out());assert not a['duplicate']
    assert s.save(out(source_hash='other'))['duplicate']
    b=s.save(out(reference='SYN-002'));assert not b['duplicate'] and not b['related']
    revision=s.save(out(weight_kg='16000'));assert revision['related']==[a['id']]
def test_history_requires_review(tmp_path):
    with pytest.raises(ValueError):Store(tmp_path/'a.db').save(render(good()))
def test_rules_versioning_and_restore(tmp_path):
    s=Store(tmp_path/'a.db');r=s.rules();r.revision=2;r.reason='Nota revisada';r.notes['TCL']='Nota alternativa'
    s.update_rules(r,1);assert s.rules().notes['TCL']=='Nota alternativa'
    restored=s.restore_rules(1,2);assert restored.revision==3 and restored.notes==DEFAULT_RULES.notes
    with pytest.raises(ValueError):s.update_rules(r,1)
def test_rules_no_arbitrary_code(tmp_path):
    r=DEFAULT_RULES.model_copy(deep=True);r.revision=2;r.notes['EVIL']='eval()'
    with pytest.raises(ValueError):Store(tmp_path/'a.db').update_rules(r,1)
def test_backup_restore(tmp_path):
    s=Store(tmp_path/'a.db');s.save(out());target=s.backup(tmp_path/'backup.db');restored=Store(target);assert len(restored.history())==1
    with pytest.raises(ValueError):s.backup(target)

def rate():return CorridorRate(id='SYNTHETIC',origin_country='Espa\u00f1a',origin_prefix='289',destination_country='Portugal',destination_prefix='267',service='FTL',vehicle='Trailer',adr=False,base_eur='500',per_km_eur='1',max_weight_kg='24000',max_linear_meters='13.6',valid_from='2026-01-01',valid_until='2026-12-31',source='Synthetic test only; not a real quote')
def test_corridor_price_and_no_revenue():
    a=render(good(adr=False,distance_km='600'),rates=[rate()],reviewed=True)
    b=render(good(adr=False,distance_km='600',client_price_eur='1'),rates=[rate()],reviewed=True)
    assert a['market_basis']==b['market_basis'];assert '1100' in a['markdown']
def test_corridor_no_distance_no_guess():assert render(good(adr=False),rates=[rate()])['market_basis']==[]
def test_corridor_no_adr_no_guess():assert render(good(distance_km='600'),rates=[rate()])['market_basis']==[]

@pytest.mark.parametrize('path',['/','/api/health','/static/app.js'])
def test_pages(client,path):assert client.get(path).status_code==200

def test_api_auth(client):
    client.headers.pop('X-XPO-Token');assert client.get('/api/history').status_code==401

def test_api_origin(client):assert client.post('/api/parse',json={'text':''},headers={'Origin':'https://evil.example'}).status_code==403
def test_api_host(client):assert client.get('/api/health',headers={'Host':'evil.example'}).status_code==403
def test_api_save_and_history(client):
    data={'load':good().model_dump(mode='json'),'reviewed':True}
    assert client.post('/api/render',json=data).json()['can_export']
    assert client.post('/api/save',json=data).status_code==200
    assert len(client.get('/api/history').json())==1

def test_cli_valid_and_empty(tmp_path):
    p=tmp_path/'valid.tsv';p.write_text(out()['tsv']+'\n',encoding='utf-8');assert validator.main(p)==0
    p.write_text('');assert validator.main(p)==1
@pytest.mark.parametrize('pos,value',[(1,'31/02/2026'),(24,'800'),(9,'UNKNOWN'),(23,'x'*501),(13,'NO')])
def test_validator_negative(pos,value):
    r=out()['columns'];r[pos]=value;assert validator.errors_for_row(r,1)

def test_audit_reader_rejects_invalid():
    spec=importlib.util.spec_from_file_location('xls_audit',ROOT/'scripts/audit_xls.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError):module.inspect(b'not an XLS')

def test_source_conflict_not_replaced_by_lg_defaults():
    d=parse('Cliente: LG\nServicio: GRUPAJE\nPeso: 2 t\nPeso: 5 t',mode='text')[0]
    x=render(Load.model_validate(d['load']),reviewed=True)
    assert x['load']['weight_kg'] is None and not x['can_export']
    assert 'weight_kg' in x['load']['blocked_fields']

def test_engine_same_semantics_different_source_hash():
    assert out(source_hash='a')['fingerprint']==out(source_hash='b')['fingerprint']


def test_decimal_scale_has_same_fingerprint():
    assert render(good(weight_kg='15000.00'))['fingerprint']==render(good(weight_kg='15000'))['fingerprint']

def test_rigid_does_not_default_trailer():
    x=render(good(service='RIGID',vehicle=None))
    assert x['load']['vehicle'] is None
    assert not x['can_export']

def test_conflict_time_never_filled_by_rule():
    x=render(good(customer='Diversey',origin={'country':'ES','postcode':'45200','locality':'Illescas'},pickup={'date':'2026-10-20'},blocked_fields=['pickup']))
    assert x['load']['pickup']['start'] is None
    assert not x['can_export']


def test_future_database_schema_is_not_downgraded(tmp_path):
    path=tmp_path/'future.sqlite3'
    with sqlite3.connect(path) as db:db.execute('PRAGMA user_version=2')
    with pytest.raises(ValueError):Store(path)
    with sqlite3.connect(path) as db:assert db.execute('PRAGMA user_version').fetchone()[0]==2

def test_excel_truncation_is_visible():
    book=Workbook();sheet=book.active
    for i in range(60):sheet.append(['SYN-'+str(i)])
    data=io.BytesIO();book.save(data)
    assert workbook_preview(data.getvalue())[0]['truncated'] is True

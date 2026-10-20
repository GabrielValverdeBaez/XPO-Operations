from decimal import Decimal
import pytest
from pydantic import ValidationError
from loadstudio.models import Load, PackageDimensions, IntermediateStop
from loadstudio.engine import render, DEFAULT_RULES
from loadstudio.route_features import dimension_meters, norauto_matches, CENTER_CODES
from loadstudio.ingest import parse, import_rows
from test_studio import good, rate, validator


def stop(**kw):
    data={'action':'DELIVERY','place':{'country':'ES','postcode':'26150','locality':'Logrono'},'window':{'date':'2026-10-21','start':'08:00','end':'09:00'}}
    data.update(kw);return data

def mult(**kw):
    data={'origin':{'country':'ES','postcode':'45224','locality':'Sesena'},'destination':{'country':'ES','postcode':'31119','locality':'Pamplona'},'stop_count':3,'intermediate_stops':[stop()]}
    data.update(kw);return good(**data)

def dims(**kw):
    data={'customer':'LG','service':'GROUPAGE','linear_meters':None,'packages':[{'length_m':'1.2','width_m':'.8','quantity':7}], 'dimensions_confirmed':True}
    data.update(kw);return good(**data)


def test_dimensions_exact_footprint():
    assert dimension_meters(dims())==Decimal('2.80')
    x=render(dims(),reviewed=True);assert x['load']['linear_meters']=='2.8'
    assert x['provenance']['linear_meters']['rule_id']=='confirmed_dimensions'
    assert x['can_export']

def test_dimensions_precede_europallet_fallback():
    x=render(dims(pallets=99,euro_pallets_confirmed=True),reviewed=True)
    assert x['load']['linear_meters']=='2.8'

def test_dimensions_precede_lg_missing_length():
    x=render(dims(weight_kg=None),reviewed=True)
    assert x['load']['linear_meters']=='2.8' and x['load']['weight_kg']=='2000'

def test_dimensions_actual_length_kept():
    x=render(dims(linear_meters='6.30'),reviewed=True)
    assert x['load']['linear_meters']=='6.3' and any(i['field']=='linear_meters' for i in x['issues'])

def test_dimensions_unconfirmed_blocks_no_fallback():
    x=render(dims(dimensions_confirmed=False),reviewed=True)
    assert not x['can_export'] and x['load']['linear_meters'] is None

def test_dimensions_never_convert_ftl():
    x=render(dims(service='FTL'),reviewed=True);assert x['load']['linear_meters']=='13.6'

def test_dimensions_round_two_decimal():
    assert dimension_meters(dims(packages=[{'length_m':1,'width_m':1,'quantity':1}]))==Decimal('.42')

@pytest.mark.parametrize('field,value',[('length_m',0),('width_m',-1),('quantity',0),('length_m','NaN'),('width_m','Infinity')])
def test_bad_dimensions_rejected(field,value):
    item={'length_m':1,'width_m':1,'quantity':1};item[field]=value
    with pytest.raises(ValidationError):PackageDimensions(**item)

def test_multistop_preserves_order_and_times():
    x=render(mult(),reviewed=True);assert x['can_export']
    text=x['markdown'];assert 'SESENA \u2192 LOGRONO \u2192 PAMPLONA' in text
    assert '**Parada 1** / *Stop 1*: 26150' in text
    assert '**Descarga parada 1** / *Stop 1 delivery*: 21/10/2026, 08:00\u201309:00' in text
    assert 'Parada 1 Descarga 26150 Logrono' in x['columns'][23]
    assert x['columns'][4]=='Sesena' and x['columns'][7]=='Pamplona'
    assert len(x['tsv'].split('\t'))==26 and not validator.errors_for_row(x['columns'],1)

def test_multistop_empty_details_blocked():
    assert not render(mult(intermediate_stops=[]),reviewed=True)['can_export']
def test_multistop_count_mismatch_blocked():
    assert not render(mult(stop_count=2),reviewed=True)['can_export']
def test_multistop_incomplete_cp_blocked():
    assert not render(mult(intermediate_stops=[stop(place={'country':'ES','locality':'Logrono'})]),reviewed=True)['can_export']
def test_multistop_missing_date_blocked():
    assert not render(mult(intermediate_stops=[stop(window={})]),reviewed=True)['can_export']
def test_multistop_date_out_of_order_blocked():
    assert not render(mult(intermediate_stops=[stop(window={'date':'2026-10-19'})]),reviewed=True)['can_export']
def test_multistop_final_before_intermediate_blocked():
    assert not render(mult(intermediate_stops=[stop(window={'date':'2026-10-22'})]),reviewed=True)['can_export']
def test_multistop_formula_rejected_deeply():
    x=render(mult(intermediate_stops=[stop(place={'country':'ES','postcode':'26150','locality':'=formula'})]),reviewed=True)
    assert not x['can_export']

def test_multistop_comment_length_never_truncated():
    stops=[stop(place={'country':'ES','postcode':'26150','locality':'L'*60}) for _ in range(8)]
    x=render(mult(stop_count=10,intermediate_stops=stops),reviewed=True)
    assert not x['can_export'] and len(x['columns'][23])>500

def test_norauto_pattern_fills_only_missing():
    x=render(mult(customer='Norauto',service_code='NT014',service=None,weight_kg=None,linear_meters=None),reviewed=True)
    assert x['can_export'];assert x['load']['service']=='FTL';assert x['load']['weight_kg']=='20000'
    assert x['load']['linear_meters']=='13.6';assert x['columns'][13:15]==['N','N']
    assert x['load']['pickup']['start']=='10:00:00'

def test_norauto_pattern_keeps_actual_quantities():
    x=render(mult(customer='Norauto',service_code='NT014',weight_kg=18000,linear_meters=12,adr=True),reviewed=True)
    assert x['load']['weight_kg']=='18000' and x['load']['linear_meters']=='12' and x['columns'][13]=='S'

@pytest.mark.parametrize('change',[{'customer':'OTHER'},{'service_code':'NT215'},{'service':'GROUPAGE'}, {'origin':{'country':'ES','postcode':'28909','locality':'Getafe'}},{'intermediate_stops':[stop(action='PICKUP')]},{'destination':{'country':'PT','postcode':'2675','locality':'Odivelas'}}])
def test_norauto_pattern_not_broad(change):
    data={'customer':'Norauto','service_code':'NT014','service':None,'weight_kg':None};data.update(change)
    x=render(mult(**data),reviewed=True)
    assert x['load']['weight_kg'] is None

def test_intermediate_center_alias_and_provenance():
    x=render(mult(intermediate_stops=[stop(place={'country':'ES','locality':'Arrubal','center':'XPO ARRUBAL'})]),reviewed=True)
    assert x['load']['intermediate_stops'][0]['place']['postcode']=='26150'
    assert x['provenance']['intermediate_stops.0.place.postcode']['rule_id']=='center_exact'

def test_multistop_no_direct_corridor_tariff():
    x=render(good(adr=False,distance_km=600,stop_count=3,intermediate_stops=[stop()]),rates=[rate()],reviewed=True)
    assert not x['market_basis']

def test_multiarrow_is_not_silently_direct():
    x=parse('ES 28909 Getafe -> ES 26150 Logrono -> ES 31119 Pamplona',mode='text')[0]
    assert x['load']['stop_count']==3 and x['load']['destination']['postcode']=='31119'
    assert not render(Load.model_validate(x['load']),reviewed=True)['can_export']

def test_import_stop_count_preserved():
    x=import_rows([['SYN-ROUTE',3]],{'reference':0,'stop_count':1})[0]
    assert x['load']['stop_count']==3

def test_json_dimensions_semantic_fingerprint():
    a=dims(packages=[{'length_m':'1.20','width_m':'.80','quantity':7}])
    assert render(a)['fingerprint']==render(dims())['fingerprint']

@pytest.mark.parametrize('place,expected',[
    ({'country':'ES','locality':'Burgos'},'09001'),
    ({'country':'ES','locality':'Burgos','center':'XPO BURGOS'},'09006'),
    ({'country':'PT','locality':'Carnaxide'},'2795'),
    ({'country':'ES','locality':'Ontigola'},'45340'),
])
def test_secondary_locality_aliases(place,expected):
    assert render(good(origin=place))['load']['origin']['postcode']==expected

def test_center_country_conflict_blocks():
    x=render(good(origin={'country':'FR','locality':'Leganes','center':'XPO LEGANES'}),reviewed=True)
    assert not x['can_export'] and x['load']['origin']['postcode'] is None

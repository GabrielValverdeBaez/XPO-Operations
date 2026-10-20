"""Explicit route stops and dimensional metrage; no inferred intermediate sites."""
from decimal import Decimal, ROUND_HALF_UP
from .models import Issue

CENTER_CODES = {
 'XPO LEGANES':'28911','XPO LEDONO':'15189','XPO CULLEREDO':'15189',
 'XPO ARRUBAL':'26150','XPO LOGRONO':'26150',
 'XPO PAMPLONA IMARCOAIN':'31119','XPO IMARCOAIN':'31119',
 'XPO SANTURTZI':'48980','CELERITAS ALOVERA':'19208',
 'NORAUTO SESENA DHL':'45224','DHL ONTIGOLA':'45340',
 'XPO LISBOA FORTE DA CASA':'2625-445','XPO POMBAL':'3100-354',
 'XPO OPORTO CANELAS':'4410-528','XPO BURGOS':'09006'
}

PORTUGUESE_CENTERS={'XPO LISBOA FORTE DA CASA','XPO POMBAL','XPO OPORTO CANELAS'}
LOCALITY_CODES={('ESPANA','ONTIGOLA'):'45340',('ESPANA','BURGOS'):'09001',('PORTUGAL','CARNAXIDE'):'2795'}

def route_places(load):
    return [('origin',load.origin)]+[(f'intermediate_stops.{i}.place',s.place) for i,s in enumerate(load.intermediate_stops)]+[('destination',load.destination)]

def dimension_meters(load):
    """The confirmed physical footprint divided by 2.40 m, not an FTL conversion."""
    if load.service != 'GROUPAGE' or not load.dimensions_confirmed or not load.packages:
        return None
    return (sum(p.length_m*p.width_m*p.quantity for p in load.packages)/Decimal('2.40')).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)

def norauto_matches(load, normalize):
    if normalize(load.customer)!='NORAUTO' or normalize(load.service_code)!='NT014':return False
    if load.service not in (None,'FTL'):return False
    if load.stop_count!=3 or len(load.intermediate_stops)!=1:return False
    stop=load.intermediate_stops[0]
    if stop.action!='DELIVERY':return False
    if any(normalize(p.country) not in ('ES','ESPANA') for _,p in route_places(load)):return False
    origin=normalize(load.origin.locality)=='SESENA'
    middle=normalize(stop.place.locality)=='LOGRONO' or (normalize(stop.place.locality)=='ARRUBAL' and normalize(stop.place.center) in ('XPO ARRUBAL','XPO LOGRONO'))
    final=normalize(load.destination.locality) in ('PAMPLONA','IMARCOAIN')
    return origin and middle and final

def route_issues(load):
    result=[]
    def error(field,msg):result.append(Issue(field=field,message=msg,severity='error'))
    if load.stop_count != 2+len(load.intermediate_stops):
        error('stop_count','El numero de paradas no coincide con el itinerario: completar todas las paradas intermedias')
    previous=load.pickup.date
    for i,stop in enumerate(load.intermediate_stops):
        key=f'intermediate_stops.{i}.window.date'
        if not stop.window.date:error(key,'Fecha de parada intermedia necesaria')
        elif previous and stop.window.date<previous:error(key,'Paradas fuera de orden cronologico')
        if stop.window.date:previous=stop.window.date
    if previous and load.delivery.date and load.delivery.date<previous:
        error('delivery.date','La descarga final es anterior a una parada intermedia')
    return result

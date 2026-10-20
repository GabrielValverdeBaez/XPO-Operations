"""One deterministic rules/formatting implementation for every input adapter."""
from __future__ import annotations
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import html
import json
import re
import unicodedata
from pathlib import Path
from .models import Load, Issue, Rules, CorridorRate
from .route_features import CENTER_CODES, PORTUGUESE_CENTERS, LOCALITY_CODES, route_places, dimension_meters, norauto_matches, route_issues

ROOT = Path(__file__).resolve().parents[1]
AUDIT = json.loads((ROOT/'evidence/template-audit.json').read_text(encoding='utf-8'))
HEADERS = AUDIT['headers']
CATALOG = {k:[row[0] for row in v if row and row[0] is not None] for k,v in AUDIT['catalogs'].items()}
DEFAULT_RULES = Rules(revision=1, reason='Reglas del operador confirmadas el 20/10/2026', notes={
 'SEB':'Adelantar hora de posicionamiento. Indicar matr\u00edculas.',
 'TCL':'Indicar matr\u00edculas.', 'MATTEL':'Indicar matr\u00edculas y nombre del conductor.'
}, enabled={k:True for k in ['defaults','lg','diversey','danone','loreal','pepco','norauto','goods','centers']})
COUNTRIES={'ES':'Espa\u00f1a','PT':'Portugal','FR':'Francia','DE':'Alemania','IT':'Italia','NL':'Holanda','BE':'B\u00e9lgica','GB':'Reino Unido'}
NOTES_KEYS=set(DEFAULT_RULES.notes)


def normalized(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(s or '')) if not unicodedata.combining(c)).upper().strip()

def client_id(s):
    aliases={'LG':'LG','LX PANTOS':'LG','LG ELECTRONICS':'LG','GROUPE SEB':'SEB','TCL':'TCL','MATTEL':'MATTEL',
             'DIVERSEY':'DIVERSEY','AGUAS DANONE':'DANONE','DANONE SIGUENZA':'DANONE_SIGUENZA',
             "L'OREAL":'LOREAL','LOREAL':'LOREAL','PEPCO':'PEPCO','NORAUTO':'NORAUTO','FASSA':'FASSA',
             'MANGO':'MANGO','ID LOGISTICS':'IDLOG','XPO TRANSPORT SOLUTIONS SPAIN SL':'XPO'}
    return aliases.get(normalized(s))

def check_rules(rules):
    if set(rules.notes)!=NOTES_KEYS or set(rules.enabled)!=set(DEFAULT_RULES.enabled):
        raise ValueError('No se pueden introducir clientes ni reglas ejecutables arbitrarias')
    for note in rules.notes.values():
        if len(note)>500 or any(c in note for c in '\r\n\t<>'):
            raise ValueError('Nota invalida: una linea, maximo 500 caracteres, sin HTML')

def rule_apply(raw: Load, rules: Rules):
    check_rules(rules)
    load=raw.model_copy(deep=True);provenance={};issues=[]
    def fill(obj,attr,value,key,rule):
        if any(key==f or key.startswith(f+'.') for f in load.blocked_fields): return
        if value is not None and getattr(obj,attr) is None:
            setattr(obj,attr,value);provenance[key]={'source':'rule','rule_id':rule,'revision':rules.revision}
    for label,p in route_places(load):
        if p.country in COUNTRIES: p.country=COUNTRIES[p.country]
        if rules.enabled['centers']:
            center=normalized(p.center)
            expected_country='Portugal' if center in PORTUGUESE_CENTERS else 'Espa\u00f1a'
            if center in CENTER_CODES and p.country and p.country!=expected_country:
                issues.append(Issue(field=label+'.country',message='Pais incompatible con el centro identificado: revisar la contradiccion',severity='error'))
            else:
                fill(p,'postcode',CENTER_CODES.get(center),label+'.postcode','center_exact')
                fill(p,'postcode',LOCALITY_CODES.get((normalized(p.country),normalized(p.locality))),label+'.postcode','locality_confirmed_alias')
    codes={'T100':'FTL','TR014':'FTL','NTIE1':'FTL','NT214':'GROUPAGE'}
    fill(load,'service',codes.get(normalized(load.service_code)),'service','service_exact')
    if normalized(load.vehicle)=='TAUTLINER STANDARD': load.vehicle='Trailer';fill(load,'body','Tautliner','body','equipment_exact')
    if rules.enabled['defaults']:
        if load.service != 'RIGID': fill(load,'vehicle','Trailer','vehicle','default_trailer')
        if load.vehicle == 'Trailer': fill(load,'body','Tautliner','body','default_body')
    if load.service=='FTL' and load.vehicle in ('Trailer','Trailer Mega'):
        fill(load,'linear_meters',Decimal('13.6'),'linear_meters','ftl_length')
    if load.service_code=='NTIE1': fill(load,'weight_kg',Decimal('24000'),'weight_kg','ntie1_weight')
    cid=client_id(load.customer)
    if rules.enabled['norauto'] and norauto_matches(load,normalized):
        for attr,value in [('service','FTL'),('weight_kg',Decimal('20000')),('linear_meters',Decimal('13.6')),('adr',False),('palletized',False)]:
            fill(load,attr,value,attr,'norauto_exact_multidrop')
    if load.service=='GROUPAGE' and load.packages:
        calculated=dimension_meters(load)
        if load.linear_meters is None:
            if calculated is None:issues.append(Issue(field='dimensions_confirmed',message='Confirmar las dimensiones antes de calcular ML; no se sustituye por un fallback',severity='error'))
            else:fill(load,'linear_meters',calculated,'linear_meters','confirmed_dimensions')
        elif calculated is not None and load.linear_meters!=calculated:
            issues.append(Issue(field='linear_meters',message='ML explicitos distintos del calculo por dimensiones: se conserva el dato actual para revision'))
    if load.service=='GROUPAGE' and not load.packages and load.euro_pallets_confirmed and load.pallets is not None:
        fill(load,'linear_meters',Decimal(load.pallets)*Decimal('.40'),'linear_meters','euro_pallets')
    if cid=='LG' and load.service=='GROUPAGE' and rules.enabled['lg']:
        fill(load,'weight_kg',Decimal('2000'),'weight_kg','lg_weight_missing')
        if not load.packages:fill(load,'linear_meters',Decimal('5'),'linear_meters','lg_length_missing')
    if cid=='DIVERSEY' and normalized(load.origin.locality)=='ILLESCAS' and rules.enabled['diversey']:
        if load.adr is False: issues.append(Issue(field='adr',message='Excepcion a Diversey ADR: revisar expresamente antes de copiar'))
        fill(load,'adr',True,'adr','diversey_adr');fill(load,'palletized',True,'palletized','diversey_palletized')
        # Only fill a wholly absent time window. Never mix an explicit time with a historical endpoint.
        if load.pickup.start is None:
            fill(load.pickup,'start',__import__('datetime').time(10),'pickup.start','diversey_times')
            if load.pickup.start is not None:fill(load.pickup,'end',__import__('datetime').time(19),'pickup.end','diversey_times')
        if load.delivery.date is None and load.pickup.date: fill(load.delivery,'date',load.pickup.date+timedelta(days=1),'delivery.date','diversey_nextday')
        fill(load.delivery,'start',__import__('datetime').time(6),'delivery.start','diversey_time_missing')
    if cid in ('DANONE','LOREAL','DANONE_SIGUENZA') and rules.enabled['danone' if cid!='LOREAL' else 'loreal']:
        fill(load,'adr',False,'adr','client_nonadr')
        if cid!='DANONE_SIGUENZA': fill(load,'palletized',True,'palletized','client_palletized')
    if cid=='PEPCO' and rules.enabled['pepco'] and load.service in (None,'FTL'):
        fill(load,'service','FTL','service','pepco_ftl');fill(load,'weight_kg',Decimal(12000),'weight_kg','pepco_weight')
        fill(load,'linear_meters',Decimal('13.6'),'linear_meters','pepco_length')
        fill(load.pickup,'start',__import__('datetime').time(13),'pickup.start','pepco_time')
        if load.delivery.date is None and load.pickup.date: fill(load.delivery,'date',load.pickup.date+timedelta(days=1),'delivery.date','pepco_nextday')
        if load.delivery.start is None:
            fill(load.delivery,'start',__import__('datetime').time(11),'delivery.start','pepco_times')
            if load.delivery.start is not None:fill(load.delivery,'end',__import__('datetime').time(14),'delivery.end','pepco_times')
    if cid=='NORAUTO' and load.service_code=='NT014' and not norauto_matches(load,normalized): issues.append(Issue(field='service',message='Norauto NT014 no coincide con el itinerario confirmado: no se aplica el patron'))
    if rules.enabled['goods']:
        goods={'LG':('Electronica y electrodomesticos paletizados','Palletized electronics and household appliances'),
               'SEB':('Peque\u00f1os electrodom\u00e9sticos','Small household appliances'),'MANGO':('Ropa','Clothing'),
               'DANONE':('Agua paletizada','Palletized water'),'DANONE_SIGUENZA':('Agua paletizada','Palletized water'),
               'DIVERSEY':('Productos ADR paletizados','Palletized ADR products'),
               'XPO':('Mercanc\u00eda paletizada','Palletized goods'),'IDLOG':('Mercanc\u00eda paletizada','Palletized goods')}
        if load.goods_es is None and load.goods_en is None and cid in goods:
            if cid!='DIVERSEY' or load.adr is True:
                fill(load,'goods_es',goods[cid][0],'goods_es','client_goods');fill(load,'goods_en',goods[cid][1],'goods_en','client_goods')
    if 'refrigerated_ok' not in load.options: load.options['refrigerated_ok']=cid!='FASSA'
    note=rules.notes.get(cid,'')
    if cid=='SEB' and normalized(load.origin.center)!='DHL ONTIGOLA':
        note='';issues.append(Issue(field='origin.center',message='Nota SEB requiere centro DHL Ontigola confirmado'))
    if cid is None and load.customer: issues.append(Issue(field='customer',message='Cliente sin reglas particulares: no se extrapolan notas'))
    for path,value in flatten(raw.model_dump(mode='json')).items():
        if value is not None and path not in provenance: provenance[path]={'source':'input'}
    return load,provenance,issues,note


def validate(load: Load):
    issues=[]
    def error(field,message): issues.append(Issue(field=field,message=message,severity='error'))
    for field in load.blocked_fields: error(field,'Conflicto de origen pendiente: corregir este campo manualmente')
    for field,value in [('reference',load.reference),('service',load.service),('pickup.date',load.pickup.date),('delivery.date',load.delivery.date),('goods_es',load.goods_es),('goods_en',load.goods_en)]:
        if value is None or value=='': error(field,'Campo necesario por confirmar')
    for side,p in route_places(load):
        if p.country not in CATALOG['NombresPaises'] or p.country=='Pa\u00eds por defecto': error(side+'.country','Pais no confirmado o fuera de catalogo')
        if not p.locality or len(p.locality)>60: error(side+'.locality','Localidad necesaria, maximo 60 caracteres')
        pattern=r'[0-9]{5}' if p.country=='Espa\u00f1a' else r'[0-9]{4}(?:-[0-9]{3})?' if p.country=='Portugal' else r'.{2,12}'
        if not p.postcode or not re.fullmatch(pattern,p.postcode): error(side+'.postcode','Codigo postal ausente o incompatible con el pais')
    issues.extend(route_issues(load))
    if load.vehicle not in CATALOG['NombresVehiculos']: error('vehicle','Vehiculo fuera del catalogo real')
    if load.service=='RIGID' and load.vehicle in ('Trailer','Trailer Mega'): error('vehicle','Un servicio rigido no se asigna a un trailer')
    if load.weight_kg is None or load.weight_kg<=0: error('weight_kg','Peso real por confirmar (no capacidad del camion)')
    if load.linear_meters is None or load.linear_meters<=0: error('linear_meters','Metros lineales por confirmar')
    if load.pickup.date and load.delivery.date and load.delivery.date<load.pickup.date: error('delivery.date','Descarga anterior a recogida')
    if load.adr is None: issues.append(Issue(field='adr',message='ADR no confirmado: se deja vacio, no se interpreta como N'))
    for key,value in flatten(load.model_dump(mode='json')).items():
        if isinstance(value,str) and (any(c in value for c in '\r\n\t\x00') or value.lstrip().startswith(('=','+','-','@'))):
            error(key,'Valor con controles o formula de hoja de calculo: revisar, no se ejecuta')
    return issues

def flatten(d,prefix=''):
    out={}
    for k,v in d.items():
        key=prefix+k
        if isinstance(v,dict):out.update(flatten(v,key+'.'))
        elif isinstance(v,list):out.update(flatten({str(i):item for i,item in enumerate(v)},key+'.'))
        else:out[key]=v
    return out

def amount(v,places=None):
    if v is None:return 'Por confirmar / To be confirmed'
    v=Decimal(v)
    if places is not None: v=v.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
    text=format(v,'f')
    if places is None and '.' in text:text=text.rstrip('0').rstrip('.')
    return text.replace('.',',')

def window(w):
    result=w.date.strftime('%d/%m/%Y') if w.date else 'Por confirmar / To be confirmed'
    if w.start:result+=', '+w.start.strftime('%H:%M')
    if w.end:result+='\u2013'+w.end.strftime('%H:%M')
    return result

def estimate(load, rates):
    # Corridor table describes direct routes; never price a multistop as direct.
    if load.intermediate_stops or load.stop_count!=2:return None,[]
    if load.adr is None or not load.pickup.date or not load.weight_kg or not load.linear_meters: return None,[]
    matches=[]
    for r in rates:
        if (load.origin.country==r.origin_country and (load.origin.postcode or '').startswith(r.origin_prefix)
            and load.destination.country==r.destination_country and (load.destination.postcode or '').startswith(r.destination_prefix)
            and load.service==r.service and load.vehicle==r.vehicle and load.adr==r.adr
            and load.weight_kg<=r.max_weight_kg and load.linear_meters<=r.max_linear_meters
            and r.valid_from<=load.pickup.date<=r.valid_until):
            if r.per_km_eur and load.distance_km is None:continue
            value=r.base_eur+r.extras_eur+r.per_km_eur*(load.distance_km or 0)
            matches.append((len(r.origin_prefix)+len(r.destination_prefix),value,r))
    if not matches:return None,[]
    best=max(x[0] for x in matches); selected=[x for x in matches if x[0]==best]
    values=sorted(x[1] for x in selected);n=len(values)
    median=values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2
    price=(median/Decimal(25)).quantize(Decimal(1),rounding=ROUND_HALF_UP)*25
    return price,[{'id':x[2].id,'source':x[2].source,'value':str(x[1])} for x in selected]

def render(raw: Load, rules: Rules=DEFAULT_RULES, rates=(), reviewed=False):
    load,provenance,issues,note=rule_apply(raw,rules);issues+=validate(load)
    market,basis=estimate(load,rates)
    route_title=' \u2192 '.join((p.locality or '?').upper() for _,p in route_places(load))
    header=f"{load.pickup.date.strftime('%d/%m/%Y') if load.pickup.date else 'Por confirmar'} \u2014 {route_title} \u2014 Ref.: {load.reference or '?'}"
    types=[{'FTL':'FTL','GROUPAGE':'Grupaje / Groupage','RIGID':'Rigido completo / Full rigid'}.get(load.service,'Por confirmar'),load.vehicle or '',load.body or '']
    vehicle=' '.join(x for x in types[1:] if x)
    type_line=' \u00b7 '.join([types[0],vehicle]+([amount(load.weight_kg/1000)+' t'] if load.weight_kg is not None else [])+([amount(load.linear_meters)+' m'] if load.linear_meters is not None else [])+(['ADR'] if load.adr is True else [])+(['paletizado / palletized'] if load.palletized is True else []))
    fields=[('Origen','Origin',load.origin.postcode or '?'),('Destino','Destination',load.destination.postcode or '?'),('Tipo','Type',type_line),
            ('Mercanc\u00eda','Goods',(load.goods_es or '?')+' / '+(load.goods_en or '?')),('Recogida','Pickup',window(load.pickup)),('Descarga','Delivery',window(load.delivery)),
            ('Precio cliente','Client price',amount(load.client_price_eur,2)+(' \u20ac' if load.client_price_eur is not None else '')),
            ('Precio mercado estimado','Estimated market price',amount(market)+(' \u20ac' if market is not None else ''))]
    # Stops keep route order; only postcodes appear in their address fields.
    if load.intermediate_stops:
        fields[1:1]=[(f'Parada {i+1}',f'Stop {i+1}',stop.place.postcode or '?') for i,stop in enumerate(load.intermediate_stops)]
        delivery_index=next(i for i,f in enumerate(fields) if f[1]=='Delivery')
        fields[delivery_index:delivery_index]=[((f'Carga parada {i+1}' if stop.action=='PICKUP' else f'Descarga parada {i+1}'),(f'Stop {i+1} pickup' if stop.action=='PICKUP' else f'Stop {i+1} delivery'),window(stop.window)) for i,stop in enumerate(load.intermediate_stops)]
    def md_escape(v):return re.sub(r'([\\`*_{}\[\]<>])',r'\\\1',str(v))
    md='**'+md_escape(header)+'**\n'+'\n'.join(f'**{es}** / *{en}*: {md_escape(value)}' for es,en,value in fields)
    plain=header+'\n'+'\n'.join(f'{es} / {en}: {value}' for es,en,value in fields)
    rich='<strong>'+html.escape(header)+'</strong><br>'+'<br>'.join(f'<strong>{html.escape(es)}</strong> / <em>{en}</em>: {html.escape(value)}' for es,en,value in fields)
    if note:md+='\nNOTA: '+md_escape(note);plain+='\nNOTA: '+note;rich+='<br>NOTA: '+html.escape(note)
    row=['']*26
    row[:13]=[load.reference or '',load.pickup.date.strftime('%d/%m/%Y') if load.pickup.date else '',load.origin.country or '',(load.origin.postcode or '')[:4] if load.origin.country=='Portugal' else load.origin.postcode or '',load.origin.locality or '',load.destination.country or '',(load.destination.postcode or '')[:4] if load.destination.country=='Portugal' else load.destination.postcode or '',load.destination.locality or '',{'FTL':'Tr\u00e1ilers Completos','GROUPAGE':'Grupajes','RIGID':'R\u00edgidos Completos'}.get(load.service,''),load.vehicle or '','Carga General',amount(load.weight_kg/1000) if load.weight_kg is not None else '',amount(load.linear_meters) if load.linear_meters is not None else '']
    sn=lambda v: 'S' if v is True else 'N' if v is False else ''
    row[13:15]=[sn(load.adr),sn(load.palletized)]
    for index,key in [(15,'pallet_exchange'),(16,'gps'),(17,'top'),(18,'side'),(19,'rear'),(20,'refrigerated_ok'),(21,'low_side_ok'),(22,'same_specialty'),(25,'alert')]:row[index]=sn(load.options.get(key))
    def comment(label,w):
        if not w.date:return ''
        s=f'{label}: '+w.date.strftime('%d/%m/%Y')
        if w.start:s+=(' de ' if w.end else ' a las ')+w.start.strftime('%H:%M')
        if w.end:s+=' a '+w.end.strftime('%H:%M')
        return s+'.'
    intermediate_comments=[]
    for i,stop in enumerate(load.intermediate_stops):
        action='Carga' if stop.action=='PICKUP' else 'Descarga'
        label=f'Parada {i+1} {action} {stop.place.postcode or "?"} {stop.place.locality or "?"}'
        intermediate_comments.append(comment(label,stop.window))
    row[23]=' '.join(filter(None,[comment('Carga',load.pickup),*intermediate_comments,comment('Descarga',load.delivery)]))
    if len(row[23])>500:issues.append(Issue(field='intermediate_stops',message='Comentarios superan 500 caracteres; no se truncan paradas',severity='error'))
    row[24]=''
    can_export=reviewed and not any(i.severity=='error' for i in issues)
    fingerprint=hashlib.sha256(json.dumps(load.model_dump(mode='json',exclude={'source_hash'}),sort_keys=True,ensure_ascii=True).encode()).hexdigest()
    return {'load':load.model_dump(mode='json'),'provenance':provenance,'issues':[i.model_dump() for i in issues],
            'markdown':md,'plain':plain,'html':rich,'tsv':'\t'.join(row) if can_export else None,'columns':row,
            'can_export':can_export,'reviewed':reviewed,'rules_revision':rules.revision,'fingerprint':fingerprint,'market_basis':basis,
            'status':'REVIEWED' if can_export else 'DRAFT'}

#!/usr/bin/env python3
"""Validate the inspected template plus explicit XPO output policies; never edits XLS."""
from datetime import datetime
import json
from pathlib import Path
import re
import sys

AUDIT=json.loads((Path(__file__).resolve().parents[1]/'evidence/template-audit.json').read_text(encoding='utf-8'))
CAT={k:{r[0] for r in v if r and r[0] is not None} for k,v in AUDIT['catalogs'].items()}
EXPECTED=26
BOOLEAN_COLS=(*range(13,23),25)
BOLSAS=CAT['NombresTiposBolsa']
VEHICULOS=CAT['NombresVehiculos']

def errors_for_row(row,row_number):
    prefix=f'fila {row_number}: '
    if len(row)!=26:return [prefix+f'{len(row)} columnas; esperadas 26']
    errors=[]
    def error(s):errors.append(prefix+s)
    if any(not isinstance(v,str) for v in row):return [prefix+'Todos los campos deben ser texto']
    for pos,v in enumerate(row):
        if any(c in v for c in '\r\n\t\x00'):error(f'control incrustado en columna {pos+1}')
        if v.lstrip().startswith(('=','+','-','@')):error(f'formula/prefijo peligroso en columna {pos+1}')
    if not row[0]:error('Referencia obligatoria en el flujo XPO')
    if row[24]!='':error('columna Y/Precio debe estar vacia')
    try:
        if not re.fullmatch(r'[0-9]{2}/[0-9]{2}/[0-9]{4}',row[1]):raise ValueError()
        datetime.strptime(row[1],'%d/%m/%Y')
    except ValueError:error('Fecha B invalida')
    for col,catalog in [(2,'NombresPaises'),(5,'NombresPaises'),(8,'NombresTiposBolsa'),(9,'NombresVehiculos'),(10,'NombresEspecialidades')]:
        if row[col] not in CAT[catalog]:error(f'columna {col+1}: fuera de catalogo real')
    if row[10]!='Carga General':error('K debe ser Carga General por politica XPO')
    for pos in BOOLEAN_COLS:
        if row[pos] not in ('S','N',''):error(f'columna {pos+1}: solo S/N/vacio')
    for country,cp,city in ((2,3,4),(5,6,7)):
        pattern=r'[0-9]{5}' if row[country]=='Espa\u00f1a' else r'[0-9]{4}' if row[country]=='Portugal' else r'.{2,12}'
        if not re.fullmatch(pattern,row[cp]):error('CP invalido')
        if not row[city] or len(row[city])>60:error('Localidad necesaria y maximo 60 caracteres')
    for pos in (11,12):
        if row[pos] and not re.fullmatch(r'[0-9]+(?:,[0-9]+)?',row[pos]):error('Peso/largo: numero no negativo con coma')
    if len(row[23])>500:error('Comentarios: maximo 500 por politica XPO')
    return errors

def main(path):
    try:raw=Path(path).read_text(encoding='utf-8-sig')
    except (OSError,UnicodeError) as e:print(str(e),file=sys.stderr);return 2
    rows=raw.splitlines();errors=[]
    if not rows:errors.append('archivo vacio')
    if len(rows)>50:errors.append('maximo 50 ofertas por lote')
    for n,line in enumerate(rows,1):errors.extend(errors_for_row(line.split('\t'),n))
    if errors:print('\n'.join(errors),file=sys.stderr);return 1
    if len(rows)>38:print('AVISO: el XLS suministrado solo tiene DV hasta la fila 39; dividir el pegado en lotes de 38.',file=sys.stderr)
    print('PASS: contrato XLS inspeccionado + reglas XPO; no prueba aceptacion por el servicio Wtransnet')
    return 0

if __name__=='__main__':
    if len(sys.argv)!=2:print('Uso: python scripts/validate_wtransnet.py archivo.tsv',file=sys.stderr);sys.exit(2)
    sys.exit(main(sys.argv[1]))

#!/usr/bin/env python3
"""Offline extraction and structural validation; never writes to a service."""
import argparse
import re
import sys
from pathlib import Path

EMAIL = re.compile(r"(?<![\w.+-])[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+")
MODES = {'Carretera', 'Marítimo', 'Aéreo', 'Ferroviario', 'Multimodal'}

def extract_emails(text, blocked=()):
    excluded = {value.lower() for value in blocked}
    return list(dict.fromkeys(value.lower() for value in EMAIL.findall(text) if value.lower() not in excluded))

def directory_errors(text):
    errors = []
    lines = text.splitlines()
    if not lines:
        return ['lote vacío']
    for n, line in enumerate(lines, 1):
        cells = line.split('\t')
        if len(cells) != 19:
            errors.append(f'fila {n}: se requieren 19 columnas'); continue
        if not cells[0].strip():
            errors.append(f'fila {n}: falta empresa/delegación')
        modes = {x.strip() for x in cells[2].split(';') if x.strip()}
        if not modes or not modes <= MODES:
            errors.append(f'fila {n}: modo físico no reconocido')
        if cells[13]:
            errors.append(f'fila {n}: Contactos secundarios debe estar vacío')
        if cells[5] in {'España', 'Portugal'}:
            width = 5 if cells[5] == 'España' else 4
            if not re.fullmatch(r'\d{' + str(width) + '}', cells[7]):
                errors.append(f'fila {n}: CP no conforme con país')
        if cells[12]:
            parts = [x.strip() for x in cells[12].split(';') if x.strip()]
            if not cells[12].endswith(';') or any(not EMAIL.fullmatch(x) for x in parts):
                errors.append(f'fila {n}: correos inválidos o sin punto y coma final')
            if len({x.lower() for x in parts}) != len(parts):
                errors.append(f'fila {n}: correos duplicados')
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    email = sub.add_parser('emails')
    email.add_argument('--blocked', type=Path, help='Lista privada; no versionar')
    sub.add_parser('directory')
    args = parser.parse_args()
    data = sys.stdin.read()
    if args.action == 'emails':
        blocked = extract_emails(args.blocked.read_text(encoding='utf-8')) if args.blocked else []
        result = extract_emails(data, blocked)
        print('; '.join(result) + (';' if result else ''))
        print('Extracción documental; comprobar exclusiones de empresa/rojo y vigencia antes de uso comercial.', file=sys.stderr)
        return 0
    errors = directory_errors(data)
    if errors:
        print('\n'.join(errors), file=sys.stderr); return 1
    print('PASS: estructura de 19 columnas; no valida formato, maestro ni aprobación comercial')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

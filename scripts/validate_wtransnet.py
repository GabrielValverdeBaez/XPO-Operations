#!/usr/bin/env python3
"""Validador provisional de filas TSV Wtransnet A:Z. Solo biblioteca estándar.

Uso: python3 scripts/validate_wtransnet.py ruta/al/archivo.tsv
No edita archivos ni accede a servicios. No equivale a validar contra el XLSX real.
"""
import csv
from datetime import datetime
import re
import sys
from pathlib import Path

EXPECTED = 26
BOOLEAN_COLS = (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25)
BOLSAS = {"Grupajes", "Rígidos Completos", "Tráilers Completos"}
VEHICULOS = {"Trailer", "Trailer Mega", "Camión Remolque", "Camión 3 ejes", "Camión 4 ejes", "Camión 2 ejes > 7,5 T. MMA", "Furgonetas"}


def errors_for_row(row, row_number):
    errors = []
    if len(row) != EXPECTED:
        return [f"fila {row_number}: {len(row)} columnas; esperadas {EXPECTED}"]
    if row[24] != "":
        errors.append(f"fila {row_number}: columna Y/Precio debe estar vacía")
    try:
        if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", row[1]):
            raise ValueError("format")
        datetime.strptime(row[1], "%d/%m/%Y")
    except ValueError:
        errors.append(f"fila {row_number}: fecha B inválida")
    if row[8] not in BOLSAS:
        errors.append(f"fila {row_number}: I/Tipo Bolsa no reconocido")
    if row[9] not in VEHICULOS:
        errors.append(f"fila {row_number}: J/Tipo Vehículo no reconocido")
    for pos in BOOLEAN_COLS:
        if row[pos] not in ("S", "N", ""):
            errors.append(f"fila {row_number}: {chr(65+pos)} admite solo S/N/vacío")
    for country_pos, cp_pos in ((2,3),(5,6)):
        country, cp = row[country_pos], row[cp_pos]
        regex = r"\d{5}" if country == "España" else r"\d{4}" if country == "Portugal" else None
        if regex and not re.fullmatch(regex, cp):
            errors.append(f"fila {row_number}: CP inválido para {country}")
    if len(row[23]) > 500:
        errors.append(f"fila {row_number}: X/Comentarios supera 500 caracteres")
    for pos in (11, 12):
        if row[pos] and not re.fullmatch(r"\d+(,\d+)?", row[pos]):
            errors.append(f"fila {row_number}: {chr(65+pos)} debe ser número no negativo con coma")
    return errors


def main(path):
    failures = []
    count = 0
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, delimiter="\t")
        for n, row in enumerate(rows, 1):
            count += 1
            failures.extend(errors_for_row(row, n))
    if count == 0:
        failures.append("archivo vacío")
    if count > 50:
        failures.append("máximo 50 ofertas por lote")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: estructura y valores preliminares coherentes (no auditado contra plantilla oficial)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 scripts/validate_wtransnet.py archivo.tsv", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

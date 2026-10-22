#!/usr/bin/env python3
"""Valida filas TSV de A:Z para la plantilla de carga masiva Wtransnet."""

from __future__ import annotations

import argparse
import math
from datetime import datetime
import re
import sys
from pathlib import Path


TIPOS_BOLSA = {"Grupajes", "Rígidos Completos", "Tráilers Completos"}
TIPOS_VEHICULO = {
    "Bitrén", "Caja móvil (sólo caja)", "Camión < 7,5 T. MMA", "Camión Grúa",
    "Camión Remolque", "Camión remolque mega", "Camión 2 ejes > 7,5 T. MMA",
    "Camión 3 ejes", "Camión 3,5 T. MMA", "Camión 4 ejes", "City Trailer",
    "Contenedor 20'", "Contenedor 30'", "Contenedor 40'", "Contenedor 45'",
    "Cualquiera", "Furgonetas", "Portacontenedor 20'", "Portacontenedor 30'",
    "Portacontenedor 40'", "Portacontenedor 45'", "Tractora", "Tractora Mega",
    "Trailer", "Trailer altura regulable", "Trailer doble Piso", "Trailer Mega",
}
ESPECIALIDADES = {
    "Bañera", "Bañera Chatarrera", "Basculantes", "Carga General",
    "Cist. Combustibles", "Cist. Gases", "Cist. Líquidos No Alimen.",
    "Cist. Pulverul. Alimen.", "Cist. Pulverul. No Alimen.", "Cisterna Alimen.",
    "Enganche", "Especiales", "Frigo carne colgada", "Frigolona", "Frigorífico",
    "Frigorífico con termógrafo", "Frigorífico doble piso",
    "Frigorífico doble temperatura", "Furgón", "Furgón Muebles", "Ganado",
    "Góndola", "Isotermo", "Jumbo", "Lateral Bajo", "Lateral bajo portabobinas",
    "Piso Móvil", "Plataforma", "Plataforma Extensible", "Porta caja móvil",
    "Porta Vehículos", "Portacontenedores", "Prenda colgada", "Semi-Tautliner",
    "Tautliner", "Tautliner-Portab.", "Tipo TIR",
}
PAISES = {
    "Albania", "Alemania", "Andorra", "Argelia", "Armenia", "Austria",
    "Azerbaiyán", "Bélgica", "Bielorussia", "Bosnia-Herzeg.", "Bulgaria",
    "Chipre", "Croacia", "Dinamarca", "Egipto", "Eslovaquia", "Eslovenia",
    "España", "Estonia", "Finlandia", "Francia", "Georgia", "Gibraltar",
    "Grecia", "Holanda", "Hungria", "Irak", "Iran", "Irlanda", "Islandia",
    "Italia", "Jordania", "Kazajistán", "Kirguistán", "Letonia", "Libia",
    "Liechtenstein", "Lituania", "Luxemburgo", "Macedonia", "Malta",
    "Marruecos", "Mauritania", "Moldavia", "Monaco", "Montenegro", "Noruega",
    "Polonia", "Portugal", "Reino Unido", "Rep. Checa", "Rumanía", "Rusia",
    "San Marino", "Serbia", "Siria", "Suecia", "Suiza", "Tayikistán", "Túnez",
    "Turkmenistán", "Turquía", "Ucrania", "Uzbekistán",
}
SI_NO_COLS = range(13, 23)
DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def number(value: str) -> float:
    return float(value.replace(",", "."))


def validate_row(line: str, row_num: int) -> list[str]:
    cells = line.rstrip("\r\n").split("\t")
    errors: list[str] = []
    if len(cells) != 26:
        return [f"fila {row_num}: {len(cells)} columnas; se requieren 26"]
    try:
        if not DATE_RE.fullmatch(cells[1]):
            raise ValueError
        datetime.strptime(cells[1], "%d/%m/%Y")
    except ValueError:
        errors.append(f"fila {row_num}: fecha inválida: {cells[1]!r}")
    for country_idx, cp_idx in ((2, 3), (5, 6)):
        pattern = r"\d{5}" if cells[country_idx] == "España" else r"\d{4}" if cells[country_idx] == "Portugal" else None
        if pattern and not re.fullmatch(pattern, cells[cp_idx]):
            errors.append(f"fila {row_num}: CP no conforme con país")
    if not cells[4].strip() or not cells[7].strip():
        errors.append(f"fila {row_num}: faltan localidades")
    for idx, label in ((2, "País origen"), (5, "País destino")):
        if cells[idx] not in PAISES:
            errors.append(f"fila {row_num}: {label} no admitido: {cells[idx]!r}")
    for idx, label in ((3, "CP origen"), (6, "CP destino")):
        if len(cells[idx]) < 2:
            errors.append(f"fila {row_num}: {label} debe tener al menos 2 caracteres")
    if cells[8] not in TIPOS_BOLSA:
        errors.append(f"fila {row_num}: Tipo Bolsa no admitido: {cells[8]!r}")
    if cells[9] not in TIPOS_VEHICULO:
        errors.append(f"fila {row_num}: Tipo Vehiculo no admitido: {cells[9]!r}")
    if cells[10] != "Carga General":
        errors.append(f"fila {row_num}: Especialidad debe ser siempre 'Carga General': {cells[10]!r}")
    for idx, label in ((11, "Peso"), (12, "Largo")):
        try:
            value = number(cells[idx])
            if not re.fullmatch(r"\d+(,\d+)?", cells[idx]) or not math.isfinite(value) or value <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"fila {row_num}: {label} debe ser numérico positivo: {cells[idx]!r}")
    for idx in SI_NO_COLS:
        if cells[idx] not in {"", "S", "N"}:
            errors.append(f"fila {row_num}: columna {idx + 1} solo admite S, N o vacío")
    if len(cells[23]) > 500:
        errors.append(f"fila {row_num}: Comentarios Públicos supera 500 caracteres")
    if cells[24]:
        errors.append(f"fila {row_num}: Precio debe estar vacío en el flujo XPO")
    if cells[25] not in {"", "S", "N"}:
        errors.append(f"fila {row_num}: Activar Serv. Alerta solo admite S, N o vacío")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", help="TSV; si se omite, lee stdin")
    args = parser.parse_args()
    text = Path(args.path).read_text(encoding="utf-8") if args.path else sys.stdin.read()
    lines = [line for line in text.splitlines() if line.strip("\t\r\n")]
    if not lines:
        print("error: lote vacío", file=sys.stderr)
        return 1
    if len(lines) > 50:
        print(f"error: {len(lines)} ofertas; la plantilla admite 50", file=sys.stderr)
        return 1
    errors = [error for i, line in enumerate(lines, 2) for error in validate_row(line, i)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {len(lines)} filas válidas, 26 columnas A:Z")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

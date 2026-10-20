# Wtransnet - Contrato auditado del XLS original

Fuente: archivo `es_EUR_CG (1).xls` aportado por el operador, **no publicado**. SHA-256 `836b2eb26bf7d33e1ae21bf266416b9ffdc68507db4fb14dc7178c52afe9c1f3` (61.952 bytes). Auditada directamente la estructura CFB/BIFF8 el 20/10/2026. Hoja Ofertas: 26 encabezados A:Z, once auxiliares AA:AK, cero celdas de ofertas no vacias bajo el encabezado.

La fuente de datos para el programa es `evidence/template-audit.json`. Incluye los encabezados exactos con sus acentos, catalogos, nombres definidos y las **12 validaciones DV**. El catalogo de vehiculos tiene **27 valores**, no solo los siete valores de la lista preliminar. Hay 65 entradas en el catalogo de paises; las opciones por defecto no confirman un pais de una expedicion.

## A:Z en orden

| Columna | Campo |
|---|---|
| A | Referencia |
| B | Fecha disponibilidad |
| C | Pais origen |
| D | CP origen |
| E | Localidad origen |
| F | Pais destino |
| G | CP destino |
| H | Localidad destino |
| I | Tipo Bolsa |
| J | Tipo Vehiculo |
| K | Especialidad |
| L | Peso |
| M | Largo |
| N | Adr |
| O | Paletizado |
| P | Intercambio Palets |
| Q | Localizador GPS |
| R | Arriba |
| S | Lateral |
| T | Detras |
| U | Sirve Frigorifico |
| V | Sirve Lateral Bajo |
| W | Misma Especialidad |
| X | Comentarios Publicos |
| Y | Precio |
| Z | Activar Serv. Alerta |

Las grafias exactas del libro estan en el JSON, sin normalizacion. AA:AD son BLANK; AE EsViernes; AF FechaHoraDispInicio; AG IdTipoBolsa; AH IdTipoVehiculo; AI IdEspecialidad; AJ IdPaisOrigen; AK IdPaisDestino. No generar ni sobrescribir estos auxiliares.

## Validaciones observadas, no supuestas

| Rango | Restriccion DV | Permite blanco |
|---|---|---|
| N2:W39 y Z2:Z39 | Lista SiNo (S/N) | Si |
| M2:M39 | Decimal >= 0 | Si |
| AD2:AE39 | Tipo cualquier valor | Si |
| J2:J39 | NombresVehiculos | Si |
| K2:K39 | NombresEspecialidades | Si |
| I2:I39 | NombresTiposBolsa | Si |
| C2:C39 y F2:F39 | NombresPaises | Si |
| D2:D39 y G2:G39 | Longitud de texto >= 2 | Si |
| L2:L39 | Decimal >= 0 | Si |
| E2:E39 | Longitud de texto <= 60 | No |
| H2:H39 | Longitud de texto <= 60 | Si |
| Y2:Y39 | Decimal entre 0 y 99999 | No |

Estas validaciones terminan en la **fila 39: 38 ofertas**. La regla operativa de lotes de hasta 50 no demuestra que las filas siguientes del XLS esten validadas. El CLI avisa si el lote supera 38; la interfaz prepara una oferta cada vez. No hay una DV de fecha en B ni una DV de 500 caracteres en X: esos controles los aporta la politica de la aplicacion.

## Politica XPO diferenciada del libro

Y siempre vacia; texto y precio cliente/mercado fuera de TSV. Esta regla del operador prevalece para la salida, no es algo que se deduzca de la validacion numerica del XLS. Pais en espanol, ES CP de 5 cifras, PT CP de 4 en TSV y completo en texto; peso t y metros m con coma decimal; especialidad Carga General. ADR/paletizado desconocidos se dejan vacios, no N. Fecha B real DD/MM/AAAA; horarios en X y hasta 500 caracteres; conservar 26 celdas incluso vacias al final.

La aplicacion exige peso y ML positivos para confirmar una oferta; el libro admite cero, lo cual no confirma que el peso real sea cero. Formula inyectable o controles que rompan TSV se rechazan. No se inventan horas, paises ni precio de mercado.

## Reproduccion

```sh
python scripts/audit_xls.py /ruta/privada/es_EUR_CG.xls /ruta/privada/audit.json
python -m pytest -q
```

El lector no ejecuta macros ni formulas; falla ante estructuras fuera de su alcance. La repeticion exacta requiere el original privado. Los tests de CI usan el manifiesto auditado, no simulan disponer del original ni certifican un envio aceptado por Wtransnet. La aceptacion operativa permanece en T-008.

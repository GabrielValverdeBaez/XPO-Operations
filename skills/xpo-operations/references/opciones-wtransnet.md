# Opciones literales de la plantilla Wtransnet

Fuente: plantilla oficial aportada por el usuario `es_EUR_CG (1).xls`. La hoja `Ofertas` tiene 26 columnas editables (`A:Z`) y 11 columnas auxiliares (`AA:AK`). Las filas tabuladas deben incluir únicamente `A:Z`.

## Tipo Bolsa

- `Grupajes`
- `Rígidos Completos`
- `Tráilers Completos`

No usar `FTL`, `LTL`, `Grupaje` en singular ni códigos de servicio en esta columna.

## Tipo Vehiculo

- `Bitrén`
- `Caja móvil (sólo caja)`
- `Camión < 7,5 T. MMA`
- `Camión Grúa`
- `Camión Remolque`
- `Camión remolque mega`
- `Camión 2 ejes > 7,5 T. MMA`
- `Camión 3 ejes`
- `Camión 3,5 T. MMA`
- `Camión 4 ejes`
- `City Trailer`
- `Contenedor 20'`
- `Contenedor 30'`
- `Contenedor 40'`
- `Contenedor 45'`
- `Cualquiera`
- `Furgonetas`
- `Portacontenedor 20'`
- `Portacontenedor 30'`
- `Portacontenedor 40'`
- `Portacontenedor 45'`
- `Tractora`
- `Tractora Mega`
- `Trailer`
- `Trailer altura regulable`
- `Trailer doble Piso`
- `Trailer Mega`

Valores predeterminados de la plantilla para vehículos frecuentes:

| Tipo Vehiculo | Peso | Largo |
| --- | ---: | ---: |
| Trailer | 24 | 13,6 |
| Trailer Mega | 24 | 13,6 |
| Camión Remolque | 24 | 15,5 |
| Camión 2 ejes > 7,5 T. MMA | 10 | 7 |
| Camión 3 ejes | 16 | 8 |
| Camión 4 ejes | 22 | 10 |
| Camión < 7,5 T. MMA | 3,5 | 5 |
| Camión 3,5 T. MMA | 1,5 | 4 |
| Furgonetas | 1 | 3 |

Usar el peso real de la carga cuando conste. No sustituirlo por la capacidad del vehículo.

## Especialidad

- `Bañera`
- `Bañera Chatarrera`
- `Basculantes`
- `Carga General`
- `Cist. Combustibles`
- `Cist. Gases`
- `Cist. Líquidos No Alimen.`
- `Cist. Pulverul. Alimen.`
- `Cist. Pulverul. No Alimen.`
- `Cisterna Alimen.`
- `Enganche`
- `Especiales`
- `Frigo carne colgada`
- `Frigolona`
- `Frigorífico`
- `Frigorífico con termógrafo`
- `Frigorífico doble piso`
- `Frigorífico doble temperatura`
- `Furgón`
- `Furgón Muebles`
- `Ganado`
- `Góndola`
- `Isotermo`
- `Jumbo`
- `Lateral Bajo`
- `Lateral bajo portabobinas`
- `Piso Móvil`
- `Plataforma`
- `Plataforma Extensible`
- `Porta caja móvil`
- `Porta Vehículos`
- `Portacontenedores`
- `Prenda colgada`
- `Semi-Tautliner`
- `Tautliner`
- `Tautliner-Portab.`
- `Tipo TIR`

## Sí/No

En `Adr`, `Paletizado`, `Intercambio Palets`, `Localizador GPS`, `Arriba`, `Lateral`, `Detrás`, `Sirve Frigorifico`, `Sirve Lateral Bajo`, `Misma Especialidad` y `Activar Serv. Alerta`, usar solo:

- `S`
- `N`

Dejar vacío cuando la fuente no permita confirmarlo y el campo no sea obligatorio. No usar `Sí`, `No`, `True`, `False`, `0` ni `1`.

## Países

Usar el nombre literal, no el código ISO. Países habituales:

- `España`
- `Portugal`
- `Francia`
- `Alemania`
- `Italia`
- `Bélgica`
- `Holanda`
- `Reino Unido`

Otros valores disponibles: `Albania`, `Andorra`, `Argelia`, `Armenia`, `Austria`, `Azerbaiyán`, `Bielorussia`, `Bosnia-Herzeg.`, `Bulgaria`, `Chipre`, `Croacia`, `Dinamarca`, `Egipto`, `Eslovaquia`, `Eslovenia`, `Estonia`, `Finlandia`, `Georgia`, `Gibraltar`, `Grecia`, `Hungria`, `Irak`, `Iran`, `Irlanda`, `Islandia`, `Jordania`, `Kazajistán`, `Kirguistán`, `Letonia`, `Libia`, `Liechtenstein`, `Lituania`, `Luxemburgo`, `Macedonia`, `Malta`, `Marruecos`, `Mauritania`, `Moldavia`, `Monaco`, `Montenegro`, `Noruega`, `Polonia`, `Rep. Checa`, `Rumanía`, `Rusia`, `San Marino`, `Serbia`, `Siria`, `Suecia`, `Suiza`, `Tayikistán`, `Túnez`, `Turkmenistán`, `Turquía`, `Ucrania` y `Uzbekistán`.

No usar `País por defecto` en una oferta real.

## Restricciones verificadas

- Máximo de 50 ofertas: filas 2–51 de `Ofertas`.
- `Peso` y `Largo`: números positivos.
- `CP origen` y `CP destino`: al menos dos caracteres; conservar ceros iniciales.
- `Comentarios Públicos`: máximo 500 caracteres.
- `Precio`: entre 0 y 99.999; en el flujo actual debe permanecer vacío.
- Las columnas `AA:AK` contienen cálculos auxiliares y no deben formar parte de la fila copiable.

## Traducciones habituales desde exports XPO

| Valor del export | Tipo Bolsa | Tipo Vehiculo | Especialidad |
| --- | --- | --- | --- |
| `TR014` + `Tautliner standard` | `Tráilers Completos` | `Trailer` | `Carga General` |
| `NT214` | `Grupajes` | Según vehículo confirmado | `Carga General` |
| `Chemical Tank` | `Tráilers Completos` | `Trailer` | `Carga General` |

Si el valor del export no tiene correspondencia inequívoca, detenerse y pedir confirmación para los campos afectados; la columna Especialidad sigue siendo siempre `Carga General`.

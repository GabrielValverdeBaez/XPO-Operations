# Reglas XPO por cliente — Auditoría T-001

**Estado:** inventario de reglas confirmadas en instrucciones operativas; revisión contra muestras reales pendiente.

## Precedencia
Instrucción explícita actual > dato visible FOTE/captura/Excel de la expedición > excepción de cliente confirmada > default documentado. Una regla de cliente se activa por identidad inequívoca, **no por localidad, mercancía genérica o CP compartido**. Conservar por campo `source, rule_id, version, confirmed` y registrar advertencia ante conflicto. Un dato vigente explícito no se sobrescribe con patrón histórico.

## Notas de texto (después de LOS DOS precios)
| Identificación inequívoca | Texto exacto | Prohibición |
|---|---|---|
| Groupe SEB + DHL Ontígola | `NOTA: Adelantar hora de posicionamiento. Indicar matrículas.` | No aplicarla a otros clientes de Ontígola |
| TCL | `NOTA: Indicar matrículas.` | No aplicarla por compartir origen/destino |
| Mattel | `NOTA: Indicar matrículas y nombre del conductor.` | No aplicarla a otros operadores |
| Otros | Sin nota | Prohibidas notas genéricas |

## Reglas y excepciones por operador
| Cliente / escenario | Regla provisional | Límite |
|---|---|---|
| LG y LX Pantos, **solo grupaje** | Peso ausente → 2 t; ML ausentes → 5 m; datos presentes conservados | Dimensiones reales calculables prevalecen |
| Diversey, origen GXO Illescas | ADR=S; paletizado=S en TSV; si faltan horarios: carga 10–19 h, entrega día siguiente 06 h | Horarios actuales FOTE prevalecen; no forzar en otras operaciones |
| Aguas Danone | ADR=N, paletizado=S | No extrapolar a Danone Sigüenza |
| L'Oréal | ADR=N, paletizado=S | Confirmar identidad del cliente |
| Danone Sigüenza | No inferir ADR | Campo vacío si no consta |
| PEPCO | FTL Trailer 12 t, 13,6 m; recogida 13:00 y entrega día siguiente 11–14 solo en ausencia | Fuente vigente prevalece; no inferir paletizado |
| Norauto Seseña → Logroño → Pamplona NT014 | 20 t, 13,6 m, ADR=N, paletizado=N | Únicamente repetición verificada de ese patrón |
| FASSA | Sirve Frigorífico=N | Confirmar en plantilla y reglas de oferta |
| XPO / ID Logistics | Mercancía por defecto: Mercancía paletizada / Palletized goods | Solo si no existe descripción actual y el cliente está confirmado |
| Groupe SEB | Mercancía fallback: Pequeños electrodomésticos / Small household appliances | No adivinar producto específico |
| Mango | Mercancía fallback: Ropa / Clothing | No sobrescribir descripción de orden |
| Danone | Mercancía fallback: Agua paletizada / Palletized water | No trasladar a toda marca sin verificar contexto |
| LG/LX | Mercancía fallback: Electrónica y electrodomésticos paletizados / Palletized electronics and household appliances | Clasificación general, no SKU |

## Alias de CP operativos (solo centro identificado)
XPO Leganés U226 28911; XPO Ledoño 15189; XPO Arrúbal 26150; Norauto Seseña DHL 45224; XPO Imárcoain 31119; XPO Santurtzi 48980; Celeritas Alovera 19208. No sustituir un CP diferente asociado a dirección actual. Corregidos anteriormente: Carnaxide Wtransnet 2795, Burgos ciudad 09001 (XPO Burgos 09006).

## Servicio y mercancía
TR014 → FTL; NT014 → FTL solo cuando confirmado; NTIE1 → tráiler completo; NT214 → grupaje. No interpretar códigos por semejanza. Grupaje con dimensiones: ML = suma(largo × ancho × cantidad / 2,40), dos decimales. NT214 con europalés confirmados y sin dimensiones contradictorias: unidades × 0,40 m. Nunca aplicar este cálculo de palés a FTL.

## Plantilla de texto — contrato preciso
```markdown
**20/10/2026 — GETAFE → ODIVELAS — Ref.: EJEMPLO**
**Origen** / *Origin*: 28909
**Destino** / *Destination*: 2675-076
**Tipo** / *Type*: FTL · Trailer Tautliner · 15 t · 13,6 m
**Mercancía** / *Goods*: Aceite / Oil
**Recogida** / *Pickup*: 20/10/2026, 10:00–16:00
**Descarga** / *Delivery*: 21/10/2026, 12:00–13:00
**Precio cliente** / *Client price*: 850,00 €
**Precio mercado estimado** / *Estimated market price*: Por confirmar / To be confirmed
```
Ejemplo de formato basado en una ruta conocida; precio de mercado deliberadamente pendiente, no tarifa cotizada. Encabezado completo negrita; solo etiquetas españolas negrita, solo etiquetas inglesas cursiva, valores planos; Origen/Destino solo CP. Dos precios obligatorios, notas solo al final para cliente correspondiente.

## Casos negativos obligatorios
1. Cliente desconocido con origen Ontígola **NO** activa nota Groupe SEB.
2. TCL con instrucciones actuales distintas: señalar conflicto y aplicar precedencia documentada.
3. Diversey con ADR explícito incompatible: detectar excepción, no corregir silenciosamente.
4. LG/LX grupaje con peso presente 10,174 t y ML 6,30 m: no sustituir por 2 t/5 m.
5. ID Logistics y Mattel misma ruta: la nota Mattel solo en Mattel.
6. Falta de CP o ingreso: estado de revisión; nunca crear datos.
7. Price cliente no sirve como base porcentual para mercado.

## Pendientes para cierre
- Confirmar identidades/códigos de cliente aplicables en FOTE y equivalencia de aliases.
- Contrastar notas, ventanas y paletización con muestras aceptadas.
- Registrar aprobación operativa y ejemplos anonimizados; si alguna regla contradice fuente actual, versionar cambio.

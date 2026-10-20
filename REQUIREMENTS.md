# XPO Load Studio — Requisitos y reglas v0.1

> Documento inicial derivado de reglas operativas existentes. Toda correspondencia con el Excel oficial y cualquier diferencia por cliente debe verificarse antes de codificar.

## Proceso funcional
1. Ingestar orden FOTE pegada o formulario.
2. Identificar campos y guardar valor, fuente, confianza y estado confirmado.
3. Normalizar a `LoadRecord` sin sobrescribir valores confirmados.
4. Resolver cliente, equipo y excepciones mediante reglas versionadas.
5. Validar requisitos y pedir solo los datos que falten o sean conflictivos.
6. Previsualizar y copiar texto ES/EN y TSV de 26 columnas.
7. Registrar un snapshot y detectar duplicados por referencia y huella normalizada.

## Modelo de datos inicial (provisional)
`source_type, source_text_hash, order_reference, customer, origin_postcode, origin_locality, destination_postcode, destination_locality, pickup_start, pickup_end, delivery_start, delivery_end, equipment, operation_type, goods_es, goods_en, weight_kg, pallets, linear_meters, adr, client_price_eur, estimated_market_price_eur, market_price_basis, notes, field_provenance, rule_version, validation_status`.

Fechas con año, zona horaria explícita y ventanas; importes como decimales; unidades sin ambigüedad. Separar valor desconocido de cero o false.

## Formato XPO ES/EN obligatorio
- Encabezado con ruta completa **en negrita**, localidades permitidas en encabezado.
- Etiquetas españolas **en negrita**, etiquetas inglesas *en cursiva*, valores sin estilo.
- Campos: **Origen** / *Origin*, **Destino** / *Destination*, **Tipo** / *Type*, **Mercancía** / *Goods*, **Recogida** / *Pickup*, **Descarga** / *Delivery*, **Precio cliente** / *Client price*, **Precio mercado estimado** / *Estimated market price*.
- En los valores de Origen/Destino SOLO CP; sin nombre de centro, empresa, dirección ni localidad. ES 5 dígitos; PT CP completo con guion cuando conste.
- Tipo: forma directa `FTL · ...` o tipo operativo verificado. Regla por defecto: tráiler + tautliner + carga general cuando no contradiga datos o cliente.
- Precio cliente y mercado independientes y al final, antes de notas específicas.
- No agregar notas genéricas a otros clientes.
- Notas particulares: Groupe SEB / DHL Ontígola adelantar posicionamiento e indicar matrículas; TCL indicar matrículas; Mattel indicar matrículas y conductor. Solo si corresponde el cliente.
- Diversey: ADR por defecto bajo regla de cliente; excepción requiere confirmación y señalamiento. Otros clientes: ADR únicamente si está indicado/confirmado.
- No completar mercancía, matrícula, conductor, horas, CP, pallets o precio con suposiciones.

## Wtransnet
- **26 columnas** en orden exacto y codificación acordada con plantilla real. Orden y nombres AÚN PENDIENTES de inspeccionar.
- Exportación TSV para pegar manualmente: sin editar plantillas, sin automatización de envío.
- Validar caracteres que rompan TSV, número de celdas, tipos, códigos postales y campos obligatorios; generar pruebas de ida/vuelta.
- Mantener mapeo versionado entre `LoadRecord` y las 26 columnas; registrar huecos y errores.

## Parsers
- MVP: extractores FOTE específicos + formulario manual.
- Fase posterior: abreviaturas con reglas transparentes y Excel con selección de columnas; OCR local Tesseract con revisión de baja confianza.
- Cuando el parseo sea ambiguo, pedir confirmación; preservar texto original y explicabilidad del parser.

## Precios
- `client_price_eur`: solo del input o introducción manual.
- `estimated_market_price_eur`: estimación independiente a partir de corredores/rangos históricos verificables, condiciones del servicio y versión de tabla; no deducir del precio cliente.
- Si falta evidencia adecuada, devolver «Pendiente de validar» en vez de número inventado.

## UI y operación
- Pegar FOTE / Texto libre (fase 2) / Manual / Importar Excel (fase 2) / Captura (fase 3).
- Tarjeta de revisión editable con alertas y bloqueos donde correspondan.
- Dos paneles de resultado, copiar texto enriquecido o plano según canal y TSV exacto.
- Historial y deduplicación en fase 3, almacenamiento SQLite con backups.
- Acceso privado por Tailscale con autenticación adecuada; no abrir puerto público.

## Pruebas
- Fixtures sintéticos o anonimizados para FOTE, ES→PT, PT→ES, ADR, ventanas, grupos, duplicados, conflicto de reglas, valores ausentes y caracteres especiales.
- Golden tests del formato ES/EN y TSV; pruebas de invariantes (mismo registro+reglas = misma salida).
- No liberar el MVP sin revisión humana de ejemplos operativos.

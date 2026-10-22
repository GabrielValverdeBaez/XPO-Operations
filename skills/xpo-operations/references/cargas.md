# Cargas y textos ES/EN

Extraer referencia, origen/destino/paradas, CP, fechas/ventanas, servicio, vehículo, peso, metros, mercancía y precio de la fuente actual. Excluir filas seleccionadas con fondo negro/oscuro. Deduplicar por referencia cuando se pide comparar; misma ruta no implica misma expedición.

Aplicar el formato confirmado por el operador: encabezado en negrita `DD/MM/AAAA — ORIGEN → DESTINO — Ref.: ...`; omitir referencia si falta. Cuerpo compacto sin líneas en blanco: etiquetas ES en negrita e inglesas en cursiva, valores sin formato. Origen/destino del cuerpo contienen solo CP; los nombres permanecen en el encabezado. Conservar CP portugués completo si consta. No traducir nombres propios, localidades, referencias ni siglas operativas.

Orden: Origen, Paradas si existen, Destino, Tipo, Mercancía, Recogida, Descarga, Observaciones si necesarias, Precio cliente, Precio mercado estimado. Integrar vehículo, peso, metros y paletización confirmados en Tipo; no campos separados de peso/metros. Usar FTL directamente y mercancía bilingüe verificada.

Consultar la skill especializada para reglas por cliente, mercancía, ADR, matrículas/conductor, horarios y excepciones. Los datos reales de peso/metros prevalecen sobre cualquier respaldo autorizado. No deducir ADR, Mega, paletización o capacidad por cliente salvo regla expresa vigente y documentada.

Precio cliente: importe exacto asociado a la carga actual (Revenue/Customer Rate), conservando céntimos. Mercado: estimación independiente basada en ruta, servicio, distancia y comparables; nunca porcentaje/margen sobre ingreso. Recuperar metodología y benchmarks vigentes del especialista antes de estimar; si faltan datos esenciales o benchmark fiable, mostrar `Por confirmar / To be confirmed`. Incluir siempre ambos campos finales.

Entregar solo el texto final solicitado. Si pide ambas salidas, primero un bloque TSV de Wtransnet y después textos ES/EN. No reutilizar cifras del ejemplo como precios actuales.

## Patrón literal con datos ficticios

**22/10/2026 — MADRID → TOLEDO — Ref.: TEST-42**
**Origen** / *Origin*: 28001
**Destino** / *Destination*: 45001
**Tipo** / *Type*: FTL · Trailer Tautliner · 5 t · 13,6 m
**Mercancía** / *Goods*: Libros / Books
**Recogida** / *Pickup*: 22/10/2026, 10:00–12:00
**Descarga** / *Delivery*: 23/10/2026, 09:00
**Precio cliente** / *Client price*: Por confirmar / To be confirmed
**Precio mercado estimado** / *Estimated market price*: Por confirmar / To be confirmed

Conservar exactamente las traducciones de etiquetas del patrón. Localidades en MAYÚSCULAS en el encabezado. Este patrón no aporta datos a otra carga.

# HIST — handoff

Departamento creado por petición expresa del usuario el 22/10/2026. Responsable funcional del histórico de viajes, precios y observaciones; usa la misma caché privada del proyecto. No se migran ni duplican las tablas existentes para crear este departamento.

Leer skills/xpo-operations/references/historico.md para operar; references/cache.md para recuperación y sincronización. Código existente: project_cache.py (trips, operations, observations, sales, notes, export/restore).

Siguiente uso: recibir un viaje, operación o nota con fuente y guardarlo; también consultar por referencia, transportista, región, cliente o estado según los datos disponibles. Mantener vacíos los precios no confirmados. Las importaciones reales pueden ser parciales; informar de su cobertura.

OPS-013 cierra la implantación documental y su enrutamiento. La aceptación global de fuentes y controles del proyecto sigue pendiente en sus tareas originales; no se declara por crear este departamento.

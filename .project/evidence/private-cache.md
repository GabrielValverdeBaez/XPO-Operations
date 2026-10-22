# Caché privada — evidencia

Implementación: scripts/project_cache.py portable, SQLite y snapshot JSON con sources/carriers/records/trips/operations/exclusions/observations/audit. Operaciones con partes comerciales, moneda y tres precios separados. Ingesta transaccional, reimportación por IDs, consultas por evidencia/estado/dirección y exclusiones. Los cambios de snapshot fuente retiran contactos obsoletos sin perder histórico/notas.

Validación: 22 pruebas nuevas de caché (52 totales con regresión), consultas de región y no inferencia por sede/nombre, deduplicación, bloqueos, frescura, fechas futuras, separación de estados y precios, precisión monetaria, pérdida de campos en actualización parcial, refresh preservando notas, rollback y export/restore íntegro. No se usan datos comerciales en fixtures.

Integración privada: se leyó el maestro vigente y el registro histórico autorizado, se pobló la caché, se guardó snapshot en carpeta privada de proyecto y se verificó mediante lectura remota, restauración en otra base y comparación exacta de todas las tablas. Datos, nombres, importes, conteos comerciales e IDs de almacenamiento permanecen en la parte privada; no se copian aquí.

Límites: texto del Excel sin formato de celdas, controles unknown; no aprobación de candidatos ni lectura binaria de rojos. Histórico documental parcial, estados provisionales/asignados/entregados separados. Catálogo geográfico explícito inicial para dos regiones, sin censo completo. Ningún mensaje, oferta, asignación o edición del maestro. Sin scheduler y sin lock remoto atómico; un escritor. La CI debe comprobar el HEAD que publique esta implementación.

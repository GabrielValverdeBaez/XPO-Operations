# Directorio y enriquecimiento

## Contrato de 19 columnas
Empresa - Delegación; Tipo de empresa; Tipo de Transporte; Servicios; Especialidad; País; Comunidad Autonoma / Provincia; CP; Ciudad; Cobertura; Ruta; Almacenes; Email; Contactos secundarios; Teléfono; Observaciones; Web; Descripción; Dirección.

Separar modo físico (Carretera/Marítimo/Aéreo/Ferroviario/Multimodal), servicio (FTL/LTL/Express/etc.) y equipo/mercancía/requisito (Tautliner/ADR/Frigorífico/etc.). No inventar servicios ni rutas. Portugal cuatro cifras en CP y CP completo en Dirección. Contactos secundarios vacío salvo cambio explícito. Email en minúsculas, sin duplicados y terminado en punto y coma. Teléfonos asociados a persona/función solo si consta.

## Perfiles recibidos
Comparar contra maestro actual, deduplicar CIF/VAT, carrier code, nombre/delegación, contacto y dirección. No fusionar empresas/delegaciones ambiguas. No corregir erratas de correo sin verificar. No buscar correos en Internet salvo solicitud expresa. Consultar bloqueos privados de correos y empresas; excluir filas oscuras. Active no implica compliance aprobado. Señalar documentación/crédito rechazado/incompleto. Flota ADR exige evidencia; SQAS solo no basta.

Entregar cuatro secciones: Transportistas nuevos (19 columnas TSV), Transportistas ya añadidos (correos), Transportistas ya añadidos con actualización, Todos los correos listos para copiar. Mantener datos faltantes vacíos. Una empresa propuesta no equivale a escritura ya realizada: mantener dedupe de sesión, volver a maestro en sesión nueva.

## Edición solicitada de Excel
Descargar libro real actual y conservar identidad/versionado. Inspeccionar cabeceras, fórmulas, filtros y colores. Escribir solo hojas operativas compatibles con modos, nunca auxiliares por defecto. Preservar datos y exclusiones rojas. Leer y aplicar formato_directorio del especialista. Validar 19 columnas y duplicados, reabrir y comprobar integridad antes de reemplazar el mismo item; registrar diferencia resumida sin datos comerciales en Git.

El validador incluido solo valida filas TSV, no estilos ni seguridad de reemplazo del libro. La aceptación de edición real exige evidencia del Excel.

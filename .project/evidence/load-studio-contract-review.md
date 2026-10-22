# Conciliación de contratos — OPS-010

Fecha: 22/10/2026. Fuente: origin/feat/load-studio-implementation-20261020, commit bf48cc4ab871482403fec10e054b4f911b260c66, docs/customer-rules.md y loadstudio/engine.py, leídos directamente del checkout Git. Comparación documental y de código, sin ejecutar aplicación ni editar esa rama.

| Contrato | Skill integrada | Load Studio leído | Decisión |
|---|---|---|---|
| Encabezado, etiquetas ES/EN y CP del cuerpo | Negrita / cursiva / CP solo | Mismo formato en render | Alineado; patrón literal añadido |
| Wtransnet | 26 columnas, Y vacía, PT cuatro cifras | Idéntico en row, export condicionado a revisión | Mantener; aceptación contra portal sigue pendiente |
| Mercado | Independiente del ingreso; metodología especialista | Tabla de corredores, mediana y redondeo; sin tabla queda pendiente | Diferentes métodos; no declarar paridad de cálculo. Proponer contrato de fuentes/fecha/servicio/estimación para revisión separada |
| Notas y campos de precio | Observaciones antes de los dos precios finales | NOTA añadida después de los precios | Diferencia detectada; resolver orden canónico con aceptación, no cambiar motor silenciosamente |
| Excepciones de peso/metros y clientes | Recuperadas de especialista privado vigente | Reglas de cliente y provenance en motor | Auditar regla por regla en OPS-006/007; datos actuales prevalecen |
| Directorio/Notion/selección | Módulos propios | No es alcance del motor leído | Mantener servicios externos fuera del runtime determinista |
| Publicación/despliegue | No autorizado por generar salida | Gate separado en PR #4 | Conservar separación |

OPS-010 cumple su alcance: matriz de diferencias y decisión. No equivale a armonización implementada, aceptación comercial ni cierre de despliegue. Seguimiento de discrepancias: OPS-006/007 y OPS-011. Idea de fuente común de reglas en IDEAS.md; no se ha creado otra implementación del motor.

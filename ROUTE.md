# XPO Operations — Ruta maestra

Estado canónico por tarea: [.project/STATE.json](.project/STATE.json). Un escritor; no avanzar dependencias sin DONE y evidencia.

| Fase | Tareas | Resultado y gate |
|---|---|---|
| F0 — Recuperación | OPS-001 | Fuentes inventariadas, estado de ramas y privacidad comprobados |
| F1 — Skill y módulos | OPS-002/003/004 | Entrada portable, módulos y contratos sin datos privados |
| F2 — Verificación | OPS-005 | Pruebas sintéticas, validadores, revisión independiente y recuperación limpia |
| F3 — Paridad operativa | OPS-006/007/008/009 | Excepciones privadas verificadas y aceptación en fuentes reales; no sustituir por mocks |
| F4 — Integración | OPS-010/011 | Contratos conciliados con Load Studio, catálogo y revisión final |

## Continuación
Leer HANDOFF y departamento. Ejecutar siguiente READY → prueba → evaluación → corrección. DONE requiere evidencia de salida, no existencia de archivo. BLOCKED debe incluir causa y acción necesaria. Registrar historial inmutable y actualizar índice/handoff. Resolver otros trabajos independientes mientras un gate esté bloqueado.

La primera integración no implica paridad completa de las seis skills, migración de contactos ni aceptación de Excel/Wtransnet/Notion. Las skills originales siguen disponibles durante transición. Tareas de Load Studio en sus ramas conservan sus propios gates y no se cierran con esta ruta.

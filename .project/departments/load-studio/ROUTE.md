> Baseline conservada de main anterior a la ampliación del 22/10/2026. No representa el estado de las ramas de implementación/cloud; consultar sus rutas y tareas vigentes.

---
schema: project-route/route@1
id: route-main
project: xpo-load-studio
status: active
baseline_version: 1.0
current_version: 1.0
depth: M
research_level: R1
execution_strategy: [sequential, parallel, iterative]
epoch: 1
state_owner: controller
quality_gate: PENDING
created_at: 2026-10-20
updated_at: 2026-10-20
---

# XPO Load Studio — Ruta ejecutable

## Estrategia
Planificar primero el contrato de datos y salidas; después construir un vertical slice útil de FOTE→revisión→texto ES/EN y TSV. Expandir parsers y características sin alterar el contrato. GitHub será el repositorio de documentación, PR y evidencia. Las tareas requieren pruebas y evidencia antes de DONE.

## Milestones
| Hito | Entregable observable | Gate |
|---|---|---|
| M0 — Contratos | Plantilla Wtransnet 26 columnas verificada, formatos gold y excepciones por cliente | Revisión operativa |
| M1 — MVP | Aplicación local que procesa FOTE y formulario y copia dos salidas | Tests y comparación manual |
| M2 — Flexibilidad | Texto abreviado, importación Excel, editor de reglas | Casos ambiguos controlados |
| M3 — Persistencia | OCR local revisable, SQLite, deduplicación y motor inicial de tarifas | Evaluación de exactitud y seguridad |
| M4 — Operación | Deployment Mac mini + Tailscale, backups, documentación y pruebas end-to-end | Aceptación final |

## Execution Graph
```text
T-001 → T-002 → T-003 → T-004
                   ├→ T-005 → T-007 → T-008
                   └→ T-006 ──────┘
T-008 → T-009 → T-010 → T-011
T-008 → T-012 → T-013
T-011 + T-013 → T-014
```

## Task contracts
| ID | Objetivos | Tarea / salida | Dependencias | Verificación / evidencia |
|---|---|---|---|---|
| T-001 | O-003 | Recuperar plantilla real Wtransnet y 5–10 ejemplos anonimizados FOTE + salidas correctas; inventariar reglas y conflictos | ninguna | Tabla exacta de 26 columnas y ejemplos revisados |
| T-002 | O-001,O-003 | Especificar `LoadRecord`, normalizaciones, fechas, provenance, campos obligatorios y estados de confirmación | T-001 | JSON Schema/Pydantic + ejemplos válidos/inválidos |
| T-003 | O-001,O-003 | Formalizar plantillas ES/EN, mapeo Wtransnet y precedencia de reglas por cliente | T-002 | Golden fixtures revisados, 26 columnas verificadas |
| T-004 | O-004,O-005 | Spike técnico: React/FastAPI/SQLite o alternativa más simple; estructura repo, test/CI, decisión documentada | T-003 | Comparación pequeña reproducible, ADR técnica |
| T-005 | O-001,O-002 | Parser de FOTE con diagnóstico de campos y validaciones | T-004 | Fixtures variados, errores no inventados |
| T-006 | O-001,O-003 | Motor determinista y dos renderizadores, tests golden | T-004 | Tests exactos ES/EN y TSV |
| T-007 | O-002 | Interfaz pegado, formulario, confirmación de errores, vista previa y copiar | T-005,T-006 | E2E con FOTE anonimizados |
| T-008 | O-001,O-002,O-003 | Gate MVP: regresión, auditoría de notas, ADR, CP, monetarios y salida Wtransnet | T-007 | Reporte validado + aprobación |
| T-009 | O-002,O-004 | Parser para texto abreviado, con puntuación de confianza y sin inferencia insegura | T-008 | Pruebas de ambigüedad y no alucinación |
| T-010 | O-003,O-004 | Importador Excel configurable, exportación TSV robusta | T-009 | Pruebas con workbook anonimizados |
| T-011 | O-004 | Editor versionado de reglas, validación de conflictos, auditoría de cambios | T-010 | Edición/revertir + golden regression |
| T-012 | O-004 | Histórico SQLite, dedupe, búsqueda, snapshots y backup | T-008 | Migraciones/duplicados/restauración |
| T-013 | O-002,O-004 | OCR local como entrada no confiable + prototipo independiente de tarifas de mercado, con fuentes y pendientes | T-012 | Evaluación OCR por campos + backtests de tarifas |
| T-014 | O-005 | Despliegue privado en Mac mini, Tailscale, manual y aceptación final | T-011,T-013 | Tests E2E + control de acceso + recuperación backup |

## Evidencia de ejecución (20/10/2026)
- Suite sintética de contrato Wtransnet: GitHub Actions `39391760772`, resultado `success` sobre commit `a3e7be2`.
- Esto valida los controles implementados, **no** la compatibilidad con el archivo Excel original.
- T-001 permanece sin cerrar hasta contraste documental y aceptación operativa; T-002 sigue bloqueada.

## READY
- **T-001** es la única tarea sin dependencias previas. XLS original recibido y encabezados contrastados. Faltan listas/validaciones exhaustivas y ejemplos aceptados; no declarar DONE aún.
- Cualquier desarrollo de código posterior está **NO INICIADO**.

## BLOCKED
- **Encabezados A:Z:** cotejados con el XLS proporcionado; **validaciones internas del libro:** todavía no auditadas íntegramente.
- **Ejemplos reales anonimizados y resultado esperado:** necesarios para golden tests.
- **Datos históricos para tarifas:** ausentes; por defecto «Pendiente de validar».

## Recuperación y handoff
- Cada tarea: rama `feat/T-xxx-...`, PR sin merge automático, pruebas adjuntas, decisiones y limitaciones.
- Si una dependencia falla, dejar la tarea BLOCKED con evidencia y propuesta reversible. No inventar contratos.
- Un único responsable actualiza estado canónico. No ejecutar tareas paralelas que alteren los mismos contratos.
- T-004 es un experimento: no fijar stack definitivamente sin evaluar simplicidad y despliegue real.

## Siguiente paso
Continuar T-001 con validaciones del XLS y ejemplos de cargas correctas anonimizados. Congelar contrato mediante revisión antes de los generadores.

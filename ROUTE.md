---
schema: project-route/route@1
id: route-main
project: xpo-load-studio
status: active
baseline_version: '1.0'
current_version: '1.1'
depth: M
research_level: R1
execution_strategy:
- sequential
- parallel
- iterative
epoch: 2
state_owner: controller
quality_gate: PASS
created_at: '2026-10-20'
updated_at: '2026-10-20'
---
# XPO Load Studio - Ruta de desarrollo

## Strategy
Continuar desarrollo reversible en rama, con evidencia antes de DONE. La aceptacion comercial y despliegue siguen siendo gates de liberacion, no requisitos para escribir prototipos. Replan R-001 en docs/DECISIONS.md conserva objetivos y limites originales. No existe un bucle de agentes ejecutandose entre conversaciones.

## Milestones
Fase 1: FOTE/manual, reglas y doble salida (nucleo implementado; equivalencia completa de reglas y aceptacion pendientes). Fase 2: entradas flexibles, XLSX y editor (implementados dentro de la gramatica/formatos documentados). Fase 3: historial, OCR y tarifas (historial probado; prototipos OCR/tarifas sin calibracion real). Operacion: Mac mini/Tailscale pendiente.

## Task index
| Tarea | Estado | Salida |
|---|---|---|
| [T-001](TASKS/T-001.md) Auditar fuente XLS y consolidar contrato tecnico | DONE | `evidence/template-audit.json` |
| [T-002](TASKS/T-002.md) Modelo normalizado tipado | DONE | `loadstudio/models.py` |
| [T-003](TASKS/T-003.md) Contratos ES/EN y TSV | DONE | `docs/wtransnet-schema.md` |
| [T-004](TASKS/T-004.md) Spike y eleccion de arquitectura local | DONE | `docs/DECISIONS.md` |
| [T-005](TASKS/T-005.md) Parser FOTE y diagnostico | DONE | `loadstudio/ingest.py` |
| [T-006](TASKS/T-006.md) Motor XPO y extensiones de reglas | REVIEW | `loadstudio/engine.py` |
| [T-007](TASKS/T-007.md) Interfaz de revision y resultados | DONE | `static/index.html` |
| [T-008](TASKS/T-008.md) Aceptacion operativa MVP | BLOCKED | `evidence/operational-acceptance.md` |
| [T-009](TASKS/T-009.md) Parser de texto con gramatica acotada | DONE | `docs/USAGE.md` |
| [T-010](TASKS/T-010.md) Importador XLSX revisable | DONE | `loadstudio/ingest.py#import_rows` |
| [T-011](TASKS/T-011.md) Editor de reglas versionadas | DONE | `loadstudio/store.py#update_rules` |
| [T-012](TASKS/T-012.md) Historial SQLite y copias | DONE | `loadstudio/store.py` |
| [T-013](TASKS/T-013.md) OCR y tarifas - prototipos verificables | REVIEW | `evidence/ocr-smoke.json` |
| [T-014](TASKS/T-014.md) Instalacion privada Mac mini y aceptacion final | BLOCKED | `evidence/deployment-acceptance.md` |

## Execution Graph

```text
T-001 -> T-002 -> T-003 -> T-004 -> T-005 -> T-007
                                  |          |-> T-009
                                  |          |-> T-010
                                  |-> T-006
                                  |-> T-011
                                  |-> T-012 -> T-013
T-006 + T-007 -> T-008
T-008 + T-013 -> T-014
```

## READY
No hay nuevas tareas TODO derivadas READY. Prioridad inmediata: resolver REVIEW de T-006 (multi-parada/dimensiones/aliases) y ampliar T-013 con capturas/tarifas verificadas. T-007 ya ha pasado el navegador conectado en CI. No volver a pedir el XLS original ni repetir una busqueda de plantilla.

## BLOCKED
T-008: aceptacion operativa real pendiente y cobertura incompleta de reglas avanzadas. T-014: gates anteriores y equipo objetivo no instalado. El repositorio no contiene los datos privados necesarios para calibrar precios. No inventar un mercado ni declarar el servidor del Mac instalado.

## Current Epoch
Epoca 2, claim unico xpo-20261020-implementation. La auditoria primaria, implementacion, tests API/modelo y revision visual offline se registran en evidence/verification.md. El informe de CI debe consultarse por commit: un run antiguo de diez tests no acredita estos cambios.

## Next execution
Completar cobertura de reglas pendiente. El workflow conectado de commit 4f4060c ya ha pasado; conservar regresiones y actualizar evidencia. Mantener PR sin merge automatico. Al desplegar de verdad, registrar host, version, prueba de acceso privado y restauracion, sin credenciales. Preguntar solo por una regla comercial no verificable, una decision reservada o acceso al equipo que no se pueda resolver tecnicamente.

## Evidencia CI conectada

GitHub Actions run [39404120752](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39404120752), job 118565768271, commit 4f4060ce15a586927f1c1e492544df986ab66ca6: SUCCESS. Pruebas 78/78, verificacion SHA de 17 fuentes, DAG, sintaxis JS y smoke_browser.py conectando navegador/API/portapapeles reales del runner. Se corrigio un uso de eval en el test, sin relajar CSP de la app. T-007 DONE. Este resultado no demuestra instalacion en Mac mini ni ofertas aceptadas por Wtransnet.

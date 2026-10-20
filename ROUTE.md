---
schema: project-route/route@1
id: route-main
project: xpo-load-studio
status: active
baseline_version: '1.0'
current_version: '1.2'
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
Fase 1: FOTE/manual, reglas y doble salida (motor y extensiones de ruta/metraje implementados; aceptacion real pendiente). Fase 2: entradas flexibles, XLSX y editor (implementados dentro de la gramatica/formatos documentados). Fase 3: historial, OCR y tarifas (historial probado; prototipos OCR/tarifas sin calibracion real). Operacion: Mac mini/Tailscale pendiente.

## Task index
| Tarea | Estado | Salida |
|---|---|---|
| [T-001](TASKS/T-001.md) Auditar fuente XLS y consolidar contrato tecnico | DONE | `evidence/template-audit.json` |
| [T-002](TASKS/T-002.md) Modelo normalizado tipado | DONE | `loadstudio/models.py` |
| [T-003](TASKS/T-003.md) Contratos ES/EN y TSV | DONE | `docs/wtransnet-schema.md` |
| [T-004](TASKS/T-004.md) Spike y eleccion de arquitectura local | DONE | `docs/DECISIONS.md` |
| [T-005](TASKS/T-005.md) Parser FOTE y diagnostico | DONE | `loadstudio/ingest.py` |
| [T-006](TASKS/T-006.md) Motor XPO y extensiones de reglas | DONE | `loadstudio/engine.py` |
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
T-006 y T-007 completadas con regresiones y navegador conectado. No hay nuevas tareas TODO derivadas READY. T-008 tiene sus dependencias tecnicas resueltas, pero mantiene el bloqueo externo de aceptacion operativa. T-013 espera evidencia de capturas/tarifas reales; no fabricar datos. No volver a pedir el XLS original.

## BLOCKED
T-008: aceptacion operativa real pendiente; no se han acreditado cinco ofertas aceptadas ni un pegado aprobado en Wtransnet. T-014: gates anteriores y equipo objetivo no instalado. El repositorio no contiene los datos privados necesarios para calibrar precios. No inventar un mercado ni declarar el servidor del Mac instalado.

## Current Epoch
Epoca 2, claim unico xpo-20261020-implementation. La auditoria primaria, implementacion, tests API/modelo y revision visual offline se registran en evidence/verification.md. El informe de CI debe consultarse por commit: un run antiguo de diez tests no acredita estos cambios.

## Next execution
Conservar la suite de 117 pruebas y el navegador conectado ya verificados sobre 2bc1e58. Continuar con la revision real de ofertas y la evaluacion de OCR/tarifas cuando existan fuentes privadas verificables. Mantener PR sin merge automatico. Al desplegar de verdad, registrar host, version, prueba de acceso privado y restauracion, sin credenciales. Preguntar solo por una regla comercial no verificable, una decision reservada o acceso al equipo que no se pueda resolver tecnicamente.

## Evidencia CI conectada

GitHub Actions run [39404120752](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39404120752), job 118565768271, commit 4f4060ce15a586927f1c1e492544df986ab66ca6: SUCCESS. Pruebas 78/78, verificacion SHA de 17 fuentes, DAG, sintaxis JS y smoke_browser.py conectando navegador/API/portapapeles reales del runner. Se corrigio un uso de eval en el test, sin relajar CSP de la app. T-007 DONE. Este resultado no demuestra instalacion en Mac mini ni ofertas aceptadas por Wtransnet.


## Cierre tecnico de la extension

Run [39406835670](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39406835670), job 118574705486, head `2bc1e582fe3fe402c41ff4054494aa697833e70c`: SUCCESS. El runner prueba el merge temporal del PR `4401b47f958d8872a0c4778fb4e4548f449d2ef3`, no una fusion publicada en main. **117 tests, 19 hashes de fuentes y navegador conectado PASS**, incluidas paradas y ML por dimensiones. T-006 DONE. Totales: 11 DONE, 1 REVIEW (T-013), 2 BLOCKED (T-008/T-014). No se ha fusionado el PR ni instalado en el equipo del usuario.

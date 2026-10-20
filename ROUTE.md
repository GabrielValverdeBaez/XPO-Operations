---
schema: project-route/route@1
id: route-main
project: xpo-load-studio
status: active
baseline_version: '1.0'
current_version: '1.3'
depth: M
research_level: R1
execution_strategy:
- sequential
- parallel
- iterative
epoch: 3
state_owner: controller
quality_gate: PASS
created_at: '2026-10-20'
updated_at: '2026-10-20'
---
# XPO Load Studio - Ruta de desarrollo

## Strategy
Continuar desarrollo reversible en rama, con evidencia antes de DONE. La aceptacion comercial y despliegue siguen siendo gates de liberacion, no requisitos para escribir prototipos. Replan R-001 en docs/DECISIONS.md conserva objetivos y limites originales. La ampliacion cloud autorizada por el operador conserva la version local y se registra en docs/CLOUDFLARE_DEPLOYMENT.md. No existe un bucle de agentes ejecutandose entre conversaciones.

## Milestones
Fase 1: FOTE/manual, reglas y doble salida (motor y extensiones de ruta/metraje implementados; aceptacion real pendiente). Fase 2: entradas flexibles, XLSX y editor (implementados dentro de la gramatica/formatos documentados). Fase 3: historial, OCR y tarifas (historial probado; prototipos OCR/tarifas sin calibracion real). Instalacion Mac mini/Tailscale pendiente e independiente. Cloudflare: integracion real workerd/D1 local PASS; recursos propios creados; publicacion remota BLOCKED por credencial de Builds y Secret de acceso.

## Task index
| Tarea | Estado | Salida |
|---|---|---|
| [T-001](TASKS/T-001.md) Auditar fuente XLS y consolidar contrato tecnico | DONE | evidence/template-audit.json |
| [T-002](TASKS/T-002.md) Modelo normalizado tipado | DONE | loadstudio/models.py |
| [T-003](TASKS/T-003.md) Contratos ES/EN y TSV | DONE | docs/wtransnet-schema.md |
| [T-004](TASKS/T-004.md) Spike y eleccion de arquitectura local | DONE | docs/DECISIONS.md |
| [T-005](TASKS/T-005.md) Parser FOTE y diagnostico | DONE | loadstudio/ingest.py |
| [T-006](TASKS/T-006.md) Motor XPO y extensiones de reglas | DONE | loadstudio/engine.py |
| [T-007](TASKS/T-007.md) Interfaz de revision y resultados | DONE | static/index.html |
| [T-008](TASKS/T-008.md) Aceptacion operativa MVP | BLOCKED | evidence/operational-acceptance.md pendiente |
| [T-009](TASKS/T-009.md) Parser de texto con gramatica acotada | DONE | docs/USAGE.md |
| [T-010](TASKS/T-010.md) Importador XLSX revisable | DONE | loadstudio/ingest.py#import_rows |
| [T-011](TASKS/T-011.md) Editor de reglas versionadas | DONE | loadstudio/store.py#update_rules |
| [T-012](TASKS/T-012.md) Historial SQLite y copias | DONE | loadstudio/store.py |
| [T-013](TASKS/T-013.md) OCR y tarifas - prototipos verificables | REVIEW | evidence/ocr-smoke.json |
| [T-014](TASKS/T-014.md) Instalacion privada Mac mini y aceptacion final | BLOCKED | evidence/deployment-acceptance.md pendiente |
| [T-015](TASKS/T-015.md) Integracion privada Worker Python y D1 | DONE | docs/CLOUDFLARE_DEPLOYMENT.md y artifact CI |
| [T-016](TASKS/T-016.md) Despliegue Cloudflare y aceptacion HTTPS persistente | BLOCKED | Evidencia remota pendiente |

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
T-002 + T-006 + T-007 + T-011 + T-012 -> T-015 -> T-016
```

## READY
No tareas TODO derivadas READY. T-016 tiene dependencias tecnicas resueltas, pero no esta ejecutable sin la credencial externa. El usuario ya autorizo alojar la aplicacion; no volver a pedir autorizacion generica ni reconexion MCP. La siguiente accion necesaria es configurar la credencial propia de XPO y su Secret en el panel. T-008 mantiene el bloqueo de aceptacion operativa y T-013 espera fuentes reales. No volver a pedir el XLS original.

## BLOCKED
T-008: faltan ofertas y pegado Wtransnet aceptados por operador. T-014: equipo objetivo no instalado y gates previos pendientes. T-016: falta token de publicacion de Workers Builds dedicado a XPO y XPO_LOGIN_KEY. El conector OAuth si crea Workers/D1, pero no puede crear tokens API (403 explicito). La unica credencial Builds preexistente pertenece a otro proyecto y no se usa. No hay app desplegada ni persistencia remota acreditada.

## Current Epoch
Epoca 3, claim unico xpo-20261020-cloudflare. T-015 DONE con prueba del adaptador sin diagnosticos ni limitador retirado. Los recursos reales son Worker xpo-load-studio y D1 xpo-load-studio-db UE, mas la conexion al repositorio. Worker deployed_on=null y rutas deshabilitadas. El resultado tecnico PASS no significa liberacion operativa. Totales: 12 DONE, 1 REVIEW, 3 BLOCKED.

## Next execution
Leer docs/CLOUDFLARE_DEPLOYMENT.md y T-016. Reutilizar IDs exactos, no recrear base/Worker. Tras configurar credenciales en Cloudflare, comprobar trigger/build, desplegar rama feat/cloudflare-deployment y verificar URL real, acceso privado y persistencia despues de otro despliegue. No importar datos reales, contratar planes ni fusionar PR automaticamente. Conservar motor y version local. Nuevos cambios de codigo requieren CI del nuevo commit.

## Evidencia cloud conectada

Commit ff61f8d89bbcbb1b9764d2b01c7618abea5c465d: [Cloudflare checks 39446374542](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374542), job 118709265212, SUCCESS; [Load Studio checks 39446374450](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374450), SUCCESS. Artifact cloudflare-runtime-evidence ID 12276231995. Local D1 real, auth/limitador, salida determinista y reinicio completo PASS. Esto no acredita publicacion remota.

## Evidencia historica preservada

GitHub Actions [39404120752](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39404120752), job 118565768271, commit 4f4060ce15a586927f1c1e492544df986ab66ca6: SUCCESS. 78/78 pruebas, SHA de 17 fuentes, DAG, JS y navegador/API/portapapeles reales del runner. Se corrigio eval en el test sin relajar CSP. T-007 DONE; no acredita instalacion Mac ni ofertas aceptadas.

Extension: [39406835670](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39406835670), job 118574705486, head 2bc1e582fe3fe402c41ff4054494aa697833e70c, SUCCESS. Merge temporal del runner 4401b47f958d8872a0c4778fb4e4548f449d2ef3, no main. 117 tests, 19 hashes y navegador conectado PASS, incluidas paradas y ML. T-006 DONE. Es evidencia historica de ese commit, no sustituto del CI actual.

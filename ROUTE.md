---
schema: project-route/route@1
id: route-main
project: xpo-load-studio
status: active
baseline_version: '1.0'
current_version: '1.4'
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
updated_at: '2026-10-21'
---
# XPO Load Studio - Ruta de desarrollo

## Strategy
Continuar desarrollo reversible en rama, con evidencia antes de DONE. La aceptacion comercial y despliegue siguen siendo gates de liberacion, no requisitos para escribir prototipos. Replan R-001 en docs/DECISIONS.md conserva objetivos y limites originales. La ampliacion cloud autorizada por el operador conserva la version local y se registra en docs/CLOUDFLARE_DEPLOYMENT.md. No existe un bucle de agentes ejecutandose entre conversaciones.

## Milestones
Fase 1: FOTE/manual, reglas y doble salida (motor y extensiones de ruta/metraje implementados; aceptacion real pendiente). Fase 2: entradas flexibles, XLSX y editor (implementados dentro de la gramatica/formatos documentados). Fase 3: historial, OCR y tarifas (historial probado; prototipos OCR/tarifas sin calibracion real). Instalacion Mac mini/Tailscale pendiente e independiente. Cloudflare: integracion real workerd/D1 local PASS; Worker version ed97eb4f-e231-40dd-a57e-63220a363da6 subida desde GitHub Actions y auditada con la API; no hay ruta publica autorizada. T-016 BLOCKED porque falta XPO_LOGIN_KEY y la aceptacion HTTPS/remota.

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
No tareas TODO derivadas READY. T-016 sigue BLOCKED por falta del Secret de inicio de sesion XPO_LOGIN_KEY (verificado mediante API), ruta HTTPS y pruebas de persistencia reales. La credencial de despliegue XPO en GitHub ya esta configurada; no volver a pedirla ni recrear Worker/D1. El usuario autorizo el alojamiento, no la carga de datos corporativos reales. T-008 mantiene el bloqueo de aceptacion operativa y T-013 espera fuentes reales. No volver a pedir XLS original.

## BLOCKED
T-008: faltan ofertas y pegado Wtransnet aceptados por operador. T-014: equipo objetivo no instalado y gates previos pendientes. T-016: falta XPO_LOGIN_KEY en Cloudflare Production, una ruta segura habilitada y pruebas reales HTTPS/D1 (sin datos corporativos). Version subida y binding DB verificados; no equivale a una app funcional. Cloudflare MCP no esta disponible en esta sesion; audit alternativo via GitHub Actions.

## Current Epoch
Epoca 3, claim unico xpo-20261020-cloudflare. T-015 DONE. Worker xpo-load-studio con version ed97eb4f-e231-40dd-a57e-63220a363da6 alojada; D1 xpo-load-studio-db en la UE; token dedicado en GitHub Actions. Audit run 39599178204: version presente, registro de despliegue presente, XPO_LOGIN_KEY NO presente. workers.dev y previews deshabilitados. No hay URL HTTPS aceptada ni prueba remota de D1. Totales sin cambios: 12 DONE, 1 REVIEW, 3 BLOCKED.

## Next execution
Operador: crear unicamente el Secret XPO_LOGIN_KEY en Cloudflare Production (no en GitHub/chat), guardando su valor en gestor de contrasenas. Controller: repetir audit read-only, comprobar secreto/version y preparar activacion segura de una ruta HTTPS; despues ejecutar pruebas remotas de acceso, render, TSV, D1, dedup, logout y persistencia usando solo datos sinteticos. No habilitar URL si no existe el Secret. No importar datos reales, comprar planes, tocar Evenio ni fusionar PR automaticamente. CI debe acompañar todo cambio nuevo de codigo.

## Evidencia cloud conectada

**Hosted release real**: [run 39596676298, intento 2](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39596676298) PASS, version `ed97eb4f-e231-40dd-a57e-63220a363da6`. La subida incluyo DB, LOGIN_LIMITER y ASSETS; `No targets deployed`. [Auditoria read-only 39599178204](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39599178204) PASS: version y deployment metadata presentes, XPO_LOGIN_KEY ausente. Evidencias en docs/CLOUDFLARE_DEPLOYMENT.md. Esto NO es aceptacion HTTPS ni autoriza trafico publico.

**Workerd local**: Commit ff61f8d89bbcbb1b9764d2b01c7618abea5c465d: [Cloudflare checks 39446374542](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374542), job 118709265212, SUCCESS; [Load Studio checks 39446374450](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39446374450), SUCCESS. Artifact cloudflare-runtime-evidence ID 12276231995. Local D1 real, auth/limitador, salida determinista y reinicio completo PASS. Esto no acredita publicacion remota.

## Evidencia historica preservada

GitHub Actions [39404120752](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39404120752), job 118565768271, commit 4f4060ce15a586927f1c1e492544df986ab66ca6: SUCCESS. 78/78 pruebas, SHA de 17 fuentes, DAG, JS y navegador/API/portapapeles reales del runner. Se corrigio eval en el test sin relajar CSP. T-007 DONE; no acredita instalacion Mac ni ofertas aceptadas.

Extension: [39406835670](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39406835670), job 118574705486, head 2bc1e582fe3fe402c41ff4054494aa697833e70c, SUCCESS. Merge temporal del runner 4401b47f958d8872a0c4778fb4e4548f449d2ef3, no main. 117 tests, 19 hashes y navegador conectado PASS, incluidas paradas y ML. T-006 DONE. Es evidencia historica de ese commit, no sustituto del CI actual.

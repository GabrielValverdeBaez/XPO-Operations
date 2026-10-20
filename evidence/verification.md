# Verificacion de la implementacion - 20/10/2026

## Fuente primaria

`python scripts/audit_xls.py <original privado> <manifiesto>` ejecutado. SHA original en template-audit.json; 26 encabezados, 12 registros DV completos, 27 vehiculos, filas 2-39. El fichero esta vacio en A:Z bajo el encabezado. No contiene cinco ejemplos aceptados y no se inventa ese resultado.

## Pruebas ejecutadas en desarrollo

`python -m pytest -q --disable-warnings`: **78 passed**, 0 failed (68 nuevos y 10 legados de main). Cubre modelos, render exacto, notas, LG por campos, CP, ADR, conflictos, parser, XLSX, reglas, dedupe/backup, version futura de SQLite y endpoints autenticados. `node --check static/app.js`: sin errores de sintaxis. Versiones exactas observadas en runtime.json.

`python scripts/visual_smoke.py`: **PASS** en Chromium 144, API simulada sin acceso de red. Formulario, revision, 26 celdas, limites de negrita, invalidacion y viewport 390px sin desbordamiento. Esto **no** es prueba E2E de navegador con el servidor. Capturas sinteticas locales revisadas; no se suben capturas de trabajo real.

`python scripts/smoke_ocr.py`: **PASS**, una imagen sintetica inglesa, salida 15000 y revision obligatoria. Confianza por palabra no calibrada; no prueba exactitud de capturas reales.

## Ensayo no superado en este entorno

`smoke_browser.py` inicia el servidor loopback, pero Chromium bloquea la navegacion a localhost con ERR_BLOCKED_BY_ADMINISTRATOR. No se eluden las politicas del navegador. El script completo queda preparado para CI/equipo autorizado. En ese ensayo local no se valido el portapapeles. El ensayo posterior en GitHub si lo verifica; el pegado en Wtransnet real sigue pendiente.

## QA de ruta

Ejecutados check_route.py (PASS) y validate_route.py de Project Route (QUALITY_GATE=PASS, errors=0, warnings=0). El estado humano no se deriva de test sintetico. T-006 y T-013 en REVIEW; T-007 DONE tras la prueba CI conectada; T-008/T-014 bloqueadas. Ver TASKS para criterios restantes.

## Publicacion

Codigo, contratos y datos sinteticos unicamente. Original XLS, base de datos de trabajo, tokens y texto FOTE real no se publican. Ninguna instalacion en Mac mini, cambio Tailscale ni envio de ofertas se ha ejecutado.

## CI conectado confirmado - iteracion final

[Run 39404120752](https://github.com/GabrielValverdeBaez/XPO-Operations/actions/runs/39404120752), job 118565768271, sobre commit `4f4060ce15a586927f1c1e492544df986ab66ca6`: **SUCCESS**. Inicio 2026-10-20T09:54:44Z; fin 09:55:28Z. Todos los pasos finalizan bien: SHA-256 de las 17 fuentes, 78 tests, check_route, node --check, instalacion Chromium, smoke_browser conectado y subida de evidencias sinteticas.

La primera ejecucion 39403520780 habia fallado en la espera del test del editor de reglas: el test usaba evaluacion de cadena que la CSP prohibia. Se sustituyo por una asercion del valor de un elemento; la CSP se conserva sin unsafe-eval. La repeticion completa pasa, incluidas copia y lectura del portapapeles, revision, guardar/no duplicar, reapertura de historial, versionado de reglas y viewport movil. El limite local de navegador no se eludio: GitHub Actions utilizo su propio runner autorizado.

El CI acredita el codigo del commit indicado, no una aceptacion comercial ni un despliegue en el ordenador del usuario.

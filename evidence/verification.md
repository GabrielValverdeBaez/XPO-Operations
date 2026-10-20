# Verificacion de la implementacion - 20/10/2026

## Fuente primaria

`python scripts/audit_xls.py <original privado> <manifiesto>` ejecutado. SHA original en template-audit.json; 26 encabezados, 12 registros DV completos, 27 vehiculos, filas 2-39. El fichero esta vacio en A:Z bajo el encabezado. No contiene cinco ejemplos aceptados y no se inventa ese resultado.

## Pruebas ejecutadas en desarrollo

`python -m pytest -q --disable-warnings`: **78 passed**, 0 failed (68 nuevos y 10 legados de main). Cubre modelos, render exacto, notas, LG por campos, CP, ADR, conflictos, parser, XLSX, reglas, dedupe/backup, version futura de SQLite y endpoints autenticados. `node --check static/app.js`: sin errores de sintaxis. Versiones exactas observadas en runtime.json.

`python scripts/visual_smoke.py`: **PASS** en Chromium 144, API simulada sin acceso de red. Formulario, revision, 26 celdas, limites de negrita, invalidacion y viewport 390px sin desbordamiento. Esto **no** es prueba E2E de navegador con el servidor. Capturas sinteticas locales revisadas; no se suben capturas de trabajo real.

`python scripts/smoke_ocr.py`: **PASS**, una imagen sintetica inglesa, salida 15000 y revision obligatoria. Confianza por palabra no calibrada; no prueba exactitud de capturas reales.

## Ensayo no superado en este entorno

`smoke_browser.py` inicia el servidor loopback, pero Chromium bloquea la navegacion a localhost con ERR_BLOCKED_BY_ADMINISTRATOR. No se eluden las politicas del navegador. El script completo queda preparado para CI/equipo autorizado. El portapapeles y pegado real no se declaran validados.

## QA de ruta

Ejecutados check_route.py (PASS) y validate_route.py de Project Route (QUALITY_GATE=PASS, errors=0, warnings=0). El estado humano no se deriva de test sintetico. T-006, T-007, T-013 en REVIEW; T-008/T-014 bloqueadas. Ver TASKS para criterios restantes.

## Publicacion

Codigo, contratos y datos sinteticos unicamente. Original XLS, base de datos de trabajo, tokens y texto FOTE real no se publican. Ninguna instalacion en Mac mini, cambio Tailscale ni envio de ofertas se ha ejecutado.

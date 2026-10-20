# XPO Load Studio - instrucciones de ejecucion

Leer PROJECT.md, ROUTE.md y la tarea concreta antes de cambiar. El usuario autoriza decisiones tecnicas reversibles y avance por tareas sin confirmacion repetitiva; no autoriza inventar datos, cotizaciones, permisos o aceptaciones.

Fuente tecnica Wtransnet: evidence/template-audit.json (26 columnas/12 DV, 38 filas validadas). Fuente de reglas: docs/customer-rules.md y correcciones del operador. No publicar XLS original, datos reales ni tokens. Las pruebas usan datos sinteticos.

Trabajar en rama y PR; no merge automatico. Un unico escritor del estado canonico. No marcar DONE por existencia de codigo: ejecutar pruebas y documentar limites. No usar un CI anterior para acreditar un commit nuevo.

Ejecutar `python -m pytest -q`, `python scripts/check_route.py` y comprobacion JS. Browser E2E: scripts/smoke_browser.py; visual offline: scripts/visual_smoke.py (no confundir). OCR: scripts/smoke_ocr.py. Nunca reemplazar evidencia primaria por expectativas generadas con el mismo codigo.

Prohibido enviar ofertas a FOTE/Wtransnet, abrir red publica, anadir IA generativa en runtime o deducir mercado como porcentaje de cliente. No fingir trabajo persistente entre sesiones. Para procesos largos en el Mac mini usar tmux. Deployment real y aceptacion humana requieren evidencia del equipo/operador.

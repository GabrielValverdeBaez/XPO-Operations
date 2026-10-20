# XPO Load Studio

Aplicacion web local para preparar cargas XPO **sin IA generativa ni servicios externos en tiempo de ejecucion**. Salida bilingue ES/EN y TSV de 26 columnas para pegar manualmente en Wtransnet.

**Estado: candidato de desarrollo 0.1, no desplegado en el Mac mini.** Implementacion y pruebas locales disponibles. La aceptacion operativa no se sustituye por tests sinteticos.

## Arranque

Python 3.13 recomendado (version ejecutada en la verificacion). Desde una copia de esta rama:

```sh
sh start.sh
```

La primera instalacion necesita Internet para paquetes Python. Despues, con el entorno instalado:

```sh
.venv/bin/python scripts/run_local.py
```

Abrir la URL que imprime el programa, incluido el fragmento `#token=...`. El servidor escucha **solo en 127.0.0.1:8765**. No cambiar a 0.0.0.0 ni publicar el token.

## Funciones implementadas

FOTE completo y multiples ordenes separadas; formulario; texto con etiquetas y rutas con flecha; importacion XLSX con mapeo y deteccion de formulas; reglas exactas por cliente; paradas intermedias ordenadas; calculo de ML por dimensiones confirmadas; patron Norauto multientrega; texto enriquecido/Markdown; validacion TSV; historial SQLite con revisiones y duplicados; reglas con control de versiones y restauracion; backups; OCR local opcional; tarifas por corredor aportadas por el operador.

## Limites explicitos

- Se requiere revision antes de copiar o guardar. Campos contradictorios bloquean la salida hasta corregirlos.
- Texto libre significa gramatica acotada, no interpretacion universal. Sin ano, pais, CP o unidades suficientes se pide completar datos.
- Rutas con paradas intermedias requieren el itinerario completo: accion, lugar y fecha de cada parada. Si faltan datos, no se convierten en rutas directas. El editor avanzado usa JSON revisable.
- El importador general admite `.xlsx`, no cualquier BIFF/XLS. El lector BIFF8 incluido audita de forma acotada la plantilla original.
- Editor de reglas: notas y activacion de reglas conocidas; no ejecuta codigo ni permite inventar clientes automaticamente.
- No hay tarifas reales precargadas ni se usa una tarifa directa para multientrega. Sin evidencia suficiente: `Por confirmar / To be confirmed`.
- OCR necesita el ejecutable Tesseract local. Su confianza no es una garantia de exactitud de campos.
- No se envia nada a FOTE ni Wtransnet. No hay agente de desarrollo persistente ejecutandose por instalar la app.

## Documentacion

[ROUTE.md](ROUTE.md) contiene tareas, evidencia y trabajo pendiente. [PROJECT.md](PROJECT.md) fija objetivos y limites. [REQUIREMENTS.md](REQUIREMENTS.md) conserva el contrato. [Uso y operacion](docs/USAGE.md), [auditoria XLS](docs/wtransnet-schema.md), [reglas por cliente](docs/customer-rules.md), [decisiones](docs/DECISIONS.md) y [verificacion](evidence/verification.md).

## Pruebas

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/check_route.py
```

Pruebas opcionales: `python scripts/smoke_ocr.py` y `python scripts/smoke_browser.py` (Playwright con Chromium instalado). El original XLS y los datos reales no se guardan en el repositorio publico.

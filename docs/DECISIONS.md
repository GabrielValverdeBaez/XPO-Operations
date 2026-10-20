# Decisiones y replan 2026-10-20

## D-001 - Recuperar la fuente primaria sin instalar un lector incompleto

Hipotesis: el archivo BIFF8 aportado permite extraer encabezados, catalogos y registros DV con un lector acotado y de solo lectura. Alternativas: instalar xlrd, convertir el libro con otra suite, o leer los registros necesarios directamente. La conectividad de este entorno impide instalar; ademas xlrd documenta que no interpreta validaciones de datos. Se eligio el lector acotado, sin macros ni evaluacion de formulas.

Evidencia: `scripts/audit_xls.py`, hash y doce DV en `evidence/template-audit.json`. Todos los tokens DV encontrados se resolvieron; estructuras no soportadas se rechazan. No se afirma compatibilidad con todo XLS.

Fuentes primarias: [MS-XLS DV](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xls/862bbc7c-009a-4fd6-a93e-3e32e591c2f8), [xlrd](https://pypi.org/project/xlrd/). El informe conserva valores observados; no ejecuta formulas del libro.

## D-002 - Una instalacion Python; interfaz web sin compilador Node

Hipotesis: para una herramienta local de un operador, FastAPI/Pydantic + SQLite + HTML/CSS/JavaScript nativo puede cubrir los flujos sin un build React. La alternativa React/TypeScript original era una preferencia a validar, no un requisito cerrado.

Comprobacion: API real mediante TestClient, servidor loopback arrancado durante smoke y UI real renderizada con API simulada en Chromium. La conexion de Chromium a localhost esta bloqueada por politica de este entorno; no se cuenta como E2E pasado. JavaScript se comprueba con `node --check`. Elegida la alternativa sin build Node para simplificar instalacion. Migracion a React sigue siendo reversible: la API y el motor estan separados.

Fuente primaria: [FastAPI deployment](https://fastapi.tiangolo.com/deployment/manually/), [SQLite backup](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).

## R-001 - Separar desarrollo verificable de aceptacion operativa

La autorizacion del usuario permite iterar todas las fases sin pedir permiso para cada tarea reversible. El gate previo a generadores se satisface tecnicamente al contrastar A:Z, catalogos, DV y reglas conocidas con la plantilla y las instrucciones aprobadas. No se elimina el gate de aceptacion real: se mantiene en T-008 y el despliegue T-014.

Los cinco o mas pares aceptados en operativa real no se inventan. Los ejemplos nuevos son sinteticos. El ensayo de pegado en Wtransnet, portapapeles real y aceptacion humana permanecen pendientes. T-009 a T-013 pueden desarrollarse y probarse en rama sin esperar a la liberacion del MVP; ahora dependen del motor/modelo ya verificados, no de la aprobacion de produccion. No hay cambios en objetivos, exposicion de red, limites comerciales, ni envio automatico.

Fuera de la cobertura inicial: multi-parada, patron Norauto multientrega, importacion XLS general, editor arbitrario de clientes, calibracion real de tarifas. Se bloquean o documentan; no se sustituyen por conjeturas. T-006 permanece en REVIEW por estas extensiones de reglas, aunque su nucleo este probado.

## Research Exit Gate

PASS para desarrollo en rama: formato primario resuelto; alternativas tecnicas evaluadas de forma acotada; ausencia de tarifas reales tratada como pendiente; incertidumbre empirica de E2E/uso real reservada a T-008 y despliegue a T-014. No es una aprobacion de produccion.

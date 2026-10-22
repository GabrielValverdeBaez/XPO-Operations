# Ruta y recuperación

Repositorio: https://github.com/GabrielValverdeBaez/XPO-Operations

Para ejecución de proyecto: leer AGENTS.md → PROJECT.md → ROUTE.md → .project/DEPARTMENTS.md → .project/HANDOFF.md → ROUTE/HANDOFF del departamento → tarea y evidencia. Consultar rama y estado remoto real; no confundir main, rama de la skill y ramas de Load Studio.

Seguir Crear Modo Ruta al adaptar estructura y Modo Ruta al ejecutar: un escritor, tareas con dependencias, implementación → pruebas → evaluación → corrección, checkpoint inmutable, handoff y siguiente READY. DONE exige salida y evidencia; registrar BLOCKED con causa y acción necesaria sin bloquear trabajo independiente. No reiniciar planificación en cada sesión.

Estados: TODO, READY, IN_PROGRESS, REVIEW, DONE, BLOCKED, CANCELLED. Una tarea READY requiere dependencias DONE. Registrar decisiones y nuevas ideas en .project/DECISIONS.md e IDEAS.md, historial por departamento. Actualizar STATE.json como índice verificable de las tareas; la ruta raíz es el único plan global.

Load Studio permanece subproyecto con motor determinista sin IA generativa obligatoria. No declarar desplegado porque exista Worker o CI local. PR #4 y rama feat/cloudflare-deployment tienen gates propios; consultarlos antes de intervenir. No fusionar automáticamente ni cambiar producción por ejecutar la ruta de la skill.

Conversación: «XPO Operations: continúa la ruta» ejecuta siguiente READY; «estado» consulta; «pausa» persiste; «done» solicita comprobar evidencia, no cerrar a ciegas. No hay ejecución fuera de sesión sin scheduler/runtime explícito.

Estado de la primera integración y limitación de publicación: [iteración inicial](iteracion-inicial.md). Leer esta nota antes de asumir existencia de la rama remota.

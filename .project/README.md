# Memoria de proyecto

ROUTE.md raíz es el único plan global. STATE.json indexa tareas y estados. DEPARTMENTS.md dirige al departamento y a su HANDOFF. Cada cierre conserva evidencia y un checkpoint inmutable en history/<departamento>/. DECISIONS.md registra decisiones; IDEAS.md propuestas no aprobadas. No guardar chats completos ni datos comerciales.

Recuperar leyendo raíz → índice → handoff → departamento → tarea/evidencia. Revisar rama remota y PR antes de actuar. Conservar fecha, commit base y limitaciones en evidencia; comprobar el HEAD nuevo con CI propio.

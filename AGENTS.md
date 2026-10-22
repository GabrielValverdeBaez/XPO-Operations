# XPO Operations — ejecución

Leer PROJECT.md, ROUTE.md, .project/DEPARTMENTS.md y .project/HANDOFF.md. Para una operación diaria leer solo SKILL.md y el módulo pertinente. No forzar planificación de proyecto en cada carga.

Un escritor actualiza estado. Usar ramas y PR; no merge automático. Ejecutar tareas READY con dependencias DONE; iterar implementación, prueba, evaluación, corrección. Persistir checkpoint inmutable y handoff. No declarar DONE por un documento, commit, CI anterior o «done» del usuario.

Repositorio público: solo reglas reutilizables y ejemplos ficticios. No subir contactos, datos de cargas reales, tarifas, matrículas, conductores, XLS corporativos, URLs privadas ni secretos. No copiar paquetes originales sin revisar contenido. Las listas de exclusión se consultan en privado; no confundir su ausencia en Git con ausencia de vetos.

No enviar ofertas/mensajes ni escribir FOTE/Wtransnet por generar textos. Consultar permisos de la acción concreta. No desplegar ni fusionar Load Studio por ejecutar esta ruta. No añadir IA generativa al motor determinista. Mercado nunca se deriva del ingreso cliente.

Checks de este alcance: `python scripts/check_operations_route.py`, `python -m unittest discover -s tests -p 'test_operations*.py'`, `python -m unittest discover -s tests`. La skill portable se valida con quick_validate del creador si está disponible. Contrastar textos/TSV con oráculos independientes y probar recuperación desde otro checkout. Registrar limitaciones.

Load Studio conserva PROJECT/ROUTE baseline en .project/departments/load-studio, implementación en feat/load-studio-implementation-20261020, cloud en feat/cloudflare-deployment. Leer sus AGENTS y tareas al intervenir allí; no asumir que main contiene su código. Procesos largos en Mac mini: tmux.

# XPO Operations

Skill y repositorio para la operativa diaria XPO, con ruta de ejecución y memoria versionada.

- [Skill principal](skills/xpo-operations/SKILL.md): cargas, Wtransnet, proveedores, directorio, correos e incidencias.
- [Proyecto](PROJECT.md), [ruta](ROUTE.md), [handoff](.project/HANDOFF.md) y [departamentos](.project/DEPARTMENTS.md).
- [Fuentes inventariadas](.project/SOURCES.json) y [decisiones](.project/DECISIONS.md).
- [Load Studio](.project/departments/load-studio/HANDOFF.md): desarrollo y despliegue separados, pendientes de sus gates.

## Uso
Copiar skills/xpo-operations en el directorio de skills del agente, o leer su SKILL.md desde Git con acceso al repositorio. Los scripts usan Python 3 y biblioteca estándar. La instalación en ChatGPT y las conexiones privadas son capacidades distintas; copiar un repo no concede acceso a OneDrive/Notion/FOTE.

| Modo | Uso |
|---|---|
| OPERATIVA | Ejecutar cargas, consultas, registros y otras tareas diarias |
| SISTEMA | Configurar o desarrollar la skill, las reglas y las herramientas |

```text
Usa $xpo-operations en modo OPERATIVA para preparar esta carga.
XPO Operations — OPERATIVA: añade este proveedor al Directorio.
XPO Operations — SISTEMA: cambia esta regla y sincroniza la skill.
XPO Operations — SISTEMA: continúa la ruta y ejecuta la siguiente tarea READY.
XPO Operations — SISTEMA: consulta el estado; no ejecutes tareas.
```

Sin prefijo, deducir la intención y usar OPERATIVA para el trabajo diario. «Continúa» mantiene el contexto activo. Consultar estado no activa desarrollo. Una excepción puntual no se guarda como regla permanente salvo que se solicite. Los commits en GitHub no actualizan automáticamente la skill instalada; un cambio solicitado en SISTEMA debe sincronizar ambas copias. Ver contrato completo en SKILL.md.

## Verificación
```bash
python scripts/check_operations_route.py
python -m unittest discover -s tests -p 'test_operations*.py'
python -m unittest discover -s tests
```

Estado: primera integración con proyecciones de seis workflows y herramientas sintéticas; la paridad completa y aceptación privada permanecen pendientes. No contiene un directorio de contactos ni tarifas comerciales. El Excel de OneDrive continúa siendo maestro. No envía ni publica ofertas automáticamente.

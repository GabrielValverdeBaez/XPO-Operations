# XPO Operations

Skill y repositorio para la operativa diaria XPO, con ruta de ejecución y memoria versionada.

- [Skill principal](skills/xpo-operations/SKILL.md): cargas, Wtransnet, proveedores, directorio, correos e incidencias.
- [Proyecto](PROJECT.md), [ruta](ROUTE.md), [handoff](.project/HANDOFF.md) y [departamentos](.project/DEPARTMENTS.md).
- [Fuentes inventariadas](.project/SOURCES.json) y [decisiones](.project/DECISIONS.md).
- [Load Studio](.project/departments/load-studio/HANDOFF.md): desarrollo y despliegue separados, pendientes de sus gates.

## Uso
Copiar skills/xpo-operations en el directorio de skills del agente, o leer su SKILL.md desde Git con acceso al repositorio. Los scripts usan Python 3 y biblioteca estándar. La instalación en ChatGPT y las conexiones privadas son capacidades distintas; copiar un repo no concede acceso a OneDrive/Notion/FOTE.

```text
Usa $xpo-operations para preparar esta carga.
XPO Operations: continúa la ruta y ejecuta las tareas READY.
XPO Operations: estado y siguiente paso.
```

## Verificación
```bash
python scripts/check_operations_route.py
python -m unittest discover -s tests -p 'test_operations*.py'
python -m unittest discover -s tests
```

Estado: primera integración con proyecciones de seis workflows y herramientas sintéticas; la paridad completa y aceptación privada permanecen pendientes. No contiene un directorio de contactos ni tarifas comerciales. El Excel de OneDrive continúa siendo maestro. No envía ni publica ofertas automáticamente.

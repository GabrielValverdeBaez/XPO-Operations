---
name: xpo-operations
description: Coordina los modos OPERATIVA para ejecutar el trabajo diario XPO y SISTEMA para configurar o desarrollar la skill y su ruta versionada en GitHub. Usar para cargas FOTE, textos ES/EN, filas Wtransnet, selección y enriquecimiento de transportistas, Directorio Excel/OneDrive, proveedores estables de Notion, correos, incidencias y continuidad de XPO Operations. Recuperar fuentes vigentes, aplicar el módulo pertinente y conservar decisiones y evidencias sin publicar datos comerciales.
---
# XPO Operations

## Elegir el modo de invocación

Distinguir dos usos de la misma skill. Los prefijos son instrucciones conversacionales, no comandos de un programa.

| Modo | Invocación explícita | Resultado |
|---|---|---|
| OPERATIVA | `XPO Operations — OPERATIVA: prepara esta carga` | Resolver el trabajo diario con las reglas vigentes |
| SISTEMA | `XPO Operations — SISTEMA: modifica esta regla de la skill` | Configurar, mantener o desarrollar la skill, sus herramientas o la ruta del proyecto |

También aceptar `$xpo-operations` seguido de la petición y deducir el modo por el objetivo:
- **OPERATIVA por defecto:** preparar textos/filas, consultar o incorporar proveedores, actualizar registros del Directorio/Notion, extraer correos o tramitar una incidencia concreta. Leer solo los módulos necesarios y terminar al entregar y validar el resultado pedido. Añadir un proveedor al Excel cambia datos operativos, no la configuración de la skill. No abrir tareas de desarrollo ni modificar las instrucciones de la skill por ejecutar una carga.
- **SISTEMA cuando se solicita un cambio del mecanismo:** configurar o corregir reglas persistentes, formatos, validadores, integraciones, documentación, memoria del proyecto o desarrollar Load Studio. Leer el estado remoto y continuar la ruta pertinente; implementar y validar el cambio, sincronizar repositorio y skill instalada cuando corresponda, registrar evidencia y cerrar la tarea al cumplir su gate. Mejoras opcionales al backlog, sin reabrir tareas aceptadas indefinidamente.
- **Consulta del sistema:** «estado de la ruta» o «cómo se invoca» permite consultar/explicar sin activar desarrollo. «Continúa la ruta» activa ejecución de tareas READY. «Continúa» solo conserva el modo y tarea del turno previo; no inicia desarrollo por sí solo.
- **Petición combinada:** si pide resolver una operación y además guardar una regla, completar primero la operación y después el cambio solicitado en SISTEMA, diferenciando ambos resultados. Una excepción para esta carga no se convierte en regla permanente sin petición de conservarla. «A partir de ahora» o «guarda esta regla» sí indica persistencia.
- Si falta un dato crítico o no puede distinguirse una excepción puntual de una regla permanente, avanzar en lo independiente y preguntar solo por esa diferencia. Evitar confirmaciones repetidas cuando la intención ya es clara.

Ejemplos:
```text
Usa $xpo-operations en modo OPERATIVA para preparar esta carga y su fila Wtransnet.
XPO Operations — OPERATIVA: añade este proveedor al Directorio.
XPO Operations — SISTEMA: cambia el formato de las ofertas y sincroniza la skill.
XPO Operations — SISTEMA: continúa la ruta y ejecuta la siguiente tarea READY.
XPO Operations — SISTEMA: consulta el estado; no ejecutes tareas.
```

La instalación de la skill y el repositorio GitHub son copias distintas: un commit en GitHub no actualiza automáticamente la skill instalada. En una modificación solicitada desde aquí, sincronizar ambas y comprobar el guardado; si una parte falla, indicar cuál quedó pendiente. Leer el HEAD remoto vigente antes de integrar cambios. Ningún modo añade por sí mismo autorización de envío, publicación de ofertas, gasto, despliegue o merge.

## Resolver una tarea diaria
1. Identificar la salida pedida y leer únicamente el módulo correspondiente de la tabla. Evitar cargar toda la ruta para producir un texto o una fila.
2. Obtener la fuente actual. Aplicar instrucción expresa → fuente actual → regla confirmada vigente. No heredar datos de expediciones anteriores.
3. Usar la skill especializada instalada si aporta reglas privadas o excepciones todavía no migradas. Su ausencia no autoriza inventarlas. Consultar [fuentes](references/fuentes.md).
4. Resolver la parte autorizada, validar y entregar en el formato del módulo. Pedir solo datos críticos realmente ausentes; ejecutar por separado las partes independientes.
5. No enviar correos, publicar ofertas ni escribir en FOTE/Wtransnet por el mero hecho de preparar una salida. Una edición concreta solicitada en Excel/Notion sí autoriza esa edición reversible, con validación y conservación de identidad.
6. Guardar reglas generalizables y cambios de proyecto en Git; mantener contactos, cargas, precios, documentos y evidencias comerciales en sus fuentes privadas. No confundir un correo extraído con un contacto aprobado o disponible.

| Intención | Leer | Especialista existente |
|---|---|---|
| Texto de una carga, oferta ES/EN | [Cargas](references/cargas.md) | xpo-textos-de-cargas |
| Excel Wtransnet, nuevas/faltantes, comparar capturas | [Wtransnet](references/wtransnet.md) | genera-excel-wtransnet |
| Quién cubre ruta, ADR, dúo, retorno o corredor | [Transportistas](references/transportistas.md) | xpo-carrier-selector |
| Analizar perfiles, nuevas empresas, correos del lote | [Directorio](references/directorio.md) | xpo-enriquecimiento-transportistas-wtransnet |
| Añadir/corregir/reclasificar Directorio.xlsx | [Directorio](references/directorio.md) | xpo-directorio-transportistas |
| Proveedores estables en provincias de Notion | [Notion](references/notion.md) | directorio-notion |
| Contactos por Andalucía/Galicia, viajes, precios históricos, observaciones o caché | [Caché privada](references/cache.md) | scripts/project_cache.py |
| Extraer correos de un fichero | [Correos](references/correos.md) | scripts/operations.py |
| Esperas, rechazos, devolución, reclamación | [Incidencias](references/incidencias.md) | investigación jurídica vigente si procede |
| Crear ruta, continuar, estado, ideas, desarrollar Load Studio | [Continuidad](references/continuidad.md) | protocolo Crear Modo Ruta / Modo Ruta |

## Persistir contactos y operaciones
Leer [Caché privada](references/cache.md) para consultar o conservar contactos, rutas, viajes, precios y observaciones. Usar el snapshot privado existente para consultas documentales rápidas; distinguir rutas declaradas, viajes registrados y entregados. Después de incorporar datos observados, guardar y verificar la copia privada persistente. Mantener Directorio.xlsx como maestro y comprobar sus controles vigentes antes de recomendar. No guardar datos reales en GitHub ni confundir caché local con persistencia remota verificada.

## Validar
- Wtransnet: ejecutar `python scripts/validate_wtransnet_rows.py` con TSV por stdin. Entregar 26 columnas, sin precios, sin Excel adjunto.
- Directorio: ejecutar `python scripts/operations.py directory` con TSV por stdin: 19 columnas, sin escritura externa.
- Correos: ejecutar `python scripts/operations.py emails` con texto por stdin; pasar exclusiones verificadas con `--blocked archivo_privado.txt`. La extracción sola no valida uso comercial.
- No declarar compatibilidad operativa, disponibilidad, aprobación, envío o persistencia externa por pasar validaciones estructurales.

## Iterar el repositorio
Leer el estado remoto vigente en `GabrielValverdeBaez/XPO-Operations` antes de ejecutar tareas de proyecto; seguir `.project/HANDOFF.md` y ROUTE.md en la rama de trabajo pertinente. No asumir que main contiene cambios en PR abiertos. Trabajar hasta cumplir el gate o encontrar un bloqueo real, registrar checkpoint y siguiente tarea. Una skill no es un proceso perpetuo ni una automatización horaria.

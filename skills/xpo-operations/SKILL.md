---
name: xpo-operations
description: Coordina la operativa diaria XPO y su ruta versionada en GitHub. Usar para cargas FOTE, textos ES/EN, filas Wtransnet, selección y enriquecimiento de transportistas, Directorio Excel/OneDrive, proveedores estables de Notion, correos, incidencias y continuidad de XPO Operations. Recuperar fuentes vigentes, aplicar el módulo pertinente y conservar decisiones y evidencias sin publicar datos comerciales.
---
# XPO Operations

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
| Extraer correos de un fichero | [Correos](references/correos.md) | scripts/operations.py |
| Esperas, rechazos, devolución, reclamación | [Incidencias](references/incidencias.md) | investigación jurídica vigente si procede |
| Crear ruta, continuar, estado, ideas, desarrollar Load Studio | [Continuidad](references/continuidad.md) | protocolo Crear Modo Ruta / Modo Ruta |

## Validar
- Wtransnet: ejecutar `python scripts/validate_wtransnet_rows.py` con TSV por stdin. Entregar 26 columnas, sin precios, sin Excel adjunto.
- Directorio: ejecutar `python scripts/operations.py directory` con TSV por stdin: 19 columnas, sin escritura externa.
- Correos: ejecutar `python scripts/operations.py emails` con texto por stdin; pasar exclusiones verificadas con `--blocked archivo_privado.txt`. La extracción sola no valida uso comercial.
- No declarar compatibilidad operativa, disponibilidad, aprobación, envío o persistencia externa por pasar validaciones estructurales.

## Iterar el repositorio
Leer el estado remoto vigente en `GabrielValverdeBaez/XPO-Operations` antes de ejecutar tareas de proyecto; seguir `.project/HANDOFF.md` y ROUTE.md en la rama de trabajo pertinente. No asumir que main contiene cambios en PR abiertos. Trabajar hasta cumplir el gate o encontrar un bloqueo real, registrar checkpoint y siguiente tarea. Una skill no es un proceso perpetuo ni una automatización horaria.

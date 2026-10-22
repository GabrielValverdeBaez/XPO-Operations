# Caché privada del proyecto

## Qué conserva
- Contactos del Directorio con correos, rutas declaradas, cobertura, observaciones y fila/fuente original.
- Viajes documentados, con Trip/Order, fechas, ruta y estado. No expandir una tabla agregada en viajes individuales inventados. Mantener registros sin IDs como provisionales.
- Operaciones y ventas con cliente, transportista cuando conste, ingreso cliente, coste de transportista, estimación de mercado y moneda por separado. Una orden disponible/oferta no es una venta realizada; coste cero sin transportista no es una tarifa contratada.
- Observaciones propias, exclusiones y auditoría. Cada registro conserva fuente, versión y fecha; no sustituir datos por memoria del chat.

## Ubicación y recuperación
Código: scripts/project_cache.py dentro de la skill. Datos locales: private/cache/xpo-cache.sqlite3 y private/cache/snapshot.json en la carpeta del proyecto; ambos excluidos de Git. XPO_CACHE_DB permite una ruta local diferente.

Copia privada persistente: OneDrive, carpeta TRANSPORTE/XPO Operations/cache, archivo snapshot.json. Localizar por carpeta y nombre con Microsoft SharePoint/OneDrive, recuperar el archivo exacto y conservar su identidad para actualizarlo. Los IDs del usuario se resuelven en privado; no se añaden a Git público. La carpeta ya se creó y se pobló durante esta integración. No crear copias en otras cuentas ni enlaces públicos.

Al inicio de sesión: comprobar la copia privada vigente. Si falta la base local, recuperar y analizar snapshot.json en código, o guardar su texto completo en un archivo privado y restaurarlo en una base vacía. Nunca imprimir el snapshot completo al chat. Si el conector aporta texto JSON, puede analizarse directamente para la consulta documental; respetar los mismos filtros de evidencia/exclusión. El backup permite reconstruir el índice; la persistencia no depende de scratch.

```bash
python skills/xpo-operations/scripts/project_cache.py restore private/cache/snapshot.json
python skills/xpo-operations/scripts/project_cache.py stats
```

Después de incorporar datos verificados solicitados, actualizar la caché, exportar snapshot y reemplazar el mismo archivo privado de OneDrive. Un único escritor; comprobar que la versión remota no haya cambiado desde la lectura y conservar cambios externos antes de subir. El conector no ofrece una escritura condicional atómica: no lanzar escritores paralelos ni afirmar bloqueo distribuido. Verificar la lectura remota antes de declarar persistencia. Si falla, conservar el cambio local y declarar que falta sincronizar; no afirmar continuidad asegurada.

## Interpretar consultas naturales
| Petición | Evidencia |
|---|---|
| Correos con viajes a Andalucía/Galicia | history y direction=to; separar estados documentados de entregados |
| Viajes realizados/entregados | delivered; no incluir asignados/provisionales/cancelados |
| Transportistas cuya ruta incluye una región | declared: campo Ruta; no inferir por sede o cobertura |
| Contactos por cobertura | coverage, indicando que no son viajes acreditados |
| Histórico de ventas y precios | sales; completed-only para entregadas/facturadas; conservar disponibles aparte |
| Anota una observación sobre un proveedor o carga | observations con referencia y fuente; no sobrescribir notas del maestro |

```bash
python skills/xpo-operations/scripts/project_cache.py query Andalucía --basis history --direction to --emails
python skills/xpo-operations/scripts/project_cache.py query Galicia --basis declared --emails
python skills/xpo-operations/scripts/project_cache.py query Galicia --basis delivered --direction to
python skills/xpo-operations/scripts/project_cache.py sales --completed-only
python skills/xpo-operations/scripts/project_cache.py notes
```

El reconocimiento inicial incluye Andalucía y Galicia, sus provincias y un catálogo explícito de localidades frecuentes. No es un geocodificador ni un censo completo. Los lugares no reconocidos quedan sin clasificar; añadir una equivalencia verificada al código para ampliar cobertura. Las rutas declaradas no se fuerzan a origen/destino cuando son texto libre. Nunca interpretar falta de coincidencia como ausencia definitiva de actividad.

En una extracción documental solicitada, devolver los correos únicos pertinentes con fuente y fecha de la caché, y aclarar alcance si no es exhaustiva. No etiquetar como viajes hechos una ruta declarada o una sede gallega/andaluza. Aplicar exclusiones explícitas de correo/empresa en todas las salidas. No interpretar como «sin bloqueos» la ausencia de estilos de celda.

## Frescura y maestro
Para una consulta documental rápida, usar la caché y comprobar metadatos/versión de la fuente cuando se afirma vigencia. Si cambió el Directorio, refrescar su snapshot dentro de una transacción; el motor retira filas antiguas de esa fuente al cambiar versión y conserva viajes, operaciones y notas propias. No borrar evidencias históricas porque desaparezca un contacto.

Para recomendar/asignar o preparar una comunicación comercial, seguir el especialista: histórico → Directorio vigente con colores/exclusiones → ampliación web cuando corresponda. La consulta de caché no sustituye esta selección. --approved-only requiere controles checked con fecha menor de 24 horas; unknown, controles futuros/antiguos y bloqueados no aprueban. La lectura inicial del Excel por el conector solo aportó valores: su formato rojo NO se considera comprobado. No cambiar controls a checked por tener datos o por pasar pruebas sintéticas.

## Ingesta y respaldo
`ingest archivo_privado.json` admite source y listas records, trips, operations, observations y exclusions. source exige key y version; opcionalmente locator, content_hash y notes. Cada record requiere row y values (19 campos). No inventar IDs de empresa ni fusionar por similitud: exactitud o alias documentado. Las reimportaciones del mismo ID no duplican viajes; las observaciones tienen fecha e identidad propia.

```bash
python skills/xpo-operations/scripts/project_cache.py ingest private/cache/nuevo-lote.json
python skills/xpo-operations/scripts/project_cache.py export private/cache/snapshot.json
```

Este índice no cambia la fuente maestra Directorio.xlsx. Importar un proveedor a la caché no equivale a darlo de alta en Excel ni a homologarlo. No se envían ofertas ni se escriben servicios externos desde el script. Los imports y copias reales permanecen exclusivamente en carpeta privada; solo fixtures sintéticos se versionan.

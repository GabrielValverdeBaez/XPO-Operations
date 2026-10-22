# HIST — Histórico de viajes, precios y observaciones

## Elegir la acción
HIST es el departamento responsable del histórico. Consultar su ruta/handoff en el repositorio solo para configuración o desarrollo; una petición diaria se resuelve aquí y con [Caché privada](cache.md).

```text
XPO Operations — OPERATIVA: guarda este viaje en Histórico con su precio y observaciones.
XPO Operations — OPERATIVA: añade esta observación al viaje con referencia TEST-001.
XPO Operations — OPERATIVA: consulta el histórico de precios de esta ruta.
XPO Operations — OPERATIVA: muestra las ventas realizadas de este cliente.
XPO Operations — SISTEMA: configura el departamento de Histórico.
```

## Contrato del registro
Conservar cuando conste: Order Number, Trip Number, cliente, transportista, origen/destino/paradas, recogida/descarga, estado, ingreso cliente, coste transportista, estimación de mercado, moneda, observaciones, fuente, fecha y versión de la evidencia. Los detalles sin columna propia pueden conservarse en observaciones vinculadas, sin inventar una estructura de datos que el motor no soporte.

Priorizar Trip Number para deduplicar viajes; usar Order Number como relación/control, no fusionar viajes diferentes de una misma orden. Sin IDs conservar registro provisional por fuente, fecha, empresa y ruta. Un registro provisional no acredita viaje realizado. Resolver identidades por exactitud o alias documentado; si no hay relación inequívoca, conservar separados.

Separar estados disponible, ofertado, asignado, recogido, entregado, cancelado y facturado. Actualizar estado con evidencia, no por haber pasado la fecha prevista. Para una operación con diferentes estados se conserva historial; antes de sumar ingresos/costes, consolidar por la identidad de la operación y evitar contar sus snapshots de estado como ventas distintas. El comando sales devuelve registros, no totales financieros conciliados.

Guardar importes como decimales exactos y su moneda. Ingreso cliente, coste transportista y estimación de mercado son campos distintos; no calcular uno como porcentaje del otro ni rellenar ausencias. Coste 0 de una orden sin transportista puede ser un marcador del sistema: guardar coste desconocido. Registrar si el precio es oferta, confirmado o realizado según la fuente/estado; una cifra histórica no acredita una tarifa vigente.

## Observaciones
Vincular cada nota a carrier, operation, route o general mediante subject_ref, conservar texto, fecha y fuente. No borrar una observación del maestro al añadir una propia. Mantener correcciones y decisiones recuperables; no reemplazar hechos por conjeturas. En una incidencia, separar hecho documentado, instrucción del operador y valoración pendiente.

## Guardar y recuperar
Usar trips/operations/observations del mismo project_cache.py y el mismo snapshot privado del proyecto. No crear un fichero público de viajes ni una segunda fuente de contactos. Las tablas carriers/records/exclusions siguen bajo responsabilidad de Proveedores y los bloqueos se aplican al reutilizar contactos históricos.

```bash
python skills/xpo-operations/scripts/project_cache.py ingest private/cache/nuevo-lote.json
python skills/xpo-operations/scripts/project_cache.py sales --completed-only
python skills/xpo-operations/scripts/project_cache.py notes --subject TEST-001
python skills/xpo-operations/scripts/project_cache.py export private/cache/snapshot.json
```

Para una consulta por referencia/cliente/ruta, leer y filtrar las tablas privadas o sales/notes según corresponda; no afirmar que existe un filtro CLI que no está implementado. Tras incorporar información, sincronizar el mismo snapshot privado, verificar su lectura remota y comunicar el resultado. Sin verificación remota no declarar persistencia entre sesiones. Un único escritor y reglas de conflicto de cache.md.

## Entrega y cierre
Responder con el viaje u operación identificada, precios confirmados separados, observación guardada y pendientes concretos. En consultas, indicar la fecha/cobertura del histórico y distinguir asignado de entregado. No iniciar envíos ni recomendaciones de asignación por registrar un viaje. Cerrar la petición diaria una vez guardada y verificada; mejoras del sistema al backlog.

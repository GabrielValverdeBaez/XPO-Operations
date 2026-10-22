# HIST — Histórico de viajes, precios y observaciones

## Misión y alcance
Conservar y consultar la experiencia operativa acumulada: viajes, estados, cliente, transportista, ingresos, costes, estimaciones y observaciones. Gestionar las tablas trips, operations y observations de la caché privada existente, sin crear otra base ni copiar datos comerciales a Git.

Proveedores mantiene identidad, contactos, rutas declaradas y exclusiones. Cargas prepara la expedición actual. Incidencias investiga y gestiona el caso; HIST conserva el resultado y observaciones verificadas. Calidad mantiene contrato, recuperación y auditoría. El controlador sigue siendo el único escritor de estado y snapshot remoto.

## Implantación
OPS-013 crea el departamento, contratos, handoff y enrutamiento en la skill. Estado en STATE.json. Se reutiliza OPS-012, ya ejecutada, para persistencia y consultas; no reabrir su implementación por una separación organizativa.

## Trabajo diario
1. Leer la petición y fuente actual; consultar el módulo de histórico de la skill.
2. Incorporar o consultar el viaje/operación/observación según sus IDs y evidencia.
3. Conservar estados, importes y procedencia; validar, deduplicar y persistir en la caché privada.
4. Verificar la copia remota y entregar resultado/recuento resumido. Si falla el guardado, declarar el pendiente y conservar los datos locales.
5. Cerrar la petición al cumplir su salida. No crear una tarea de programación por cada viaje. Las ampliaciones de capacidades se tramitan en SISTEMA como tareas independientes.

Una orden disponible o asignada no se trata como viaje entregado ni venta realizada. Una ruta declarada no se convierte en viaje histórico. Los precios son históricos, no cotizaciones actuales.

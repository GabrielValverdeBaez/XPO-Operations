# XPO Operations

## Objetivo
Convertir la operativa diaria de tráfico XPO en una skill reusable, modular y versionada en este repositorio: cargas y textos ES/EN, Wtransnet, proveedores y contactos, Directorio Excel/OneDrive, selección estable de Notion, incidencias, memoria y herramientas deterministas.

El usuario autoriza crear la ruta e iterar con decisiones reversibles y mínima intervención. Git guarda procedimientos, contratos, tareas y evidencias sintéticas. Las fuentes comerciales siguen privadas. Consultar ROUTE.md y .project/HANDOFF.md para estado real.

## Arquitectura
- skills/xpo-operations: entrada portable y módulos cargados bajo demanda; scripts independientes.
- Skills XPO actuales: especialización y reglas privadas que aún no están migradas íntegramente; conservarlas hasta aceptación de paridad.
- .project: departamentos, tareas, estado, decisiones, ideas, checkpoints y evidencias.
- Load Studio: herramienta determinista existente en ramas de desarrollo; su baseline documental se conserva bajo .project/departments/load-studio. No reconstruir ni declarar su despliegue terminado.

## Fuentes y límites
Directorio.xlsx vigente de OneDrive es maestro; histórico de viajes verifica experiencia; Notion es selección estable. FOTE/export/captura actual aporta cada carga. No versionar contactos, importes/cargas reales, XLS, credenciales ni endpoints privados en este repositorio público. Conservar exclusiones y estilos rojos. Nunca inferir ADR, disponibilidad, cotización o aprobación.

Crear la skill no autoriza envíos, publicación de ofertas, escritura en FOTE, despliegue, gasto, ni merge automático. Ediciones concretas de Excel/Notion se realizan cuando se solicitan, con validación y conservación de identidad. No crear otra fuente maestra de proveedores.

## Aceptación global
Paridad de los seis flujos, validadores ejecutables, recuperación desde Git sin el chat, pruebas sintéticas y aceptación con fuentes privadas vigentes. Una prueba sintética no demuestra integridad del Excel, exclusiones comerciales ni aceptación de Wtransnet.

## Departamento HIST
Histórico de viajes, precios y observaciones: conserva experiencia operativa en las tablas privadas ya existentes. Proveedores mantiene contactos y rutas declaradas. Consultar .project/DEPARTMENTS.md y módulo historico.md de la skill.

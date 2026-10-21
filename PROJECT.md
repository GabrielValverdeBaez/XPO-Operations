---
schema: project-route/project@1
id: xpo-load-studio
title: XPO Load Studio
status: active
stage: extension
domain:
- logistics
- software
project_type: create
subtype: local-and-private-cloud-web-application
complexity: 3
uncertainty: 3
risk: 3
reversibility: moderate
external_dependencies: medium
automation_target: assisted
research_level: R1
freshness: evolving
execution_environment:
- local
- cloud
- web
duration_profile: medium
collaboration_model: human-agent
agent_suitability: high
verification_difficulty: medium
statefulness: persistent
compliance_sensitivity: medium
change_rate: medium
route_depth: M
created_at: '2026-10-20'
updated_at: '2026-10-21'
---
# XPO Load Studio - Proyecto

## Intent
Sustituir la generacion manual y variable con IA por un flujo verificable y reproducible de textos XPO bilingues y filas Wtransnet. Mantener la version local y anadir alojamiento privado Cloudflare autorizado expresamente por el operador el 20/10/2026.

## Desired Outcome
Un operador pega una orden o introduce datos, revisa campos y copia dos salidas exactas con historial y trazabilidad. Entradas adicionales: texto libre acotado, Excel y OCR local; tarifas con fuentes verificables. La variante Cloudflare comparte el motor, no depende del Mac mini y declara OCR no disponible en cloud.

## Objectives
### O-001 Fiabilidad
Misma carga normalizada, reglas y comparables producen la misma salida; tests de regresion.
### O-002 Usabilidad
Procesar FOTE y formularios sin IA obligatoria; completar solo ausencias y ambiguedades.
### O-003 Interoperabilidad
Texto conforme al formato aprobado y registro de 26 columnas contrastado con la plantilla original.
### O-004 Extensibilidad
Parsers, reglas por cliente, historial, OCR y precios separados de los renderizadores.
### O-005 Privacidad y operacion
Conservar ejecucion local y futura instalacion Mac mini. Anadir variante Cloudflare con autenticacion privada y D1 dedicado; nunca acceso anonimo a datos operativos.

## Scope
Ingesta, modelo tipado, trazabilidad, reglas deterministas, revision, doble salida, importacion, pruebas y persistencia. La autorizacion de implementacion autonoma sustituye la antigua fase de solo documentos. La ampliacion cloud permite crear exclusivamente recursos XPO y publicar la aplicacion protegida, no exponer datos ni secretos. Ver ROUTE para cobertura real.

## Non-goals
Publicacion automatica en Wtransnet, escritura de FOTE, sustituir decisiones comerciales, inventar tarifas, confiar ciegamente en OCR, integrar IA generativa obligatoria, exponer datos sin autenticar o credenciales, modificar otros proyectos o contratar planes de pago.

## Constraints
No datos reales ni original XLS en GitHub publico. Datos actuales prevalecen sobre defaults. ADR solo explicito o regla confirmada. Dos precios independientes; un unico mercado estimado o pendiente. CP no inventados. Sin fusion automatica de ramas. La aceptacion operativa y cambios comerciales requieren evidencia del operador. El despliegue cloud ya esta autorizado, pero los secretos deben configurarse por un canal privado y una URL asignada no demuestra funcionamiento.

## Critical Assumptions
La plantilla ha sido auditada directamente (hash y DV persistidos). Variaciones de FOTE siguen exigiendo fixtures. No existen tarifas reales ni cinco pares operativos aceptados nuevos. Mac mini/Tailscale no han sido desplegados en esta ejecucion. Cloudflare tiene Worker y D1 exclusivos de XPO. GitHub Actions tiene token de despliegue dedicado y ha subido la version ed97eb4f-e231-40dd-a57e-63220a363da6 sin activar destinos publicos. La auditoria API confirmó que falta XPO_LOGIN_KEY en Production (run 39599178204); hasta crearlo y validar HTTPS/D1 en remoto, T-016 no esta completada. La conexion Cloudflare MCP muestra un error interno, pero no impide la auditoria Cloudflare de solo lectura desde GitHub.

## Gates
No liberar como MVP operativo hasta pruebas de navegador, pegado y ejemplos revisados. No reducir limites comerciales, de privacidad o de envio. T-015 verifica workerd y D1 local; T-016 exige secreto privado, ruta HTTPS y persistencia remota reales. Replan local original en docs/DECISIONS.md; ampliacion cloud y handoff verificable en docs/CLOUDFLARE_DEPLOYMENT.md.

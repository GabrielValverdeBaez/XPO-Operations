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
subtype: local-web-application
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
updated_at: '2026-10-20'
---
# XPO Load Studio - Proyecto

## Intent
Sustituir la generacion manual y variable con IA por un flujo local, verificable y reproducible de textos XPO bilingues y filas Wtransnet.

## Desired Outcome
Un operador pega una orden o introduce datos, revisa campos y copia dos salidas exactas con historial y trazabilidad. Entradas adicionales: texto libre acotado, Excel y OCR local; tarifas con fuentes verificables.

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
Ejecucion local, futuro Mac mini y acceso privado, sin exposicion publica.

## Scope
Ingesta, modelo tipado, trazabilidad, reglas deterministas, revision, doble salida, importacion, pruebas y persistencia. La autorizacion de implementacion autonoma sustituye la antigua fase de solo documentos. Ver ROUTE para cobertura real, no solo intencion.

## Non-goals
Publicacion automatica en Wtransnet, escritura de FOTE, sustituir decisiones comerciales, inventar tarifas, confiar ciegamente en OCR, integrar IA generativa obligatoria, exponer Internet o credenciales.

## Constraints
No datos reales ni original XLS en GitHub publico. Datos actuales prevalecen sobre defaults. ADR solo explicito o regla confirmada. Dos precios independientes; un unico mercado estimado o pendiente. CP no inventados. Sin fusion automatica de ramas ni acceso publico. La aceptacion operativa, cambios comerciales y configuracion de red requieren intervencion explicita cuando corresponda.

## Critical Assumptions
La plantilla ha sido auditada directamente (hash y DV persistidos). Variaciones de FOTE siguen exigiendo fixtures. No existen tarifas reales ni cinco pares operativos aceptados nuevos. Mac mini/Tailscale no han sido desplegados en esta ejecucion. Estos pendientes no bloquean desarrollar en rama; si bloquean declarar produccion lista.

## Gates
No liberar como MVP operativo hasta pruebas de navegador, pegado y ejemplos revisados. No reducir los limites comerciales, de privacidad o de envio. Replan y decision de stack en docs/DECISIONS.md.

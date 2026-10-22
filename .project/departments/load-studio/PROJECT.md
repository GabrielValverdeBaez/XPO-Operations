> Baseline conservada de main anterior a la ampliación del 22/10/2026. No representa el estado de las ramas de implementación/cloud; consultar sus rutas y tareas vigentes.

---
schema: project-route/project@1
id: xpo-load-studio
title: XPO Load Studio
status: active
stage: greenfield
domain: [logistics, software]
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
execution_environment: [local, web]
duration_profile: medium
collaboration_model: human-agent
agent_suitability: high
verification_difficulty: medium
statefulness: persistent
compliance_sensitivity: medium
change_rate: medium
route_depth: M
created_at: 2026-10-20
updated_at: 2026-10-20
---

# XPO Load Studio — Project

## Intent
Sustituir la generación manual y variable de cargas con IA por un flujo local, verificable y reproducible que produzca textos XPO bilingües y filas tabuladas Wtransnet.

## Desired outcome
Un operador pega una orden FOTE o introduce datos en un formulario, revisa los valores detectados, y copia dos salidas exactas: texto operativo ES/EN y fila Wtransnet de 26 columnas, preservando historial y trazabilidad. Las ampliaciones incorporarán texto libre, Excel, OCR local y tarifas estimadas.

## Objectives
- **O-001 — Fiabilidad:** salidas idénticas para el mismo input normalizado y versión de reglas, con tests golden.
- **O-002 — Usabilidad:** procesar FOTE y formularios manuales sin IA obligatoria y corregir únicamente campos incompletos.
- **O-003 — Interoperabilidad:** producir texto conforme al formato XPO y registro Wtransnet de 26 columnas validado con plantilla oficial.
- **O-004 — Extensibilidad:** añadir parsers, reglas por cliente, histórico, OCR y estimaciones sin reescribir los generadores.
- **O-005 — Privacidad y operación:** ejecución local en Mac mini y acceso privado mediante Tailscale, sin exposición pública por defecto.

## Scope
FOTE copiado, entrada manual, normalización tipada, procedencia por campo, advertencias, motor de reglas versionado, generación ES/EN y TSV de 26 columnas, copia rápida, tests automatizados y persistencia local; posteriormente texto libre/Excel/OCR, historial y precios de mercado.

## Non-goals
Automatizar publicación de ofertas en Wtransnet, escritura directa en FOTE, sustituir decisiones comerciales, inventar precios, confiar en OCR sin revisión, integración obligatoria de modelos generativos, acceso público a Internet o gestión de credenciales XPO en Git.

## Constraints
- Repositorio: GabrielValverdeBaez/XPO-Operations. No se implementará código de aplicación en esta fase documental.
- Mac mini como servidor privado, acceso portátil por Tailscale. Preferencia técnica a validar: React/TypeScript, FastAPI/Python, SQLite, reglas JSON/YAML, Pytest, OCR Tesseract.
- El texto y la fila Wtransnet deben basarse en un modelo canónico y reglas deterministas.
- No exponer datos de clientes, matrículas, conductores, importes reales ni pantallas privadas como fixtures públicos.
- No calcular un precio de mercado como porcentaje del ingreso del cliente; mostrar fuente, intervalo/confianza y pendiente de revisión cuando falten datos.
- Codigos postales ES de 5 cifras y PT completo cuando conste; nunca inventarlos.
- ADR no se asume salvo regla explícita verificada (Diversey: ADR por defecto) o entrada confirmada.

## Critical assumptions
1. **Media/alta:** el esquema de 26 columnas Wtransnet existe pero no está incluido en esta conversación. **Impacto:** exportación incorrecta. **Acción:** recopilar y congelar esquema oficial antes de implementar.
2. **Media:** algunos campos se obtienen de FOTE mediante extractores con patrones estables. **Impacto:** variaciones de pantalla requieren fixtures y adaptadores.
3. **Media:** las reglas XPO evolucionan por cliente. **Impacto:** motor con versiones, precedencia y pruebas por cliente.
4. **Media:** se dispone de ejemplos reales anonimizados para pruebas. **Impacto:** sin ellos no declarar compatibilidad real.

## Gates
- La fase MVP no se declara completa hasta comparar salidas con ejemplos de referencia aprobados.
- Cambios que afecten precios, ADR, notas comerciales, formatos oficiales, exposición de red o escritura en servicios externos necesitan aprobación expresa.
- Cualquier integración externa queda fuera del MVP.

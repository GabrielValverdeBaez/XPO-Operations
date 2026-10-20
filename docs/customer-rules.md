# Matriz de reglas XPO y cobertura 0.1

Fuente operativa: instrucciones de XPO Cargas y Wtransnet y correcciones expresas del usuario en esta conversacion. Son reglas del operador, no restricciones inferidas de Wtransnet. Codigo canonico: `loadstudio/engine.py`; notas y switches persistentes en SQLite.

Precedencia: dato actual confirmado > excepcion exacta de cliente > fallback documentado. Un conflicto del parser bloquea el campo: una regla no lo rellena como si fuera una simple ausencia. Cliente no reconocido no recibe notas de un cliente vecino. Aliases son exactos, normalizando mayusculas/acentos; no se adivina identidad por el CP.

| Caso | Implementacion y evidencia |
|---|---|
| Notas | SEB y centro DHL Ontigola: adelantar posicionamiento y matriculas. TCL: matriculas. Mattel: matriculas y conductor. Siempre despues de ambos precios; casos positivos/negativos probados. |
| LG/LX Pantos grupaje | Solo falta peso: 2000 kg; solo falta ML: 5; ambos independientes; conservar valores presentes. Europales confirmados usan 0,40 m/unidad antes del fallback. No aplicar a FTL. |
| Diversey Illescas | ADR y paletizado; carga 10-19 y dia siguiente 06 solo donde falta dato, sin sobrescribir hora explicita. ADR false explicito se conserva con advertencia de excepcion. |
| Danone/L'Oreal | Aguas Danone y L'Oreal: ADR N y paletizado S. Danone Siguenza: ADR N, no inferir paletizado. Corregida la antigua anotacion del repositorio que dejaba ADR Siguenza desconocido. |
| PEPCO | FTL 12 t / 13,6 m; horas de respaldo solo si faltan; datos actuales prevalecen. |
| FASSA | Sirve frigorifico N; otros S segun politica vigente. |
| Servicios | T100, TR014, NTIE1 FTL; NT214 grupaje. NT014 no se interpreta por semejanza. |
| Equipos | Tautliner standard se normaliza a Trailer + Tautliner. Sin Mega inventado. Un rigido no recibe Trailer por defecto. |
| CP centros | XPO Leganes 28911, Ledono 15189, Arrubal 26150 y otros aliases exactos presentes en codigo; nunca reemplazar CP actual. |
| Mercancia | Fallback solo para cliente confirmado y descripcion ausente; se mantiene una descripcion actual aunque no haya traduccion, exigiendo completarla. |
| Norauto multientrega | **Pendiente**: no aplicar el patron Seseña-Logroño-Pamplona a cualquier ruta. Se bloquean >2 paradas; no inventar una ruta directa. |
| Dimensiones y nuevos clientes | ML por dimensiones detalladas, nuevas reglas arbitrarias y todos los aliases secundarios de la Skill quedan pendientes de ampliar con pruebas; usar ML confirmado manualmente. |

## Formato bloqueado por contrato

Encabezado completo en negrita. Solo etiquetas ES en negrita y etiquetas EN en cursiva; valores planos. Origen/Destino del cuerpo solo CP. Tipo directo `FTL · Trailer Tautliner · 15 t · 13,6 m` ajustado a datos actuales, sin expandir FTL. Peso/ML no se separan en otra linea. Dos precios finales; mercado independiente, pendiente cuando no existen comparables. Notas exactas al final. Los tests verifican estas fronteras de formato.

## Revision humana

Las reglas documentadas no acreditan cinco ofertas reales aceptadas. El editor permite corregir notas conocidas de forma explicita y auditable, sin codigo ejecutable. Los casos que no cubre la version permanecen visibles o bloqueados; no se ocultan tras un estado DONE global.

# Contrato Wtransnet A:Z — Auditoría T-001

**Estado:** reconstruido desde instrucciones XPO existentes; **NO VERIFICADO CONTRA EL XLSX OFICIAL**. No declarar T-001 completada hasta cotejo de plantilla real y muestras.

## Mapa provisional de 26 columnas

| Pos | Excel | Campo | Regla / verificación pendiente |
|---:|:---:|---|---|
| 1 | A | Referencia | Identificador de expedición, preservar texto |
| 2 | B | Fecha disponibilidad | DD/MM/AAAA; sin hora |
| 3 | C | País origen | Nombre en español |
| 4 | D | CP origen | ES cinco cifras; PT cuatro |
| 5 | E | Localidad origen | Obligatoria para búsqueda de bolsa |
| 6 | F | País destino | Nombre en español |
| 7 | G | CP destino | ES cinco cifras; PT cuatro |
| 8 | H | Localidad destino | Obligatoria para búsqueda de bolsa |
| 9 | I | Tipo Bolsa | Grupajes / Rígidos Completos / Tráilers Completos |
| 10 | J | Tipo Vehículo | Trailer, Trailer Mega, Camión Remolque, Camión 3 ejes, Camión 4 ejes, Camión 2 ejes > 7,5 T. MMA, Furgonetas; sujeto a lista de plantilla |
| 11 | K | Especialidad | Carga General (regla XPO actual) |
| 12 | L | Peso | Toneladas, separador decimal coma |
| 13 | M | Largo | Metros, separador decimal coma; FTL tráiler 13,6 salvo dato contrario |
| 14 | N | Adr | S, N o vacío; no asumir N por ausencia |
| 15 | O | Paletizado | S, N o vacío |
| 16 | P | Intercambio Palets | S, N o vacío |
| 17 | Q | Localizador GPS | S, N o vacío |
| 18 | R | Arriba | S, N o vacío |
| 19 | S | Lateral | S, N o vacío |
| 20 | T | Detrás | S, N o vacío |
| 21 | U | Sirve Frigorífico | S por defecto según regla existente; FASSA N |
| 22 | V | Sirve Lateral Bajo | S, N o vacío |
| 23 | W | Misma Especialidad | S, N o vacío |
| 24 | X | Comentarios Públicos | Máximo 500 caracteres, horarios Carga/Descarga; sanitizar tabuladores/saltos |
| 25 | Y | Precio | **SIEMPRE VACÍO**; nunca copiar ingreso ni estimación |
| 26 | Z | Activar Serv. Alerta | S, N o vacío |

## Restricciones deterministas
- Exportar TSV sin encabezado, una fila por carga, máximo 50; pegar en `Ofertas!A2`. Preservar vacíos, incluido el último y penúltimo campo.
- Comprobar `row.split("\\t").length === 26`; nunca quitar tabs finales con trim.
- Normalizar fecha a DD/MM/AAAA; horas exclusivamente en comentarios: `Carga: DD/MM/AAAA de HH:MM a HH:MM. Descarga: DD/MM/AAAA de HH:MM a HH:MM.`.
- Texto bilingüe usa CP PT íntegro (`2675-076`), mientras TSV usa `2675`.
- Para cargas FTL el peso proviene del dato de la orden, no de la capacidad máxima teórica. No derivar metros lineales de unidades FTL.
- No sustituir por localidad/alias un CP explícito de la fuente actual sin detectar contradicción.
- Declarar error o revisión ante campos críticos ausentes o valores fuera de catálogo.

## Matriz de pruebas mínimas — a convertir en golden fixtures
| Caso | Entrada | Oráculo |
|---|---|---|
| S1 | ES 28909 → PT 2675-076, 15 t FTL | D=28909, G=2675, I=Tráilers Completos, J=Trailer, L=15, M=13,6; Y vacío |
| S2 | PT con CP 0410-001 | En TSV preservar 0410 como texto con cero inicial |
| S3 | ADR no mencionado | N vacía, no N |
| S4 | Diversey Illescas ADR confirmado por regla | N=S, O=S, con procedencia de regla |
| S5 | Servicio de grupaje LG/LX sin peso ni ML | L=2, M=5; no imponer si hay valor real |
| S6 | Comentario con salto de línea o TAB | Una sola fila y exactamente 26 columnas |
| S7 | Dos expediciones misma ruta con distintas referencias | Dos filas, no deduplicar por corredor |
| S8 | Precio cliente 850 y precio mercado 950 | Y queda vacío en TSV |

## Gate documental pendiente
**Fuente primaria ya facilitada:** archivo XLS original aportado el 20/10/2026. Orden A:Z y nombres de hoja confirmados según auditoría inicial. Falta completar la lectura de validaciones internas, obligatoriedad, listas permitidas y ejemplos operativos aceptados. La biblioteca de lectura XLS no estaba disponible en el entorno de ejecución actual; no declarar esos campos comprobados.

**Para cerrar:** contrastar validaciones con el XLS ya recibido y cinco o más muestras anonimizadas con salida aceptada; registrar diferencias antes de congelar versión 1.0. No subir el XLS a repositorio público.


## Auditoría del XLS recibido (20/10/2026)

Se inspeccionó la estructura del archivo binario XLS proporcionado por el usuario sin publicarlo en GitHub. La primera fila de `Ofertas` confirma exactamente los 26 encabezados A:Z enumerados arriba. La hoja también contiene once columnas auxiliares AA:AK, que no deben rellenarse al generar las ofertas. Existen hojas auxiliares `Paises`, `Especialidades`, `Vehículos`, `Otras listas`, `Horas` y `Vigencia`. Los tres valores documentados de Tipo Bolsa coinciden con los del libro.

**Verificado:** nombres y orden A:Z; presencia de hojas y columnas auxiliares. **Pendiente:** auditoría completa de las restricciones de validación y comparación de muestras aceptadas antes del cierre de T-001.

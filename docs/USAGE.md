# Uso y operacion local

## Preparar una carga

Pegar FOTE, analizar y revisar cada campo. Una entrada con varias ordenes produce varios borradores, no una consolidacion por ruta. Los campos que no se pueden decidir se senalan sin inventar valores. `Actualizar resultados` permite ver el texto; la casilla de revision habilita copiar/guardar solo cuando no hay errores criticos. Cualquier edicion invalida la revision y la salida anterior.

`Copiar para correo` usa HTML con texto plano alternativo; `Copiar Markdown` conserva marcadores; `Copiar fila Wtransnet` conserva tabuladores finales. El pegado real en Excel y en el cliente de correo debe probarse en la aceptacion operativa.

Origen y Destino del texto contienen solo CP. En TSV siguen existiendo pais, CP y localidad. Para Portugal se conserva el CP completo en el texto y sus cuatro primeros digitos en TSV. Y permanece vacia por politica XPO, aunque el Excel tenga validacion numerica de precio.

## Entradas flexibles

Ejemplo SINTETICO, no oferta ni precio de mercado:

```text
Referencia: DEMO-001
Cliente: XPO TRANSPORT SOLUTIONS SPAIN SL
Origen: ES 28909 Getafe
Destino: PT 2675-076 Odivelas
Recogida: 20/10/2026 10:00-16:00
Descarga: 21/10/2026 12:00-13:00
Servicio: FTL
Peso: 15 t
Mercancia: Aceite / Oil
Precio cliente: 900
```

Se permiten etiquetas reordenadas, lineas separadas por punto y coma, paises ISO reconocidos y ruta con flecha. Fecha sin ano o precio sin etiqueta no se adivinan. Los mensajes de parser incluyen campos bloqueados; editar el campo concreto resuelve el bloqueo, no basta con marcar la casilla general.

XLSX: primera fila como encabezados, elegir hoja y mapear campos. Maximo 50 cargas por lote, 40 columnas y 5 MB; la interfaz no importa una hoja truncada. CP numerico implica revision por posibles ceros perdidos. No se ejecutan formulas ni macros; una formula mapeada se rechaza.

La plantilla original tiene validaciones solo en filas 2-39 (38 ofertas). La aplicacion prepara una oferta revisada cada vez. No escribir en AA:AK.

## Historial y reglas

Datos por defecto: `~/.local/share/xpo-load-studio/`. Cambiar con `XPO_DATA_DIR` a una carpeta privada autorizada. `studio.sqlite3` guarda instantaneas normalizadas, reglas y tarifas; no guarda el texto FOTE original. Misma carga semantica/reglas/base de precio no se duplica. Misma referencia con cambios crea otra revision, nunca sobrescribe la anterior.

El editor JSON solo modifica notas y switches conocidos. Incluir una razon de cambio; las escrituras usan control de revision. Restaurar crea una nueva version. No relaja las 26 columnas, el precio vacio ni la revision obligatoria. Las instantaneas anteriores conservan su resultado y revision de reglas.

## Tarifas

Sin tabla local suficiente el mercado queda pendiente. Las tarifas deben tener fuente comprobada por el operador, vigencia, paises/prefijos, servicio, vehiculo, ADR y limites de carga. Con precio por kilometro se requiere distancia introducida y contrastada; no se consulta un mapa automaticamente. El precio cliente no interviene.

Esquema de ejemplo **sintetico**, exclusivamente para probar la funcion; no es una tarifa recomendada:

```json
{"id":"synthetic-test","origin_country":"Espa\u00f1a","origin_prefix":"28","destination_country":"Portugal","destination_prefix":"26","service":"FTL","vehicle":"Trailer","adr":false,"base_eur":"1000","per_km_eur":"0","extras_eur":"0","max_weight_kg":"24000","max_linear_meters":"13.6","valid_from":"2026-01-01","valid_until":"2026-12-31","source":"SINTETICO - NO USAR EN OPERACIONES"}
```

La seleccion usa el prefijo mas especifico compatible, mediana de comparables con la misma especificidad y redondeo a 25 EUR. Devuelve un precio unico y las fuentes en la trazabilidad. No hay benchmark comercial real ni calibracion de mercado validada. ADR desconocido o distancia necesaria ausente impiden estimar.

## OCR opcional

Instalar Tesseract con las herramientas autorizadas del equipo. No es requisito para FOTE, formularios, texto o XLSX. PNG/JPEG/WEBP hasta 5 MB y 12 megapixeles; procesamiento temporal local con limite de tiempo. El resultado vuelve a la entrada, no a una carga confirmada. La prueba existente usa una sola imagen sintetica en ingles: no acredita exactitud sobre capturas reales en espanol.

## Backup y recuperacion

`Crear copia de seguridad` usa la API de backup SQLite y guarda un archivo en `backups/` bajo el directorio de datos. Para restaurar: detener el servidor, conservar aparte la base actual, copiar una copia verificada como `studio.sqlite3` y arrancar de nuevo. No restaurar mientras este escribiendo la aplicacion. Las bases con version de esquema futura se rechazan, no se rebajan.

## Mac mini y acceso remoto

La instalacion real sigue pendiente: este trabajo no tiene una sesion SSH autenticada en tu Mac. Una vez instalado alli, mantener procesos largos en `tmux`, como exige la operativa del proyecto. No se configura Tailscale ni se abren puertos desde este repositorio.

Opcion de despliegue a validar: tunel SSH sobre la red privada existente, manteniendo el servidor en loopback. El acceso mediante proxy/Tailscale Serve requiere revisar host permitido y HTTPS antes de activarlo; no esta configurado ni probado. No modificar reglas de red, cuentas o llaveros automaticamente.


## Paradas y dimensiones - extension verificada

En Campos adicionales, introducir las paradas intermedias como lista JSON en su orden real. El numero total se actualiza al editar la lista. Ejemplo sintetico de una descarga intermedia:

```json
[{"action":"DELIVERY","place":{"country":"ES","postcode":"26150","locality":"Logrono"},"window":{"date":"2026-10-21","start":"08:00","end":"09:00"}}]
```

La ruta debe incluir todas las paradas y fechas en orden; no se inventa el detalle a partir de una flecha o del contador FOTE. El texto conserva CP y horarios; TSV conserva origen/final y refleja cada parada en Comentarios. Comentarios de mas de 500 caracteres bloquean la salida sin recortarlos. No se aplica el motor de tarifas directas a una ruta con paradas.

Para metraje dimensional de grupaje, introducir grupos de bultos en metros y confirmar las dimensiones:

```json
[{"length_m":"1.2","width_m":"0.8","quantity":7}]
```

Con ML vacios, este ejemplo produce 2,80 m. **Si ya hay ML explicitos, no se sobrescriben**: vaciar ese campo deliberadamente para calcular desde dimensiones. No usar esta conversion en FTL. No activar el fallback LG cuando hay dimensiones pendientes de confirmar. La edicion invalida la revision anterior y exige volver a revisar la salida.

# XPO Load Studio - Contrato de desarrollo 0.1

## Modelo canonico

`loadstudio/models.py`: Load, Place, Window, Rules, CorridorRate. Esquema tipado Pydantic; errores para campos extra, fechas imposibles, ventanas invertidas, numeros no finitos, servicio no reconocido y opcion desconocida. Desconocido es null, distinto de false y cero. Peso interno kg; ML metros; importes Decimal. Fechas completas con ano; horas locales de cada centro, sin conversion de zona silenciosa. Ventanas que cruzan medianoche no se adivinan.

Entradas: FOTE, formulario, texto con etiquetas, XLSX mapeado y OCR local opcional. Todas pasan por Load -> motor determinista -> validacion -> render. Fuente raw solo en memoria; hash y datos normalizados en la instantanea. Se conservan procedencia de campos de entrada/reglas y bloqueos de conflictos. No se asignan porcentajes inventados de confianza a los parsers.

## Texto y TSV

Contrato exacto en `docs/customer-rules.md` y `docs/wtransnet-schema.md`. Solo etiquetas espanolas en negrita, inglesas en cursiva, valores normales. Encabezado negrita; CP solo en Origen/Destino del cuerpo. Dos precios; notas particulares despues de ellos. El precio de mercado tiene fuentes separadas del ingreso y por defecto esta pendiente.

26 columnas reales A:Z contrastadas con BIFF8. Catologos y 12 DV en `evidence/template-audit.json`; las politicas mas estrictas de XPO se distinguen de la validacion del libro. El generador no modifica plantillas ni escribe AA:AK ni envia a Wtransnet. Y vacia siempre. Horarios en X; CP portugues reducido solo en TSV.

## Revision y seguridad

Un borrador puede mostrar vista previa, pero copiar o guardar requiere revision y ausencia de errores criticos. Edicion posterior invalida el resultado, incluidas respuestas de red antiguas. Contradicciones no se transforman en defaults. ADR no informado no significa N. Errores de traduccion o identificacion se completan manualmente.

Solo loopback; token aleatorio local; comprobacion de Host/Origin; sin CORS abierto; CSP y escape HTML; bloqueo de formulas en TSV/XLSX; limites de archivos; no macros; directorio de datos privado. Sin llamadas de IA, telemetria, contactos a terceros ni puertos publicos.

## Persistencia y tarifas

SQLite version1, instantaneas inmutables, dedupe semantica y revisiones relacionadas, control de revision de reglas, restauracion como version nueva y backup consistente. No degradar una base de version futura. Tabla de corredores con fuente y vigencia, sin precios reales precargados ni cotizaciones inferidas del cliente.

## Criterio de liberacion

Tests unitarios y API no sustituyen la prueba completa de navegador/portapapeles, pegado aceptado en Wtransnet, cinco ejemplos operativos y aceptacion humana. OCR sobre una imagen sintetica no acredita exactitud general. No anunciar la app desplegada en el Mac mini sin sesion e inspeccion reales. Las limitaciones enumeradas en README y ROUTE siguen siendo trabajo pendiente.

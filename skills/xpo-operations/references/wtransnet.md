# Wtransnet — contrato A:Z

Preparar exclusivamente filas TSV para pegar en Ofertas!A2; no crear, editar ni rellenar Excel. Sin encabezados salvo petición expresa. Usar tabs reales y preservar vacíos finales; nunca strip() sobre una fila. Máximo 50 ofertas. Excluir seleccionadas oscuras y deduplicar por referencia al comparar; consolidar solo por orden expresa.

Orden exacto de 26 campos:
1. Referencia
2. Fecha disponibilidad
3. País origen
4. CP origen
5. Localidad origen
6. País destino
7. CP destino
8. Localidad destino
9. Tipo Bolsa
10. Tipo Vehiculo
11. Especialidad
12. Peso
13. Largo
14. Adr
15. Paletizado
16. Intercambio Palets
17. Localizador GPS
18. Arriba
19. Lateral
20. Detrás
21. Sirve Frigorifico
22. Sirve Lateral Bajo
23. Misma Especialidad
24. Comentarios Públicos
25. Precio
26. Activar Serv. Alerta

Fecha literal DD/MM/AAAA real; horas solo en comentarios. Peso toneladas y largo metros con coma decimal, positivos. España CP cinco cifras, Portugal cuatro primeras en TSV; conservar completo en texto. Países y vehículo por literal de plantilla; especialidad siempre Carga General. Precio siempre vacío. Booleanos S/N/vacío. Comentario hasta 500 caracteres, sin tabs ni saltos.

Consultar [opciones](opciones-wtransnet.md) y especialista para códigos internos, alias, delegaciones, respaldos confirmados, reglas de cliente y operaciones con paradas. No completar dato crítico sin evidencia. Las listas copiadas de la referencia instalada no sustituyen aceptación contra el XLS vigente.

Ejecutar scripts/validate_wtransnet_rows.py. Solo después entregar un único bloque de código sin identificador. El validador comprueba estructura y restricciones conocidas; no acredita publicación ni aceptación del portal.

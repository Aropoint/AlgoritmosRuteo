# Estructura de `salida/rutas_ejemplo.json`

Lo genera `rutas_ejemplo.py` para la secuencia completa de la tabla `mision`, con las preferencias por defecto. Calcula por separado cada tramo entre puntos obligatorios y evalúa la misión completa. El sitio web lo muestra al abrirse (punto 8 del enunciado). La API `POST /api/rutas` devuelve esta estructura cuando `usar_mision=true`; con `usar_mision=false` conserva la estructura de consulta libre entre dos nodos.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `origen`, `destino` | int | `id` de los nodos de origen y destino. |
| `modo` | string | `mision` para la secuencia completa. |
| `secuencia_mision` | int[] | Nodos obligatorios en orden: inicio, observaciones y destino. |
| `preferencias` | object | Preferencias usadas (`ruteo.config.Preferencias`): `altura_vuelo_m`, `margen_vertical_m`, `respetar_zonas_restringidas`, `viento_max_m_s`, `velocidad_crucero_m_s`, `desvio_max` (α), `presupuesto_extra` (β) y `peso_riesgo` (w_R). |
| `parametros_algoritmo` | object | `k_candidatas` (K de `pgr_KSP`), `peso_longitud`, `peso_solape`, `d_separacion_km`, `radio_incertidumbre_km` y `penalizacion_incertidumbre`. |
| `elevacion_origen_m` | float o null | Elevación del despegue: es la referencia de la altura de vuelo. |
| `viento` | object | Viento representativo: fuente, ventana, mediana y p95 a 100 m, velocidad a la altura de vuelo y dirección. Si no hay datos, `{"fuente": "sin_dato", ...}`. |
| `aristas_excluidas` | int[] | Tramos fuera del grafo admisible por las restricciones (altura y relieve, zonas). Son los mismos para ambos métodos. |
| `advertencias` | string[] | Por ejemplo, misión no admisible por viento o un solo camino encontrado. |
| `tramos` | array | Un elemento por par consecutivo de `secuencia_mision`. Cada elemento indica `numero`, `origen`, `destino`, `etiqueta`, dos rutas `dijkstra`, dos rutas `propuesta` cuando existen y `seleccion` (términos `J`, estiramiento, solape, riesgo y candidatas). |
| `resiliencia` | object | Métrica de resiliencia y diferencial (ver abajo). |
| `id_evaluacion` | int | Fila de la tabla `evaluaciones` donde quedó guardado. |
| `generado_utc` | string | Fecha y hora de generación. |

## Ruta (elementos de `tramos[].dijkstra[]` y `tramos[].propuesta[]`)

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `nodos` | int[] | — | Nodos en orden de recorrido. |
| `aristas` | int[] | — | Tramos en orden de recorrido (ids de `aristas`). |
| `largo_km` | float | km | Distancia recorrida. |
| `costo` | float | km o km equivalentes | Costo según el método: km en Dijkstra; `largo · f_viento · (1 + w_R · riesgo)` en la propuesta. |
| `riesgo_medio` | float | [0, 1] | Riesgo de los tramos, ponderado por su largo. |
| `coordenadas` | array | grados | `[[lat, lon], …]` de los nodos, en el orden de Leaflet. |
| `id_bd` | int | — | Fila de la tabla `rutas`. |

## `resiliencia`

| Campo | Descripción |
|---|---|
| `n_escenarios`, `n_fallas`, `prob_foco`, `semillas` | Escenarios simulados: semillas del rango `sitio` (20000–20099), fallas por escenario y fracción de fallas generadas cerca de focos de amenaza. |
| `largo_minimo_km`, `presupuesto_km` | `L*` (ruta mínima admisible) y `(1 + β) · L*`. |
| `secuencia_mision` | Los puntos obligatorios evaluados, en orden. |
| `r_par` | `dijkstra` y `propuesta`: fracción de escenarios en que **cada tramo** conserva al menos una ruta de su par sin fallas. No equivale por sí sola a completar la misión. |
| `delta_r_par_pp`, `p_mcnemar_par` | Diferencia de `R_par` en puntos porcentuales y su prueba de McNemar. |
| `r_mision` | Fracción de escenarios en que el UAV visita todos los puntos obligatorios en orden y llega al destino dentro del presupuesto, descubriendo las fallas en vuelo: `A_dijkstra_fijo` (línea base), `D_dijkstra_replan` (ablación) y `C_propuesta`. |
| `diferencial_C_vs_A`, `diferencial_C_vs_D` | `delta_R_pp`, `delta_R_relativo`, escenarios que solo completa cada método, `p_mcnemar` y km extra pareados (ver `ruteo/metricas.py`). |
| `origen_focos`, `n_focos` | De dónde salieron los focos de las fallas: `incendios_guerra_evaluacion`, `incendios_guerra_historicos`, `eventos_ucdp` o `sinteticos`. |

# Estructura de `salida/caso_ejemplo.json`

Lo genera `BD/caso_ejemplo.py` (Tarea 3, punto 9) y lo sirve `GET /api/t3/caso_ejemplo`; el botón «Cargar caso de ejemplo» del sitio lo usa para fijar la consulta y recalcularla en vivo.

**Qué muestra.** Inicio → destino de la misión con el perfil «Inspección de daños» y R_min = 0,70. Con ese R_min la ruta más corta ya cumple, así que en la etapa 1 las técnicas parten de la misma ruta. En la etapa 2 aparece una zona de amenaza abstracta, centrada en el punto a la mitad de la ruta de `pgr_dijkstra` en metros: esa técnica la sigue cruzando, y las que consideran amenazas la rodean. El centro de la zona se calcula, no se elige a mano.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"caso_ejemplo_t3"`. |
| `generado_utc` | string | Fecha y hora. |
| `descripcion` | string | El caso en una frase (la muestra el sitio). |
| `perfil` | string | Clave del perfil de aplicación (`inspeccion`). |
| `preferencias` | object | Las preferencias completas usadas (las de `ruteo.config.Preferencias`). |
| `origen`, `destino` | object | `nodo`, `lat`, `lon`. |
| `zona_amenaza` | object | `lat`, `lon`, `radio_m`, `p` y `criterio` con que se ubicó. |
| `etapa1`, `etapa2` | object | Sin y con la zona (ver abajo). |
| `sorteo` | object | `semilla`, `criterio` y, por técnica, `intacta`, `exito` y `motivo` en ese sorteo. |
| `objetivos` | array | `{texto, cumple}`: las comprobaciones del punto 9. |
| `id_evaluacion` | int | Fila de `evaluaciones_t3` con la etapa 2. |

## `etapa1` y `etapa2`

| Campo | Descripción |
|---|---|
| `tecnicas` | Por clave (`dijkstra_m`, `milp_gurobi`, `dijkstra_ponderado`, `aco`): `largo_km`, `fiabilidad`, `resiliencia`, `sin_recuperar`, `tiempo_ms`, `cumple_autonomia`, `cumple_fiabilidad` y `cruza_zona` (si la ruta toca el disco de la zona). |
| `mas_resiliente` | Clave de la técnica con mayor resiliencia. |
| `autonomia_km`, `r_min` | Restricciones de la consulta. |

## El sorteo ilustrativo

La semilla es la primera del rango `SEMILLAS["sorteos"]` en que la ruta de `pgr_dijkstra` en metros no completa la misión y la del MILP sí. Está **elegida para ilustrar** y se rotula así en el sitio. Las cifras de resiliencia no salen de ese sorteo, sino de los 300.

## Resultado de la corrida actual

| Técnica | Etapa 1: km · R | Etapa 2: km · R | ¿Cruza la zona? |
|---|---|---|---|
| `pgr_dijkstra` (metros) | 8,46 · 86,3 % | 8,46 · **48,7 %** | sí |
| MILP con Gurobi | 8,46 · 86,3 % | 8,58 · **86,3 %** | no |
| `pgr_dijkstra` ponderado | 8,46 · 86,3 % | 8,58 · 86,3 % | no |
| Colonia de hormigas | 8,58 · 86,0 % | 8,58 · 86,3 % | no |

Sorteo ilustrativo: semilla 30007. Se cumplen los cuatro objetivos. El desvío cuesta 116 m (+1,4 %) y conserva la resiliencia, mientras que la ruta más corta pierde 38 puntos.

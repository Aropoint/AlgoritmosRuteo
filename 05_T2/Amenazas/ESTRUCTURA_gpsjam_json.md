# Estructura de `salida/gpsjam.json`

Lo genera `gpsjam.py` y lo carga `cargar_gpsjam.py` en la tabla `amz_gpsjam_celdas`. GPSJam publica cada día, por celda H3 de resolución 4 (~1.770 km²), cuántos aviones reportaron navegación GNSS buena o degradada según sus mensajes ADS-B. El script agrega esos conteos en las celdas que cubren el AOI y su primer anillo, durante la ventana de `VENTANA_DIAS` días. Solo produce estadística agregada por celda: no intenta localizar emisores.

**Uso en el ruteo (peso, rúbrica 5.2).** `p_gnss` de un tramo es `frac_dias_rojos` de la celda que contiene su punto medio. Entra al riesgo combinado `riesgo = 1 − (1 − r_eventos)(1 − r_incendios)(1 − p_gnss)`. Una celda sin aviones da `p_gnss = 0`: es un dato ausente, no una garantía de que no haya interferencia.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"amenaza_gpsjam"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia, ventana, regla y advertencias. |
| `celdas` | array | Una entrada por celda H3 del AOI y su anillo (normalmente 7 a 14 celdas). |

## `celdas[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `h3` | string | — | Índice H3 de resolución 4 (por ejemplo `"841e5ebffffffff"`). |
| `contiene_aoi` | bool | — | `true` si la celda toca el AOI; `false` si es del anillo de contexto. |
| `dias_ventana` | int | días | Días de la ventana con archivo de GPSJam. |
| `dias_con_datos` | int | días | Días en que la celda tuvo al menos un avión. |
| `dias_rojos` | int | días | Días en que la celda cumplió la regla roja (ver abajo). |
| `frac_dias_rojos` | float o null | [0, 1] | `dias_rojos / dias_con_datos`. `null` si no hubo datos. **Es el `p_gnss`.** |
| `pct_malo_medio` | float o null | % | Promedio diario de `(malos − 1)/(buenos + malos)`. |
| `aviones_buenos`, `aviones_malos` | int | aviones-día | Suma de los conteos diarios de la ventana. |
| `geometria` | object | grados | GeoJSON `Polygon` del hexágono. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | GPSJam (`https://gpsjam.org/data/<fecha>-h3_4.csv`). El sitio no declara licencia; se cita la fuente. |
| `generado_utc` | Fecha y hora de la extracción. |
| `parametros` | `desde`, `hasta`, `ventana_dias`, `resolucion_h3` (4), `celdas_aoi` y `anillo` (1). |
| `regla_roja` | Regla publicada por GPSJam: una celda es roja si `(malos − 1)/(buenos + malos) > 10 %`. Se resta un avión para que un único avión con problemas no tiña la celda. |
| `dias_sin_archivo` | Fechas de la ventana para las que GPSJam no tenía CSV. |
| `advertencias` | Mide aviones en altura, no drones; la celda es mucho mayor que el AOI; sin tráfico no hay dato; cambio de red de receptores el 2026-08-27. |

## Carga en la BD

`celdas[]` → `amz_gpsjam_celdas(h3, dias_ventana, dias_con_datos, dias_rojos, frac_dias_rojos, pct_malo_medio, aviones_buenos, aviones_malos, contiene_aoi, geom Polygon 4326, fuente_id)`.

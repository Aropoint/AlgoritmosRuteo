# Estructura de `salida/viento.json`

Lo genera `viento.py` y lo carga `cargar_viento.py` en la tabla `meta_viento`. Es la serie horaria de viento del reanálisis ERA5 en el centro del AOI, para los `VENTANA_DIAS` días (30 por defecto) que terminan en `FECHA_CORTE` (2024-12-31 por defecto). Es la misma ventana que usa GPSJam.

**Uso en el ruteo:**
- **Restricción (rúbrica 6.1).** El viento representativo es la mediana a 100 m, llevada a la altura de vuelo con la ley potencial `v(h) = v₁₀₀ · (h/100)^(1/7)`. Si supera `viento_max_m_s`, la misión no es admisible.
- **Peso del método propuesto.** En cada tramo se aplica el factor `v / (v − h)`, donde `h` es la componente de viento de frente según el rumbo del tramo y `v` la velocidad de crucero.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"metadata_viento"`. |
| `metadatos` | object | Procedencia y parámetros. |
| `punto` | object | `lat`, `lon` y `elevacion_m` de la celda ERA5 que devolvió la API. |
| `unidades` | object | Unidades de cada variable según la API (`m/s`, `°`). |
| `resumen` | object | Estadísticos de la ventana (ver abajo). |
| `horas` | array | Un objeto por hora. |

## `horas[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `ts_utc` | string | ISO 8601 UTC | Inicio de la hora, por ejemplo `"2024-12-02T00:00Z"`. |
| `velocidad_m_s` | float o null | m/s | Velocidad media del viento a 100 m sobre el suelo. |
| `direccion_grados` | float o null | grados | Dirección **desde** la que sopla (convención meteorológica: 0 = norte, 90 = este). |
| `rafaga_10m_m_s` | float o null | m/s | Ráfaga máxima a 10 m. |

## `resumen`

| Campo | Descripción |
|---|---|
| `horas_validas` | Horas con velocidad y dirección. |
| `velocidad_mediana_m_s`, `velocidad_p95_m_s` | Mediana y percentil 95 de la velocidad a 100 m. |
| `rafaga_max_10m_m_s` | Ráfaga máxima de la ventana. |
| `direccion_media_grados` | Media circular ponderada por velocidad (350° y 10° promedian 0°, no 180°). |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | Open-Meteo Historical Weather API (ERA5); CC BY 4.0 de uso no comercial. |
| `generado_utc` | Fecha y hora de la consulta. |
| `parametros` | Parámetros exactos de la llamada (`latitude`, `longitude`, `start_date`, `end_date`, `hourly`, unidades) y `ventana_dias`. |
| `advertencias` | Resolución de ~25 km (un solo valor para todo el AOI) y extrapolación a la altura de vuelo. |

## Carga en la BD

`horas[]` → `meta_viento(ts_utc, velocidad_m_s, direccion_grados, rafaga_10m_m_s, fuente_id)`. El `resumen` se recalcula en la vista `v_viento_resumen`, de modo que la BD no depende del resumen del JSON.

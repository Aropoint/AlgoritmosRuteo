# Estructura de `salida/incendios_guerra.json`

Lo genera `incendios_guerra.py` y lo carga `cargar_incendios_guerra.py` en la tabla `amz_incendios`. Son focos de calor detectados por satélite (NASA FIRMS, sensor VIIRS) que el modelo de The Economist clasifica como relacionados con la guerra, filtrados al AOI más `BUFFER_KM` (5 km). El archivo se guarda sin sangría.

**Uso en el ruteo:**
- **Peso (rúbrica 5.2).** Con los incendios de guerra del período `historico`, `BD/pesos.sql` calcula una densidad de núcleo gaussiano (σ = 0,5 km) en el punto medio de cada tramo y la normaliza por el máximo del AOI. El resultado es `r_incendios`, en [0, 1].
- **Modelo de fallas (rúbrica 5.1).** Los incendios de guerra del período `evaluacion`, posteriores a la fecha de corte, son los focos alrededor de los cuales se generan las fallas simuladas. Así, los datos que fijan los pesos y los que generan las fallas son de períodos distintos.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"amenaza_incendios_guerra"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia, períodos y conteos. |
| `incendios` | array | Un objeto por foco de calor. |

## `incendios[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `fecha` | string | AAAA-MM-DD | Fecha de adquisición del satélite. |
| `hora_utc` | int o null | HHMM | Hora de adquisición (`ACQ_TIME`), por ejemplo `1251` = 12:51 UTC. |
| `guerra` | bool | — | `true` si el modelo lo clasificó como relacionado con la guerra (`war_fire = 1`). Solo estos entran a pesos y fallas. |
| `periodo` | string | — | `"historico"` si `fecha ≤ FECHA_CORTE`; `"evaluacion"` si cae en los `DIAS_EVALUACION` días siguientes. |
| `lat`, `lon` | float | grados | Posición del foco (centro del píxel VIIRS, ~375 m). |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | The Economist war-fire model (`output-data/ukraine_war_fires.csv` en GitHub); datos CC BY 4.0. Los focos son de NASA FIRMS. |
| `generado_utc` | Fecha y hora de la extracción. |
| `parametros` | `bbox` con buffer, `buffer_km` y los rangos de fechas `historico` y `evaluacion`. |
| `conteos` | Filas leídas del CSV completo, focos guardados y focos de guerra por período. |
| `advertencias` | Clasificación probabilística, nubes, eventos sin fuego visible y la ola de calor de abril de 2023, en que el modelo no clasifica. |

## Carga en la BD

`incendios[]` → `amz_incendios(fecha, hora_utc, guerra, periodo, geom Point 4326, fuente_id)`.

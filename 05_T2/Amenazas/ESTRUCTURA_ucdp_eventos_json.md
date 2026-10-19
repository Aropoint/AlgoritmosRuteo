# Estructura de `salida/ucdp_eventos.json`

Lo genera `ucdp_eventos.py` y lo carga `cargar_ucdp_eventos.py` en la tabla `amz_eventos`. Son eventos de violencia organizada del UCDP Georeferenced Event Dataset (GED) para Ucrania, publicados en HDX. Se filtran al AOI más `BUFFER_KM`, al período `[INICIO_HISTORICO, FECHA_CORTE]` y a eventos con lugar preciso (`where_prec ≤ 2`).

**Uso en el ruteo (peso, rúbrica 5.2).** `BD/pesos.sql` calcula la densidad de núcleo gaussiano (σ = 1 km) de estos eventos en el punto medio de cada tramo y la normaliza por el máximo del AOI. El resultado es `r_eventos`, en [0, 1]. Si no hay incendios del período de evaluación, los eventos sirven también como focos de las fallas simuladas.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"amenaza_eventos_ucdp"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia, filtros y conteos. |
| `eventos` | array | Un objeto por evento. |

## `eventos[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `id` | int | — | Identificador del evento en UCDP (columna `id`). |
| `fecha_inicio`, `fecha_fin` | string | AAAA-MM-DD | Rango de fechas del evento (`date_start`, `date_end`). |
| `tipo_violencia` | int | — | 1 = conflicto estatal, 2 = no estatal, 3 = violencia unilateral contra civiles. |
| `precision_lugar` | int | — | `where_prec`: 1 = lugar exacto; 2 = a menos de 25 km. Los eventos con valor mayor se descartan. |
| `precision_fecha` | int | — | `date_prec`: 1 = día exacto … 5 = más de un mes. |
| `muertes_estimadas` | int | personas | Mejor estimación (`best`). |
| `adm1`, `adm2` | string | — | Óblast y raión. |
| `lugar` | string | — | Localidad a la que se asignaron las coordenadas (`where_coordinates`). |
| `lat`, `lon` | float | grados | Coordenadas del evento. Varios eventos de una localidad comparten coordenadas. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | UCDP GED vía HDX (paquete `ucdp-data-for-ukraine`, URL vigente obtenida de la API de HDX); CC BY-IGO según HDX. Citar Sundberg y Melander (2013) y Davies et al. |
| `generado_utc` | Fecha y hora de la extracción. |
| `parametros` | `bbox`, `buffer_km`, `desde`, `hasta` y `precision_lugar_max`. |
| `conteos` | Filas leídas, eventos guardados y descartados por precisión. |
| `advertencias` | El CSV llega hasta 2024-12-31, las coordenadas son de la localidad y solo incluye eventos con víctimas fatales. |

## Carga en la BD

`eventos[]` → `amz_eventos(id, fecha_inicio, fecha_fin, tipo_violencia, precision_lugar, precision_fecha, muertes_estimadas, adm1, adm2, lugar, geom Point 4326, fuente_id)`.

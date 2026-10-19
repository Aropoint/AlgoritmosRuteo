# Estructura de `salida/osm_edificios.json`

Lo genera `osm_edificios.py` y lo carga `cargar_osm_edificios.py` en la tabla `meta_edificios`. Contiene los edificios de OpenStreetMap dentro del AOI con su altura, cuando OSM la tiene. El archivo se guarda sin sangría porque puede pesar varios MB.

**Uso en el ruteo (restricción dura).** `BD/pesos.sql` asigna a cada tramo la altura del edificio más alto a menos de `buffer_edificio_m` (15 m). Si esa altura, sumada al relieve relativo al despegue, es mayor o igual que `altura_vuelo_m − margen_vertical_m`, el tramo queda fuera del grafo admisible. Un edificio sin altura no restringe.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"metadata_edificios_osm"`. |
| `crs` | string | `"EPSG:4326"` (WGS84, grados). |
| `metadatos` | object | Procedencia y parámetros (ver abajo). |
| `edificios` | array | Un objeto por edificio. |

## `edificios[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `osm_tipo` | string | — | `"way"` (polígono simple) o `"relation"` (multipolígono). Con `osm_id` forma la clave. |
| `osm_id` | int | — | Identificador del elemento en OSM (`https://www.openstreetmap.org/<osm_tipo>/<osm_id>`). |
| `tipo_edificio` | string | — | Valor del tag `building` (`yes`, `apartments`, `house`, `industrial`…). |
| `altura_m` | float o null | m | Tag `height` interpretado (admite `"12 m"`, `"12,5"` y pies). `null` si no existe o no se entiende. |
| `niveles` | int o null | pisos | Tag `building:levels` (si trae varios valores, el mayor). |
| `altura_estimada_m` | float o null | m | `altura_m` si existe; si no, `niveles × 3 m`; si no, `null` (sin dato). **Es la que usa la restricción.** |
| `origen_altura` | string o null | — | `"height"`, `"building:levels"` o `null`. |
| `geometria` | object | grados | GeoJSON `MultiPolygon`: `coordinates` = lista de polígonos, cada uno una lista de anillos `[[lon, lat], …]` cerrados. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | OpenStreetMap vía Overpass API; servidor que respondió; ODbL 1.0. |
| `generado_utc` | Fecha y hora de la extracción (ISO 8601, UTC). |
| `parametros.bbox` | `sur`, `oeste`, `norte`, `este` del AOI consultado. |
| `parametros.consulta_overpass` | Consulta Overpass QL exacta, para reproducirla. |
| `parametros.metros_por_nivel` | 3,0: altura asumida por piso. |
| `conteos` | Elementos devueltos por OSM, edificios guardados, cuántos tienen altura y cuántos se descartaron por no tener geometría cerrada. |
| `advertencias` | Límites conocidos: cobertura incompleta de alturas, multipolígonos sin huecos y datos que pueden no reflejar daños recientes. |

## Carga en la BD

`edificios[]` → `meta_edificios(osm_tipo, osm_id, tipo_edificio, altura_m, niveles, altura_estimada_m, origen_altura, geom MultiPolygon 4326, fuente_id)`. Las geometrías inválidas se corrigen con `ST_MakeValid`.

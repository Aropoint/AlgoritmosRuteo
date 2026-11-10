# Estructura de `salida/zonas_restringidas.json`

Lo genera `zonas_restringidas.py` y lo carga `cargar_zonas_restringidas.py` en la tabla `meta_zonas_restringidas` (Tarea 3, punto 2: bloqueos). Contiene las zonas aeronáuticas civiles de OpenStreetMap dentro del AOI: aeródromos (`aeroway=aerodrome`) y helipuertos (`heliport`, `helipad`).

**Uso en el ruteo (restricción dura).** `BD/pesos.sql` marca `aristas.en_zona_restringida` en todo tramo que toca una zona. Si el usuario deja activa «Respetar zonas restringidas publicadas» y la casilla «Considerar» de la capa, ninguna técnica puede usar esos tramos. A los helipuertos se les aplica un radio de protección de `buffer_helipuerto_m` (150 m, en `parametros_pesos`), vengan como punto o como el pequeño polígono de la losa.

**Qué no se usa.** No se consulta `landuse=military`: en una ciudad en conflicto equivaldría a mapear instalaciones militares, y el proyecto no liga sus datos a instalaciones concretas. Las zonas prohibidas que el usuario dibuja en el sitio cumplen el mismo papel de bloqueo.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"metadata_zonas_restringidas_osm"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia y parámetros. |
| `zonas` | array | Una entrada por zona. |

## `zonas[]`

| Campo | Tipo | Descripción |
|---|---|---|
| `osm_tipo`, `osm_id` | string, int | Elemento de OSM (`node`, `way` o `relation`). |
| `clase` | string | Valor del tag `aeroway`. |
| `nombre` | string o null | Tag `name`. |
| `geometria` | object | GeoJSON `Point` (nodos) o `MultiPolygon` (vías y relaciones cerradas). |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | OpenStreetMap vía Overpass; servidor que respondió; ODbL 1.0. |
| `generado_utc` | Fecha y hora de la extracción. |
| `parametros` | `bbox`, `clases` y la `consulta_overpass` exacta. |
| `conteos` | Elementos devueltos, zonas guardadas y descartadas sin geometría cerrada. |
| `advertencias` | No reemplaza la cartografía aeronáutica oficial; sin zonas, la restricción queda neutra. |

## Carga en la BD y resultado actual

`zonas[]` → `meta_zonas_restringidas(osm_tipo, osm_id, clase, nombre, buffer_m, geom MultiPolygon 4326, fuente_id)`. En el AOI hay **un helipuerto** (`way 675032571`), y su radio de protección excluye 2 tramos.

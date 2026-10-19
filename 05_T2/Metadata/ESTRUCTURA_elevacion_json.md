# Estructura de `salida/elevacion.json`

Lo genera `elevacion.py` y lo carga `cargar_elevacion.py` en la tabla `meta_elevacion`. Contiene la elevación del terreno, según el modelo Copernicus DEM GLO-90, en cada nodo del grafo y en el punto medio de cada tramo.

**Uso en el ruteo (restricción dura).** El UAV vuela a altura constante sobre el punto de despegue. `BD/pesos.sql` calcula `terreno_max_m` de cada tramo como el máximo entre sus dos extremos y su punto medio. Al calcular rutas, el obstáculo del tramo es `(terreno_max_m − elevación del origen) + altura del edificio`. Si ese obstáculo es mayor o igual que `altura_vuelo_m − margen_vertical_m`, el tramo se excluye.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"metadata_elevacion"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia y parámetros. |
| `puntos` | array | Un objeto por punto consultado (196 nodos + 618 puntos medios con la malla por defecto). |

## `puntos[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `tipo` | string | — | `"nodo"` o `"punto_medio"` (de una arista). |
| `ref_id` | int | — | `id` del nodo o de la arista en `Infraestructura/salida/infraestructura.json`. |
| `lat`, `lon` | float | grados | Punto consultado. El punto medio es el promedio de los extremos del tramo. |
| `elevacion_m` | float o null | m sobre el nivel del mar | Elevación del modelo GLO-90. `null` si la API no la entregó. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | Open-Meteo Elevation API; Copernicus DEM GLO-90 (CC BY 4.0 en Open-Meteo, más la atribución de Copernicus). |
| `generado_utc` | Fecha y hora de la consulta. |
| `parametros` | `resolucion_m` (90), número de `puntos` y `por_consulta` (máximo de coordenadas por llamada, 100). |
| `resumen` | `min_m` y `max_m` de las elevaciones obtenidas. |
| `advertencias` | GLO-90 es un modelo de superficie (incluye en parte árboles y edificios) y cada tramo se muestrea solo en tres puntos. |

## Carga en la BD

`puntos[]` → `meta_elevacion(tipo, ref_id, elevacion_m, geom Point 4326, fuente_id)`. Después, `BD/pesos.sql` copia la elevación a `nodos.elevacion_m` y calcula `aristas.terreno_max_m`.

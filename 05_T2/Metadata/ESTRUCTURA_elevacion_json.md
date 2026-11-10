# Estructura de `salida/elevacion.json`

Lo genera `elevacion.py` y lo carga `cargar_elevacion.py` en la tabla `meta_elevacion`. Contiene la elevación del terreno, según el modelo Copernicus DEM GLO-90, en cada nodo del grafo y a lo largo de cada tramo: una muestra cada ~90 m (la resolución del modelo), además de los dos nodos.

**Uso en el ruteo (restricción dura).** El UAV vuela a altura constante sobre el punto de despegue. `BD/pesos.sql` calcula `terreno_max_m` de cada tramo como el máximo entre sus dos extremos y todas sus muestras (Tarea 3, punto 2: una loma a mitad de camino no queda entre dos muestras). Al calcular rutas, el obstáculo del tramo es `(terreno_max_m − elevación del origen) + altura del edificio`. Si ese obstáculo es mayor o igual que `altura_vuelo_m − margen_vertical_m`, el tramo se excluye.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"metadata_elevacion"`. |
| `crs` | string | `"EPSG:4326"`. |
| `metadatos` | object | Procedencia y parámetros. |
| `puntos` | array | Un objeto por punto consultado (196 nodos + 3.850 muestras de tramo con la malla por defecto: 4.046 en total). |

## `puntos[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `tipo` | string | — | `"nodo"` o `"muestra"` (de una arista). Un JSON anterior a la Tarea 3 trae `"punto_medio"`, que el cargador toma como la muestra 1. |
| `ref_id` | int | — | `id` del nodo o de la arista en `Infraestructura/salida/infraestructura.json`. |
| `orden` | int | — | Posición de la muestra a lo largo del tramo, desde `source` (1, 2, …); 0 en los nodos. |
| `lat`, `lon` | float | grados | Punto consultado. Las muestras se interpolan linealmente entre los extremos del tramo. |
| `elevacion_m` | float o null | m sobre el nivel del mar | Elevación del modelo GLO-90. `null` si la API no la entregó. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `url`, `licencia` | Open-Meteo Elevation API; Copernicus DEM GLO-90 (CC BY 4.0 en Open-Meteo, más la atribución de Copernicus). |
| `generado_utc` | Fecha y hora de la consulta. |
| `parametros` | `resolucion_m` (90), `paso_muestras_km` (0,09), número de `puntos` y `por_consulta` (máximo de coordenadas por llamada, 100). |
| `resumen` | `min_m` y `max_m` de las elevaciones obtenidas. |
| `advertencias` | GLO-90 es un modelo de superficie (incluye en parte árboles y edificios) y cada tramo se muestrea cada ~90 m. |

## Carga en la BD

`puntos[]` → `meta_elevacion(tipo, ref_id, orden, elevacion_m, geom Point 4326, fuente_id)`. Después, `BD/pesos.sql` copia la elevación a `nodos.elevacion_m` y calcula `aristas.terreno_max_m`.

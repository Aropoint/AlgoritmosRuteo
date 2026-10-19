# Estructura de `salida/infraestructura.json`

Generado por `generar_infraestructura.py`. Contiene el grafo de navegación: **vértices = puntos geográficos** y **aristas = tramos de vuelo rectos y no dirigidos**. Es una malla **sintética** de simulación académica: no representa corredores aéreos reales ni un plan de vuelo.

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"grafo_navegacion_uav"`. |
| `crs` | string | Sistema de coordenadas: `"EPSG:4326"` (WGS84, grados). |
| `nodos` | array | Vértices del grafo (ver abajo). |
| `aristas` | array | Tramos del grafo (ver abajo). |
| `metadatos` | object | Procedencia y parámetros de generación. |

## `nodos[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `id` | int | — | Identificador único; es el `source`/`target` que usa pgRouting. |
| `lat` | float | grados | Latitud WGS84 (6 decimales ≈ 0,1 m). |
| `lon` | float | grados | Longitud WGS84. |
| `tipo` | string | — | `navegacion`, `inicio`, `observacion` o `destino`. |

## `aristas[]`

| Campo | Tipo | Unidad | Descripción |
|---|---|---|---|
| `id` | int | — | Identificador único del tramo. |
| `source`, `target` | int | — | `id` de los nodos extremos. El tramo se recorre en ambos sentidos (`cost = reverse_cost = largo_km`). |
| `largo_km` | float | km | Longitud geodésica (haversine, R = 6371,0088 km). Es el **único costo** de la línea base Dijkstra. |
| `geometria` | array | grados | `[[lon, lat], [lon, lat]]`, en el orden de GeoJSON `LineString`. |
| `atributos.riesgo` | float | [0, 1] | Densidad normalizada de eventos históricos de amenaza cerca del punto medio del tramo (núcleo gaussiano, σ = 0,5 km). Hoy es **sintético** (`metadatos.origen_riesgo`). |
| `atributos.altura_max_edificio_m` | float, opcional | m | Altura máxima de las edificaciones bajo el tramo. Si existe y supera `altura_vuelo − margen`, el tramo se excluye. Ausente = sin dato = no restringe. |
| `atributos.en_zona_restringida` | bool, opcional | — | `true` si el tramo intersecta una zona restringida publicada. Ausente = `false`. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `generado_utc` | Fecha y hora de generación (ISO 8601, UTC). |
| `aoi` | Recorte de estudio: `sur`, `oeste`, `norte`, `este` en grados y `nombre`. |
| `parametros_malla` | `espaciado_km`, `jitter`, `diagonales`, `fraccion_eliminada` y `semilla`. Con la misma semilla se obtiene el mismo grafo. |
| `secuencia_mision` | `[inicio, P1, …, Pm, destino]` como `id` de nodos. |
| `origen_riesgo` | `"sintetico"` mientras no se carguen las fuentes de `Amenazas/`. |
| `advertencia` | Recordatorio de que es una simulación. |

## Carga en la BD

`cargar_infraestructura.py` hace tres cargas:

- `nodos` → tabla `nodos(id, tipo, geom Point 4326)`.
- `aristas` → `aristas(id, source, target, largo_km, rumbo_grados, geom LineString 4326)`. El rumbo se calcula con `ST_Azimuth`.
- `metadatos.secuencia_mision` → `mision(orden, nodo_id, rol)`.

El `riesgo` sintético de este JSON **no se carga**. En la BD, `BD/pesos.sql` recalcula `riesgo`, `altura_max_edificio_m` y `terreno_max_m` desde las tablas de metadata y amenazas reales.

Con eso, `pgr_dijkstra('SELECT id, source, target, largo_km AS cost, largo_km AS reverse_cost FROM aristas', a, b, directed => true)` reproduce la línea base (ver `BD/MODELO_BD.md`).

# Validacion completa del proyecto

Proyecto: ruteo resiliente en redes UAV  
Fecha de ejecucion local: 2026-09-03 22:58:27 -04  
Base geoespacial local: PostgreSQL/PostGIS, base `ruteo_uav`

Este documento resume las pruebas ejecutadas una por una sobre los scripts relevantes del proyecto. Se registran endpoints, metodos HTTP, parametros principales no sensibles, codigos HTTP, datos obtenidos, evidencia generada, estado y limitaciones. No se incluyen API keys, tokens, passwords ni valores sensibles del `.env`.

## Scripts considerados

Scripts ejecutados:

```text
01_opensky.py
02_opentopography.py
03_openweather.py
04_opencellid.py
04b_osm_buildings_fallback.py
05_gpsjam.py
06_acled.py
07_openaip.py
postgis_evidence.py
common.py
```

Scripts no ejecutados en esta ronda:

```text
run_all.py
import_geojson_to_postgis.py
```

`run_all.py` es un wrapper que ejecuta nuevamente los scripts `01` a `07`; no se ejecuto para cumplir la solicitud de ejecutar las pruebas una por una. `import_geojson_to_postgis.py` realiza upserts sobre PostGIS, con `ON CONFLICT DO UPDATE`; se omitio en esta ronda para respetar la restriccion de no ejecutar operaciones modificantes durante la validacion SQL. La base ya estaba levantada y cargada, por lo que se valido mediante consultas `SELECT` de solo lectura.

## Parametros no sensibles usados

```text
BBOX_S=-33.60
BBOX_W=-70.80
BBOX_N=-33.30
BBOX_E=-70.50
POINT_LAT=-33.45
POINT_LON=-70.66
COMM_RANGE_KM=
GPSJAM_DATE=
ACLED_COUNTRY=Ukraine
ACLED_DATE_FROM=2026-08-01
ACLED_DATE_TO=2026-09-03
OPENAIP_COUNTRY=CL
```

Como `GPSJAM_DATE` estaba vacio, el script GPSJam uso automaticamente el dia anterior en UTC: `2026-09-03`.

## OpenSky

### Prueba ejecutada

- Script: `01_opensky.py`
- Fuente/API utilizada: OpenSky Network
- Tipo de informacion: posiciones reales de aeronaves
- Categoria para el modelo: metadata de movilidad, no amenaza
- Endpoint de autenticacion: `POST https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token`
- Endpoint de datos: `GET https://opensky-network.org/api/states/all`
- Metodo HTTP: `POST` para OAuth2, `GET` para estados
- Parametros principales: `lamin=-33.60`, `lomin=-70.80`, `lamax=-33.30`, `lomax=-70.50`
- Codigo HTTP obtenido: `200` en consulta con bbox; `200` en fallback global
- Resultado: `PARCIAL`

### Datos relevantes obtenidos

- OAuth2: OK, token obtenido y no impreso.
- La consulta con bbox configurado respondio HTTP 200, pero no tuvo posiciones validas.
- El script reintento una consulta global autenticada.
- Posiciones/nodos validos obtenidos en fallback global: `7635`.
- Rate limit restante reportado: `3985` en la consulta inicial y `3981` en el fallback.

### Evidencia generada

- `evidencia/opensky_raw.json`
- `evidencia/opensky_nodes.csv`

### Interpretacion

La API quedo validada porque respondio correctamente y genero posiciones reales. La prueba es parcial para el bbox local, ya que no habia aeronaves validas dentro del area configurada al momento de ejecucion. Para ruteo UAV, estos datos pueden servir como trazas sustitutas de movilidad o como muestra de nodos georreferenciados, pero OpenSky no entrega enlaces UAV observados ni calidad de comunicacion entre nodos.

### Limitacion principal

La disponibilidad de posiciones depende del momento y del area consultada. Ademas, las aeronaves OpenSky no son UAV del experimento y no representan enlaces RF entre UAV.

## OpenTopography

### Prueba ejecutada

- Script: `02_opentopography.py`
- Fuente/API utilizada: OpenTopography Global DEM
- Tipo de informacion: raster de elevacion del terreno
- Categoria para el modelo: metadata geografica/ambiental
- Endpoint: `GET https://portal.opentopography.org/API/globaldem`
- Metodo HTTP: `GET`
- Parametros principales: `demtype=SRTMGL3`, `south=-33.60`, `north=-33.30`, `west=-70.80`, `east=-70.50`, `outputFormat=GTiff`
- Codigo HTTP obtenido: `200`
- Content-Type: `application/octet-stream`
- Resultado: `OK`

### Datos relevantes obtenidos

- Raster: `360 x 360`
- CRS: `EPSG:4326`
- Bounds: `[-70.80041666669148, -33.59958333331206, -70.50041666669155, -33.29958333331213]`
- Elevacion minima: `440.0 m`
- Elevacion maxima: `1881.0 m`
- Elevacion media: `643.7796913580247 m`
- Punto de muestra: lat `-33.45`, lon `-70.66`
- Elevacion en punto de muestra: `552.0 m`

### Evidencia generada

- `evidencia/terreno.tif`
- `evidencia/opentopography_stats.json`
- `evidencia/opentopography_dem.png`

### Interpretacion

La prueba demuestra que el proyecto puede obtener un DEM real para el area de estudio. Esta capa puede afectar el modelo de ruteo al evaluar linea de vista, obstruccion por relieve, costo de enlaces o factibilidad de aristas entre nodos UAV.

### Limitacion principal

La resolucion del DEM SRTM puede ser suficiente para validacion universitaria, pero no reemplaza un modelo local de alta resolucion para analisis fino de propagacion o vuelo.

## OpenWeather

### Prueba ejecutada

- Script: `03_openweather.py`
- Fuente/API utilizada: OpenWeather
- Tipo de informacion: meteorologia actual
- Categoria para el modelo: metadata ambiental
- Endpoint: `GET https://api.openweathermap.org/data/2.5/weather`
- Metodo HTTP: `GET`
- Parametros principales: `lat=-33.45`, `lon=-70.66`, `units=metric`
- Codigo HTTP obtenido: `200`
- Resultado: `OK`

### Datos relevantes obtenidos

- Temperatura: `13.41 C`
- Humedad: `66 %`
- Presion: `1021 hPa`
- Visibilidad: `10000 m`
- Viento: `2.57 m/s`
- Direccion del viento: `150 grados`
- Rafaga: `null`
- Lluvia 1h: `null`
- Nubosidad: `98 %`

### Evidencia generada

- `evidencia/openweather_raw.json`
- `evidencia/openweather_summary.json`

### Interpretacion

La prueba demuestra integracion con una API meteorologica actual. Para redes UAV, los valores de viento, visibilidad y condiciones operacionales pueden afectar disponibilidad de nodos, estabilidad de posicion o penalizacion de rutas. Para enlaces de 2.4 GHz, la lluvia no debe sobredimensionarse como fuente principal de atenuacion en distancias cortas.

### Limitacion principal

Entrega una condicion puntual y temporal, no una prediccion espacial detallada sobre todo el grafo. Su uso debe modelarse como metadata operacional, no como medicion directa de calidad RF.

## OpenCellID

### Prueba ejecutada

- Script: `04_opencellid.py`
- Fuente/API utilizada: OpenCellID
- Tipo de informacion: celdas de red celular
- Categoria para el modelo: infraestructura/metadata adicional
- Endpoint de conteo: `GET https://opencellid.org/cell/getInAreaSize`
- Endpoint de detalle: `GET https://opencellid.org/cell/getInArea`
- Metodo HTTP: `GET`
- Parametros principales: `BBOX=-33.60,-70.80,-33.30,-70.50`, `format=json`, `limit=50`
- Codigo HTTP obtenido: `200` en conteo inicial, `200` en conteo con bbox reducido, `200` en detalle
- Resultado: `OK`

### Datos relevantes obtenidos

- La primera respuesta HTTP fue exitosa, pero el contenido indico que el bbox original era demasiado grande.
- El script reintento con un bbox pequeno centrado en `POINT_LAT=-33.45`, `POINT_LON=-70.66`.
- Conteo reportado en bbox reducido: `2333`
- Celdas detalladas guardadas: `50`

### Evidencia generada

- `evidencia/opencellid_size.json`
- `evidencia/opencellid_raw.json`
- `evidencia/opencellid_cells.csv`

### Interpretacion

La prueba demuestra que se puede obtener informacion de infraestructura celular para el area de interes. En el contexto UAV, esta fuente puede servir como metadata de densidad de infraestructura o urbanizacion, pero no mide congestion Wi-Fi ni calidad directa de enlaces UAV.

### Limitacion principal

OpenCellID puede limitar bboxes grandes y su acceso puede depender de cuotas, whitelist o contribuciones. Aunque la respuesta HTTP fue 200, el contenido inicial incluyo una restriccion logica que obligo a reducir el area.

## OpenStreetMap/Overpass

### Prueba ejecutada

- Script: `04b_osm_buildings_fallback.py`
- Fuente/API utilizada: OpenStreetMap via Overpass API
- Tipo de informacion: poligonos de edificaciones
- Categoria para el modelo: infraestructura/metadata geoespacial
- Endpoint: `GET https://overpass-api.de/api/interpreter`
- Metodo HTTP: `GET`
- Parametros principales: consulta Overpass para `way["building"]` y `relation["building"]` dentro del bbox configurado
- Codigo HTTP obtenido: `200`
- Resultado: `OK`

### Datos relevantes obtenidos

- Elementos OSM recibidos: `237572`
- Poligonos simples exportados: `236791`
- Tipo geometrico exportado: `Polygon`

### Evidencia generada

- `evidencia/osm_buildings_raw.json`
- `evidencia/osm_buildings.geojson`

### Interpretacion

La prueba demuestra que el proyecto puede generar una capa geoespacial real de edificios desde OSM. Esta capa es relevante para el ruteo resiliente porque puede afectar linea de vista, clutter urbano, riesgo de obstruccion o penalizacion de aristas en zonas densamente construidas.

### Limitacion principal

La cobertura y exactitud dependen de OpenStreetMap. El script exporta poligonos simples de `way`; no todos los elementos complejos de OSM necesariamente quedan representados con igual detalle.

## GPSJam

### Prueba ejecutada

- Script: `05_gpsjam.py`
- Fuente/API utilizada: dataset diario GPSJam
- Tipo de informacion: celdas H3 de degradacion GNSS
- Categoria para el modelo: amenaza/riesgo de navegacion
- Endpoint: `GET https://gpsjam.org/data/2026-09-03-h3_4.csv`
- Metodo HTTP: `GET`
- Parametros principales: fecha `2026-09-03`, resolucion H3 provista por el archivo `h3_4`
- Codigo HTTP obtenido: `200`
- Resultado: `OK`

### Datos relevantes obtenidos

- Filas CSV descargadas: `48781`
- Poligonos GeoJSON generados: `48781`
- Celdas con `percent_bad > 10`: `509`
- En PostGIS, `2` registros GPSJam quedaron como `ST_MultiPolygon` y `48779` como `ST_Polygon`.

### Evidencia generada

- `evidencia/gpsjam_2026-09-03_raw.csv`
- `evidencia/gpsjam_2026-09-03.geojson`

### Interpretacion

La prueba demuestra que se puede integrar una capa espacial de degradacion GNSS. En el ruteo resiliente, esta capa puede penalizar nodos o rutas expuestas a zonas con mala confiabilidad de navegacion.

### Limitacion principal

GPSJam infiere degradacion GNSS desde datos ADS-B. No demuestra por si solo jamming de radio de datos UAV ni interferencia en enlaces de comunicacion.

## ACLED

### Prueba ejecutada

- Script: `06_acled.py`
- Fuente/API utilizada: ACLED
- Tipo de informacion: eventos de conflicto georreferenciados
- Categoria para el modelo: amenaza contextual
- Endpoint de autenticacion: `POST https://acleddata.com/oauth/token`
- Endpoint de datos: `GET https://acleddata.com/api/acled/read`
- Metodo HTTP: `POST` para OAuth2, `GET` para eventos
- Parametros principales: `country=Ukraine`, `event_date=2026-08-01|2026-09-03`, `event_date_where=BETWEEN`, `limit=500`
- Codigo HTTP obtenido: `200` en autenticacion, `200` en consulta inicial, `200` en consulta fallback
- Resultado: `PARCIAL`

### Datos relevantes obtenidos

- Autenticacion: HTTP `200`
- Consulta inicial: HTTP `200`, pero sin eventos en el rango configurado.
- La API reporto una fecha disponible por restriccion de recencia: `2025-09-04`.
- Consulta fallback para `2025-09-04`: HTTP `200`
- Eventos obtenidos: `235`
- Puntos validos exportados: `235`

### Evidencia generada

- `evidencia/acled_raw.json`
- `evidencia/acled_events.geojson`

### Interpretacion

La prueba valida la conectividad con ACLED y la conversion de eventos a puntos GeoJSON. Para ruteo resiliente, estos puntos pueden representar zonas de riesgo contextual si se transforman posteriormente a buffers o ventanas temporales.

### Limitacion principal

El rango configurado no devolvio datos y fue necesario usar la fecha disponible indicada por la API. Ademas, ACLED entrega puntos de eventos; cualquier radio de amenaza debe definirse como parametro explicito del modelo y no inventarse en la base de datos.

## OpenAIP

### Prueba ejecutada

- Script: `07_openaip.py`
- Fuente/API utilizada: OpenAIP
- Tipo de informacion: zonas de espacio aereo Restricted/Danger/Prohibited
- Categoria para el modelo: amenaza/geofence operacional
- Endpoint: `GET https://api.core.openaip.net/api/airspaces`
- Metodo HTTP: `GET`
- Parametros principales: `country=CL`, `limit=100`, `page=1`
- Codigo HTTP obtenido: `200`
- Resultado: `OK`

### Datos relevantes obtenidos

- Airspaces descargados: `36`
- Zonas Restricted/Danger/Prohibited con poligonos: `27`
- Tipo geometrico exportado: `Polygon`

### Evidencia generada

- `evidencia/openaip_raw_page1.json`
- `evidencia/openaip_restricted.geojson`

### Interpretacion

La prueba valida una fuente de poligonos de amenaza/regla operacional. Para ruteo resiliente, permite consultar si una ruta, arista o enlace cruza una zona restringida, peligrosa o prohibida.

### Limitacion principal

La interpretacion del campo `type` depende de la codificacion OpenAIP usada por el script. La cobertura queda limitada al pais o bbox configurado.

## PostgreSQL/PostGIS

### Prueba ejecutada

- Script de evidencia ejecutado: `postgis_evidence.py`
- Fuente utilizada: base local PostgreSQL/PostGIS
- Tipo de informacion: repositorio geoespacial integrado
- Categoria para el modelo: base geoespacial local de integracion
- Endpoint/servicio: contenedor Docker Compose `postgis`, base `ruteo_uav`
- Metodo: SQL de solo lectura
- Resultado: `OK`

### Consultas ejecutadas

Version de PostGIS:

```sql
SELECT PostGIS_Version();
```

Resultado:

```text
3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
```

Cantidad de registros por tabla:

```sql
SELECT 'airspaces' AS tabla, COUNT(*) AS registros FROM airspaces
UNION ALL
SELECT 'gpsjam_zones', COUNT(*) FROM gpsjam_zones
UNION ALL
SELECT 'osm_buildings', COUNT(*) FROM osm_buildings
UNION ALL
SELECT 'acled_events', COUNT(*) FROM acled_events
ORDER BY tabla;
```

Resultado:

| tabla | registros |
|---|---:|
| acled_events | 235 |
| airspaces | 27 |
| gpsjam_zones | 48781 |
| osm_buildings | 236791 |

Tipos de geometria:

```sql
SELECT 'airspaces' AS tabla, ST_GeometryType(geom) AS geometry_type, COUNT(*) AS registros
FROM airspaces
GROUP BY 1, 2
UNION ALL
SELECT 'gpsjam_zones', ST_GeometryType(geom), COUNT(*)
FROM gpsjam_zones
GROUP BY 1, 2
UNION ALL
SELECT 'osm_buildings', ST_GeometryType(geom), COUNT(*)
FROM osm_buildings
GROUP BY 1, 2
UNION ALL
SELECT 'acled_events', ST_GeometryType(geom), COUNT(*)
FROM acled_events
GROUP BY 1, 2
ORDER BY tabla, geometry_type;
```

Resultado:

| tabla | geometry_type | registros |
|---|---|---:|
| acled_events | ST_Point | 235 |
| airspaces | ST_Polygon | 27 |
| gpsjam_zones | ST_MultiPolygon | 2 |
| gpsjam_zones | ST_Polygon | 48779 |
| osm_buildings | ST_Polygon | 236791 |

SRID por tabla:

```sql
SELECT 'airspaces' AS tabla, ST_SRID(geom) AS srid, COUNT(*) AS registros
FROM airspaces
GROUP BY 1, 2
UNION ALL
SELECT 'gpsjam_zones', ST_SRID(geom), COUNT(*)
FROM gpsjam_zones
GROUP BY 1, 2
UNION ALL
SELECT 'osm_buildings', ST_SRID(geom), COUNT(*)
FROM osm_buildings
GROUP BY 1, 2
UNION ALL
SELECT 'acled_events', ST_SRID(geom), COUNT(*)
FROM acled_events
GROUP BY 1, 2
ORDER BY tabla, srid;
```

Resultado:

| tabla | srid | registros |
|---|---:|---:|
| acled_events | 4326 | 235 |
| airspaces | 4326 | 27 |
| gpsjam_zones | 4326 | 48781 |
| osm_buildings | 4326 | 236791 |

### Selects limitados

OpenAIP, muestra `LIMIT 5`:

| id | name | airspace_type | country | geom_type | area_m2 |
|---:|---|---:|---|---|---:|
| 1 | SC-D11 SANTIAGO PIRQUE | 2 | CL | ST_Polygon | 167094641.07 |
| 2 | SC-P10 ANTOFAGASTA | 3 | CL | ST_Polygon | 27062061493.58 |
| 3 | SC-P23 TALCAHUANO | 3 | CL | ST_Polygon | 265798619.21 |
| 4 | SC-P23 TALCAHUANO VFR | 3 | CL | ST_Polygon | 258210972.52 |
| 5 | SC-P26 EX CONGRESO NACIONAL | 3 | CL | ST_Polygon | 242306.17 |

GPSJam, muestra `LIMIT 5` ordenada por mayor `percent_bad`:

| id | h3 | good | bad | percent_bad | geom_type |
|---:|---|---:|---:|---:|---|
| 10123 | 841f715ffffffff | 0 | 3 | 66.67 | ST_Polygon |
| 10116 | 841f703ffffffff | 1 | 4 | 60.00 | ST_Polygon |
| 17734 | 842d239ffffffff | 16 | 21 | 54.05 | ST_Polygon |
| 10137 | 841f739ffffffff | 1 | 3 | 50.00 | ST_Polygon |
| 25872 | 8443ad5ffffffff | 4 | 6 | 50.00 | ST_Polygon |

OSM Buildings, muestra `LIMIT 5`:

| id | osm_id | name | building | geom_type |
|---:|---:|---|---|---|
| 1 | 23393750 | Terminal Sur de Buses Santiago | yes | ST_Polygon |
| 2 | 23477423 | Cenco Alto Las Condes | retail | ST_Polygon |
| 3 | 23674761 | Cinepolis | yes | ST_Polygon |
| 4 | 23675225 | Lider | yes | ST_Polygon |
| 5 | 24402037 | Lider | yes | ST_Polygon |

ACLED, muestra `LIMIT 5`:

| id | event_id_cnty | event_date | event_type | sub_event_type | location | fatalities | point_wkt |
|---:|---|---|---|---|---|---:|---|
| 1 | UKR257421 | 2025-09-04 | Battles | Armed clash | Andriivka-Klevtseve | 0 | POINT(36.5918 48.0485) |
| 2 | UKR257422 | 2025-09-04 | Battles | Armed clash | Antonivka | 0 | POINT(32.6925 46.6799) |
| 3 | UKR257423 | 2025-09-04 | Explosions/Remote violence | Air/drone strike | Arkhypivka | 0 | POINT(32.8243 52.2355) |
| 4 | UKR257424 | 2025-09-04 | Battles | Armed clash | Balahan | 4 | POINT(37.2975 48.2901) |
| 5 | UKR257425 | 2025-09-04 | Explosions/Remote violence | Air/drone strike | Baranivka | 0 | POINT(32.3002 52.0647) |

### ST_Intersects de prueba

Ruta de prueba creada por nosotros, no observada:

```text
LINESTRING(-70.595 -33.72833500000001,-70.555 -33.688335)
```

Consulta resumida:

```sql
WITH route AS (
  SELECT ST_SetSRID(
    ST_GeomFromText('LINESTRING(-70.595 -33.72833500000001,-70.555 -33.688335)'),
    4326
  ) AS geom
)
SELECT a.id, a.name, a.airspace_type, a.country,
       ST_Length(ST_Intersection(a.geom, route.geom)::geography)::numeric(12,2) AS intersection_length_m
FROM airspaces a
CROSS JOIN route
WHERE ST_Intersects(a.geom, route.geom)
ORDER BY a.id
LIMIT 5;
```

Resultado:

| id | name | airspace_type | country | intersection_length_m |
|---:|---|---:|---|---:|
| 1 | SC-D11 SANTIAGO PIRQUE | 2 | CL | 5782.15 |

Interpretacion: la arista/ruta UAV de prueba intersecta una zona OpenAIP almacenada en `airspaces`. Esto valida que la base puede responder la pregunta: "Una arista entre dos UAV atraviesa una zona restringida o de riesgo?".

### Evidencia generada

- `evidencia/postgis/00_summary.json`
- `evidencia/postgis/01_postgis_version.txt`
- `evidencia/postgis/02_table_counts.csv`
- `evidencia/postgis/03_geometry_types.csv`
- `evidencia/postgis/04_route_airspace_intersections.csv`
- `evidencia/postgis/04_route_airspace_intersections_note.txt`

### Interpretacion

PostGIS funciona como repositorio geoespacial local. No es la fuente original de los datos; integra capas externas y permite consultas espaciales utiles para el algoritmo de ruteo, incluyendo conteos, verificacion de SRID, tipos de geometria e intersecciones.

### Limitacion principal

La base refleja el ultimo estado importado de los GeoJSON. En esta validacion no se ejecuto el importador para evitar operaciones modificantes; si los GeoJSON cambian, debe ejecutarse la importacion en una fase separada de preparacion de datos.

## Archivos de evidencia disponibles

| Archivo | Tamano aproximado | Contenido |
|---|---:|---|
| `evidencia/opensky_nodes.csv` | 591856 bytes | 7635 posiciones validas |
| `evidencia/opentopography_stats.json` | 329 bytes | estadisticas DEM |
| `evidencia/openweather_summary.json` | 238 bytes | resumen meteorologico |
| `evidencia/opencellid_cells.csv` | 2559 bytes | 50 celdas detalladas |
| `evidencia/osm_buildings.geojson` | 77323585 bytes | 236791 poligonos de edificios |
| `evidencia/gpsjam_2026-09-03.geojson` | 21793434 bytes | 48781 poligonos H3 |
| `evidencia/acled_events.geojson` | 75493 bytes | 235 puntos de eventos |
| `evidencia/openaip_restricted.geojson` | 69092 bytes | 27 poligonos OpenAIP filtrados |
| `evidencia/postgis/00_summary.json` | 1443 bytes | resumen PostGIS |

## Diferenciacion de resultados HTTP

| Caso | Fuente | Resultado |
|---|---|---|
| Respuesta HTTP exitosa con datos utilizables | OpenTopography, OpenWeather, OSM/Overpass, GPSJam, OpenAIP | OK |
| Respuesta HTTP 200 con contenido que indica restriccion logica | OpenCellID | BBOX original demasiado grande; fallback exitoso |
| Respuesta HTTP 200 sin datos en consulta inicial | OpenSky, ACLED | OpenSky sin posiciones validas en bbox; ACLED sin eventos en rango configurado |
| Prueba completamente exitosa despues de fallback | OpenSky, ACLED, OpenCellID | Datos utilizables obtenidos tras reintento |
| Falla completa | Ninguna | No hubo scripts con codigo de salida distinto de 0 |

## Resumen final de validacion

| Fuente | Tipo | Estado | Datos obtenidos | Utilidad para ruteo | Limitacion |
|---|---|---|---|---|---|
| OpenSky | Metadata de movilidad | PARCIAL | 7635 posiciones validas globales | nodos/trazas sustitutas para pruebas | bbox local sin posiciones; no mide enlaces UAV |
| OpenTopography | Metadata geografica | OK | DEM 360 x 360, EPSG:4326, 440-1881 m | terreno, LOS, costos por relieve | resolucion limitada para analisis fino |
| OpenWeather | Metadata ambiental | OK | temperatura, viento, visibilidad, humedad | condiciones operacionales y penalizacion ambiental | dato puntual, no campo espacial completo |
| OpenCellID | Infraestructura/metadata | OK | 2333 celdas estimadas, 50 detalladas | densidad de infraestructura/contexto urbano | bbox grande limitado; no mide Wi-Fi ni RF UAV |
| OSM/Overpass | Infraestructura/metadata geoespacial | OK | 236791 poligonos de edificios | obstrucciones, clutter, LOS urbano | depende de cobertura/calidad OSM |
| GPSJam | Amenaza GNSS | OK | 48781 celdas H3, 509 con percent_bad > 10 | penalizacion por riesgo GNSS | no prueba jamming del enlace de datos |
| ACLED | Amenaza contextual | PARCIAL | 235 eventos como puntos | riesgo contextual y buffers parametrizados | rango configurado sin datos; puntos requieren radio modelado |
| OpenAIP | Amenaza/geofence | OK | 27 poligonos Restricted/Danger/Prohibited | evitar/intersectar zonas restringidas | depende de cobertura y codigos OpenAIP |
| PostgreSQL/PostGIS | Base geoespacial | OK | 4 tablas, SRID 4326, tipos validados | consultas espaciales para el algoritmo | requiere reimportar si cambian GeoJSON |

### Conclusiones

- Fuentes completamente validadas: OpenTopography, OpenWeather, OpenCellID, OSM/Overpass, GPSJam, OpenAIP y PostgreSQL/PostGIS.
- Fuentes parcialmente validadas: OpenSky y ACLED. Ambas respondieron HTTP 200 y entregaron datos utilizables despues de fallback, pero la consulta inicial no produjo datos dentro del criterio configurado.
- Fuentes fallidas: ninguna prueba termino con error.
- Se cumple con al menos 3 metadata: si. OpenTopography, OpenWeather, OSM/Overpass, OpenCellID y OpenSky aportan metadata o infraestructura.
- Se cumple con al menos 3 amenazas: si. GPSJam, ACLED y OpenAIP aportan capas de riesgo o amenaza operacional.
- Se cumple con el uso de al menos una API: si. Se validaron multiples APIs/endpoints HTTP externos.
- Se cumple con una base de datos geoespacial con poligonos: si. PostGIS contiene `airspaces`, `gpsjam_zones` y `osm_buildings` con geometria poligonal en SRID 4326 e indices espaciales.
- Datos efectivamente disponibles para la siguiente etapa de ruteo: DEM de terreno, meteorologia puntual, edificios OSM, celdas GPSJam, eventos ACLED como puntos, zonas OpenAIP como poligonos y tablas PostGIS listas para consultas espaciales.

La validacion demuestra que el proyecto cuenta con datos externos reales, evidencia reproducible y una base geoespacial local capaz de responder consultas espaciales relevantes para ruteo resiliente UAV.

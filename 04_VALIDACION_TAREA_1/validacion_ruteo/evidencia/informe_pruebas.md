# Informe de pruebas de fuentes externas y PostGIS

Proyecto: validacion de ruteo resiliente en redes UAV  
Fecha de ejecucion local: 2026-09-03, zona America/Santiago  
Base geoespacial local: PostgreSQL + PostGIS, base `ruteo_uav`

Este informe resume las pruebas ejecutadas con los scripts Python del proyecto, los endpoints consultados, la evidencia generada y algunas consultas limitadas sobre PostGIS. No se incluyen tokens, claves API ni passwords.

## Comandos ejecutados

Las rutas `/tmp/validacion_ruteo_venv/...` corresponden al entorno usado en esa ejecución histórica. Para repetir la validación en otro equipo, seguir la [guía de reproducción](../../REPRODUCIBILIDAD_Y_DATOS.md).

```bash
/tmp/validacion_ruteo_venv/bin/python run_all.py
/tmp/validacion_ruteo_venv/bin/python import_geojson_to_postgis.py
/tmp/validacion_ruteo_venv/bin/python postgis_evidence.py
/tmp/validacion_ruteo_venv/bin/python common.py
```

Consulta interactiva a la base:

```bash
docker compose exec postgis psql -U postgres -d ruteo_uav
```

## Parametros de ejecucion no secretos

```text
BBOX_S=-33.60
BBOX_W=-70.80
BBOX_N=-33.30
BBOX_E=-70.50
POINT_LAT=-33.45
POINT_LON=-70.66
OPENAIP_COUNTRY=CL
ACLED_COUNTRY=Ukraine
ACLED_DATE_FROM=2026-08-01
ACLED_DATE_TO=2026-09-03
```

`GPSJAM_DATE` estaba vacio en `.env`, por lo que `05_gpsjam.py` uso automaticamente el dia anterior en UTC disponible para la ejecucion: `2026-09-03`.

## Resultado general de scripts

Todos los scripts de validacion terminaron con codigo de salida 0:

| Script | Estado | Evidencia principal |
|---|---:|---|
| `01_opensky.py` | OK | `evidencia/opensky_raw.json`, `evidencia/opensky_nodes.csv` |
| `02_opentopography.py` | OK | `evidencia/terreno.tif`, `evidencia/opentopography_stats.json`, `evidencia/opentopography_dem.png` |
| `03_openweather.py` | OK | `evidencia/openweather_raw.json`, `evidencia/openweather_summary.json` |
| `04_opencellid.py` | OK | `evidencia/opencellid_size.json`, `evidencia/opencellid_raw.json`, `evidencia/opencellid_cells.csv` |
| `04b_osm_buildings_fallback.py` | OK | `evidencia/osm_buildings_raw.json`, `evidencia/osm_buildings.geojson` |
| `05_gpsjam.py` | OK | `evidencia/gpsjam_2026-09-03_raw.csv`, `evidencia/gpsjam_2026-09-03.geojson` |
| `06_acled.py` | OK | `evidencia/acled_raw.json`, `evidencia/acled_events.geojson` |
| `07_openaip.py` | OK | `evidencia/openaip_raw_page1.json`, `evidencia/openaip_restricted.geojson` |
| `import_geojson_to_postgis.py` | OK | carga de GeoJSON existentes a PostGIS |
| `postgis_evidence.py` | OK | `evidencia/postgis/` |
| `common.py` | OK | modulo auxiliar, sin salida propia |

El detalle crudo de ejecucion quedo en `evidencia/resumen_validacion.json`.

## Prueba 01: OpenSky

Endpoint de autenticacion:

```text
POST https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token
```

Endpoint de datos:

```text
GET https://opensky-network.org/api/states/all
```

Resultado relevante:

```text
OAuth2 OpenSky: OK
Consulta con bbox configurado: HTTP 200
Rate limit restante inicial: 3990
BBOX sin posiciones validas; se reintento consulta global autenticada.
Consulta global: HTTP 200
Rate limit restante posterior: 3986
Nodos/posiciones validas: 7771
```

Archivos generados:

```text
evidencia/opensky_raw.json
evidencia/opensky_nodes.csv
```

Descripcion del resultado: OpenSky entrego posiciones reales de aeronaves. En el bbox configurado no habia posiciones validas, por lo que el script hizo fallback a consulta global autenticada. Para el trabajo UAV, estos puntos pueden usarse como trazas sustitutas o evidencia de datos de movilidad, pero no prueban enlaces de comunicacion UAV.

## Prueba 02: OpenTopography

Endpoint:

```text
GET https://portal.opentopography.org/API/globaldem
```

Parametros principales:

```text
demtype=SRTMGL3
south=-33.60
north=-33.30
west=-70.80
east=-70.50
outputFormat=GTiff
```

Resultado relevante:

```text
HTTP 200
Content-Type: application/octet-stream
CRS: EPSG:4326
Shape raster: 360 x 360
Elevacion minima: 440.0 m
Elevacion maxima: 1881.0 m
Elevacion media: 643.7796913580247 m
Punto de muestra: lat=-33.45, lon=-70.66, elevacion=552.0 m
```

Archivos generados:

```text
evidencia/terreno.tif
evidencia/opentopography_stats.json
evidencia/opentopography_dem.png
```

Descripcion del resultado: se obtuvo un DEM real en GeoTIFF para el area de trabajo. Es util para analisis posteriores de linea de vista, obstruccion por terreno o penalizacion de enlaces UAV.

## Prueba 03: OpenWeather

Endpoint:

```text
GET https://api.openweathermap.org/data/2.5/weather
```

Parametros principales:

```text
lat=-33.45
lon=-70.66
units=metric
```

Resultado relevante:

```text
HTTP 200
Temperatura: 13.79 C
Humedad: 66 %
Presion: 1021 hPa
Visibilidad: 10000 m
Viento: 2.57 m/s desde 150 grados
Rafaga: null
Lluvia 1h: null
Nubosidad: 98 %
```

Archivos generados:

```text
evidencia/openweather_raw.json
evidencia/openweather_summary.json
```

Descripcion del resultado: se obtuvieron condiciones meteorologicas actuales para el punto de interes. Para enlaces UAV, viento y visibilidad son mas defendibles como variables operacionales que la lluvia para atenuacion en 2.4 GHz a distancias cortas.

## Prueba 04: OpenCellID

Endpoint de conteo:

```text
GET https://opencellid.org/cell/getInAreaSize
```

Endpoint de detalle:

```text
GET https://opencellid.org/cell/getInArea
```

Resultado relevante:

```text
getInAreaSize HTTP 200
El BBOX original era demasiado grande para OpenCellID.
Se reintento con bbox pequeno centrado en POINT_LAT/POINT_LON.
getInAreaSize retry HTTP 200
Conteo reportado: 2333
getInArea HTTP 200
Celdas detalladas guardadas: 50
```

Archivos generados:

```text
evidencia/opencellid_size.json
evidencia/opencellid_raw.json
evidencia/opencellid_cells.csv
```

Descripcion del resultado: OpenCellID entrego densidad y una muestra limitada de celdas celulares. Esta evidencia no mide ocupacion del canal Wi-Fi ni calidad RF UAV; sirve como metadata contextual de infraestructura/densidad.

## Prueba 04b: OSM Buildings via Overpass

Endpoint:

```text
GET https://overpass-api.de/api/interpreter
```

Consulta conceptual:

```text
way["building"](south,west,north,east)
relation["building"](south,west,north,east)
out geom
```

Resultado relevante:

```text
HTTP 200
Elementos OSM recibidos: 237572
Poligonos simples exportados: 236791
```

Archivos generados:

```text
evidencia/osm_buildings_raw.json
evidencia/osm_buildings.geojson
```

Descripcion del resultado: se obtuvieron poligonos reales de edificaciones desde OSM/Overpass. Esta capa es util como proxy de clutter urbano u obstrucciones potenciales para analisis de ruteo y conectividad.

## Prueba 05: GPSJam

Endpoint de descarga:

```text
GET https://gpsjam.org/data/2026-09-03-h3_4.csv
```

Resultado relevante:

```text
HTTP 200
Filas CSV: 48781
Poligonos GeoJSON generados: 48781
Celdas con percent_bad > 10: 509
```

Archivos generados:

```text
evidencia/gpsjam_2026-09-03_raw.csv
evidencia/gpsjam_2026-09-03.geojson
```

Descripcion del resultado: se descargaron celdas H3 de degradacion GNSS y se convirtieron a poligonos GeoJSON. GPSJam infiere degradacion GNSS desde ADS-B; no demuestra directamente jamming de radio de datos UAV.

## Prueba 06: ACLED

Endpoint de autenticacion:

```text
POST https://acleddata.com/oauth/token
```

Endpoint de datos:

```text
GET https://acleddata.com/api/acled/read
```

Parametros principales no secretos:

```text
country=Ukraine
event_date=2026-08-01|2026-09-03
event_date_where=BETWEEN
limit=500
```

Resultado relevante:

```text
Token HTTP 200
API HTTP 200
Sin eventos en rango configurado.
ACLED reporto fecha disponible por restriccion de recencia: 2025-09-04
Reintento para 2025-09-04: API HTTP 200
Eventos recibidos: 235
Puntos validos exportados: 235
```

Archivos generados:

```text
evidencia/acled_raw.json
evidencia/acled_events.geojson
```

Descripcion del resultado: ACLED entrego eventos de conflicto como puntos geograficos. En PostGIS se mantienen como `Point`; si el modelo necesita zonas de amenaza, debe crear buffers con un radio explicito y configurable.

## Prueba 07: OpenAIP

Endpoint:

```text
GET https://api.core.openaip.net/api/airspaces
```

Parametros principales:

```text
country=CL
limit=100
page=1
```

Resultado relevante:

```text
page 1 HTTP 200
Airspaces descargados: 36
Restricted/Danger/Prohibited con poligonos: 27
```

Archivos generados:

```text
evidencia/openaip_raw_page1.json
evidencia/openaip_restricted.geojson
```

Descripcion del resultado: se obtuvieron zonas reales de espacio aereo desde OpenAIP y se filtraron las zonas Restricted, Danger y Prohibited con geometria Polygon/MultiPolygon. Esta capa permite responder si una arista o ruta UAV intersecta zonas restringidas.

## Importacion a PostGIS

Script ejecutado:

```bash
/tmp/validacion_ruteo_venv/bin/python import_geojson_to_postgis.py
```

Resultado final de importacion:

```text
airspaces: archivo=openaip_restricted.geojson features=27 copiados=27 omitidos_sin_geom=0 geometrias_invalidas=0 importados=27 rechazados=0 inserted=0 updated=27
osm_buildings: archivo=osm_buildings.geojson features=236791 copiados=236791 omitidos_sin_geom=0 geometrias_invalidas=0 importados=236791 rechazados=0 inserted=5 updated=236786
acled_events: archivo=acled_events.geojson features=235 copiados=235 omitidos_sin_geom=0 geometrias_invalidas=0 importados=235 rechazados=0 inserted=0 updated=235
gpsjam_zones: archivo=gpsjam_2026-09-03.geojson features=48781 copiados=48781 omitidos_sin_geom=0 geometrias_invalidas=2 importados=48781 rechazados=0 inserted=0 updated=48781
```

Descripcion del resultado: PostGIS quedo sincronizado con los GeoJSON reales existentes. Los GeoJSON originales no se borraron ni reemplazaron durante la importacion. Se detectaron 2 geometries invalidas en GPSJam, reparadas con PostGIS e importadas.

## Evidencia PostGIS

Script ejecutado:

```bash
/tmp/validacion_ruteo_venv/bin/python postgis_evidence.py
```

Archivos generados:

```text
evidencia/postgis/00_summary.json
evidencia/postgis/01_postgis_version.txt
evidencia/postgis/02_table_counts.csv
evidencia/postgis/03_geometry_types.csv
evidencia/postgis/04_route_airspace_intersections.csv
evidencia/postgis/04_route_airspace_intersections_note.txt
```

Version PostGIS:

```sql
SELECT current_database() AS database, PostGIS_Version() AS postgis_version;
```

Resultado:

```text
database: ruteo_uav
postgis_version: 3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
```

Conteo de registros por tabla:

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

## Selects limitados sobre la base

Muestra limitada de OpenAIP:

```sql
SELECT id, name, airspace_type, country, ST_GeometryType(geom) AS geom_type,
       ROUND(ST_Area(geom::geography)::numeric, 2) AS area_m2
FROM airspaces
ORDER BY id
LIMIT 5;
```

Resultado:

| id | name | airspace_type | country | geom_type | area_m2 |
|---:|---|---:|---|---|---:|
| 1 | SC-D11 SANTIAGO PIRQUE | 2 | CL | ST_Polygon | 167094641.07 |
| 2 | SC-P10 ANTOFAGASTA | 3 | CL | ST_Polygon | 27062061493.58 |
| 3 | SC-P23 TALCAHUANO | 3 | CL | ST_Polygon | 265798619.21 |
| 4 | SC-P23 TALCAHUANO VFR | 3 | CL | ST_Polygon | 258210972.52 |
| 5 | SC-P26 EX CONGRESO NACIONAL | 3 | CL | ST_Polygon | 242306.17 |

Muestra limitada de GPSJam:

```sql
SELECT id, h3, good, bad, percent_bad, ST_GeometryType(geom) AS geom_type
FROM gpsjam_zones
ORDER BY percent_bad DESC NULLS LAST, id
LIMIT 5;
```

Resultado:

| id | h3 | good | bad | percent_bad | geom_type |
|---:|---|---:|---:|---:|---|
| 10123 | 841f715ffffffff | 0 | 3 | 66.66666666666667 | ST_Polygon |
| 10116 | 841f703ffffffff | 1 | 4 | 60 | ST_Polygon |
| 17734 | 842d239ffffffff | 16 | 21 | 54.054054054054056 | ST_Polygon |
| 10137 | 841f739ffffffff | 1 | 3 | 50 | ST_Polygon |
| 25872 | 8443ad5ffffffff | 4 | 6 | 50 | ST_Polygon |

Muestra limitada de OSM Buildings:

```sql
SELECT id, osm_id, COALESCE(name, '') AS name, building, ST_GeometryType(geom) AS geom_type
FROM osm_buildings
ORDER BY id
LIMIT 5;
```

Resultado:

| id | osm_id | name | building | geom_type |
|---:|---:|---|---|---|
| 1 | 23393750 | Terminal Sur de Buses Santiago | yes | ST_Polygon |
| 2 | 23477423 | Cenco Alto Las Condes | retail | ST_Polygon |
| 3 | 23674761 | Cinepolis | yes | ST_Polygon |
| 4 | 23675225 | Lider | yes | ST_Polygon |
| 5 | 24402037 | Lider | yes | ST_Polygon |

Muestra limitada de ACLED:

```sql
SELECT id, event_id_cnty, event_date, event_type, sub_event_type,
       location, fatalities, ST_AsText(geom) AS point_wkt
FROM acled_events
ORDER BY event_date DESC NULLS LAST, id
LIMIT 5;
```

Resultado:

| id | event_id_cnty | event_date | event_type | sub_event_type | location | fatalities | point_wkt |
|---:|---|---|---|---|---|---:|---|
| 1 | UKR257421 | 2025-09-04 | Battles | Armed clash | Andriivka-Klevtseve | 0 | POINT(36.5918 48.0485) |
| 2 | UKR257422 | 2025-09-04 | Battles | Armed clash | Antonivka | 0 | POINT(32.6925 46.6799) |
| 3 | UKR257423 | 2025-09-04 | Explosions/Remote violence | Air/drone strike | Arkhypivka | 0 | POINT(32.8243 52.2355) |
| 4 | UKR257424 | 2025-09-04 | Battles | Armed clash | Balahan | 4 | POINT(37.2975 48.2901) |
| 5 | UKR257425 | 2025-09-04 | Explosions/Remote violence | Air/drone strike | Baranivka | 0 | POINT(32.3002 52.0647) |

## Consulta espacial: ruta UAV de prueba contra OpenAIP

Ruta de ejemplo creada por nosotros:

```text
LINESTRING(-70.595 -33.72833500000001,-70.555 -33.688335)
```

Esta ruta no es una ruta UAV observada real. Fue construida como dato de prueba para validar la consulta espacial `ST_Intersects`.

Consulta:

```sql
WITH route AS (
  SELECT ST_SetSRID(
    ST_GeomFromText('LINESTRING(-70.595 -33.72833500000001,-70.555 -33.688335)'),
    4326
  ) AS geom
)
SELECT a.id, a.name, a.airspace_type, a.country,
       ST_AsText(ST_Intersection(a.geom, route.geom)) AS intersection_wkt
FROM airspaces a
CROSS JOIN route
WHERE ST_Intersects(a.geom, route.geom)
ORDER BY a.id
LIMIT 5;
```

Resultado:

| id | name | airspace_type | country | intersection_wkt |
|---:|---|---:|---|---|
| 1 | SC-D11 SANTIAGO PIRQUE | 2 | CL | LINESTRING(-70.595 -33.72833500000001,-70.555 -33.688335) |

Interpretacion: para esta arista UAV de prueba, la respuesta es si: la `LINESTRING` intersecta una zona OpenAIP almacenada en `airspaces`. Por lo tanto, la base permite responder la pregunta: "Una arista entre dos UAV atraviesa una zona restringida?".

## Resumen final

Las pruebas confirmaron que el proyecto puede obtener datos externos reales, transformarlos a formatos geoespaciales y consolidarlos en PostGIS como repositorio local. OpenAIP, GPSJam, OSM Buildings y ACLED quedaron integrados como capas separadas con SRID 4326 e indices espaciales GiST.

Los resultados mas relevantes para el ruteo resiliente son:

- OpenAIP aporta poligonos de restricciones del espacio aereo para detectar intersecciones con rutas o enlaces.
- GPSJam aporta celdas H3 de degradacion GNSS, utiles como capa de riesgo de navegacion, no como prueba directa de interferencia RF.
- OSM Buildings aporta poligonos de edificios, utiles para clutter urbano, obstaculos y analisis de linea de vista.
- ACLED aporta eventos de conflicto como puntos; cualquier buffer de amenaza debe ser una decision parametrizada del modelo.
- PostGIS permite consultas espaciales reproducibles como `ST_Intersects`, `ST_GeometryType`, `ST_Area` y agregaciones por capa.

La evidencia queda lista para capturas de pantalla en:

```text
evidencia/
evidencia/postgis/
evidencia/informe_pruebas.md
```

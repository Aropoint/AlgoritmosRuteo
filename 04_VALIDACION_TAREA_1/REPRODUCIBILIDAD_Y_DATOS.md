# Datos y reproducción de la validación inicial

Este directorio conserva el trabajo de **Tarea 1**. Su código consulta fuentes, transforma respuestas a archivos y carga algunas capas en PostGIS. No contiene aún el grafo de trayectorias, pgRouting, el algoritmo resiliente ni el sitio Leaflet pedidos para la Tarea 2.

## Qué se incluye en el repositorio

- Código, `docker-compose.yml`, SQL, colección Postman sin claves y [ejemplo de variables de entorno](validacion_ruteo/.env.example).
- [Informe de pruebas](validacion_ruteo/evidencia/informe_pruebas.md), [resumen de ejecución](validacion_ruteo/evidencia/resumen_validacion.json) y estadísticas breves de relieve y clima. Son **registros de una ejecución anterior**, no una garantía de que las APIs respondan igual hoy.
- [Figura del DEM](validacion_ruteo/evidencia/opentopography_dem.png), conservada como vista previa de la validación. La fuente LaTeX disponible usa el mapa de `03_TAREA_1/pruebas_iniciales/`.

Los JSON, GeoJSON, CSV y TIFF descargados se conservan localmente pero se excluyen de Git. Algunos ocupan cientos de MB y otros provienen de proveedores con condiciones de uso propias. El ZIP de respaldo y el video de la conversación tampoco forman parte del repositorio. Los documentos que nombran esos archivos describen la ejecución histórica; para obtener nuevos archivos hay que volver a correr los scripts.

## Reproducir

Desde `04_VALIDACION_TAREA_1/validacion_ruteo/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env: credenciales propias, zona y fechas de consulta.
python run_all.py
docker compose up -d
python import_geojson_to_postgis.py
python postgis_evidence.py
```

Se necesita Python 3.10 o posterior, Docker con Compose y acceso a las APIs. Algunas fuentes requieren cuenta, clave o autorización; una ejecución parcial puede dejar fallos documentados en `evidencia/resumen_validacion.json`. `run_all.py` ejecuta las consultas desde su propio directorio y continúa aunque una fuente falle. Los dos scripts de PostGIS dependen de que exista `.env`, de que Docker esté activo y de que se hayan generado los GeoJSON correspondientes.

## Salidas por fuente

| Script | Fuente | Salidas principales en `evidencia/` | Precaución de interpretación |
|---|---|---|---|
| `01_opensky.py` | OpenSky | `opensky_raw.json`, `opensky_nodes.csv` | Aeronaves observadas, no una flota UAV del experimento. |
| `02_opentopography.py` | OpenTopography | `terreno.tif`, `opentopography_stats.json`, `opentopography_dem.png` | Elevación del suelo; no altura de vuelo. |
| `03_openweather.py` | OpenWeather | `openweather_raw.json`, `openweather_summary.json` | Condición puntual; no prueba interferencia de radio. |
| `04_opencellid.py` | OpenCellID | `opencellid_raw.json`, `opencellid_cells.csv` | Antenas celulares; no ocupación del canal UAV. |
| `04b_osm_buildings_fallback.py` | OSM/Overpass | `osm_buildings_raw.json`, `osm_buildings.geojson` | Huellas de edificios; no bloqueo 3D sin alturas. |
| `05_gpsjam.py` | GPSJam | CSV de entrada y GeoJSON por fecha | Degradación GNSS inferida; no mide el enlace de datos UAV. |
| `06_acled.py` | ACLED | `acled_raw.json`, `acled_events.geojson` | Eventos de conflicto; no son mediciones de jamming. |
| `07_openaip.py` | OpenAIP | `openaip_raw_page1.json`, `openaip_restricted.geojson` | Zonas aeronáuticas; hay que considerar límites verticales. |

El [README del paquete](validacion_ruteo/README.md) contiene detalles de cada consulta. El [resumen técnico](../01_PROYECTO_ACTUAL/RESUMEN_PROYECTO_Y_TAREA_2.md) explica las cifras registradas, las diferencias entre fuentes y los límites de la propuesta.

## Antes de compartir o publicar

No subir `.env`, `credentials.json`, la carpeta `Credentials/` ni el entorno virtual. Las pruebas antiguas de OpenTopography y OpenWeather ahora leen sus claves desde `OPENTOPOGRAPHY_API_KEY` y `OPENWEATHER_API_KEY`. Si esas claves estuvieron en alguna copia o repositorio previo, deben reemplazarse en los servicios que las emitieron; borrar una línea de código no invalida la clave anterior.

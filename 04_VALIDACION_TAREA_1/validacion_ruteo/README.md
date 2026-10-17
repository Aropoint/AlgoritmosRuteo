# Pack de validación — Ruteo resiliente UAV

> **Material histórico de la Tarea 1.** Este paquete valida fuentes y operaciones geoespaciales; no implementa el algoritmo de trayectorias físicas acordado para la Tarea 2. El [enfoque actual](../../01_PROYECTO_ACTUAL/CONTEXTO_PARA_EL_GRUPO_TAREA_2.md) está documentado aparte.

Al clonar el repositorio solo se reciben resultados resumidos y la figura del DEM. Los datos descargados que aparecen en los informes se regeneran al ejecutar los scripts; el [inventario de datos](../REPRODUCIBILIDAD_Y_DATOS.md) explica qué se incluye y qué se excluye de Git.

Objetivo: generar evidencia reproducible de que las fuentes propuestas entregan datos utilizables para construir/enriquecer un grafo geolocalizado y capas de riesgo.

## 1. Instalación
```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\\Scripts\\activate       # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```
Rellena las claves en `.env`. **No subas `.env` a Git ni a Canvas.** Si una key ya apareció en un archivo compartido, revócala/rota y crea una nueva.

## 2. Ejecutar
```bash
python 01_opensky.py
python 02_opentopography.py
python 03_openweather.py
python 04_opencellid.py
python 04b_osm_buildings_fallback.py
python 05_gpsjam.py
python 06_acled.py
python 07_openaip.py
```
Todos los resultados se guardan en `evidencia/`. Toma una captura del terminal con HTTP 200 + una captura/preview del JSON/CSV/GeoJSON/TIFF producido.

## 3. Qué demuestra cada evidencia
- **OpenSky**: posiciones/velocidad reales de aeronaves. Úsalo como *traza sustituta de movilidad*, no como prueba de una red UAV ni de enlaces RF. Las aristas deben derivarse con un modelo de alcance/LOS.
- **OpenTopography**: raster DEM real; permite calcular elevación y posteriormente LOS/difracción para cada enlace.
- **OpenWeather**: variables meteorológicas. Para una red 2.4 GHz, el argumento más defendible es viento/movilidad y disponibilidad operacional; no sobredimensionar la atenuación por lluvia.
- **OpenCellID**: densidad de celdas; acceso gratuito puede estar condicionado a contribución/whitelist y no mide ocupación Wi‑Fi 2.4 GHz. Si falla o el profesor cuestiona relevancia, usa **OSM Buildings** como metadata de clutter/obstrucción.
- **GPSJam**: dataset diario de celdas H3 sobre degradación de navegación ADS-B; es GNSS, no jamming comprobado de la radio de datos.
- **ACLED**: puntos de conflicto geolocalizados. Son contexto de riesgo; para ruteo deben transformarse a buffers/ventanas temporales justificadas.
- **OpenAIP**: polígonos reales de espacios Restricted/Danger/Prohibited. Cumple muy bien el requisito geoespacial con Polygon/MultiPolygon.
- **PostGIS**: almacenamiento y consultas espaciales sobre polígonos.

## 4. Integración local con PostGIS
PostGIS se usa como repositorio geoespacial local para integrar los GeoJSON reales generados por las fuentes externas. No es la fuente original de OpenAIP, GPSJam, OSM ni ACLED.

Configura las credenciales locales sin hardcodearlas:
```bash
cp .env.example .env
# editar POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB y DATABASE_URL
```

Levanta PostgreSQL + PostGIS:
```bash
docker compose up -d
```

Importa automaticamente solo los GeoJSON existentes en `evidencia/`:
```bash
python import_geojson_to_postgis.py
```

Genera evidencia legible para la presentacion:
```bash
python postgis_evidence.py
```

Las tablas creadas son `airspaces`, `gpsjam_zones`, `osm_buildings` y `acled_events`, todas con SRID 4326 e indices GiST. ACLED se mantiene inicialmente como `Point`; si se transforma a buffer/poligono, el radio debe quedar como parametro configurable y documentarse como decision del modelo de amenaza.

## 5. Modelo de integración recomendado para Tarea 2
Mantén la idea CLUN-LSR pero separa disponibilidad de link y costo de ruteo:
1. Construir grafo candidato `G_t=(V,E)` con posiciones y rango.
2. Eliminar/degradar `E` si terreno/LOS o condiciones operacionales hacen inviable el enlace.
3. Marcar nodos/aristas que intersectan polígonos/zonas de amenaza.
4. Sobre los enlaces sobrevivientes usar el peso CLUN-LSR `1/m_j`, o una extensión multiobjetivo claramente definida.
5. Comparar ruta base vs. ruta enriquecida con métricas: exposición a riesgo, saltos, distancia, cambios de ruta, PDR/throughput/delay si el simulador lo permite.

Esto evita mezclar “ruta de vuelo” con “ruta de paquetes”: el paper trata principalmente ruteo de red entre UAV.

# Mapa del proyecto AlgoritmosRuteo

**Revisado:** 18 de octubre de 2026 · **Rama:** `tarea-2` (la base es `main`, con un único commit: `8c6eef8 Documentation of Project - Ruteo`).

Este documento describe qué hay en cada carpeta, qué sirve para la nueva propuesta de ruteo físico resiliente y qué debe tratarse solo como antecedente. Para entender la propuesta en sí, lee [CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md](CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md) y luego [PROPUESTA_TECNICA.md](PROPUESTA_TECNICA.md).

## 1. Vista general

```text
AlgoritmosRuteo/
├── README.md                         Portada del repo (escrita antes de la Tarea 2; parte de su texto quedó desactualizado, ver §4)
├── Journal of Field Robotics - 2024 - Luna - ….pdf   Paper de Luna et al. (2024): cobertura multi-UAV con replanificación
├── .vscode/settings.json             Oculta venv y cachés en el explorador
├── 01_PROYECTO_ACTUAL/               Documentos de decisión para la Tarea 2 (17-oct)
├── 02_REUNION_PROFESOR/              Transcripción de la reunión y guion previo
├── 03_TAREA_1/                       Entrega 1 (CLUN-LSR), material histórico
├── 04_VALIDACION_TAREA_1/            Código de extracción de APIs, PostGIS y evidencia
└── 05_T2/                            NUEVA PROPUESTA: ruteo físico resiliente (este directorio)
```

La historia del proyecto en tres pasos:

| Momento | Enfoque | Dónde está |
|---|---|---|
| Tarea 1 | **CLUN-LSR**: recuperar caminos de *comunicación* entre UAV ante jamming. Nodo = UAV, arista = enlace de radio. | `03_TAREA_1/`, `04_VALIDACION_TAREA_1/` |
| Reunión con el profesor (17-oct) | La pérdida de reporte de un UAV como alerta para cambiar la *trayectoria física* de los siguientes; misión de reconocimiento de una zona. | `01_PROYECTO_ACTUAL/`, `02_REUNION_PROFESOR/` |
| Propuesta actual (18-oct) | **Ruteo físico resiliente**: un UAV recorre puntos de inspección sobre un grafo geolocalizado (Mykolaiv). Yen + selección resiliente + replanificación, comparado contra Dijkstra. | `05_T2/` |

## 2. Carpeta por carpeta

### `01_PROYECTO_ACTUAL/`: decisiones previas a la propuesta actual

| Archivo | Contenido | Vigencia |
|---|---|---|
| `ENUNCIADO_Y_RUBRICA_TAREA_2.txt` | Enunciado y rúbrica de la Tarea 2 (60 pts). | **Vigente.** Es la fuente de requisitos. |
| `ENFOQUE_TRAS_CHARLA_PROFESOR.md` | Interpretación de la reunión: de rutas de datos a trayectorias físicas, varios UAV, cobertura. | Parcial: la propuesta actual reduce el alcance a 1 UAV y a puntos de inspección (no cobertura continua). |
| `CONTEXTO_PARA_EL_GRUPO_TAREA_2.md` | Resumen para el grupo: Tarea 1, retroalimentación, casos reales (Chile, México, Ucrania). | Antecedente útil para la problemática. |
| `RESUMEN_PROYECTO_Y_TAREA_2.md` | Estado técnico, tabla de requisitos de la Tarea 2 contra lo existente, preguntas abiertas. | La tabla "requisito / estado / pendiente" sigue siendo válida. |

### `02_REUNION_PROFESOR/`

| Archivo | Contenido |
|---|---|
| `Charla_profesor.txt` | Transcripción automática (188 líneas, con errores de reconocimiento). El video está excluido por `.gitignore`. |
| `GUION_CONSULTA_PROFESOR_TAREA_2.md` | Guion preparado antes de la reunión (histórico). |

### `03_TAREA_1/`: entrega 1 (histórico)

| Ruta | Contenido |
|---|---|
| `informes/Informe_Ruteo_APO_DPC_AML-1.pdf` y `…_corregido.tex` | Informe entregado y su fuente LaTeX. |
| `CONTEXTO_PROYECTO_CODEX.md` | Decisiones iniciales y explicación del paper CLUN-LSR. |
| `referencias/Tecnicas_de_Intercepcion_Telefonica.pdf` | Informe BCN sobre jamming en Chile (el nombre del archivo no coincide con el contenido). |
| `pruebas_iniciales/main.py` | Descarga DEM SRTMGL3 de OpenTopography (bbox de Santiago). |
| `pruebas_iniciales/terreno.py` + `terreno.tif` + `mapa_terreno.png` | Lectura y gráfico del DEM. |
| `pruebas_iniciales/OpeanWeather.py` | Clima actual de Santiago (OpenWeather). |
| `pruebas_iniciales/SpectrumITU.py` | SINR con ruido simulado (urbano −85 dBm / rural −100 dBm); no consulta ninguna base real. |

### `04_VALIDACION_TAREA_1/validacion_ruteo/`: código reutilizable

| Archivo | Qué hace | Reuso en la Tarea 2 |
|---|---|---|
| `common.py` | `env()`, `bbox()`, `save_json()`, `haversine_km()`. | Sí (patrón de configuración por `.env`). |
| `01_opensky.py` | Estados de aeronaves (OpenSky). | **No**: aviones comerciales; la retroalimentación lo objetó. |
| `02_opentopography.py` | DEM + estadísticas + PNG. | **Metadata** (terreno / modelo 2,5D). Cambiar el bbox a Mykolaiv. |
| `03_openweather.py` | Clima actual. | Reemplazar por Open-Meteo **histórico** para que la fecha sea coherente con los eventos. |
| `04_opencellid.py` | Densidad de antenas. | No (no aporta al ruteo físico). |
| `04b_osm_buildings_fallback.py` | Edificios OSM vía Overpass. | **Metadata**; falta conservar `height`/`building:levels` y multipolígonos. |
| `05_gpsjam.py` | Celdas H3 de degradación GNSS. | Amenaza candidata (contexto; no mide jamming del enlace). |
| `06_acled.py` | Eventos ACLED (OAuth). Por defecto `country=Ukraine`. | **Amenaza** candidata para focos de fallas. |
| `07_openaip.py` | Espacios aéreos restringidos. | Restricción dura (`en_zona_restringida`) si hay geometrías vigentes. |
| `sql/init_postgis.sql`, `08_postgis_poligonos.sql` | Tablas PostGIS de 4 capas + ejemplo de intersección ruta/zona. | Base para el esquema nuevo; **no tiene pgRouting**. |
| `import_geojson_to_postgis.py`, `postgis_evidence.py` | Carga de GeoJSON por COPY y consultas de evidencia. | Patrón reutilizable para los cargadores `*.json → BD`. |
| `docker-compose.yml` | `postgis/postgis:16-3.4`. | Cambiar a una imagen con pgRouting. |
| `run_all.py` | Ejecuta todos los scripts y resume. | Inspiración para el `main` raíz. |
| `evidencia/` | Resultados resumidos (DEM, clima, informe de pruebas). | Evidencia de la Tarea 1 (Santiago). |

### `05_T2/`: nueva propuesta

| Ruta | Contenido |
|---|---|
| `CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md` | Contexto y propuesta para el grupo (documento base). |
| `MAPA_PROYECTO.md` | Este mapa. |
| `PROPUESTA_TECNICA.md` | Formalización del algoritmo, del modelo de fallas, de las métricas y del protocolo experimental, con resultados preliminares. |
| `README.md` | Cómo ejecutar, estado y próximos pasos. |
| `ruteo/` | Núcleo en Python, solo con biblioteca estándar: grafo, Dijkstra, Yen, selección resiliente, fallas, simulador y métricas. |
| `Infraestructura/` | Generador del grafo → `salida/infraestructura.json` + documento de su estructura (rúbrica punto 1). |
| `experimentos/run_experimentos.py` | Comparación A/B/C/D sobre escenarios con semilla. |
| `resultados/` | JSON generados por los experimentos. |
| `tests/` | Pruebas unitarias (Yen se valida contra una enumeración exhaustiva). |

## 3. Qué falta para cumplir la rúbrica (resumen)

Actualizado el 19 de octubre de 2026. Todo lo marcado "escrito" está implementado, pero **aún no se ha ejecutado en Docker**. El detalle, criterio por criterio, está en [ENTREGA_TAREA2.md](ENTREGA_TAREA2.md).

| Rúbrica | Estado |
|---|---|
| Docker con PostGIS + pgRouting, diagrama y SQL | Escrito: `docker-compose.yml` (raíz), `05_T2/Dockerfile`, `BD/schema.sql`, `BD/diagrama_bd.py` y `BD/MODELO_BD.md`. |
| Infraestructura → JSON → BD | Hecho (`Infraestructura/`); el cargador está escrito. |
| n metadata y n amenazas → JSON + cargadores | Escrito: `Metadata/` (OSM, elevación, viento) y `Amenazas/` (GPSJam, incendios de guerra, UCDP), cada uno con su documento de estructura. |
| Modelo de fallas, pesos y restricciones con valores por defecto | Implementado en `ruteo/` y en `BD/pesos.sql`. |
| Algoritmo, paper y explicación | Implementado (Yen 1971 + selección y replanificación propias) y documentado en `PROPUESTA_TECNICA.md`. |
| k ≥ 2 rutas Dijkstra y k ≥ 2 rutas del algoritmo | En Python, probado. En SQL (`pgr_dijkstra` / `pgr_KSP`, `comun/rutas.py`), escrito. |
| Métrica de resiliencia y diferencial | Implementados (`ruteo/metricas.py`, `comun/resiliencia.py`). |
| Leaflet con origen/destino y preferencias; `main` raíz | Escritos: `SitioWeb/` y `main.py`. |

## 4. Inconsistencias detectadas en el repositorio

1. `README.md` (raíz) dice que el repo está "sin remoto ni commit" y que la Tarea 2 "no se ha implementado"; ya hay un commit, una rama `tarea-2` y, ahora, `05_T2/`.
2. El documento de contexto menciona `CONTEXTO_INTEGRAL_CODEX_RUTEO_UAV_2026_V3.md` en la raíz, pero ese archivo no existe en el repositorio.
3. `.env.example` y los valores por defecto de `common.py` apuntan a **Santiago** (bbox, `POINT_LAT/LON`, `ACLED_COUNTRY=Chile`), mientras que `06_acled.py` usa `Ukraine` por defecto. Para Mykolaiv hay que crear un `.env` nuevo.
4. `docker-compose.yml` usa `postgis/postgis` sin pgRouting, que la rúbrica exige.
5. El enunciado pide entregar en **GitLab UDP**; el remoto conocido por el grupo está en GitHub.

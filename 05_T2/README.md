# 05_T2: ruteo físico resiliente de UAV

Nueva propuesta de la Tarea 2. Un UAV simulado recorre puntos de inspección sobre un grafo geolocalizado (Mykolaiv, referencia provisional). Comparamos **Dijkstra por km** (`pgr_dijkstra`) con **Yen + selección resiliente + replanificación** (`pgr_KSP` + selección propia) frente a fallas espaciales reproducibles. La metadata y las amenazas salen de fuentes públicas.

**Flota con aviso compartido** (`ruteo/flota.py`, PROPUESTA_TECNICA §10):
- **Flota:** de 3 a 5 UAV que hacen la misma misión.
- **Aviso por detección:** el UAV que detecta interferencia avisa de inmediato a los demás, y el aviso se retransmite entre los UAV como en CLUN-LSR.
- **Cambio de ruta en vuelo:** los UAV que reciben el aviso cambian de ruta en ese momento.
- **Aviso por silencio:** si un UAV queda dentro de una zona, deja de emitir su beacon y la flota marca esa zona para evitarla.

En el sitio se puede animar un escenario con aviso y sin aviso.

**Misión editable en el sitio** (22-oct-2026): la flota **siempre** recorre los puntos de observación. Marcar origen y destino cambia de dónde sale y a dónde llega, no la inspección. Los puntos amarillos se arrastran para moverlos, se pulsan para quitarlos y se añaden con "Añadir punto" (hasta 8). Si la secuencia difiere de la misión de la base de datos, el panel de resultados lo advierte, porque esas cifras **no** son comparables con las del informe.

> **Corregido.** Hasta esa fecha, marcar origen y destino —o pulsar "Usar la misión", que tomaba solo el primer y el último punto— hacía que la flota simulara un vuelo directo entre dos nodos y se saltara los tres puntos de observación.

| Documento | Para qué |
|---|---|
| [ENTREGA_TAREA2.md](ENTREGA_TAREA2.md) | **Cada criterio de la rúbrica → archivo y evidencia.** Guía para la presentación. |
| [PROPUESTA_TECNICA.md](PROPUESTA_TECNICA.md) | Formalización: fallas, pesos, restricciones, algoritmo, métricas, protocolo y resultados preliminares. |
| [BD/MODELO_BD.md](BD/MODELO_BD.md) | Modelo de la base de datos, diagrama y consultas pgRouting. |
| [CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md](CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md) | Por qué cambiamos de CLUN-LSR a ruteo físico. |
| [MAPA_PROYECTO.md](MAPA_PROYECTO.md) | Qué hay en todo el repo. |

## Ejecutar todo (Docker)

Solo requiere Docker Desktop o Docker Engine con Compose v2: **Python corre únicamente dentro de los contenedores**. Desde la **raíz del repo**:

```bash
docker compose up --build           # BD + main.py: descarga, carga, pesos, rutas, diagrama y sitio
docker compose up -d --build        # lo mismo, en segundo plano; avance con: docker compose logs -f main
docker compose down                 # detiene; los datos de la BD se conservan (volumen db_data)
```

`docker compose up` levanta dos servicios: `db` (PostgreSQL + PostGIS + pgRouting) y `main`, que ejecuta el `main.py` de la raíz: primero el pipeline y después, en el mismo contenedor, el sitio en **http://localhost:8000**. Dos variables cambian lo que hace `main.py`:

| Variable | Efecto |
|---|---|
| `SIN_DESCARGA=1` | Reutiliza los JSON ya generados; no llama a las APIs |
| `SOLO_SITIO=1` | No corre el pipeline: levanta el sitio sobre la BD existente |

Se fijan en `.env` o antes del comando: `SIN_DESCARGA=1 docker compose up` en bash, o `$env:SIN_DESCARGA=1; docker compose up` en PowerShell. Sin `.env`, Compose usa los valores de `.env.example`, incluidas las fechas de la ventana de datos. La BD no se publica fuera de Docker; para consultarla: `docker compose exec db psql -U postgres -d ruteo_uav`.

## Pruebas, experimentos y scripts sueltos (en Docker)

El servicio `pruebas` corre las pruebas y el servicio `app` acepta cualquier comando dentro de `05_T2/`:

```bash
docker compose run --rm pruebas                                                          # 36 pruebas del núcleo, la flota y el ETL
docker compose run --rm app python pipeline.py --solo metadata,amenazas,pesos,rutas     # parte del pipeline
docker compose run --rm app python experimentos/run_experimentos.py --conjunto ajuste                 # A/B/D/C0/C1/C, ~12 s
docker compose run --rm app python experimentos/run_experimentos.py --conjunto ajuste --sensibilidad  # prob_foco x n_fallas, ~2 min
docker compose run --rm app python experimentos/run_flota.py --conjunto ajuste                        # flota con y sin aviso, ~30 s
docker compose run --rm app python experimentos/run_flota.py --conjunto ajuste --sensibilidad --n-fallas 5   # n_uav x p_det, ~5 min
```

> **No ejecutes `--conjunto evaluacion` hasta que el grupo congele los parámetros** (PROPUESTA_TECNICA §8). Ojo: es el valor por defecto de ambos scripts, así que `--conjunto ajuste` siempre va explícito.

## Estructura

```text
05_T2/
├── Dockerfile, requirements.txt   Imagen de la aplicación (ETL, cargas, sitio)
├── pipeline.py                    Orden de ejecución del ETL (lo llama main.py en el servicio main)
├── ruteo/                         Núcleo algorítmico (stdlib): grafo, Dijkstra, Yen, selección, fallas, simulador, flota, métricas
├── comun/                         Compartido: ajustes, transformaciones, descargas, BD, rutas pgRouting, resiliencia, servicio
├── BD/                            schema.sql, MODELO_BD.md, crear_bd.py, pesos.sql + asignar_pesos.py, rutas_ejemplo.py, diagrama_bd.py
├── Infraestructura/               generar_infraestructura.py, cargar_infraestructura.py, ESTRUCTURA_*.md
├── Metadata/                      osm_edificios, elevacion, viento: extracción, carga y ESTRUCTURA_*.md de cada uno
├── Amenazas/                      gpsjam, incendios_guerra, ucdp_eventos: extracción, carga y ESTRUCTURA_*.md
├── SitioWeb/                      app.py (FastAPI) + static/ (Leaflet)
├── experimentos/                  run_experimentos.py (un UAV) y run_flota.py (flota con aviso), con semillas
├── resultados/                    JSON de los experimentos
└── tests/                         test_ruteo.py (núcleo), test_flota.py (flota y avisos), test_etl.py (transformaciones)
```

Fuera de `05_T2/`, en la raíz del repo: `main.py`, `docker-compose.yml` y `.env.example`.

## Fuentes

Ninguna de las seis fuentes externas pide credenciales.

| Rol | Fuente | Se convierte en |
|---|---|---|
| Metadata 1 | OpenStreetMap (Overpass): edificios con altura | Restricción: altura de obstáculos por tramo |
| Metadata 2 | Open-Meteo Elevation (Copernicus DEM GLO-90) | Restricción: relieve relativo al despegue |
| Metadata 3 | Open-Meteo Historical Weather (ERA5): viento a 100 m | Restricción: viento máximo. Peso: factor de viento de frente |
| Amenaza 1 | GPSJam: degradación GNSS por celda H3 | Peso: `p_gnss` |
| Amenaza 2 | The Economist war-fire model (NASA FIRMS) | Peso: `r_incendios`. Focos de las fallas simuladas |
| Amenaza 3 | UCDP GED (vía HDX) | Peso: `r_eventos` |

## Estado

| Hecho | Pendiente |
|---|---|
| Núcleo, simulador, métricas y experimento con ablaciones (conjunto de ajuste), con pruebas | Corrida única sobre el conjunto de evaluación (decisión del grupo) |
| Docker, `schema.sql`, cargadores, pesos en SQL, `pgr_dijkstra` / `pgr_KSP`, diagrama, sitio Leaflet y `main.py` | Mejorar la metadata floja: zonas restringidas, GPSJam y viento (PROPUESTA_TECNICA §11.1) |
| ETL de 3 metadata y 3 amenazas con su documento de estructura | Arreglar el recorte de los focos al borde de la malla (PROPUESTA_TECNICA §2) |
| **Rutas de ejemplo regeneradas y verificadas** tras el arreglo de los focos (22-oct-2026) | Presentación (guía en ENTREGA_TAREA2.md) y subida a GitLab UDP |
| **Flota con aviso** (20-oct-2026): simulador, experimento de ajuste, pruebas (36/36 OK) y sección del sitio | |
| **Verificado en Docker** (22-oct-2026): `python main.py --sin-descarga` con los 18 pasos en `ok`, `POST /api/flota` y `POST /api/rutas` respondiendo, y las seis capas del mapa | |
| **Solo Docker Compose** (22-oct-2026): `docker compose up --build` corre `main.py` dentro del contenedor `main` (pipeline y luego sitio); el equipo ya no necesita Python | |

**Resultado preliminar de la flota** (ajuste, 4 UAV, 3 fallas, `p_det = 0,5`): con el aviso compartido, los UAV que vienen detrás completan **+10 pp** más misiones con Dijkstra (D_A frente a D: 30 escenario-UAV ganados y 0 perdidos) y **+16 pp** con la propuesta (C_A frente a D). Si la interferencia siempre se nota antes de entrar (`p_det = 1`), el aviso casi no cambia la tasa. Detalle en PROPUESTA_TECNICA §10.

### Resultado de la primera corrida completa (19 de octubre de 2026)

`python main.py` terminó con código 0 y los 18 pasos en `ok` (≈13 min, de los cuales 10 fueron Overpass).

| Qué | Valor obtenido |
|---|---|
| Motor | PostGIS 3.5.2, pgRouting 3.8.0; 13 tablas creadas |
| Infraestructura | 196 nodos, 618 aristas (374,18 km), misión `[15, 131, 65, 151, 181]` |
| Metadata | 33.593 edificios OSM (1.022 con altura) · 814 puntos de elevación (0–57 m) · 720 horas de viento (mediana 6,92 m/s desde 4,5°) |
| Amenazas | 7 celdas GPSJam (máx. 0,3333 de días en rojo) · 41 incendios de guerra (26 históricos, 15 de evaluación) · 65 eventos UCDP |
| Pesos | 179 aristas con edificio en el buffer (máx. 77 m); riesgo medio 0,4511 |
| Rutas de ejemplo (15 → 181) | Dijkstra 8,462 y 9,166 km · propuesta 8,462 y 8,587 km |
| Resiliencia (100 escenarios, 3 fallas) | R_par 0,91 / 0,89 · R_misión A 0,91, D 1,00, C 1,00 · ΔR(C−A) = 9 pp (p = 0,0039), ΔR(C−D) = 0 pp |
| Pruebas unitarias | 28/28 OK en local y dentro de la imagen |

Se confirma el resultado preliminar: **C supera a A pero empata con la ablación D.**

Reproducir sin volver a descargar: `SIN_DESCARGA=1 docker compose up` (Overpass tardó 614 s y el
servidor principal respondió HTTP 502; el espejo `overpass.kumi.systems` salvó el paso).

### Hallazgo de la primera corrida: los focos de las fallas salían del período equivocado

**Qué pasaba.** Los incendios de guerra cumplen dos papeles deliberadamente separados
(PROPUESTA_TECNICA §2): los del **período histórico** fijan el peso `r_incendios` de cada tramo, y
los del **período de evaluación** son los focos de las fallas simuladas. Separarlos es lo que evita
evaluar el método con los mismos datos que ajustaron sus pesos.

**La causa.** `Amenazas/incendios_guerra.py` descarga los incendios del AOI **más `BUFFER_KM`**
(5 km), pero `comun/resiliencia.py` buscaba los focos dentro del **AOI estricto** (`bbox(0.0)`).
Los 15 incendios del período de evaluación cayeron todos en el anillo del buffer: ninguno quedaba
dentro del AOI, la primera consulta de `CONSULTAS_FOCOS` devolvía vacío y `focos_bd` caía al
*fallback*, usando 3 incendios **históricos**, los mismos que habían fijado `r_incendios`.

Comprobación en la BD de la corrida del 19 de octubre:

```sql
SELECT periodo, count(*) AS total,
       count(*) FILTER (WHERE geom && ST_MakeEnvelope(31.950,46.945,32.040,47.005,4326)) AS dentro_aoi
FROM amz_incendios WHERE guerra GROUP BY periodo;
--  evaluacion | 15 | 0     <- ninguno dentro del AOI estricto
--  historico  | 26 | 3     <- el fallback que terminaba usándose
```

El sitio lo dejaba a la vista en el panel de resultados: «Focos de las fallas:
incendios_guerra_historicos (3)».

**El arreglo.** `focos_bd` ahora busca en `bbox(BUFFER_KM)`, la misma ventana con que las fuentes de
`Amenazas/` filtraron sus descargas. Además es lo correcto físicamente: una falla centrada justo
fuera del AOI igual alcanza tramos de la malla.

**Consecuencia para los números.** La tabla de más arriba (rutas de ejemplo y resiliencia de la BD)
se produjo **antes** de este arreglo, con focos históricos. Los JSON de `resultados/` **no** se ven
afectados: salen del simulador en Python, con focos sintéticos. Hay que **regenerar las rutas de
ejemplo y su evaluación** antes de presentar:

```bash
docker compose run --rm app python BD/rutas_ejemplo.py
```

Es esperable que ΔR(C−A) cambie: con focos históricos las fallas caían sobre los tramos que el
método ya evitaba por tener `r_incendios` alto, lo que favorecía a la propuesta.

**Resultado preliminar principal:** C supera a Dijkstra (A) en hasta +22 pp de misiones completadas, pero **no** supera a la ablación D (Dijkstra que replanifica). El detalle está en PROPUESTA_TECNICA §9.

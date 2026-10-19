# 05_T2: ruteo físico resiliente de UAV

Nueva propuesta de la Tarea 2. Un UAV simulado recorre puntos de inspección sobre un grafo geolocalizado (Mykolaiv, referencia provisional). Comparamos **Dijkstra por km** (`pgr_dijkstra`) con **Yen + selección resiliente + replanificación** (`pgr_KSP` + selección propia) frente a fallas espaciales reproducibles. La metadata y las amenazas salen de fuentes públicas.

| Documento | Para qué |
|---|---|
| [ENTREGA_TAREA2.md](ENTREGA_TAREA2.md) | **Cada criterio de la rúbrica → archivo y evidencia.** Guía para la presentación. |
| [PROPUESTA_TECNICA.md](PROPUESTA_TECNICA.md) | Formalización: fallas, pesos, restricciones, algoritmo, métricas, protocolo y resultados preliminares. |
| [BD/MODELO_BD.md](BD/MODELO_BD.md) | Modelo de la base de datos, diagrama y consultas pgRouting. |
| [CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md](CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md) | Por qué cambiamos de CLUN-LSR a ruteo físico. |
| [MAPA_PROYECTO.md](MAPA_PROYECTO.md) | Qué hay en todo el repo. |

## Ejecutar todo (Docker)

Requiere Docker Desktop o Docker Engine con Compose v2. Desde la **raíz del repo**:

```bash
python main.py                  # BD + descarga + carga + pesos + rutas + diagrama + sitio
python main.py --sin-descarga   # reutiliza los JSON ya generados
python main.py --solo-sitio     # solo BD y sitio
python main.py --pruebas        # pruebas unitarias en el contenedor
python main.py --detener
```

El sitio queda en **http://localhost:8000**. `main.py` crea `.env` con una contraseña aleatoria si no existe (plantilla en `.env.example`). Las fechas de la ventana de datos también se definen ahí.

Si se prefiere hacerlo a mano:

```bash
docker compose up -d --wait db
docker compose --profile tareas run --rm app python pipeline.py      # o un script suelto: python Metadata/viento.py
docker compose up -d web
```

## Ejecutar el núcleo sin Docker

El paquete `ruteo/` y los experimentos usan **solo la biblioteca estándar** (Python ≥ 3.10):

```bash
cd 05_T2
python -m unittest discover -s tests -v                                   # pruebas del núcleo y del ETL
python Infraestructura/generar_infraestructura.py                         # -> Infraestructura/salida/infraestructura.json
python experimentos/run_experimentos.py --conjunto ajuste                 # comparación A/B/D/C0/C1/C, ~12 s
python experimentos/run_experimentos.py --conjunto ajuste --sensibilidad  # barrido prob_foco x n_fallas, ~2 min
```

> **No ejecutes `--conjunto evaluacion` hasta que el grupo congele los parámetros** (PROPUESTA_TECNICA §8).

En Windows, si la consola muestra mal los acentos: `$env:PYTHONIOENCODING="utf-8"` (PowerShell).

## Estructura

```text
05_T2/
├── Dockerfile, requirements.txt   Imagen de la aplicación (ETL, cargas, sitio)
├── pipeline.py                    Orden de ejecución del ETL dentro del contenedor (lo llama main.py)
├── ruteo/                         Núcleo algorítmico (stdlib): grafo, Dijkstra, Yen, selección, fallas, simulador, métricas
├── comun/                         Compartido: ajustes, transformaciones, descargas, BD, rutas pgRouting, resiliencia, servicio
├── BD/                            schema.sql, MODELO_BD.md, crear_bd.py, pesos.sql + asignar_pesos.py, rutas_ejemplo.py, diagrama_bd.py
├── Infraestructura/               generar_infraestructura.py, cargar_infraestructura.py, ESTRUCTURA_*.md
├── Metadata/                      osm_edificios, elevacion, viento: extracción, carga y ESTRUCTURA_*.md de cada uno
├── Amenazas/                      gpsjam, incendios_guerra, ucdp_eventos: extracción, carga y ESTRUCTURA_*.md
├── SitioWeb/                      app.py (FastAPI) + static/ (Leaflet)
├── experimentos/                  run_experimentos.py (simulación con semillas)
├── resultados/                    JSON de los experimentos
└── tests/                         test_ruteo.py (núcleo), test_etl.py (transformaciones)
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
| Núcleo, simulador, métricas y experimento con ablaciones (conjunto de ajuste), con pruebas | **Primera ejecución completa con Docker** (`python main.py`): todo lo de Docker está escrito, pero **aún no se ha ejecutado** |
| Docker, `schema.sql`, cargadores, pesos en SQL, `pgr_dijkstra` / `pgr_KSP`, diagrama, sitio Leaflet y `main.py` | Revisar que las seis fuentes respondan y ajustar lo que falle |
| ETL de 3 metadata y 3 amenazas con su documento de estructura | Corrida única sobre el conjunto de evaluación (decisión del grupo) |
| | Presentación (guía en ENTREGA_TAREA2.md) y subida a GitLab UDP |

**Resultado preliminar principal:** C supera a Dijkstra (A) en hasta +22 pp de misiones completadas, pero **no** supera a la ablación D (Dijkstra que replanifica). El detalle está en PROPUESTA_TECNICA §9.

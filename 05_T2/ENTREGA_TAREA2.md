# Entrega de la Tarea 2: rúbrica → evidencia

La rúbrica se evalúa sobre la **presentación**. Para cada criterio, esta guía indica qué archivo lo cumple y qué mostrar en la diapositiva. Puntaje total: 60.

> **Estado (22 de octubre de 2026):** todo se ejecuta con `docker compose up --build` desde la raíz;
> el equipo solo necesita Docker, porque `main.py` corre dentro del contenedor `main`. La ejecución
> completa terminó con los 18 pasos del pipeline en `ok` y las seis fuentes externas respondieron.
> El detalle de los números está en [README.md](README.md#estado). Falta capturar las pantallas
> que pide esta guía y resolver el pendiente de los focos de evaluación (README, §Estado).
>
> Cuidado al preparar la presentación: Overpass llegó a tardar 614 s (el servidor principal
> devolvió HTTP 502 y respondió el espejo). Conviene correr `docker compose up --build` con
> antelación y, en la demo, usar `SIN_DESCARGA=1` o `SOLO_SITIO=1` (README, §Ejecutar todo). El
> sitio carga Leaflet desde `unpkg` y los *tiles* desde OSM: la demostración necesita internet en
> el navegador.

## Proceso ETL completo (lo que pide el enunciado)

`docker compose up` → contenedor `main` → `main.py` (raíz) → `05_T2/pipeline.py` y, al terminar, el sitio:

1. **Esquema.** `BD/crear_bd.py` ejecuta `BD/schema.sql` (crea la BD desde cero).
2. **Infraestructura.** `generar_infraestructura.py` produce el JSON y `cargar_infraestructura.py` lo carga en `nodos`, `aristas` y `mision`.
3. **Metadata (3).** Extracción a JSON en `Metadata/salida/` y carga en `meta_*`.
4. **Amenazas (3).** Extracción a JSON en `Amenazas/salida/` y carga en `amz_*`.
5. **Transformación a pesos.** `BD/asignar_pesos.py` ejecuta `BD/pesos.sql`: restricciones y riesgo por arista.
6. **Rutas de ejemplo.** `BD/rutas_ejemplo.py`: `pgr_dijkstra` y `pgr_KSP` + selección, con su resiliencia.
7. **Diagrama.** `BD/diagrama_bd.py` genera `BD/diagrama_bd.png`.
8. **Sitio.** El mismo `main.py` levanta FastAPI + Leaflet → http://localhost:8000.

## Criterio por criterio

| # | Criterio | Pts | Dónde está | Qué mostrar |
|---|---|---|---|---|
| 1 | Docker con postgres, postgis y pgrouting | 2 | `docker-compose.yml` (imagen `pgrouting/pgrouting:17-3.5-3.8.0`), `05_T2/Dockerfile` | `docker compose ps` y la salida de `crear_bd.py` (versiones de PostGIS y pgRouting) |
| 2 | Explicar el modelo de BD y entregar el SQL | 2 | `BD/schema.sql`, `BD/MODELO_BD.md`, `BD/diagrama_bd.png` | El diagrama y la tabla de grupos de MODELO_BD |
| 3.1 | Scripts que obtienen n metadata → JSON | 6 | `Metadata/osm_edificios.py`, `elevacion.py`, `viento.py` + `ESTRUCTURA_*.md` | Fragmento de cada JSON y su documento de estructura |
| 3.2 | Scripts que cargan la metadata en la BD | 2 | `Metadata/cargar_*.py` | Conteos de `meta_*` (los imprime cada cargador) |
| 4.1 | Scripts que obtienen n fallas → JSON | 6 | `Amenazas/gpsjam.py`, `incendios_guerra.py`, `ucdp_eventos.py` + `ESTRUCTURA_*.md` | Fragmento de cada JSON y la capa en el mapa |
| 4.2 | Scripts que cargan las fallas en la BD | 2 | `Amenazas/cargar_*.py` | Conteos de `amz_*` |
| 5.1 | Explicar el modelamiento de las fallas | 3 | PROPUESTA_TECNICA §2, `ruteo/fallas.py` | Disco `(c, r, t_on)`, descubrimiento local y focos tomados de incendios del período de evaluación |
| 5.2 | Asignación de pesos a partir de las fallas | 2 | `BD/pesos.sql`, `ruteo/pesos.py` | Densidad gaussiana por tramo, `riesgo = 1 − Π(1 − rᵢ)` y costo `largo · f_viento · (1 + w_R · riesgo)` |
| 6.1 | Metadata convertida en restricciones (preferencias del usuario) | 3 | `comun/transformar.py` (`obstaculo_relativo_m`), `ruteo/pesos.py` (`arista_admisible`, `mision_admisible`) | Obstáculo = relieve relativo + edificio ≥ altura − margen → tramo excluido; viento > máximo → misión no admisible |
| 6.2 | Preferencias por defecto | 2 | `ruteo/config.py` (`Preferencias`), tabla en PROPUESTA_TECNICA §3 | El formulario del sitio con los valores por defecto |
| 7.1 | Nombre del algoritmo y paper | 4 | PROPUESTA_TECNICA §4 | Yen (1971), *Management Science* 17(11), doi:10.1287/mnsc.17.11.712 (`pgr_KSP`), más el aporte propio |
| 7.2 | Explicar el algoritmo | 6 | PROPUESTA_TECNICA §4, `ruteo/algoritmos.py`, `comun/rutas.py` | Pseudocódigo PLANIFICAR / AL_DESCUBRIR / REACCIONAR y J(p, q) |
| 8 | k ≥ 2 rutas solo con `pgr_dijkstra` por km | 4 | `comun/rutas.py` (`dijkstra_dos_rutas_pgr`), `BD/rutas_ejemplo.py` | Mapa con las 2 rutas azules del ejemplo y la consulta SQL |
| 9 | k ≥ 2 rutas con el algoritmo propuesto | 4 | `comun/rutas.py` (`ksp_pgr`, `propuesta_pgr`) | Mapa con las 2 rutas naranjas |
| 10 | Métrica de resiliencia de k rutas | 6 | `comun/resiliencia.py`, `ruteo/metricas.py` | `R_par` (alguna ruta del par queda libre) y `R_mision` (llega dentro del presupuesto) sobre N escenarios. Para la flota, `R_seguidores` (PROPUESTA_TECNICA §10) |
| 11.1 | Plataforma: (inicio, objetivo) + restricciones → mapa con el par | 4 | `SitioWeb/app.py`, `SitioWeb/static/` | Demostración: clic en origen y destino, cambio de una preferencia, "Calcular rutas". Después, la sección 4 "Flota con aviso": mover o añadir un punto de observación, reproducir el escenario y cambiar entre con aviso y sin aviso |
| 11.2 | Diferencial de resiliencia | 2 | Panel de resultados del sitio, tabla `evaluaciones`, panel de la flota | ΔR = R(C) − R(A) en pp, con el p de McNemar. Mostrar también C − D (ablación) y, en la flota, D_A − D (valor del aviso) y C_A − D_A |

## Flota con aviso compartido (idea del profesor y base en CLUN-LSR)

No es un criterio aparte de la rúbrica, pero responde la observación de la reunión: con un solo dron, avisar al resto "es un problema que no existe".

- **Qué es:** de 3 a 5 UAV hacen la misma misión. El que detecta interferencia avisa a la flota, el aviso se retransmite de UAV en UAV, y los demás cambian de ruta en pleno vuelo. Si un UAV queda dentro de una zona, deja de emitir su beacon y la flota marca esa zona. Ver `ruteo/flota.py` y PROPUESTA_TECNICA §10.
- **Qué mostrar:** la animación del sitio, en el mismo escenario con aviso y sin aviso. Después, la tabla de PROPUESTA_TECNICA §10. Con `p_det ≤ 0,5`, D_A − D da entre +10 y +17 pp en los seguidores, sin ningún caso perdido. Con `p_det = 1`, el aviso casi no cambia la tasa, y hay que decirlo.
- **Cómo reproducir:** `docker compose run --rm app python experimentos/run_flota.py --conjunto ajuste` y lo mismo con `--sensibilidad --n-fallas 5`.

## Puntos del enunciado que no son criterios

- **Punto 0.** Imagen del diagrama más el `.sql`: `BD/diagrama_bd.png` (se genera con `docker compose up`) y `BD/schema.sql`.
- **Punto 4.** Un documento por cada JSON:

  | JSON | Documento |
  |---|---|
  | `infraestructura.json` | `Infraestructura/ESTRUCTURA_infraestructura_json.md` |
  | `osm_edificios.json` | `Metadata/ESTRUCTURA_osm_edificios_json.md` |
  | `elevacion.json` | `Metadata/ESTRUCTURA_elevacion_json.md` |
  | `viento.json` | `Metadata/ESTRUCTURA_viento_json.md` |
  | `gpsjam.json` | `Amenazas/ESTRUCTURA_gpsjam_json.md` |
  | `incendios_guerra.json` | `Amenazas/ESTRUCTURA_incendios_guerra_json.md` |
  | `ucdp_eventos.json` | `Amenazas/ESTRUCTURA_ucdp_eventos_json.md` |
  | `rutas_ejemplo.json` | `BD/ESTRUCTURA_rutas_ejemplo_json.md` |

- **Punto 9.** El `main.py` está en la raíz y `docker compose up` lo ejecuta dentro de un contenedor: descarga, carga en la BD y habilitación del sitio.
- **Docker.** Todo corre en contenedores y el equipo no necesita Python: `db` y `main` con `docker compose up`; `pruebas` y `app` para las pruebas y los comandos sueltos.

## Advertencias que conviene decir en la presentación

- La malla es **sintética** y geolocalizada. No representa corredores aéreos reales ni es un plan de vuelo.
- GPSJam mide **aviones en altura**. Sobre zonas de guerra sin tráfico civil suele no haber datos, y eso es ausencia de dato, no de interferencia. Y en nuestro AOI **no discrimina**: toda el área cabe en una celda H3 de ~1 775 km², así que los 618 tramos reciben el mismo `0,3333`. Si preguntan por el riesgo medio de 0,45, hay que decir que esa constante es la que lo infla (PROPUESTA_TECNICA §11.1).
- **Si preguntan por las zonas restringidas:** la preferencia existe en el sitio y el simulador la evalúa, pero ninguna fuente la activa; hoy `en_zona_restringida` es `false` en los 618 tramos. Es lo primero de la lista de mejoras.
- El modelo de jamming del simulador es **abstracto**: discos con radio, momento de activación y focos. No se modelan sistemas reales.
- **La comparación honesta incluye la ablación D.** Con los datos de ajuste, C supera a A, pero no a D (PROPUESTA_TECNICA §9).
- **El aviso de la flota sirve cuando la interferencia no se nota antes de entrar.** Con detección perfecta en el borde, cada UAV esquiva solo y el aviso únicamente ahorra km (PROPUESTA_TECNICA §10). La probabilidad de detección es un supuesto, por eso se muestra el barrido.

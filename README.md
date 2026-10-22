# Ruteo resiliente de UAV para reconocimiento de una zona

Repositorio académico del grupo 7. La Tarea 2 está **implementada y en ejecución**: una flota de UAV simulados recorre un grafo geolocalizado de Mykolaiv y, cuando uno detecta interferencia, avisa al resto —el aviso se retransmite de UAV en UAV, como en CLUN-LSR— y los demás cambian su ruta en pleno vuelo. Lo que falta es la corrida de evaluación con las semillas reservadas; los resultados publicados son del conjunto de ajuste.

## Lectura recomendada

1. [05_T2/README.md](05_T2/README.md): cómo correr todo y qué documento leer según lo que se busque.
2. [Entrega de la Tarea 2](05_T2/ENTREGA_TAREA2.md): cada criterio de la rúbrica con el archivo y la evidencia que lo respalda.
3. [Propuesta técnica](05_T2/PROPUESTA_TECNICA.md): fallas, pesos, restricciones, algoritmo, métricas y la flota con aviso compartido (§10).
4. [Informe de la Tarea 2](05_T2/Informe_Tarea_2_Ruteo_Resiliente_UAV.tex): borrador en LaTeX, formato IEEEtran.
5. [Enunciado y rúbrica de la Tarea 2](01_PROYECTO_ACTUAL/ENUNCIADO_Y_RUBRICA_TAREA_2.txt): copia del texto facilitado al grupo.

## Estructura

| Ruta | Contenido |
|---|---|
| [01_PROYECTO_ACTUAL/](01_PROYECTO_ACTUAL/) | Enunciado, rúbrica y los documentos con que se reformuló la Tarea 2 tras la reunión. |
| [02_REUNION_PROFESOR/](02_REUNION_PROFESOR/) | Transcripción de la reunión y guion anterior a ella. La grabación queda solo en el equipo local. |
| [03_TAREA_1/](03_TAREA_1/README.md) | Informe entregado, fuente LaTeX, referencia chilena sobre jamming y pruebas iniciales. Es material histórico. |
| [04_VALIDACION_TAREA_1/](04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md) | Scripts, SQL, Docker, resultados resumidos y guía para reproducir la validación de fuentes. |
| [05_T2/](05_T2/README.md) | **Entrega vigente:** ruteo físico resiliente y flota con aviso compartido. Pipeline Docker, base PostGIS/pgRouting, núcleo Python, experimentos, sitio Leaflet e informe. |

La Tarea 1 tomó como base **CLUN-LSR**, que recupera caminos de comunicación entre UAV. La Tarea 2 cambia el objeto de optimización —ahora el grafo son lugares y tramos de vuelo, no enlaces de radio— y conserva de CLUN-LSR solo **su efecto**: que el aviso de interferencia llegue por multisalto y los demás UAV replanifiquen. No se simula el protocolo (capas, espectro, MP-OLSR). La distinción se desarrolla en [CONTEXTO_PROPUESTA…](05_T2/CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md).

## Estado técnico

| Componente | Estado verificable en este repositorio |
|---|---|
| Consultas a fuentes geoespaciales y meteorológicas | Seis fuentes implementadas con cargador y documento de estructura por cada JSON (`05_T2/Metadata/`, `05_T2/Amenazas/`). |
| PostgreSQL/PostGIS/pgRouting | `docker-compose.yml`, `05_T2/BD/schema.sql`, diagrama generado y pipeline completo que corre en contenedores. |
| Grafo físico de puntos y tramos, rutas `pgr_dijkstra` y `pgr_KSP` | Implementado: malla de 196 nodos y 618 aristas, dos rutas por método en `05_T2/comun/rutas.py` y `BD/rutas_ejemplo.py`. |
| Algoritmo resiliente, comparación de rutas y métricas | Implementado: Yen + selección por `J(p,q)` + replanificación (`05_T2/ruteo/`), con `R_par`, `R_mision` y McNemar pareado. |
| **Flota reactiva con aviso compartido** | Implementado: `05_T2/ruteo/flota.py`, animación en el sitio y barrido en `05_T2/resultados/`. |
| Sitio Leaflet y ejecución integral desde un `main` raíz | Implementado: `python main.py` levanta BD, pipeline y sitio en http://localhost:8000. |
| Corrida de evaluación con semillas reservadas | **Pendiente.** Todo lo publicado usa las semillas 0–99 del conjunto de ajuste. |
| Calidad de la metadata | **Desigual.** Los edificios OSM deciden 79 de las 83 exclusiones, pero GPSJam no discrimina, el viento nunca restringe y las zonas restringidas no tienen fuente. Auditoría en [PROPUESTA_TECNICA §11.1](05_T2/PROPUESTA_TECNICA.md). |

La existencia de datos y consultas PostGIS **no demuestra** que el algoritmo de ruteo funcione, y los resultados del simulador son de escenarios sintéticos: discos de interferencia con radio y momento de activación supuestos. Los conteos de las fuentes son registros extraídos, no tasas de incidencia de jamming.

## Ejecutar la Tarea 2

Requiere Docker con Compose v2. Desde la raíz del repositorio:

```bash
python main.py                  # BD + descarga + carga + pesos + rutas + diagrama + sitio
python main.py --sin-descarga   # reutiliza los JSON ya generados, sin llamar a las APIs
python main.py --pruebas        # 36 pruebas unitarias en el contenedor
python main.py --detener
```

El sitio queda en **http://localhost:8000**: se elige origen y destino sobre el mapa, se ajustan las preferencias y la sección "Flota con aviso" anima el mismo escenario con aviso y sin aviso. Los puntos de observación de la misión se pueden mover, quitar y añadir desde esa misma sección. Los experimentos se reproducen con `experimentos/run_experimentos.py` y `experimentos/run_flota.py` desde `05_T2/`.

## Reproducir la validación de la Tarea 1

Es material histórico y usa su propio entorno. La guía completa está en [Datos y reproducción](04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md):

```bash
cd 04_VALIDACION_TAREA_1/validacion_ruteo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Completar .env con credenciales propias y parámetros de la zona.
python run_all.py
```

Para la carga espacial se requiere Docker Compose: `docker compose up -d`, seguido de `python import_geojson_to_postgis.py` y `python postgis_evidence.py`. Estos comandos se ejecutan desde `04_VALIDACION_TAREA_1/validacion_ruteo/`. Los [scripts exploratorios](03_TAREA_1/pruebas_iniciales/) son independientes y se ejecutan desde su propia carpeta.

## Qué se comparte mediante Git

Se incluyen código, documentación, informe de la Tarea 1, figura del DEM y resultados **resumidos**. El `.gitignore` excluye credenciales, entornos Python, respuestas crudas de APIs, archivos de datos voluminosos, el ZIP antiguo y el video de la reunión. Estos archivos permanecen en el equipo local; no aparecen al clonar el repositorio. La transcripción sí se incluye como antecedente y puede contener errores de reconocimiento de voz.

Las claves que aparecían en dos scripts exploratorios se sustituyeron por variables de entorno. Si se compartieron copias anteriores con esas claves, hay que reemplazarlas en los servicios correspondientes. Antes de un `git add`, revisar `git status` y comprobar que no se estén incluyendo secretos o datos crudos.

## Incorporarlo al repositorio del grupo

El directorio está inicializado como repositorio Git local, en la rama `main`, **sin remoto ni commit**. Si el grupo ya tiene un proyecto en GitLab UDP, usar un clon de ese proyecto y copiar allí el contenido de esta carpeta **sin copiar `.git/`**; así se conserva la historia del equipo. Si el proyecto remoto está vacío y se usará esta carpeta como origen, revisar y crear el primer commit:

```bash
git status --short
git add .
git diff --cached --stat
git commit -m "Documentar proyecto UAV y validación inicial"
```

Después, configurar la URL real del repositorio del grupo como `origin` y enviar la rama. No hay una URL remota configurada en esta copia.

## Abrir en VS Code

Abre la carpeta `AlgoritmosRuteo` completa. [`.vscode/settings.json`](.vscode/settings.json) oculta `venv` y cachés en el explorador; no elimina archivos. Las carpetas numeradas mantienen el mismo orden en VS Code y en el gestor de archivos.

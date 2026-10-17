# Ruteo resiliente de UAV para reconocimiento de una zona

Repositorio académico del grupo 7. Aquí están los antecedentes, el código de validación geoespacial y el planteamiento que surgió tras la conversación con el profesor. **La Tarea 2 todavía está en fase de diseño:** no se ha implementado ni validado un algoritmo de trayectorias resilientes.

## Lectura recomendada

1. [Contexto para el grupo](01_PROYECTO_ACTUAL/CONTEXTO_PARA_EL_GRUPO_TAREA_2.md): qué se hizo, qué se observó en la corrección y cómo se propone avanzar.
2. [Enfoque tras la reunión](01_PROYECTO_ACTUAL/ENFOQUE_TRAS_CHARLA_PROFESOR.md): interpretación de las orientaciones del profesor y decisiones abiertas.
3. [Resumen técnico](01_PROYECTO_ACTUAL/RESUMEN_PROYECTO_Y_TAREA_2.md): resultados de la Tarea 1, evidencia, límites y contraste con la Tarea 2.
4. [Enunciado y rúbrica de la Tarea 2](01_PROYECTO_ACTUAL/ENUNCIADO_Y_RUBRICA_TAREA_2.txt): copia del texto facilitado al grupo.

## Estructura

| Ruta | Contenido |
|---|---|
| [01_PROYECTO_ACTUAL/](01_PROYECTO_ACTUAL/) | Documentos vigentes para decidir y formular la Tarea 2. |
| [02_REUNION_PROFESOR/](02_REUNION_PROFESOR/) | Transcripción de la reunión y guion anterior a ella. La grabación queda solo en el equipo local. |
| [03_TAREA_1/](03_TAREA_1/README.md) | Informe entregado, fuente LaTeX, referencia chilena sobre jamming y pruebas iniciales. Es material histórico. |
| [04_VALIDACION_TAREA_1/](04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md) | Scripts, SQL, Docker, resultados resumidos y guía para reproducir la validación de fuentes. |

La Tarea 1 tomó como base **CLUN-LSR**, que recupera caminos de comunicación entre UAV. El enfoque actual usa la pérdida de reporte como señal para **replanificar una trayectoria física de reconocimiento**. Son problemas relacionados, pero sus grafos, algoritmos y métricas no son equivalentes; esta distinción se desarrolla en los documentos de `01_PROYECTO_ACTUAL/`.

## Estado técnico

| Componente | Estado verificable en este repositorio |
|---|---|
| Consultas a fuentes geoespaciales y meteorológicas | Scripts y evidencia de ejecuciones anteriores. Algunas fuentes requieren credenciales y pueden cambiar sus respuestas. |
| PostgreSQL/PostGIS | `docker-compose.yml`, SQL y scripts de carga/consulta de cuatro capas. |
| Grafo físico de puntos y tramos, pgRouting y rutas `pgr_dijkstra` | Pendiente para la Tarea 2. |
| Algoritmo resiliente, comparación de rutas y métrica de cobertura | Pendiente para la Tarea 2. |
| Sitio Leaflet y ejecución integral desde un `main` raíz | Pendiente para la Tarea 2. |

La existencia de datos y consultas PostGIS **no demuestra** que el algoritmo de ruteo funcione. Los conteos del informe son resultados de consultas puntuales y no tasas de incidencia de jamming.

## Reproducir la validación disponible

La guía completa está en [Datos y reproducción](04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md). Como punto de partida:

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

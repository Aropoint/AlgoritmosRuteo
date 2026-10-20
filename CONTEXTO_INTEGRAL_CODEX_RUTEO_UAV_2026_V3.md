# Actualización V3 — Historial completo de Codex, retroalimentación y estado del repositorio

> **18 de octubre de 2026 · Prioridad máxima.** Esta actualización es el punto de entrada obligatorio. Está construida a partir del historial de conversación exportado en `Texto pegado(3).txt`, los materiales originales de Tarea 1 y 2, la transcripción del profesor, el contexto v2 y las capturas del repositorio. **Las afirmaciones sobre modificaciones de archivos y Git provienen de la conversación con Codex, y deben verificarse de nuevo en el repositorio actual.**
>
> **Precedencia:** para decisiones nuevas, usar esta sección V3. El resto del documento conserva el contexto y propuestas previas, incluidas alternativas descartadas, como antecedentes históricos. **No interpretar una alternativa antigua como decisión actual.**

## V3.1. Resumen ejecutivo (leer antes de tocar el código)

1. El grupo empezó proponiendo extender **CLUN-LSR** (rutas **de paquetes** en una red de UAV bajo jamming), y en Tarea 1 validó parcialmente fuentes de datos y PostGIS; **no implementó un algoritmo completo de rutas resilientes**.
2. El ayudante objetó la falta de **problemática cuantificada, hipótesis refutable, aporte algorítmico, dinámica del grafo, realismo tridimensional y citas**. La capacidad de obtener APIs no sustituye el objetivo de diseñar y validar un algoritmo.
3. La reunión con el profesor abrió la posibilidad de reinterpretar el problema como **ruteo físico de UAV y continuidad de una misión de reconocimiento/cobertura**, usando interrupciones de información como alertas **inciertas**, no como pruebas de jamming ni de destrucción. Sus menciones de guerra y ataque son ejemplos, no requisitos.
4. La decisión registrada en la conversación con Codex fue **reconocimiento/cobertura de un polígono**, no necesariamente una sola llegada a un punto. En conversaciones posteriores se exploró un **único grafo físico y la comparación origen–destino** porque la rúbrica lo exige. **La compatibilidad entre cobertura del polígono y 2 rutas entre un par de puntos sigue siendo una decisión de diseño a justificar, no un hecho resuelto.**
5. El último contexto trabajado en ChatGPT usa una **simulación académica de monitoreo territorial no ofensivo**, con una **ciudad de referencia (Mykolaiv, Ucrania)** y un único grafo físico. **La localidad exacta, el polígono y la cobertura de cada API siguen sin validarse con una extracción reproducida para ese lugar.** Sumy, Reino Unido, Chile y México se investigaron como candidatos históricos; no son decisiones simultáneas.
6. Se ha explorado **Yen / `pgr_KSP`** como generador de alternativas físicas y `pgr_dijkstra` por distancia como línea base. **No confundir enumerar rutas con garantizar resiliencia; se requiere criterio de selección, escenarios de falla, controles, métricas y comparación justa.**
7. La conversación posterior con Codex **afirma** que el repositorio fue ordenado, documentado y preparado para compartir, con `.gitignore`, README, scripts saneados de claves, sintaxis verificada y una rama `main` sin commit ni remoto. **Revalidar estado Git actual: esas conclusiones corresponden al instante de la sesión exportada, no al presente.**
8. **Primera misión nueva de Codex:** auditoría incremental y reconciliación de estos documentos, no reordenar por segunda vez el repositorio ni implementar 3 soluciones en paralelo.

## V3.2. Retroalimentación del ayudante (14 reparos) y correcciones obligatorias

| N.º | Reparos del ayudante, sintetizados fielmente | Acción requerida |
|---:|---|---|
| 1 | La problemática real carece de cifras | Sustentar con literatura o informes adecuados al fenómeno; no inventar incidencia local |
| 2 | “Mucho tiempo” de recuperación está indefinido | Definir formalmente tiempo de recuperación, unidad, baseline y origen de datos |
| 3 | UAV móviles con aristas estáticas es incoherente | Si se simula movimiento, actualizar estado de nodo/arista a lo largo del tiempo; en un grafo físico estático modelar *explícitamente* que son puntos de navegación, no drones |
| 4 | “Será posible estudiar” no es hipótesis refutable | Establecer predicción sobre métrica con escenario, baseline y criterio de falsación |
| 5 | Hacer una BD no es diseñar y validar algoritmo | Priorizar algoritmo + experimentos; ETL/BD son infraestructura de soporte |
| 6 | Objetivos reducidos a Tarea 1 | Específicos deben abarcar diseño, implementación y comparación |
| 7 | Un objetivo simplemente parafrasea la rúbrica | Formular acciones particulares al problema |
| 8 | Depuración de código no es objetivo científico | Dejar debugging como actividad técnica, no objetivo principal |
| 9 | Un objetivo sí se considera específico | Identificarlo en versión corregida y preservar su intención |
| 10 | Relieve de 1.881 m comparado con avión de ~10.000 m | No usar magnitudes sin contexto físico apropiado |
| 11 | OpenSky mide principalmente aeronaves convencionales, no UAV a baja altura | Retirar OpenSky como prueba de trayectorias UAV o reemplazar por movilidad sintética validada como tal |
| 12 | Representación 2D insuficiente para afirmaciones 3D | Incluir altitud, supuestos y limitación de obstáculos; evitar afirmar seguridad de vuelo real |
| 13 | Hay texto repetido | Reducir redundancias en informe/presentación |
| 14 | Afirmaciones, figuras y tablas sin fuentes | Añadir citas o etiquetas de resultado propio en cada caso |

**Dato importante sobre la evaluación:** la conversación exportada atribuye **problemática 1/6, hipótesis 0/6, factibilidad de infraestructura 6/6 y un subtotal visible de 20/44**. Ese subtotal corresponde a la porción de rúbrica visible en aquella conversación; **NO afirmarlo como nota final 20/60** ni usarlo sin revisar la evaluación oficial.

En el historial se menciona un ejemplo del paper con tiempos **7,16 s y 2,24 s**; **no son promedios universales de reacción de UAV**. Confirmar tabla/figura y definición antes de citar. Se menciona también un aumento agregado de eventos GNSS en aviación según EASA/IATA; **no equivale a incidencia de jamming de enlaces UAV**.

## V3.3. Qué dijo el profesor versus qué decidió el grupo

**Profesor (interpretación de la transcripción):** aterrizar en una misión específica y una razón de ser de la resiliencia; distinguir rutas físicas de vuelo de rutas de comunicación; dar valor a lo que se observa; usar una alerta de pérdida de reporte como incertidumbre, no asumir causa; considerar polígonos de cobertura para misiones de reconocimiento; construir algo realizable en el curso y dejar extensiones como trabajo futuro.

**Decisión tomada por el grupo en Codex:** “Reconocimiento de una zona” para cubrir un polígono de observación, tomando como candidato el paper de Luna et al. (2024) para replanificación por pérdida de UAV; CLUN-LSR queda como antecedente conceptual de comunicaciones.

**Evolución posterior del diálogo con ChatGPT:** para controlar complejidad y cumplir la Tarea 2 se discutió un único grafo de **puntos/segmentos físicos**, una localidad **urbana de referencia (Mykolaiv)**, condiciones de conectividad como atributo simplificado y un ejemplo **origen–destino** con Dijkstra y Yen. **No hay confirmación documentada de que el profesor haya aprobado abandonar la cobertura de área en favor de solo llegar a B.**

**Decisión de diseño recomendada para Codex (no fijar sin aprobación):** construir **un único grafo de navegación** y representar un polígono de misión con puntos de observación. Para la rúbrica, seleccionar pares **inicio–punto de observación** y ejecutar las comparaciones sobre los **mismos** puntos y escenarios. Como extensión, medir cobertura lograda/reporte de observaciones durante rutas consecutivas. El MVP debe cumplir origen–destino sin prometer resolver el problema completo de cobertura multi-UAV.

**Advertencia operacional:** la zona de guerra solo proporciona contexto histórico, humano y científico. Los puntos de navegación, eventos de indisponibilidad y rutas evaluadas deben ser sintéticos o abstractos; no construir un plan de reconocimiento militar real, optimización ofensiva, evasión de defensas o explotación de interferencias actuales. Centrarse en inspección territorial/civil o simulación no operativa.

## V3.4. Alternativas exploradas y por qué no se adoptaron

| Alternativa discutida | Estado / aprendizaje |
|---|---|
| CLUN-LSR tal cual en red mesh | Base científica original; no resuelve rutas físicas exigidas por enfoque posterior |
| Extender CLUN-LSR con edificios y DEM | Cambia y complica la evaluación RF; exige 3D/movilidad y no responde por sí solo a la necesidad de misión |
| San Bernardo, Chile: seguridad logística | Existieron reportes sobre inhibidores, pero no evidencian una FANET cooperativa allí |
| Cárceles chilenas: contrabando | Inhibidores usados por autoridades contra drones intrusos; fenómeno distinto de red propia bajo jamming |
| Reino Unido: ensayo de 20 drones | Documenta cooperación; requisitos de mesh resistente a interferencia; la prueba pública no confirma jamming concreto |
| México: actividad criminal y anti-UAV | Contexto explorado; no se encontró operación específica con red mesh, falla medida y recuperación |
| Sumy rural/fronteriza | Contexto discutido; menor riqueza urbana y riesgos de confusión con trayectorias militares actuales |
| Mykolaiv urbana, Ucrania | **Candidata actual**, por interés de infraestructura civil y datos geográficos; sin validación ETL local todavía |
| Dos grafos (vuelo + mesh) | Mayor fidelidad, mayor complejidad; descartado para MVP |
| Un solo grafo físico + enlaces como restricción | **Propuesta de MVP**, pendiente de validar modelo simplificado y definición de métrica |

## V3.5. Estado del repositorio reportado por la conversación exportada

La conversación con Codex expone pasos de reorganización de carpeta y documentación; **la captura de VS Code y el historial no equivalen a inspección de archivos vigente**. Verificar in situ:

- Existe `AlgoritmosRuteo/` y las carpetas `01_PROYECTO_ACTUAL`, `02_REUNION_PROFESOR`, `03_TAREA_1`, `04_VALIDACION_TAREA_1`; nombres y rutas reales deben comprobarse.
- En la validación figuran `run_all.py`, `docker-compose.yml`, `common.py`, `01_opensky.py` a `07_openaip.py`, `08_postgis_poligonos.sql`, `import_geojson_to_postgis.py`, scripts de evidencia y README.
- Codex **reportó**: README principal revisado, `03_TAREA_1/README.md`, `04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md`, ajustes en `.gitignore`, dos secretos hardcodeados retirados de scripts, figura LaTeX reparada, y exclusión de claves, datos crudos, virtualenv y ZIP de Git.
- Codex **reportó** comprobación de **48 archivos candidatos de Git (1,71 MB)**, **61 enlaces locales**, sintaxis Python/JSON sin incidencias en ese momento; **rama `main` sin commit y sin remoto configurado**. Verificar de nuevo, sin copiar secretos a logs.
- Historial e informe inicial deben preservarse como legado: no mezclar evidencias de Chile con validación Mykolaiv.
- El historial no demuestra que existan ya red UAV 3D, rutas físicas, k-rutas, estimaciones de conectividad real, evaluación de resiliencia, sitio Leaflet operativo para tarea 2 ni pipeline completo; todos deben auditarse.

**Riesgo de versiones:** el historial menciona `.tex` como `PRIMERA_ITERACION`, `FINAL_VALIDADO` y `corregido`. Determinar cuál es el artefacto vigente; mantener versiones históricas con etiquetas. El ZIP o Markdown v2 pueden estar duplicados en el repo; no sobrescribirlos silenciosamente.

## V3.6. Diseño técnico mínimo coherente con Tarea 2

### Grafo único físico

- **Nodos:** posiciones hipotéticas de navegación y puntos de inspección georreferenciados con elevación/altitud de escenario.
- **Aristas:** segmentos geométricos de desplazamiento potencial; usar distancia en kilómetros como costo de referencia.
- **Peso enriquecido:** función documentada de distancia y restricciones de escena, nunca inferida directamente de “hubo conflicto” o “hay edificio”. Mantener costo no negativo cuando el algoritmo lo requiera.
- **Zonas/polígonos:** polígono de estudio, edificaciones, uso de suelo y áreas de eventos; distinguir intersección geográfica de bloqueo real de vuelo.
- **Tiempo:** ETL histórico por fecha y escenarios de falla por intervalo; si se utiliza un grafo estático para cada ensayo, declararlo como instantánea de navegación y no afirmar una FANET dinámica.

### Fuentes candidatas y verificaciones (NO validación automática)

| Componente | Fuente candidata | Papel | Verificación pendiente |
|---|---|---|---|
| Infraestructura base | OSM / Overpass | Polígono, edificios/uso de suelo y cartografía | Descarga urbana, geometrías válidas, cobertura y licencia |
| Terreno | OpenTopography | DEM/elevación | Resolución y cobertura de polígono elegido |
| Edificios | OSM | Polígonos, alturas si existen | % de edificios con alturas/niveles; no asumir 3D preciso |
| Clima | OpenWeather u Open-Meteo histórico | Viento, ráfagas, tiempo | Alinear fechas y reconocer resolución/modelado |
| Eventos históricos | ACLED | Contexto de conflicto; **NO** falla de arista automática | Acceso, precisión espacial, registros periodo/área |
| Navegación degradada | GPSJam | Contexto de señales GNSS; **NO** mide enlaces RF UAV | Cobertura real en Ucrania y validez temporal |
| Anomalías/incendios | NASA FIRMS | Observaciones ambientales | Eventos reales y falsos positivos posibles |
| Espacio aéreo | OpenAIP (histórica T1) | Fuente a reevaluar; no permisos de vuelo | Utilidad limitada en espacio aéreo civil cerrado |
| Movilidad aérea | OpenSky (histórica T1) | **NO** fuente de rutas UAV de baja altura | Eliminar del grafo físico, preservar como histórico |

**Comprobación de independencia de fuentes para rúbrica:** si utilizan OSM tanto en infraestructura como metadata, una misma API no debe contarse como *dos bases diferentes* dentro de n-metadata. Clima “normal” y viento “amenaza” de la misma API tampoco son dos fuentes distintas dentro de una misma categoría. Contar **n servicios/bases independientes por categoría** de manera conservadora y obtener confirmación docente si hay duda.

### Algoritmos y evaluación

1. **Base Dijkstra:** generar al menos **dos rutas distintas** entre el mismo origen y destino a través de `pgr_dijkstra`; documentar procedimiento para la segunda (p. ej., consulta con exclusión controlada). Las aristas disponibles solo usan **longitud en km** para el costo; no incorporar metadata/amenazas a la baseline.
2. **Alternativa documentada:** Yen mediante `pgr_KSP` como candidato operativo en PostgreSQL; fundamentar con el paper original; explicar el paso de generación de rutas y el **criterio propio de selección resiliente**.
3. **Equidad:** igual origen/destino, grafo base, k, conjunto de eventos de falla y presupuesto de rutas para ambas alternativas; documentar cómo se penalizan o excluyen aristas, para evitar ventaja tautológica del algoritmo propuesto.
4. **Métrica primaria:** fracción de escenarios donde al menos una de las k rutas permanece disponible, `R = válidos / total`. Métricas complementarias: desvío en distancia; cobertura de puntos de inspección (si se incluye misión de polígono); tiempo computacional; sensibilidad a número y ubicación abstracta de fallas.
5. **Límite científico:** Yen no garantiza mayor resiliencia; el resultado puede ser nulo o negativo. No falsificar mejoras; presentar también contraejemplos.
6. **Si se elige cobertura:** la tarea completa implica visitar múltiples puntos y medir cobertura; **no confundir k rutas A→B con Coverage Path Planning**. Restringir MVP y documentar futuro desarrollo.

### Tarea 2: checklist exigido

- Docker Compose con PostgreSQL, PostGIS y pgRouting; SQL reproducible + diagrama.
- Scripts de extracción/transformación de infraestructura a JSON/GeoJSON y carga a DB.
- **Tres fuentes independientes de metadata y tres de amenazas** (según equipo de 3): cada una con extractor, JSON, documentación de campos y cargador.
- Modelo de fallas y asignación de pesos a nodos/aristas; conversión de metadata en restricciones; defaults de usuario.
- Algoritmo fundamentado en paper, documentado e implementado.
- Dos rutas `pgr_dijkstra` por distancia y dos rutas con el algoritmo propuesto; diferencial de resiliencia.
- Plataforma Leaflet que reciba inicio, destino y restricciones y muestre rutas, capas y comparativa.
- `main` de automatización: ETL → DB → preparación ruteo → plataforma, ejecutado dentro de Docker.
- Verificar contradicción interna: texto de fase 2 difiere de rúbrica sobre peso de amenazas; **cubrir rúbrica completa** y confirmar con profesor.

## V3.7. Hallazgos que podrían invalidar la propuesta y deben detectarse temprano

- Las 3 fuentes de amenaza no ofrecen registros reales para el mismo sector/fecha, o su localización es demasiado imprecisa.
- Las alturas de edificios faltan y se hace una afirmación 3D no sustentada.
- No existen dos rutas alternativas en el grafo generado entre los pares de prueba.
- La comparación mezcla cobertura por área con rutas A–B sin definición común de misión.
- La fórmula de resiliencia mide solo redundancia geométrica que fue impuesta por construcción, sin amenazas independientes ni validación.
- Se confunde interferencia GNSS con interferencia del enlace de control/datos.
- El escenario urbano de guerra se presenta como rutas reales desplegadas o recomendables, cuando son simulaciones.

## V3.8. Preguntas bloqueantes para el grupo o profesor

1. ¿El MVP de Tarea 2 debe evaluar **origen–destino**, o la cobertura completa del **polígono**, o ambos por etapas?
2. ¿Se acepta una **malla sintética de navegación** derivada de geografía pública como infraestructura extraída/transformada, siempre que se explique su construcción y las aristas?
3. ¿Se aceptan eventos reales como capas de contexto y fallas de arista **sintéticas** como ensayos, sin equivaler ACLED/GPSJam directamente a enlaces bloqueados?
4. ¿Qué nivel de aporte algorítmico espera el ayudante: aplicación fundamentada de Yen + criterio de resiliencia, modificación original, o una replanificación de cobertura más novedosa?
5. ¿Con qué precisión espera el docente tratamiento de altitud y obstáculos en un sistema de vuelo simulado?
6. ¿Está aprobada la región urbana candidata y puede sustituirse si faltan datos de amenazas válidos?

## V3.9. Orden estricto de trabajo de Codex

**Fase 0 — solo lectura y auditoría.** Confirmar `git status`, branch/remoto, raíz, rutas históricas, README/AGENTS, secretos sin mostrarlos, scripts existentes, estado del SQL y rúbrica. Comparar este V3 contra los archivos y reportar discrepancias.

**Fase 1 — factibilidad de un escenario no operativo.** Definir un polígono de prueba abstracto basado en cartografía urbana; ejecutar extracción limitada con permisos y almacenar evidencia de estado/fecha/cobertura por fuente. No generar rutas de misión militar real.

**Fase 2 — modelo y ETL.** Diseño PostGIS/pgRouting, nodos y aristas espaciales, tres metadata y tres amenazas verificadas, JSON + esquemas/READMEs + cargadores; scripts reutilizados siempre que sea razonable.

**Fase 3 — algoritmos.** Baseline Dijkstra, candidatos Yen, regla de selección, escenarios de falla, métricas y comparativas reproducibles con semillas fijas.

**Fase 4 — app.** Leaflet, selector inicio/destino, restricciones/defaults, rutas y diferencial; Docker Compose + `main` sin dependencias ocultas.

**Fase 5 — validación e informe.** Tests, gráficas, matriz de 60 puntos, citas/limitaciones, documentación y presentación.

**No codificar todo de golpe.** Al terminar Fase 0 detenerse y entregar diagnóstico con evidencia; esperar aprobación antes de rediseñar infraestructura y migrar fuentes.

## V3.10. Fuentes y archivos prioritarios disponibles

- `ENUNCIADO_Y_RUBRICA_TAREA_2.txt` — fuente normativa para implementación (leer desde repo actual).
- `Charla_profesor.txt` — orientación para acotar misión y diferenciar rutas de paquetes y trayectorias físicas.
- `Informe_Ruteo_APO_DPC_AML_corregido(1).tex` y `PROPUESTA · EXTENSIÓN CLUN-LSR.pdf` — descripción de Tarea 1 (el repo puede contener nombres/versiones distintos).
- `Texto pegado(3).txt` — historial exportado de Codex, incluidas observaciones del ayudante, alternativas, decisiones y preparación del repositorio.
- `CONTEXTO_INTEGRAL_CODEX_RUTEO_UAV_2026_V2.md` — síntesis previa, que ahora se complementa y en partes se sustituye por V3.
- Zheng et al., *Cross-layer UAV network routing protocol for spectrum denial environments*, **Ad Hoc Networks**. [Acceso](https://www.sciencedirect.com/science/article/pii/S1570870524003135) — rutas de comunicaciones, no trayectorias físicas.
- Luna et al., *A multi-UAV system for coverage path planning applications with in-flight re-planning capabilities*, **Journal of Field Robotics**. [DOI](https://doi.org/10.1002/rob.22342) — cobertura y replanificación; no jamming probado.
- Yen, *Finding the K Shortest Loopless Paths in a Network*. [DOI](https://doi.org/10.1287/mnsc.17.11.712) — generación de k rutas simples.
- pgRouting [documentación](https://docs.pgrouting.org/latest/en/); PostGIS [documentación](https://postgis.net/documentation/); OSM/Overpass [wiki](https://wiki.openstreetmap.org/wiki/Overpass_API), OpenTopography [web](https://opentopography.org/), ACLED [web](https://acleddata.com/), FIRMS [web](https://firms.modaps.eosdis.nasa.gov/).

**Nota de citación:** verificar las versiones exactas, disponibilidad y fecha de las fuentes externas al momento de escribir el informe. Este historial transcrito incluye respuestas de asistentes; **no reemplaza artículos originales ni nuevas pruebas de API**.

---

# Archivo V2 conservado como antecedente y especificación técnica secundaria

# Documento maestro para Codex — Proyecto de Ruteo Resiliente UAV (UDP, 2026-2)

> **Tipo:** contexto de proyecto, decisiones de alcance, requisitos académicos y guía de ejecución.
> **Actualizado:** 18 de octubre de 2026 (v2: estructura observada del repositorio en VS Code).
> **Destinatario:** Codex trabajando en el repositorio del grupo.
> **Estado:** repositorio existente con material de tarea 1 y validación; propuesta reformulada; **NO** asumir que el proyecto de la tarea 2 ya existe o que las fuentes están validadas para Ucrania.
> **Idioma del trabajo:** español.

## 0. Instrucciones inmediatas para Codex

**Lee este documento íntegramente y localiza primero los documentos originales ya presentes en el repositorio antes de modificar código.** Trata los archivos originales como evidencia del trabajo entregado, y este documento como el registro de decisiones y la propuesta actual. Si alguna decisión no está cerrada, consúltala o regístrala como pendiente; no inventes resultados ni asumas que una API tiene datos solo porque responde HTTP 200.

### Tu primera misión

1. Inspecciona el repositorio: estructura, scripts existentes, pruebas, Docker, credenciales esperadas, SQL, resultados y archivos de evidencia. **No borres ni reemplaces el trabajo de la tarea 1.**
2. Genera un diagnóstico de brechas entre el estado real del repositorio y la rúbrica de la tarea 2, con una matriz **requisito → archivo existente → estado → evidencia → tarea pendiente**.
3. Propón un plan incremental y pide aprobación **antes** de cambios conceptuales irreversibles, como eliminar CLUN-LSR de la documentación, sustituir fuentes o redefinir el grafo.
4. Implementa primero una prueba de factibilidad reproducible, sin afirmar que representa aeronaves o rutas operacionales reales.
5. Trabaja con cambios pequeños y verificables: código, pruebas, documentación, comandos de ejecución y evidencia real. No falsifiques salidas, pruebas, cantidades ni resultados experimentales.
6. Mantén separadas tres etiquetas de procedencia: `OBSERVADO`, `MODELADO` y `SINTETICO` (además de `NO_VALIDADO` cuando corresponda).
7. No publiques secretos ni claves; utiliza variables de entorno, `.env.example`, permisos mínimos y exclusión de `.env` del control de versiones.

### Límites de uso y carácter de la investigación

La guerra Rusia-Ucrania **motiva el problema histórico y científico**. La implementación será una **plataforma académica de planificación de rutas geográficas sintéticas para inspección territorial no ofensiva**, con mapa público, datos históricos y fallas artificiales declaradas. No se construirán herramientas de selección de objetivos militares, planificación de ataques, evasión de defensa antiaérea, detección de posiciones militares actuales, rutas para infiltración o explotación operacional de zonas de guerra. No asumir permisos de vuelo en el espacio aéreo ucraniano. Para demostrar el algoritmo en el mapa se pueden usar **geometrías abstraídas o un sector de prueba ficticio basado en características urbanas generales**, no una trayectoria lista para operar en la guerra actual.

---

## 0.A. ACTUALIZACIÓN CRÍTICA — Codex YA CONOCE EL REPOSITORIO EXISTENTE (18-10-2026)

> **Esta sección actualiza y tiene precedencia sobre cualquier instrucción genérica de crear un repositorio nuevo.** El usuario confirmó que Codex ya tiene contexto histórico, acceso al repositorio y archivos de las tareas. Este documento NO es una solicitud de iniciar de cero; es una **actualización de objetivos y alcance sobre una base existente**.
>
> **Límite de evidencia:** el árbol siguiente se reconstruyó **solo de tres capturas del explorador de VS Code**, no de una inspección directa del contenido de los archivos ni del historial Git. Los nombres truncados, implementaciones reales, versiones, pruebas exitosas, permisos y rutas absolutas deben verificarse en el repositorio.

### 0.A.1 Árbol del proyecto observado en las capturas

```text
AlgoritmosRuteo/                         # workspace mostrado en VS Code
├── .vscode/
├── 01_PROYECTO_ACTUAL/
│   ├── CONTEXTO_PARA_EL_GRUPO_TAR...   # nombre truncado en imagen
│   ├── ENFOQUE_TRAS_CHARLA_PROFES...    # nombre truncado
│   ├── ENUNCIADO_Y_RUBRICA_TAREA_2...  # verificar extensión
│   └── RESUMEN_PROYECTO_Y_TAREA_2...   # nombre truncado
├── 02_REUNION_PROFESOR/
│   ├── Charla_profesor.mp4
│   ├── Charla_profesor.txt
│   └── GUION_CONSULTA_PROFESOR_TA...   # nombre truncado
├── 03_TAREA_1/
│   ├── informes/
│   │   ├── Informe_Ruteo_APO_DPC_AML_c... .tex  # nombre truncado
│   │   └── Informe_Ruteo_APO_DPC_AML-1...pdf  # nombre truncado
│   ├── pruebas_iniciales/
│   │   ├── main.py
│   │   ├── mapa_terreno.png
│   │   ├── OpenWeather.py
│   │   ├── requirements.txt
│   │   ├── SpectrumITU.py
│   │   ├── terreno.py
│   │   └── terreno.tif
│   └── referencias/                 # paper(s) y otros materiales
├── 04_VALIDACION_TAREA_1/
│   ├── validacion_ruteo/
│   │   ├── .codex/
│   │   ├── [directorio de credenciales: nombre por verificar]
│   │   ├── evidencia/
│   │   ├── sql/
│   │   ├── .env                      # SENSIBLE
│   │   ├── .env.example
│   │   ├── 01_opensky.py
│   │   ├── 02_opentopography.py
│   │   ├── 03_openweather.py
│   │   ├── 04_opencellid.py
│   │   ├── 04b_osm_buildings_fallback.py
│   │   ├── 05_gpsjam.py
│   │   ├── 06_acled.py
│   │   ├── 07_openaip.py
│   │   ├── 08_postgis_poligonos.sql
│   │   ├── common.py
│   │   ├── credentials.json          # POTENCIALMENTE SENSIBLE
│   │   ├── docker-compose.yml
│   │   ├── import_geojson_to_postgis.py
│   │   ├── postgres_evidence.py
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── run_all.py
│   │   ├── Ruteo_UAV_APIs.postman_collec... # nombre truncado
│   │   ├── VALIDACION_COMPLETA.md
│   │   ├── VALIDACION_Y_CORRECCIONES... # nombre truncado
│   │   └── REPRODUCIBILIDAD_Y_DATOS.md
│   ├── validacion_ruteo_uav.zip
│   └── [otros documentos, verificar]
├── .gitignore
├── CONTEXTO_PROYECTO_CODEX.md
├── README.md
└── [PDF de Journal of Field Robotics, nombre por verificar]
```

**Precisión:** que un archivo aparezca en VS Code significa que está en el árbol mostrado; **no** prueba que el script funcione hoy, que esté versionado, que la API tenga credenciales vigentes ni que exista una tabla cargada.

### 0.A.2 Cómo interpretar el nuevo contexto

1. **No asumir repositorio vacío ni crear uno nuevo.** Iniciar en `AlgoritmosRuteo/` y reconocer su raíz Git real mediante `git rev-parse --show-toplevel`. Si hay más de un `.git`, informar antes de decidir en cuál trabajar.
2. **No pedir al usuario que vuelva a cargar documentos ya presentes.** Primero localizar y leer las versiones existentes en `01_PROYECTO_ACTUAL`, `02_REUNION_PROFESOR`, `03_TAREA_1`, `04_VALIDACION_TAREA_1` y `CONTEXTO_PROYECTO_CODEX.md`. Si un archivo no existe de verdad, marcarlo como no encontrado.
3. **Comprobar el contexto de Codex ya disponible.** Revisar `AGENTS.md` donde corresponda y los documentos/instrucciones existentes de la carpeta `.codex` antes de proponer nueva organización. No duplicar políticas ni sobrescribir trabajo de otros agentes.
4. **No crear `01_...`, `02_...`, etc. otra vez.** Mantener las carpetas de la tarea 1 como registro histórico. Proponer un área claramente aislada para la tarea 2 (por ejemplo `05_TAREA_2/`, **solo si el usuario aprueba el nombre**), usando módulos existentes cuando sea razonable. No mover todo el repositorio por estética.
5. **Inspeccionar antes de reescribir:** `run_all.py`, `common.py`, `docker-compose.yml`, SQL, scripts de importación, los ocho extractores, evidencia, `.env.example`, README y documentos de reproducibilidad. Clasificar cada componente como `REUTILIZABLE`, `ADAPTABLE`, `SOLO_HISTÓRICO`, `NO_VALIDADO` o `REEMPLAZABLE`.
6. **No inventar nombres ni rutas truncados.** Confirmarlos con `find`, `rg --files` u operaciones de listado equivalentes. Este documento no acredita la existencia de `docs/`, `AGENTS.md` ni `05_TAREA_2/`.
7. **No tocar credenciales por defecto.** Comprobar el estado de seguimiento de `.env` y `credentials.json` usando `git ls-files` sin abrir, imprimir, copiar o subir sus contenidos. Mantenerlos fuera de salidas de diagnóstico, adjuntos, capturas, prompts y commits; recomendar revocación/rotación si se confirma exposición en Git. Inspeccionar primero `.gitignore` y evitar cargar secretos en logs.
8. **No ejecutar APIs, `run_all.py`, contenedores o scripts que escriban datos automáticamente antes de revisar sus efectos.** Para la auditoría, inspección estática y comprobaciones de bajo impacto primero; las pruebas con red, credenciales, volúmenes o cambios persistentes requieren un plan explícito.
9. **Conservar originales**: informe `.tex`, PDF, presentación y evidencias de la primera entrega. Producir revisiones nuevas; nunca alterar retroactivamente lo que se entregó.
10. **Diferenciar lo que Codex recuerda de lo que el repositorio acredita.** Toda afirmación de prueba o resultado debe incluir comando ejecutado, archivo fuente o salida verificable del repo, y fecha de la verificación.

### 0.A.3 Reutilización: mapa inicial de archivos a funciones

| Archivo o grupo presente en capturas | Función probable a confirmar | Trabajo recomendado |
|---|---|---|
| `01_opensky.py` | Extracción de estados aeronáuticos | Conservar como evidencia tarea 1; **no** usar como fuente de waypoints del grafo físico. |
| `02_opentopography.py` | Descarga de DEM | Adaptar consultas/CRS/cobertura a escenario de referencia. |
| `03_openweather.py` | Meteorología | Adaptar localidad y temporalidad; evaluar reproducibilidad histórica. |
| `04_opencellid.py` | Datos celulares | Mantener opcional; no convertir en calidad RF demostrada. |
| `04b_osm_buildings_fallback.py` | Polígonos OSM | Reutilizar para caracterización urbana; validar geometría y atributos. |
| `05_gpsjam.py` | Indicadores GNSS | Evaluar pertinencia y cobertura; **no** equiparar a jamming del enlace de datos. |
| `06_acled.py` | Eventos geolocalizados | Conservar como fuente histórica/contextual, no como prueba de cierre de vuelo. |
| `07_openaip.py` | Zonas aeronáuticas | Auditar; cobertura/pertinencia para Ucrania pendiente. |
| `08_postgis_poligonos.sql`, `sql/` | SQL geoespacial | Revisar esquema, migraciones, geometrías y reutilización. |
| `import_geojson_to_postgis.py` | Carga de GeoJSON | Adaptar de manera idempotente, con validación de SRID y origen. |
| `common.py` | Código común | Reutilizar autenticación, peticiones, normalización o configuración, solo tras leerlo. |
| `run_all.py` | Orquestación de validación | **No reemplazarlo** sin entender entradas/salidas y dependencias. Integrarlo o mantenerlo como pipeline de tarea 1. |
| `docker-compose.yml` | Infraestructura de contenedores | Verificar servicios, volúmenes e imágenes; ampliar a pgRouting si hace falta. |
| `postgres_evidence.py`, `evidencia/` | Validaciones anteriores | Conservar como evidencia histórica; no mezclar con resultados nuevos. |
| `VALIDACION_COMPLETA.md`, `REPRODUCIBILIDAD_Y_DATOS.md` | Estado y metodología previos | Leer antes de concluir qué APIs ya funcionan o qué falta. |
| `CONTEXTO_PROYECTO_CODEX.md` y documentos de `01_PROYECTO_ACTUAL` | Decisiones y contexto previo | Comparar con este documento; registrar conflictos en una tabla, no resolverlos silenciosamente. |
| `pruebas_iniciales/` | Prototipos y experimentos anteriores | Conservar; extraer pruebas o métodos útiles, sin tratarlos como app productiva. |

Esta tabla es una **hipótesis de reutilización basada en nombres de archivos**, no una auditoría funcional. Codex debe confirmar cada función leyendo el código.

### 0.A.4 Regla de precedencia y decisiones

- **Requisitos obligatorios del curso:** archivos originales de enunciado y rúbrica tienen precedencia sobre ejemplos de estructura y deseos de implementación.
- **Estado técnico:** el código, pruebas y artefactos realmente presentes en Git prevalecen sobre afirmaciones no verificadas del contexto previo.
- **Historia:** tarea 1 y conversación con profesor explican el punto de partida y motivación; no se deben reescribir como si ya correspondieran a la nueva propuesta.
- **Propuesta actual:** este documento define la dirección preferida (grafo físico único, evaluación no ofensiva), pero **la migración conceptual, el algoritmo final y la región quedan sometidos a aprobación y pruebas de factibilidad**.
- Cuando haya desacuerdos entre `CONTEXTO_PROYECTO_CODEX.md`, archivos de `01_PROYECTO_ACTUAL`, este documento y el código, crear **registro de contradicciones** con evidencia y proponer resolución; no decidir sin consultar cuando altere el alcance.

### 0.A.5 Fase 0 revisada: trabajo de Codex, no reimplementación

Primero entregar **solo un informe de auditoría**, sin reestructurar el repositorio ni implementar la tarea 2:

1. Árbol real del proyecto y ubicación de raíz Git; `git status` y rama activa, sin incluir secretos.
2. Inventario de scripts, SQL, contenedores, evidencias, documentación y funcionalidades **probadas / no probadas**.
3. **Matriz de reutilización** `archivo actual → componente tarea 2 → cambio requerido → pruebas necesarias → riesgo`.
4. **Matriz rúbrica 60 puntos** `criterio → evidencia actual → brecha → artefacto objetivo → validación`.
5. **Mapa de fuentes**: cuáles se probaron para Chile, cuáles requieren consulta nueva para Ucrania y cuáles son opcionales o no equivalentes.
6. Propuesta de ubicación de nuevos archivos sin alterar tarea 1, reutilizando estructura Git y herramientas existentes.
7. Riesgos de seguridad (solo nombres de rutas/estado de seguimiento, nunca valores de secretos), dependencias, Docker, datos y acceso a servicios.
8. Decisiones para aprobación: grafo físico vs mesh original; región/caso de estudio; Yen como candidato vs alternativa; fuentes de amenazas; organización de tarea 2.
9. **No dar por completadas** extracción, importación, `docker compose` ni validación de API solo porque los nombres aparecen en VS Code.

**Entregable al usuario tras la fase 0:** resumen de diagnóstico y plan priorizado, con referencias a archivos existentes y comandos de verificación, **antes de ejecutar cambios de implementación**.

---

## 1. Contexto del curso y de los archivos originales

Universidad Diego Portales (UDP), curso universitario de ruteo resiliente. Trabajo grupal en dos entregas principales documentadas y referencia posterior a una posible fase 3.

**Documentos originales: deben localizarse preferentemente en el repositorio (y también pueden acompañar este paquete):**

1. `Informe_Ruteo_APO_DPC_AML_corregido(1).tex` — informe de la primera entrega, formato IEEEtran; fuente de mayor detalle sobre objetivos iniciales, experimentos, API, resultados y limitaciones.
2. `PROPUESTA · EXTENSIÓN CLUN-LSR.pdf` — presentación de 15 páginas entregada para la primera fase.
3. `ENUNCIADO_Y_RUBRICA_TAREA_2.txt` — requisitos técnicos y rúbrica de la segunda entrega, 60 puntos.
4. `Charla_profesor.txt` — transcripción automática de una conversación de orientación con el profesor; puede contener errores de reconocimiento de voz, por lo que debe interpretarse conceptualmente y no tratarse como cita literal perfecta.

**Integrantes según el documento original:** tres. Esto implica **al menos tres fuentes independientes de metadata y tres fuentes independientes de eventos/amenazas**, conforme a la regla `n = cantidad de integrantes`. No contar PostgreSQL/PostGIS como API de origen de datos; es el almacenamiento. Un endpoint y un conjunto de datos del mismo proveedor no se cuentan automáticamente como dos fuentes independientes.

**Punto crítico:** la tarea 1 definía nodos = UAV y aristas = enlaces de comunicación. La versión actualmente preferida es **nodos = posiciones de navegación y aristas = segmentos físicos hipotéticos**, lo que exige una corrección explícita del planteamiento inicial. No afirmar que el informe original ya describe el nuevo grafo.

---

## 2. Qué se presentó y probó en la tarea 1

### 2.1 Problema y solución original

**Título del informe:** “Ruteo Resiliente en Redes UAV bajo Denegación de Espectro: Propuesta de Evaluación con Información Geoespacial Real”.

- Antecedente: *Cross-layer UAV network routing protocol for spectrum denial environments* (Zheng et al., *Ad Hoc Networks*, vol. 167, art. 103702, 2025; DOI `10.1016/j.adhoc.2024.103702`).
- CLUN-LSR: protocolo de **ruteo de paquetes** en redes UAV bajo jamming. Usa información espectral de la capa de enlace y decisiones de la capa de red; el artículo utiliza MP-OLSR como plataforma de referencia en simulación EXata.
- Hipótesis de la tarea 1: enriquecer escenarios idealizados con relieve, edificios, clima y amenazas geolocalizadas permitiría estudiar ruteo resiliente bajo condiciones menos simplificadas.
- Grafo original `G=(V,E,W)`: `V=UAV`, `E=enlaces RF candidatos`, `W=costos de transmisión`.
- **No se había implementado una reproducción completa de CLUN-LSR** ni una función final de pesos; la primera entrega verificó factibilidad inicial de fuentes y almacenamiento espacial.

### 2.2 Evidencia declarada en el informe/PPT (no reproducida en esta conversación)

| Fuente | Papel original | Resultado histórico declarado | Precaución |
|---|---|---|---|
| OpenSky Network | Posiciones/trazas sustitutas de aeronaves | OAuth2 y consulta HTTP 200; BBOX Santiago sin posiciones útiles; fallback global **7.635** posiciones | No son UAV militares ni topología de enlaces; no usar para crear directamente el nuevo grafo físico. |
| OpenTopography | DEM / relieve | Malla **360 × 360**, elevación **440–1.881 m** en sector de Santiago | La cobertura de Ucrania debe consultarse de nuevo. |
| OpenWeather | Meteorología actual | Santiago: aprox. **13,41 °C**, viento **2,57 m/s**, humedad **66 %**, visibilidad **10.000 m**, nubosidad **98 %** | Una lectura aislada no es serie histórica ni prueba de variabilidad espacial urbana. |
| OSM / Overpass | Polígonos de edificaciones | **236.791** polígonos exportados en ensayo chileno | Validar cantidad, geometría y atributos de alturas para nuevo contexto. |
| OpenCellID | Infraestructura celular adicional | **2.333** celdas indicadas, **50** descargadas | Densidad celular no demuestra cobertura real de UAV. Opcional, no esencial. |
| GPSJam | Celdas H3 de baja precisión GNSS | **48.781** celdas globales; **509** con `percent_bad > 10 %` | No equivale a interferencia del enlace de datos de UAV. |
| ACLED | Eventos georreferenciados de conflicto | **235** registros históricos en fallback; consulta de Ucrania 2026 parcial | La ubicación reportada no es necesariamente exacta; no extrapolar radios de riesgo como hechos. |
| OpenAIP | Restricciones del espacio aéreo | **36** áreas en Chile, **27** Restricted/Danger/Prohibited | No demuestra aplicabilidad al espacio aéreo ucraniano. |
| PostgreSQL + PostGIS | Repositorio geoespacial | PostGIS 3.4, cuatro tablas, SRID 4326, `ST_Intersects` probado | Debe reproducirse automáticamente dentro de Docker en la tarea 2. |

Tablas reportadas en el informe original: `airspaces` (27 Polygon), `gpsjam_zones` (48.781 Polygon/MultiPolygon), `osm_buildings` (236.791 Polygon), `acled_events` (235 Point). Son **evidencias de la tarea 1**, NO registros que deban aparecer como datos de Mykolaiv ni garantía de que existan esos archivos en el repositorio.

Referencias a scripts históricos: `01_opensky.py`, `02_opentopography.py` y posiblemente otros generadores de evidencia. **Codex deberá descubrir los nombres reales de archivos y sus rutas**, en lugar de inventarlos. En el TEX hay referencias a `../pruebas_iniciales/mapa_terreno.png` y a artefactos `evidencia/...`; comprobar si están en Git.

### 2.3 Qué permanece y qué cambia

**Permanece:** Python/ETL, uso de información pública geoespacial, GeoJSON, PostGIS, OSM/Overpass, DEM, meteorología, análisis de eventos, visualización y comparación de algoritmos.

**Cambia:** problema principal de **conectividad de paquetes entre UAV** a **rutas físicas de navegación simulada**; los nodos dejan de ser drones; OpenSky deja de ser fuente de infraestructura del grafo; CLUN-LSR pasa de protocolo central a antecedente de comunicaciones degradadas.

**No confundir:** actualizar una arista de navegación no es lo mismo que conmutar un enlace RF. Los datos de GPSJam tampoco equivalen a detectar un jammer contra el canal de telemetría.

---

## 3. Qué sugirió el profesor y cómo evolucionó la idea

### 3.1 Lectura de `Charla_profesor.txt`

La transcripción muestra que el profesor buscaba:

- Un **caso de uso real y específico**; no limitar el trabajo a “cambiar de ruta porque falla un protocolo”.
- Justificar **por qué los UAV necesitan ir de un origen a un destino o inspeccionar sectores**.
- Aclarar la distinción entre **ruta de comunicaciones** y **ruta física de vuelo**.
- Considerar cómo un evento inesperado cambia la ruta y cómo esa modificación se relaciona con **resiliencia**.
- Aprovechar lo hecho en la tarea 1, respaldar la propuesta en un paper y dejar las extensiones complejas para trabajo futuro.
- Reconocer que en reconocimiento de cobertura de área importa la **superficie observada**, no solamente llegar a un punto. Pero, para la tarea 2, el requisito de par origen-destino recomienda acotar la prueba inicial.
- No exigir vuelos reales: los drones físicos disponibles en el curso pueden utilizarse a futuro, pero **no figuran como requisito de la rúbrica**.

La charla también incluye ejemplos de operaciones ofensivas y defensas militares, usados como analogías durante el brainstorming. **No son el alcance implementable** de la propuesta actual y no deben transformarse en instrucciones de ataque o evasión.

### 3.2 Evolución de alternativas discutidas

1. Extender directamente CLUN-LSR y su tratamiento del jamming: **demasiado rígido y complejo** para esta entrega.
2. Estudiar una FANET mesh donde caen nodos y se recuperan rutas de paquetes: viable, pero la rúbrica pide rutas geográficas entre origen y destino y distancia en km.
3. Diseñar **dos grafos**, uno de vuelo y otro de comunicaciones, con replanificación multi-UAV: interesante como investigación, pero **demasiado amplio** para el curso.
4. Construir **un solo grafo físico** de navegación, con restricciones ambientales/geoespaciales y **comunicación degradada como atributo simplificado**: **opción actualmente preferida**.
5. Misiones consideradas: inspección humanitaria de minas; evaluación de daños a infraestructura civil; monitoreo ambiental; vigilancia defensiva. Se descartó incluir detección de minas como capacidad, porque requeriría sensores especializados y validación adicional.
6. Zona rural de Sumy vs. entorno urbano: se prefirió **Mykolaiv urbana**, debido a mayor utilidad de polígonos de edificaciones y documentación reciente de recuperación civil. La elección definitiva está pendiente de validación de APIs.

### 3.3 Alcance actual que Codex debe tomar como referencia

**Propuesta principal:** simulador académico de **ruteo físico resiliente** para UAV de observación territorial no ofensiva en un **entorno urbano sintético inspirado en Mykolaiv, Ucrania**. Priorizar **inspección de infraestructura civil y recuperación territorial** como misión demostrativa; el conflicto aporta el contexto de perturbaciones y degradación de servicios. No construir un plan real de vigilancia militar.

- **Un solo grafo:** posiciones hipotéticas y segmentos de movimiento, no mesh real entre aeronaves.
- **Un par origen-destino** para demostrar claramente la rúbrica; múltiples puntos de inspección o cobertura completa son trabajos futuros.
- **Dijkstra** con distancia pura como baseline.
- **Yen / `pgr_KSP`** para generar alternativas de recorrido, con costos/restricciones documentados y evaluación posterior de resiliencia.
- **Fallas simuladas reproducibles:** cierres temporales de aristas, degradación abstracta de comunicaciones, meteorología extrema hipotética; no atribuirlas automáticamente a armas o agentes reales.
- **No implementaremos CLUN-LSR completo ni una malla RF real en el MVP.**

---

## 4. Problemática, hipótesis y objetivos reformulados

### Título tentativo

**“Evaluación de ruteo físico resiliente para UAV de inspección territorial bajo restricciones geoespaciales y degradación de comunicaciones: caso académico inspirado en Mykolaiv, Ucrania”.**

### Problema

Las misiones de inspección georreferenciada de infraestructura civil en entornos urbanos con restricciones cambiantes pueden enfrentar indisponibilidad de tramos o ventanas de comunicación degradada. La selección por distancia mínima, por sí sola, no modela estas restricciones ni la existencia de rutas alternativas que mantengan la continuidad del recorrido.

### Pregunta de investigación

> ¿Cómo cambia la disponibilidad de rutas alternativas de inspección aérea al incorporar restricciones geoespaciales y fallas sintéticas, frente a una selección basada exclusivamente en distancia, sobre un grafo físico geolocalizado y reproducible?

### Hipótesis (comprobable, no resultado asumido)

> Bajo escenarios controlados de indisponibilidad de aristas, la selección de un conjunto de rutas alternativas evaluadas con información geoespacial y modelos explícitos de fallas **puede** mantener una mayor proporción de escenarios con ruta válida que una selección basada únicamente en distancia; esa diferencia debe medirse y no se garantiza para todas las topologías.

### Objetivo general

Diseñar e implementar una plataforma reproducible que construya un grafo geolocalizado de desplazamiento UAV simulado, integre metadata y eventos externos y compare rutas de distancia mínima con alternativas sometidas a escenarios de fallas, utilizando PostGIS, pgRouting, Python, Docker y Leaflet.

### Objetivos específicos

1. Definir un polígono de referencia urbano sintético y construir nodos/aristas de navegación con procedencia explícita.
2. Validar **tres fuentes de metadata** y **tres fuentes independientes de eventos/amenazas**, con procesos ETL documentados y carga espacial.
3. Modelar restricciones configurables y escenarios reproducibles de indisponibilidad de enlaces **físicos de navegación**.
4. Obtener por lo menos **dos rutas con `pgr_dijkstra` basadas únicamente en distancia**, según el enunciado.
5. Obtener por lo menos **dos rutas usando el algoritmo/paper elegido** (candidato: Yen / `pgr_KSP`).
6. Medir resiliencia y comparar diferencial de disponibilidad, longitud y restricciones entre ambos enfoques.
7. Exponer una interfaz Leaflet que permita seleccionar origen, destino y preferencias, y visualizar rutas y métricas.

### Qué NO se pretende demostrar

- No que una ruta sea segura para un vuelo real.
- No que los obstáculos urbanos puedan evaluarse en 3D sin alturas confiables.
- No que los eventos de ACLED o celdas de GPSJam midan directamente la calidad RF de un UAV.
- No superioridad universal de Yen sobre Dijkstra. Yen enumera rutas; **la resiliencia depende del criterio de elección y los escenarios**.
- No detección de minas, daños automáticos por IA, ni optimización de reconocimiento/ataque militar.

---

## 5. Zona de referencia y consistencia espacio-temporal

### Zona candidata: Mykolaiv urbana

**Motivo contextual:** programas de recuperación civil vigentes en 2025–2028, iniciativas geoespaciales ucranianas en 2026 y documentación de perturbaciones a infraestructura civil. No elegir Mykolaiv solo por el número de ataques; elegirla si las fuentes entregan datos integrables.

**Implementación segura y académica:**

- Definir un polígono ficticio urbano equivalente a un área de estudio aproximada de `4 km × 4 km`, con geometría desplazada o abstraída; **no usar coordenadas de operaciones reales**.
- Asignar al escenario la etiqueta `inspirado_en: Mykolaiv, Ukraine`, con metadatos que indiquen procedencia, fecha y nivel de abstracción.
- Si se consulta cartografía pública de Mykolaiv para un análisis **descriptivo agregado**, no derivar rutas operacionales, zonas de evasión ni un optimizador ligado a amenazas militares actuales.
- Separar **época del evento** de **época de la cartografía** y del **momento de ejecución del ETL**.
- Verificar si el conjunto de cada fuente realmente intersecta el polígono y el intervalo temporal seleccionados. Registrar `count=0` cuando corresponda; no inventar eventos para completar una cuota.

### Justificación reciente verificada

- [UNDP — Mykolaiv Strategic Partnership](https://www.undp.org/ukraine/projects/mykolaiv-strategic-partnership): proyecto en desarrollo entre **julio de 2025 y junio de 2028**, orientado a recuperación e infraestructura civil.
- [UNDP — New office in Mykolaiv](https://www.undp.org/ukraine/press-releases/undp-opens-new-office-bolster-recovery-and-reconstruction-across-mykolaiv-oblast), **26-01-2026**: ampliación de capacidad para reconstrucción.
- [UNDP — Equipment for five communities](https://www.undp.org/ukraine/press-releases/undp-provides-equipment-five-ukrainian-communities-support-data-driven-recovery), **31-03-2026**: equipamiento de teledetección y recopilación espacial, incluido Olshanske en Mykolaiv; **no prueba por sí mismo vuelos multi-UAV mesh**.
- [ONU — Protección de civiles, septiembre 2026](https://ukraine.un.org/en/324561-protection-civilians-armed-conflict-%E2%80%94-september-2026), publicado **16-10-2026**: continuidad reciente de los efectos del conflicto sobre población y servicios, no un dataset de segmentos de vuelo.
- [UNOSAT — Mykolaiv damage assessment](https://unosat.org/products/3404), **2022**: **solo referencia histórica**, no fuente principal para demostrar actualidad del problema.

**Si al revisar la evidencia el área urbana no es adecuada, comparar una segunda candidata con el mismo checklist de datos antes de cambiarla.**

---

## 6. Grafo único: definición, construcción y restricciones

### Modelo lógico

`G = (V, E, W)`:

- `V`: **waypoints sintéticos** de navegación (no aeronaves).
- `E`: segmentos geométricos candidatos entre waypoints vecinos, con identificadores `source` y `target`.
- `W`: mínimo `distancia_km > 0`; en una vista alternativa puede existir `costo_modelado` con componentes documentados, **sin presentar el costo como medida física validada**.
- Cada nodo: `id`, `geom(Point, 4326)`, `escenario_id`, `tipo`, `origen_dato`.
- Cada arista: `id`, `source`, `target`, `geom(LineString, 4326)`, `distancia_km`, `costo_base`, `costo_modelado`, `reverse_cost`, `estado`, `modelo_version`, `provenance`.

### Flujo de construcción

1. Cargar un polígono `zona_estudio` sintético y la cartografía pública **solo como capa de contexto**.
2. Generar una malla regular de waypoints dentro del polígono (ejemplo inicial: 100–300 nodos; **parámetro ajustable**, no hecho demostrado).
3. Crear segmentos entre vecinos admitidos por la topología sintética (evitar aristas duplicadas, longitud cero y geometrías inválidas).
4. Calcular longitudes en kilómetros con una proyección métrica apropiada o `ST_Length(geom::geography)/1000`, nunca en grados de EPSG:4326.
5. Garantizar explícitamente un caso demostrativo con origen y destino conectados y, cuando se requiera, **dos caminos distintos**; no falsificarlo si la topología real del experimento no los permite.
6. Enriquecer aristas con atributos o relaciones a capas de metadata y condiciones simuladas; las aristas que se vuelvan indisponibles deben quedar justificadas por el `escenario_falla_id`.
7. Mantener la **misma red base** para todos los métodos en una comparación justa.

### Precauciones geoespaciales

- El DEM describe superficie, no altura de cada edificio.
- Edificios OSM pueden carecer de `height` o `building:levels`.
- Sobrevolar una huella de edificio no equivale automáticamente a colisión; la simulación 2D es una aproximación.
- OSM `highway` es una vía terrestre, **no** arista de vuelo aérea.
- No asumir que mayor densidad urbana implica mayor conectividad del grafo; depende de la malla generada.
- Los UAV pueden moverse en 3D, pero el MVP modelará proyecciones 2D y anotará la ausencia de evaluación aerodinámica y altitudinal realista.

---

## 7. Metadata: selección, valor, limitaciones y ETL

**Criterio:** una fuente cuenta solo si se ejecutó la extracción, se persistió un archivo reproducible y se pudo asociar al grafo o al área. No basta un enlace a la documentación.

| Fuente | Qué se obtiene | Uso específico y válido | Límites | Estado para Ucrania |
|---|---|---|---|---|
| **OpenTopography** — [API](https://www.opentopography.org/developers) | DEM raster con elevación | caracterizar relieve y pendientes generales del escenario | resolución global 30/90 m, no edificios detallados | **no validado** |
| **OSM / Overpass** — [documentación](https://wiki.openstreetmap.org/wiki/Overpass_API) | edificios Polygon, tipo de uso de suelo y otras geometrías | contexto urbano, densidad, huellas de estructuras; capas visibles en Leaflet | alturas faltantes; no rutas aéreas listas | **no validado** |
| **OpenWeather** — [API](https://openweathermap.org/api) | meteorología por punto (viento, visibilidad, nubosidad, etc.) | metadata atmosférica del escenario; restricciones solo si están explícitamente modeladas | cobertura espacial/temporal y plan de API; un punto no representa todos los tramos | **no validado** |

**Fuente meteorológica opcional/histórica:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), que ofrece reanálisis. Puede sustituir o complementar OpenWeather para experimentos temporales reproducibles; si se contabilizan ambas como fuentes distintas, reconocer que cubren una temática similar y justificar la independencia de proveedores/datasets.

**Fuente adicional antigua:** OpenCellID, útil solo como referencia de infraestructura civil; no inferir cobertura, espectro RF ni conectividad aeronáutica.

### Requisito ETL por fuente

- Script Python independiente en `metadata/` (o convención exigida por el repositorio).
- Parámetros de tiempo/área o fixture sin claves embebidas.
- JSON o GeoJSON + `README` de campos/unidades/SRID/fecha/licencia + prueba de transformación.
- Persistencia en PostGIS y conteos verificables antes/después.
- Registro de `source_url`, fecha de extracción, fecha de observación, `status`, `license`, `schema_version`, hash del archivo.
- Test de campos obligatorios, geometría y validación de unidades.

---

## 8. Eventos/amenazas: qué sirve, qué no y cómo tratarlas

La rúbrica solicita **mínimo tres fuentes** de eventos o fallas externas a la infraestructura. Es fundamental distinguir un **registro observado** de un **mecanismo causal modelado**.

### Candidatos principales — todavía sujetos a prueba de factibilidad

| Fuente | Contenido | Aplicación defendible | Principal limitación | Decisión provisional |
|---|---|---|---|---|
| **ACLED** — [API](https://acleddata.com/api-documentation/acled-endpoint) | eventos históricos georreferenciados, tipo, fecha y precisión geográfica | contextualizar perturbaciones territoriales históricas en mapa/estadística | no es registro de rutas RF ni polígonos precisos de daño/amenaza | mantener como fuente contextual si el acceso funciona |
| **NASA FIRMS** — [API por área](https://firms.modaps.eosdis.nasa.gov/api/area/) | anomalías térmicas / focos detectados por sensor satelital, fecha y coordenadas | evaluar disponibilidad de eventos térmicos históricos y crear casos de estudio abstractos | una anomalía no equivale a incendio confirmado ni indisponibilidad de vuelo | validar si hay registros suficientes |
| **Open-Meteo histórico** — [API](https://open-meteo.com/en/docs/historical-weather-api) | viento, ráfagas, precipitación en series temporales | construir escenario de **evento meteorológico** a partir de datos históricos/modelados | no es otra amenaza militar; reanálisis no es medición en UAV | alternativa robusta si falta tercera fuente válida |

### Fuentes candidatas complementarias, no asumidas como válidas

- [GPSJam FAQ](https://gpsjam.org/faq): mapa diario de proporción de reportes de baja precisión de navegación de aeronaves ADS-B; no permite concluir interrupción de enlaces de control de UAV ni localizar con precisión equipos interferentes. Solo usar si hay suficientes observaciones y como **capa GNSS contextual**.
- [OpenAIP](https://www.openaip.net/): geometrías de espacio aéreo; los polígonos obtenidos para Chile no validan Ucrania. Las restricciones reales de espacio aéreo activo no deben convertirse en rutas operacionales.
- [Copernicus Emergency Management Service](https://mapping.emergency.copernicus.eu/): eventuales productos vectoriales de emergencias; revisar si existe activación relevante y su licencia/temporalidad.

### Reglas de modelamiento

1. `ACLED.evento` **no** causa automáticamente que una arista esté bloqueada.
2. `FIRMS.anomalia` **no** demuestra zona no volable; puede representar un evento georreferenciado a estudiar.
3. `GPSJam.percent_bad` **no** debe convertirse directamente en probabilidad de pérdida de comunicación UAV.
4. Las condiciones ambientales (ej. viento) requieren **umbrales hipotéticos claramente parametrizados y no utilizados como recomendaciones de vuelo**.
5. Las fallas de aristas se generan en un **motor de simulación** controlado, con semilla fija, intensidad abstracta y duración. Distinguir una capa observada de los polígonos hipotéticos de indisponibilidad.
6. No usar eventos del conflicto en tiempo real para elegir caminos más convenientes para vigilancia militar. Para la evaluación, desacoplar las observaciones históricas de cualquier modelo que optimice operaciones militares.

### Plan de contingencia de APIs

Si alguna fuente de amenazas no da datos útiles en el polígono/ventana temporal:

- registrar `SIN_DATOS` con logs, request sanitizada, periodo y número de objetos; no inventar registros;
- ampliar **periodo histórico dentro de lo permitido** o considerar otra fuente de un proveedor distinto;
- mostrar capas sintéticas **solo como fallas del experimento**, pero **no contarlas como API externa**;
- elevar al equipo/profesor el impacto en la cuota de tres fuentes si no se puede validar la cobertura.

---

## 9. Algoritmos, rutas y comparación rigurosa

### Baseline exigida

El enunciado/rúbrica requiere usar **`pgr_dijkstra` y únicamente distancia en kilómetros** para obtener `k ≥ 2` rutas distintas entre un par `(origen, destino)`.

`pgr_dijkstra` por sí solo devuelve la menor ruta por consulta. Para una segunda alternativa se puede repetir sobre el mismo grafo con una **exclusión documentada** de aristas, siempre manteniendo el peso de distancia entre las aristas restantes; es preciso explicar cómo se elige la exclusión para no sesgar el benchmark. No decir que dos llamadas idénticas a Dijkstra producen espontáneamente rutas distintas.

### Algoritmo propuesto

**Candidato seleccionado:** *Finding the K Shortest Loopless Paths in a Network* — Jin Y. Yen, **1971**, DOI [10.1287/mnsc.17.11.712](https://doi.org/10.1287/mnsc.17.11.712). En pgRouting: `pgr_KSP`. Ver [manual oficial pgRouting](https://docs.pgrouting.org/latest/en/).

- Genera rutas candidatas simples (sin ciclos) entre los mismos nodos.
- Sus costos pueden incluir restricciones modeladas, documentadas y normalizadas.
- **Yen no es un mecanismo de resiliencia por sí mismo.** La resiliencia se evalúa después, sobre conjuntos de rutas, en escenarios comparables.
- `pgr_KSP` **no garantiza disyunción de nodos o aristas**. Si interesa independencia, medir solapamiento y explorar filtros posteriores. Suurballe se consideró como alternativa para caminos disjuntos, pero **no es la selección vigente**.
- No comparar directamente una distancia en km con un costo adimensional sin explicar unidades y normalización.

### Comparación justa

Para ambos enfoques:

1. Mismo grafo base, mismos pares origen-destino, misma cantidad final `k = 2` (o informar explícitamente la falta de rutas).
2. Mismos escenarios de falla generados antes de evaluar.
3. Fijar semilla aleatoria y guardar ID/versiones de escenarios.
4. Separar **costos utilizados para seleccionar rutas** de **métricas usadas para evaluar resultados**.
5. Reportar distancia y un indicador de redundancia: compartir muchas aristas reduce independencia ante fallas localizadas.
6. Hacer baseline adicional opcional: `pgr_KSP` por **distancia pura**, para distinguir el efecto del algoritmo del efecto del costo enriquecido.

### Resiliencia propuesta

Sea `P = {p1, p2}` el par de rutas seleccionado por cada método. Para cada escenario sintético de falla `s`, `disponible(p,s) = 1` si todos los segmentos de la ruta permanecen operativos (bajo **la definición abstracta del experimento**).

`R(P) = (1/N) * Σ_s I[existe p en P tal que disponible(p,s)=1]`

`ΔR = R(P_propuesto) - R(P_dijkstra)` (en **puntos porcentuales** si las tasas se expresan en porcentaje).

**Importante:** esto mide **supervivencia de rutas preseleccionadas**, no recuperación en tiempo real, tasa de entrega RF ni probabilidad operacional de vuelo seguro. Si implementan replanificación posterior a una falla, medirla **por separado** con costo, tiempo de cálculo y factibilidad.

Métricas secundarias: longitud total, máxima longitud individual, porcentaje de escenarios desconectados, solapamiento de aristas, tiempo de cálculo y cobertura de restricciones declaradas.

**No adelantar resultados**. Los porcentajes 65/82 o 68/87 mencionados anteriormente eran *ejemplos ilustrativos*, nunca pruebas del proyecto.

---

## 10. Requisitos exactos de la tarea 2 (según archivo original)

### Artefactos obligatorios

1. Repositorio del equipo en GitLab UDP (`https://giteit.udp.cl`), respetando su estructura existente.
2. **Imagen/diagrama de la BD** y **archivo `.sql`** para reconstruir el esquema desde cero.
3. Carpeta **Infraestructura**: automatización de extracción/transformación de **nodos y aristas** a JSON.
4. Carpeta **Metadata**: `n` programas independientes de extracción/transformación a JSON.
5. Carpeta **Amenazas**: `n` programas independientes de extracción/transformación a JSON.
6. **Documentación por cada JSON/GeoJSON** que explique valores, unidades, geometrías y estructura.
7. **Cargador por cada JSON/GeoJSON** a la BD.
8. Carpeta **Sitio Web**: Leaflet mostrando infraestructura, metadata, amenazas y rutas.
9. Ejemplo de una ruta con `pgr_dijkstra` basada **solo en longitud**.
10. Script `main` en raíz para automatizar descarga → transformación → carga BD → habilitación del sitio.
11. **Docker obligatorio** con PostgreSQL, PostGIS y pgRouting; preferible Docker Compose para todos los servicios.
12. También según la **rúbrica**: pesos de fallas, restricciones derivadas de metadata, valores por defecto, selección y explicación de paper/algoritmo, `k ≥ 2` rutas por Dijkstra y por algoritmo seleccionado, métrica de resiliencia, UI con dupla origen/destino y preferencias, cálculo del diferencial.

### Ponderación de la rúbrica: 60 puntos

| Criterio | Puntos |
|---|---:|
| Docker con PostgreSQL/PostGIS/pgRouting | 2 |
| Modelo BD explicado + SQL reproducible | 2 |
| Extracción `n` metadata → JSON | 6 |
| Carga `n` metadata → BD | 2 |
| Extracción `n` fallas → JSON | 6 |
| Carga `n` fallas → BD | 2 |
| Explicar modelos de fallas | 3 |
| Asignación de pesos a enlaces/nodos | 2 |
| Convertir metadata en restricciones/preferencias | 3 |
| Restricciones por defecto | 2 |
| Identificar algoritmo y paper | 4 |
| Explicar funcionamiento del algoritmo | 6 |
| Obtener `k≥2` rutas vía `pgr_dijkstra`, solo distancia | 4 |
| Obtener `k≥2` rutas vía algoritmo seleccionado | 4 |
| Implementar métrica de resiliencia | 6 |
| Plataforma con origen/destino, restricciones, mapa y rutas | 4 |
| Diferencial de resiliencia | 2 |
| **TOTAL** | **60** |

**Ambigüedad documental importante:** el apartado narrativo del enunciado dice que la ruta inicial solo debe considerar distancia y que metadata/amenazas serán parte de una “fase 3”. Sin embargo, **la rúbrica de la misma tarea 2 sí puntúa restricciones, pesos, múltiples rutas y comparación de resiliencia**. Codex debe **implementar el alcance completo de la rúbrica** como opción por defecto, pero el equipo debe consultar esta contradicción con el profesor y documentar la respuesta.

### Condiciones heredadas de la tarea 1

- Problemática real, hipótesis, objetivo general y al menos 3 objetivos específicos.
- Infraestructura geolocalizada constituida por nodos y aristas, con **fuente y evidencia de factibilidad**.
- Mínimo `n` fuentes de metadata y `n` fuentes de fallas/eventos externas.
- En todo caso, **al menos una API y una base geoespacial con polígonos**.
- La plataforma debe permitir comparar **rutas alternativas entre dos puntos**, preparando la segunda fase.

---

## 11. Arquitectura tecnológica sugerida

```text
            API(s) y datasets históricos
  OSM/Overpass   OpenTopography   OpenWeather
  ACLED          NASA FIRMS       Open-Meteo
                      |
             scripts ETL Python
         validación + provenance + logs
                      |
           JSON/GeoJSON documentados
                      |
          Cargadores idempotentes SQL
                      |
     PostgreSQL + PostGIS + pgRouting
            |                   |
     grafo físico          capas/escenarios
            \___________________/
                      |
      servicio API / motor de evaluación
       Dijkstra | Yen | resiliencia
                      |
          Frontend Leaflet (web)
  mapa, origen/destino, parámetros, rutas

  Docker Compose: db + etl + api + frontend
```

La tecnología exacta del backend se decidirá tras inspeccionar el repositorio; Python + FastAPI sería una opción, **no una implementación existente presumida**.

### Estructura objetivo orientativa (NO recrear el repositorio; adaptar sobre el árbol de §0.A)

```text
/
├─ AGENTS.md
├─ README.md
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
├─ main.py                      # o script equivalente
├─ sql/
│  ├─ 001_schema.sql
│  └─ 002_seed_demo.sql
├─ db/
│  └─ er_diagram.png
├─ Infraestructura/
│  ├─ generar_grafo.py
│  ├─ cargar_grafo.py
│  └─ schema_grafo.md
├─ Metadata/
│  ├─ extraer_opentopography.py
│  ├─ extraer_osm.py
│  ├─ extraer_openweather.py
│  ├─ cargar_*.py
│  └─ esquemas/
├─ Amenazas/
│  ├─ extraer_acled.py
│  ├─ extraer_firms.py
│  ├─ extraer_openmeteo.py
│  ├─ cargar_*.py
│  └─ esquemas/
├─ Simulacion/
│  ├─ escenarios.py
│  ├─ costos.py
│  ├─ rutas.py
│  ├─ resiliencia.py
│  └─ fixtures/
├─ SitioWeb/
│  └─ ...
├─ tests/
├─ docs/
│  ├─ metodologia.md
│  ├─ fuentes_y_licencias.md
│  ├─ validacion_de_fuentes.md
│  ├─ comparacion_algoritmos.md
│  └─ trazabilidad_rubrica.md
└─ data/
   ├─ raw/                     # evitar archivos enormes en Git
   └─ processed/
```

**IMPORTANTE:** el árbol anterior es solo una referencia genérica, no la estructura que debe imponerse al proyecto. El repositorio real contiene `01_PROYECTO_ACTUAL/`, `02_REUNION_PROFESOR/`, `03_TAREA_1/` y `04_VALIDACION_TAREA_1/validacion_ruteo/` (§0.A). **No crear una nueva raíz ni duplicar `docker-compose.yml`, `run_all.py`, los ETL y los SQL sin justificarlo**. Proponer un destino para la tarea 2 y pedir aprobación; las carpetas exigidas por el curso pueden mapearse en documentación, respetando nombres cuando el corrector las espera.

### Tablas lógicas mínimas

- `zonas_estudio(id, nombre, geom Polygon/MultiPolygon, synthetic, ...)`
- `nodos(id, escenario_id, geom Point, origen_dato, ...)`
- `aristas(id, source, target, geom LineString, distancia_km, costo_base, costo_modelado, ...)`
- `edificaciones(id, geom Polygon/MultiPolygon, tags, fuente, ...)`
- `metadata_terreno(...)` (raster almacenado o referencias reproducibles + estadísticas por área/arista)
- `metadata_meteorologia(...)`
- `eventos_acled(id, geom Point, fecha, precision_geo, ...)`
- `eventos_firms(id, geom Point, fecha, instrumento, confianza, ...)`
- `eventos_meteorologicos(...)`
- `escenarios_falla(id, seed, version_modelo, parametros, ...)`
- `aristas_falladas(escenario_id, arista_id, intervalo, motivo_sintetico)`
- `rutas(id, experimento_id, metodo, ruta_orden, costo, ...)`
- `rutas_aristas(ruta_id, orden, arista_id)`
- `experimentos(id, version_datos, seed,...)`
- `resultados(id, experimento_id, metodo, resiliencia, distancia, ...)`

Es un punto de partida **no un SQL definitivo**; normalizar luego de comprobar los archivos reales y evitar tablas innecesarias. Mantener claves foráneas e índices GIST para geometrías. `ST_Intersects`, `ST_Within` y `ST_DWithin` se usarían en **capas de prueba**, sin convertir automáticamente proximidad a un evento bélico en riesgo operativo.

### Ejecución y seguridad

- `docker compose up --build` crea servicios reproducibles.
- `main` debe ejecutar flujos en orden, controlar errores y dejar estados identificables.
- Fixture *offline* obligatorio para que la demo funcione sin API keys ni internet.
- Modo `--online` opcional para revalidar fuentes; nunca incrustar claves.
- Limitar volumen, tiempo y frecuencia de APIs y conservar atribución/licencias.
- Registrar fallas de red, respuestas no JSON, geometrías nulas y respuestas vacías.
- Tests automatizados sin credenciales reales, con datos miniatura.
- README con versiones fijadas y comandos de inicio desde cero.

---

## 12. Interfaz Leaflet esperada

Un usuario académico debe poder:

1. Ver el polígono simulado y el grafo de navegación física (nodos y aristas).
2. Activar/desactivar capas de contexto con leyenda y **tipo de procedencia** (observada/modelada/sintética).
3. Seleccionar nodo de origen y nodo de destino (nodos de **waypoint**, no UAV reales).
4. Definir preferencias sencillas para el experimento (activar/desactivar restricción, ponderación, escenario y `k`), con **valores por defecto** documentados.
5. Ejecutar cálculo de rutas de referencia y alternativas.
6. Visualizar al menos dos rutas por método cuando existan, marcando las faltantes con explicación.
7. Ver distancia por ruta, cantidad de aristas, costo modelado, tasa de escenarios superados y `ΔR`.
8. Repetir escenario con la misma semilla y obtener el mismo resultado.
9. Ver una advertencia visible: **“Simulación académica; datos históricos/sintéticos; no apto para navegación real”**.

**No debe mostrar ubicaciones militares actuales, corredores operativos, instrucciones de evasión de defensas ni cálculos para ejecutar ataques.**

---

## 13. Plan incremental de implementación para Codex

### Fase 0 — Auditoría (bloqueante)

**Aplicar además el procedimiento de la §0.A.5: Codex ya posee el repositorio y debe auditarlo, no reconstruirlo.**

- Confirmar archivos existentes y estado de ramas.
- Comprobar que el repo contiene pruebas de APIs/SQL anunciadas o etiquetarlas como no encontradas.
- Relacionar cada punto de la rúbrica con código/documentos existentes.
- Crear `docs/diagnostico_inicial.md`, sin cambios destructivos.

**Gate:** aprobación del plan y aceptación del cambio conceptual de grafo.

### Fase 1 — Diseño de escenario y validación de datos

- Crear fixture de área urbana **sintética** y fechas históricas documentadas.
- Ejecutar **smoke tests de las seis fuentes** (o registrar fuentes sustitutas explícitas): estado HTTP, esquema, conteo, geometría, SRID, licencias, ventana temporal, acceso.
- Generar `docs/validacion_de_fuentes.md` con evidencia real y ejemplos anonimizados.
- Verificar que haya datos útiles; una respuesta vacía **no** supera el gate.

**Gate:** al menos 3 metadata y 3 amenazas/eventos de proveedores independientes con ETL verificable, o bloqueo transparente y decisión aprobada.

### Fase 2 — Datos y grafo geolocalizado

- Crear esquema SQL y diagrama ER desde cero.
- Construir generador de nodos/aristas con validaciones y exportación a JSON.
- Calcular distancias reales de geometría en km, con precisión/unidades explicitadas.
- Crear loaders idempotentes e índices espaciales.
- Probar conectividad y existencia de dos alternativas entre par de demostración.

**Gate:** Docker con `postgis_version()` y funciones pgRouting disponibles; fixture reproducible.

### Fase 3 — Algoritmos y métricas

- `pgr_dijkstra`: dos rutas distintas por distancia pura, con exclusión de aristas documentada.
- `pgr_KSP` (Yen): generar y seleccionar `k` rutas candidatas; explicar criterios de costo.
- Simular fallas con semillas persistidas; comparación bajo mismos escenarios.
- Computar `R(P)`, `ΔR`, longitud y solapamiento, respetando casos de no existencia de caminos.
- Comparar con baseline extra `pgr_KSP` + distancia pura si queda tiempo.

**Gate:** resultados exportados, pruebas de consistencia, ninguna mejora declarada sin medición.

### Fase 4 — Frontend y automatización

- Leaflet con mapas, capas, filtros, rutas y tabla/gráficos de resultados.
- API de lectura y cálculo sobre datos sintéticos.
- `main` reproducible; scripts JSON y loaders.
- Prueba end-to-end desde cero con Docker y sin secretos reales.

**Gate:** demostración completa de la rúbrica.

### Fase 5 — Material académico

- Actualizar informe y diapositivas después de que exista evidencia de ejecución.
- Sección **diferencia entre tarea 1 y tarea 2**; aclarar que CLUN-LSR queda como antecedente, no como algoritmo implementado.
- Fuentes, metodología de validación, decisiones, métricas, limitaciones, trabajo futuro y capturas reales de la app.
- Documento trazabilidad de los 60 puntos con enlaces a archivos/figuras/comandos.

---

## 14. Casos de prueba y criterios de aceptación

### Tests mínimos

- **ETL:** duplicados, paginación, API caída, timeout, respuesta vacía, campos faltantes, geometrías inválidas y fechas incompatibles.
- **BD:** creación desde cero, integridad `source/target`, SRID 4326 y longitudes en km, restricciones y claves únicas, índices GIST.
- **Grafo:** sin aristas de longitud 0, sin self loops no deseados, pares conexos y pares desconectados, `k<2` informado correctamente.
- **Dijkstra:** costo exclusivamente longitud, y ruta 2 obtenida por exclusión replicable.
- **Yen:** rutas sin ciclos, continuidad de nodos y costos reportados, `k` controlado.
- **Métricas:** en ausencia de fallas todas las rutas existentes deben sobrevivir; fallo de una arista compartida afecta las rutas correspondientes; `R` entre 0 y 1; `ΔR` con signo correcto; semillas deterministas.
- **UI:** seleccionar par origen-destino, preferencias por defecto, visualizar fuentes y rutas, advertencia de simulación y manejo de 0 resultados.
- **Docker:** levantar desde repositorio limpio, migrar datos, cargar fixtures y mostrar resultados sin intervención manual.

### Aceptación del trabajo

- [ ] Alcance aprobado: **un grafo físico**, no mesh real.
- [ ] Justificación de contexto vigente (2025–2026) referenciada.
- [ ] Escenario con procedencia y carácter sintético declarados.
- [ ] 3 metadata y 3 amenazas/eventos **de fuentes independientes** con evidencia de extracción e importación.
- [ ] Al menos una API externa y PostGIS con Polygon/MultiPolygon.
- [ ] Nodos/aristas exportados en JSON y documentados.
- [ ] `.sql` e imagen del esquema de BD.
- [ ] Scripts de carga por fuente, Docker y `main`.
- [ ] Ruta Dijkstra demostrable + otras alternativas, `k ≥ 2` según condiciones.
- [ ] Rutas alternativas con Yen o decisión algorítmica justificada.
- [ ] R(P) y diferencial medidos en los mismos escenarios.
- [ ] Leaflet operativo, selección de puntos y restricciones por defecto.
- [ ] README de instalación y modo offline totalmente reproducible.
- [ ] Trazabilidad entre rúbrica y evidencia, sin números fabricados.

---

## 15. Papers y literatura especializada — verificados

### Núcleo científico

1. **Zheng, S., Zhu, X., Qin, Z. & Dong, C.** (2025). *Cross-layer UAV network routing protocol for spectrum denial environments*. **Ad Hoc Networks, 167, 103702**. DOI: https://doi.org/10.1016/j.adhoc.2024.103702  
   **Papel:** origen conceptual sobre jamming y redes UAV. **No implementar obligatoriamente**: es ruteo de comunicación, diferente del grafo físico actual.

2. **Luna, M. A., Molina, M., Da-Silva-Gomez, R., Melero-Deza, J., Arias-Perez, P. & Campoy, P.** (2024). *A multi-UAV system for coverage path planning applications with in-flight re-planning capabilities*. **Journal of Field Robotics, 41(5), 1480–1497**. https://doi.org/10.1002/rob.22342  
   **Papel:** replanificación de cobertura/inspección y fallas durante misión; el proyecto actual **no** reproduce toda la arquitectura multi-UAV.

3. **Yen, J. Y.** (1971). *Finding the K Shortest Loopless Paths in a Network*. **Management Science, 17(11), 712–716**. https://doi.org/10.1287/mnsc.17.11.712  
   **Papel:** base algorítmica de `pgr_KSP`. Nota: no maximiza resiliencia por definición.

4. **Ejaz, M. M., Bingi, K., Ibrahim, R., Rajamallaiah, A. & Omar, M. B.** (2026). *Communication-aware path planning in multi-UAV networks: A systematic review and cross-layer analysis*. **Vehicular Communications, 60, 101043**. https://doi.org/10.1016/j.vehcom.2026.101043  
   **Papel:** revisión sistemática de **99 trabajos**; confirma que integrar movilidad y restricciones de comunicaciones es una línea activa. **No demuestra novedad automática** de nuestro proyecto.

5. **Stopochkina, I. et al.** (publicado **31-03-2025**, número 6(2) atribuido a 2024). *Simulation of UAV networks on the battlefield, taking into account cyber-physical influences that affect availability*. **Theoretical and Applied Cybersecurity**. https://doi.org/10.20535/tacs.2664-29132024.2.318182  
   **Papel:** modelos de disponibilidad de redes UAV bajo perturbaciones. **Trabajo de redes/comunicaciones** y contexto militar; no autoriza extrapolar su modelo a trayectorias civiles.

### Contexto de guerra electrónica (no fuentes de rutas operativas)

6. **Watling, J. & Sylvia, N.** (2025). *Competitive Electronic Warfare in Modern Land Operations*. **RUSI**, 30-01-2025. https://www.rusi.org/explore-our-research/publications/occasional-papers/competitive-electronic-warfare-modern-land-operations  
   **Papel:** evidencia analítica de perturbaciones electromagnéticas en la guerra moderna.

7. **Iorillo, P. & Simonetti, R. M.** (2025). *Electromagnetic Operations in Ukraine: Lessons Learned, Capability Development and Future Implications*. **The RUSI Journal**. https://doi.org/10.1080/03071847.2025.2561585  
   **Papel:** evaluación del contexto Rusia-Ucrania como caso de estudio.

8. **Slusher, M.** (2025). *Lessons from the Ukraine Conflict: Modern Warfare in the Age of Autonomy, Information, and Resilience*. **CSIS**, 02-05-2025. https://www.csis.org/analysis/lessons-ukraine-conflict-modern-warfare-age-autonomy-information-and-resilience  
   **Papel:** contexto actualizado de UAV, información, guerra electrónica y resiliencia; no proporciona datos GIS de enlaces físicos.

### Documentación de herramientas

9. **pgRouting Manual**: https://docs.pgrouting.org/latest/en/ — comprobar versión instalada; `pgr_dijkstra` y `pgr_KSP`.
10. **PostGIS**: https://postgis.net/documentation/ — tipos geométricos, funciones e índices espaciales.
11. **OpenTopography API**: https://www.opentopography.org/developers — DEM globales, parámetros y licencias.
12. **Overpass**: https://wiki.openstreetmap.org/wiki/Overpass_API — consultas de objetos OSM.
13. **OpenWeather**: https://openweathermap.org/api — meteorología y condiciones de uso.
14. **Open-Meteo Historical**: https://open-meteo.com/en/docs/historical-weather-api — reanálisis y resoluciones.
15. **ACLED API**: https://acleddata.com/api-documentation/acled-endpoint — filtros y acceso.
16. **NASA FIRMS API**: https://firms.modaps.eosdis.nasa.gov/api/area/ — anomalías térmicas y parámetros de consulta.
17. **GPSJam FAQ**: https://gpsjam.org/faq — interpretación y limitaciones de ADS-B.

### Fuentes de contexto y noticias recientes

18. **UNDP** (2025–2028): *Mykolaiv Strategic Partnership*. https://www.undp.org/ukraine/projects/mykolaiv-strategic-partnership
19. **UNDP**, 26-01-2026: *UNDP opens a new office to bolster recovery and reconstruction across Mykolaiv Oblast*. https://www.undp.org/ukraine/press-releases/undp-opens-new-office-bolster-recovery-and-reconstruction-across-mykolaiv-oblast
20. **UNDP**, 31-03-2026: *UNDP provides equipment to five Ukrainian communities to support data-driven recovery*. https://www.undp.org/ukraine/press-releases/undp-provides-equipment-five-ukrainian-communities-support-data-driven-recovery
21. **UNDP**, 23-09-2026: *UNDP participates in Embassy of Sweden’s Partnership Fair in Poltava*. https://www.undp.org/ukraine/press-releases/undp-participates-embassy-swedens-partnership-fair-poltava — equipos de monitoreo ambiental con drones en Poltava, **otra región**; antecedente de misión, no evidencia de vuelos en Mykolaiv.
22. **United Nations in Ukraine**, 16-10-2026: *Protection of Civilians in Armed Conflict — September 2026*. https://ukraine.un.org/en/324561-protection-civilians-armed-conflict-%E2%80%94-september-2026
23. **UNOSAT**, 14-10-2022: *Mykolaiv Damage Assessment Overview Map*. https://unosat.org/products/3404 — **histórico**, no fuente suficiente para justificar la necesidad actual.
24. **UNDP**, 2025: *Aerial detection technology to accelerate humanitarian demining operations*. https://www.undp.org/ukraine/press-releases/undp-equips-sesu-cutting-edge-ukrainian-aerial-detection-technology-accelerate-humanitarian-demining-operations — antecedente de uso civil de tecnología aérea, **no** alcance del proyecto (no detectar minas).

> **Sobre la bibliografía:** los enlaces anteriores se contrastaron con las páginas de los editores/instituciones o documentación oficial a fecha de preparación. Para una cita formal en LaTeX, Codex deberá verificar nuevamente autores, volumen, DOI y fecha desde el artículo completo. No atribuir capacidades a un paper que no estén explícitamente descritas en él.

---

## 16. Gap de investigación: formulación honesta

**Estado del arte conocido:** ya existen algoritmos de rutas alternativas, planificación de cobertura con replanificación, planificación sensible a comunicaciones y protocolos contra jamming.

**Brecha candidata para este curso:** falta de **validación contextual reproducible** de cómo diferentes representaciones de restricciones geográficas y disponibilidad de tramos cambian el desempeño de conjuntos de rutas físicas de inspección, cuando se comparan contra rutas de distancia mínima sobre el **mismo grafo** y **los mismos escenarios de falla**.

No afirmar “es el primer método” ni “nadie investigó esto”. Se trata de una contribución de **integración, ingeniería de datos y evaluación**. Si el grupo desea una publicación, hará falta una revisión sistemática adicional y un mecanismo propio bien definido.

**Ventaja:** modelo implementable y evaluable mediante PostGIS/pgRouting; muchos componentes se reaprovechan.

**Desventaja:** gran parte de la infraestructura aérea y las fallas son sintéticas; extrapolación a vuelos reales o guerra electrónica real **no justificada**.

---

## 17. Decisiones abiertas y preguntas que Codex NO debe resolver arbitrariamente

| Pregunta | Estado | Conducta solicitada |
|---|---|---|
| ¿Acepta el profesor el cambio formal de infraestructura: nodos UAV → waypoints físicos? | **Pendiente** | Preparar explicación y matriz de cambios; pedir confirmación del equipo. |
| ¿El nombre oficial de la entrega actual es fase 2 y la parte de restricciones debe entregarse ahora o en fase 3? | **Contradictorio en el enunciado** | Cumplir por defecto toda la rúbrica y levantar consulta formal. |
| ¿La zona urbana inspirada en Mykolaiv tiene tres metadata y tres amenazas con datos útiles en mismo periodo? | **No probado** | Realizar smoke tests; no declararlo validado. |
| ¿Qué hacer si ACLED/FIRMS no cubren el periodo/polígono? | **Pendiente** | Registrar fallo, evaluar alternativa independiente, obtener aprobación. |
| ¿Cuántos UAV reales o virtuales deben aparecer en la demo? | **No fijado** | MVP centrado en rutas de un waypoint A al B, sin simulación de flota. |
| ¿Se requiere cobertura de varios sectores o un par origen-destino? | **MVP decidido: origen-destino** | Cobertura multi-UAV como trabajo futuro. |
| ¿Cuál es la fórmula final de costo enriquecido y sus pesos? | **Pendiente de diseño** | Proponer opciones adimensionales, analizar sensibilidad; no asignar números como leyes físicas. |
| ¿Cómo obtener dos rutas Dijkstra no idénticas? | **Método por definir/documentar** | Proponer exclusión replicable y controlar sesgo de comparación. |
| ¿Qué versión de pgRouting/PostGIS se instalará? | **Depende del repo** | Pin de imágenes compatibles; `SELECT` de versiones en test. |
| ¿Hasta qué punto reescribir PPT/TEX? | **Después de evidencia** | Conservar originales y crear nueva revisión separada. |

---

## 18. Prompt ejecutivo que debería orientar cada sesión de Codex

> Actúa como ingeniero/a de software, bases de datos geoespaciales, algoritmos de grafos y metodología de investigación. **Ya tienes acceso al repositorio `AlgoritmosRuteo` y parte de su historia: inspecciónalo, no lo recrees, y aplica la sección 0.A de este documento.** Debes continuar el proyecto universitario de ruteo resiliente en la UDP, partiendo del repositorio existente y los cuatro documentos anexos. La propuesta cambió desde CLUN-LSR (redes UAV y jamming) hacia un **grafo único de rutas físicas sintéticas** para inspección territorial civil, inspirado en el contexto urbano de Mykolaiv, Ucrania. Mantén CLUN-LSR como antecedente, no como obligación de implementación. La tarea 2 requiere ETL, tres metadata, tres fuentes de amenazas/eventos, API y base geoespacial con polígonos, Docker/PostgreSQL/PostGIS/pgRouting, Dijkstra (`k≥2` por distancia), rutas alternativas fundamentadas en paper (candidato: Yen / `pgr_KSP`), métrica de resiliencia, Leaflet y automatización completa. **Reutiliza y audita los scripts existentes de `04_VALIDACION_TAREA_1/validacion_ruteo/`, `run_all.py`, su SQL, su Docker y documentación. No dupliques el proyecto; no manipules `.env` ni `credentials.json` en salidas o commits. No asumas que lo hecho para Santiago está validado para Ucrania ni inventes observaciones.** Antes de programar, audita el repositorio y construye matriz de trazabilidad de la rúbrica. Trabaja por fases con pruebas y evidencia; separa datos históricos públicos, parámetros modelados y simulaciones sintéticas. El software es una demostración académica no operativa; no generar rutas o herramientas para ataques, infiltración ni evasión militar. Entrégame primero diagnóstico, riesgos, plan, pruebas de factibilidad y lista de decisiones pendientes. Después ejecutaremos cada fase con aprobación.

---

## 19. Registro de advertencias para evitar malentendidos

- **`CLUN-LSR` es la sigla correcta** del paper original; no usar `CLNR` como nombre oficial (en la transcripción aparece por errores de reconocimiento de voz).
- En la presentación se lee **“CLUN-LSR extendido”**, pero **la propuesta nueva no es una extensión técnica directa del protocolo**. Reflejarlo en documentos.
- No contabilizar `OpenSky` como la red de navegación física.
- No confundir “ruta de retransmisión de paquetes” con “trayectoria que recorre el UAV”.
- No confundir “dos rutas distintas” con “dos rutas disjuntas”: Yen no garantiza disyunción.
- No confundir “viabilidad de API” con “existencia de observaciones locales pertinentes”.
- No elevar una celda de GNSS degradado o un evento de conflicto a zona RF comprobada.
- No suponer que edificios OSM tienen altura; no prometer evitar colisiones con un grafo 2D.
- No reutilizar sin contexto los **7.635** estados OpenSky globales, **236.791** edificios chilenos, **235** eventos ACLED históricos ni los **27** polígonos OpenAIP chilenos como datos de Mykolaiv.
- No agregar datos sintéticos a una fuente real para que parezca que la API devolvió más registros.
- No asumir que mejoras hipotéticas de resiliencia son resultados experimentales.
- Distinguir que existe un **contexto bélico real** de que el software es un **estudio académico no operacional**.

---

## 20. Primer entregable que espero de Codex

**Sin alterar aún el código principal**, producir los siguientes documentos en una ubicación existente apropiada o proponer `docs/` para aprobación (no asumir que `docs/` ya existe):

1. `diagnostico_inicial.md`: qué hay realmente en el repositorio, qué está probado y qué falta.
2. `matriz_rubrica_tarea2.md`: los 17 criterios con 60 puntos y evidencia/estado/tarea para cada uno.
3. `decisiones_tecnicas.md`: grafo único, fuentes, algoritmo, unidad de costos, simulación y riesgos.
4. `plan_etapas.md`: tareas priorizadas P0–P3 y dependencias/gates de aceptación.
5. `fuentes_factibilidad.md`: plan de pruebas para 3 metadata + 3 amenazas, con fechas, coberturas y acceso.

Luego esperar mi validación del plan antes de implementar. Priorizar una **demo offline simple de extremo a extremo**, pero nunca disfrazarla como datos verificados o como capacidades de vuelo real.

**Fin del documento maestro.**

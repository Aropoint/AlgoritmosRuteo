# Contexto completo del proyecto UAV para continuar en Claude

**Actualizado:** 19 de octubre de 2026. **Repositorio local:** `AlgoritmosRuteo`. **Rama inspeccionada:** `tarea-2`, commit `7a4e002`; el único remoto configurado es `origin` en GitHub (`Aropoint/AlgoritmosRuteo`). Este documento resume el estado observado en esa copia del repositorio y debe cotejarse con `git status` y el código antes de asumir que sigue vigente.

## 1. Resumen que conviene leer primero

El grupo 7 pasó de estudiar **rutas de comunicación entre UAV** ante interferencia, mediante CLUN-LSR, a implementar **rutas físicas de un UAV simulado** para una misión civil de inspección territorial. El caso usa como referencia histórica y cartográfica un recorte urbano de **Mykolaiv, Ucrania**; la misión, la red de navegación y las fallas son construcciones académicas, no vuelos observados ni un plan operativo.

El resultado implementado consta de un único grafo geolocalizado de puntos y segmentos de vuelo, tres puntos de observación obligatorios, una línea base Dijkstra por distancia, un método que genera candidatas con Yen y selecciona rutas por longitud, exposición contextual y separación espacial, y un simulador que replantea el recorrido cuando descubre tramos bloqueados. PostgreSQL/PostGIS/pgRouting, tres fuentes de metadata, tres de amenazas, Docker y un sitio Leaflet dan soporte al ejercicio. La primera corrida integral de Docker terminó; **la evaluación final reservada y la regeneración del ejemplo de base de datos tras un arreglo siguen pendientes**.

En los escenarios sintéticos de *ajuste* conservados, la propuesta supera a un par Dijkstra fijo, pero **no muestra una ventaja consistente frente a Dijkstra que también replanifica**. Esa comparación debe permanecer visible en cualquier informe o presentación.

### Convención de evidencia

| Marca | Significado en este documento |
|---|---|
| **Implementado** | Existe código o un artefacto en la rama inspeccionada. |
| **Comprobado** | Hay salida conservada o una ejecución documentada; se indica cuándo procede de una corrida anterior. |
| **Antecedente** | Literatura, noticia, informe o trabajo anterior que motiva el caso, sin probar un evento del simulador. |
| **Supuesto** | Parámetro o regla elegida para la simulación, sin atribuirle validez aeronáutica o causal empírica. |
| **Pendiente** | Requiere decisión, nueva ejecución, revisión visual o evidencia de entrega. |

**Orden de autoridad:** el enunciado y la rúbrica de la Tarea 2 fijan requisitos; el código, los JSON conservados y `05_T2/README.md` describen la implementación actual. `CONTEXTO_INTEGRAL_CODEX_RUTEO_UAV_2026_V3.md`, la auditoría Fase 0, el README de la raíz y parte de `05_T2/PROPUESTA_TECNICA.md` contienen estados anteriores a la primera corrida completa; sirven como antecedentes y no deben prevalecer sobre el código actual.

## 2. Historia del problema y delimitación actual

### Tarea 1: comunicación, no trayectoria

El punto de partida fue el artículo de **Zheng et al., CLUN-LSR**, sobre recuperación de caminos de *datos* en una red UAV bajo denegación de espectro. En ese modelo un UAV es un nodo, un enlace de radio entre vehículos es una arista y la ruta determina por qué UAV pasan los paquetes. La Tarea 1 exploró fuentes y almacenamiento geoespacial en Santiago, principalmente OpenTopography, OSM/Overpass, OpenWeather, GPSJam, ACLED, OpenAIP, OpenSky y PostGIS; no produjo un algoritmo evaluado de trayectorias físicas. El material está en [`03_TAREA_1/`](03_TAREA_1/README.md) y [`04_VALIDACION_TAREA_1/`](04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md).

La revisión posterior del planteamiento inicial permitió identificar problemas de sustento y coherencia que debían resolverse: no había una incidencia cuantificada de jamming contra esa red UAV, se usaba un tiempo de reacción sin definición ni promedio pertinente, la hipótesis no predecía una métrica refutable y los objetivos se concentraban en la base de datos y tareas técnicas. También se había representado como estático un grafo cuyos nodos eran UAV móviles; OpenSky describía sobre todo aviones comerciales y no vuelos UAV a baja altura; una tabla horizontal no respaldaba afirmaciones sobre navegación tridimensional; y faltaba vincular afirmaciones, tablas y figuras con sus fuentes. La solución actual **cambia la pregunta de investigación**, en vez de presentar CLUN-LSR como si planificara vuelos.

El PDF histórico [`03_TAREA_1/referencias/Tecnicas_de_Intercepcion_Telefonica.pdf`](03_TAREA_1/referencias/Tecnicas_de_Intercepcion_Telefonica.pdf) contiene un informe de la Biblioteca del Congreso Nacional sobre caracterización y estatus legal del jamming en Chile; su nombre de archivo no coincide con su título. Aporta contexto general, pero no demuestra una misión como la simulada. Se exploraron cárceles chilenas, crimen organizado en México y otros ejemplos internacionales; la evidencia disponible no permitió reconstruir un caso público único con flota, interferencia medida, trayectorias y recuperación observada. Esos lugares son **alternativas históricas**, no escenarios implementados simultáneamente.

### Conversación con el profesor y alcance reducido

La [transcripción](02_REUNION_PROFESOR/Charla_profesor.txt) contiene errores de reconocimiento de voz. La idea discutida era que una alerta sobre un UAV que deja de reportar podría influir en la **ruta física** de otros, siempre dentro de una misión concreta; también se distinguieron misiones de llegada a destino y misiones de reconocimiento de zona. Se escogió el reconocimiento como motivación, pero la implementación de Tarea 2 reduce el alcance a **un UAV que visita puntos de observación en orden**. No modela varios UAV, comunicación entre ellos, beacons, pérdida real de reporte, propagación de alertas ni cobertura continua de un polígono. Los comentarios del profesor sobre operaciones militares fueron ejemplos para razonar sobre la misión, **no requisitos de construir una planificación militar**.

La formulación actual es una **inspección territorial civil simulada**. CLUN-LSR queda como antecedente de resiliencia de comunicaciones; **Yen (1971)** es la base algorítmica para obtener caminos físicos simples, y **Luna et al. (2024)** es un antecedente sobre replanificación de inspección. No se reproduce el sistema multi-UAV ni la cobertura poligonal de Luna. El [informe `.tex` actual](05_T2/Informe_Tarea_2_Ruteo_Resiliente_UAV.tex) explica esta distinción y debe mantenerse así.

## 3. Caso de estudio: hechos documentados frente a simulación

Mykolaiv es una **referencia cartográfica e histórica provisional**. El [producto UNOSAT](https://unosat.org/products/3404) identificó 198 estructuras con daño visible en imágenes del 21 de julio de 2022 y lo calificó como análisis preliminar no validado en terreno. El borrador del informe cita, según reportes de la Policía Nacional de Ucrania, [un ataque del 3 de agosto de 2026](https://mk.npu.gov.ua/news/zahybla-ta-semero-postrazhdalykh-z-nykh-dvoie-ditei-u-mykolaievi-politseiski-dokumentuiut-naslidky-cherhovoho-voiennoho-zlochynu-rf) con una muerte y siete personas heridas, [otro del 2 de octubre](https://npu.gov.ua/news/postrazhdaly-troie-hromadian-zaznaly-poshkodzhen-tsyvilni-obiekty-u-mykolaievi-politseiski-dokumentuiut-naslidky-cherhovykh-voiennykh-zlochyniv-rf) con tres residentes heridos y daños en edificios, y [uno del 10 de octubre](https://npu.gov.ua/news/politseiski-fiksuiut-naslidky-nichnoi-cherhovoi-vorozhoi-ataky-rf-na-mykolaiv) con nuevos daños urbanos. También cita al [PNUD sobre recuperación regional](https://www.undp.org/ukraine/projects/mykolaiv-strategic-partnership) y [recopilación de datos espaciales/aéreos](https://www.undp.org/ukraine/press-releases/undp-provides-equipment-five-ukrainian-communities-support-data-driven-recovery). Las referencias y fechas deben verificarse nuevamente antes de publicar.

**Actualización documental del 19 de octubre de 2026:** la [Policía Nacional de Ucrania informó otro ataque con UAV sobre Mykolaiv](https://npu.gov.ua/news/u-mykolaievi-politseiski-dokumentuiut-naslidky-cherhovoi-ataky-vorozhymy-bpla), con daños en cuatro viviendas según el resumen de su publicación. Este antecedente aún no está incorporado en el informe `.tex` ni en la presentación; antes de usarlo en la entrega, se deben cotejar la fecha del hecho, la publicación y el texto íntegro de la fuente.

Esos antecedentes explican el interés académico por observación territorial, pero **no prueban que haya existido esta misión, que un UAV local haya perdido conectividad o que sus rutas hayan sido bloqueadas por jamming**. El grafo no representa corredores autorizados y ninguna trayectoria generada debe publicarse como ruta de vuelo real. El proyecto evita planificación operativa militar: las posiciones de la misión se fijan como fracciones de un recorte cartográfico y los bloqueos se crean sintéticamente.

## 4. Qué exige exactamente la Tarea 2

La fuente primaria está en [`01_PROYECTO_ACTUAL/ENUNCIADO_Y_RUBRICA_TAREA_2.txt`](01_PROYECTO_ACTUAL/ENUNCIADO_Y_RUBRICA_TAREA_2.txt), reproducida también en la [guía de entrega](05_T2/ENTREGA_TAREA2.md). La **presentación se entrega en Canvas** y debe evidenciar el ETL y cada criterio; el proyecto debe estar en el **GitLab UDP asignado**, aunque la copia local solo tiene remoto GitHub. La rúbrica suma **60 puntos**:

| Criterio | Puntos | Evidencia de la rama y límite |
|---|---:|---|
| Docker con PostgreSQL, PostGIS y pgRouting | 2 | Compose, Dockerfile y primera corrida completa documentada. |
| Modelo de BD, diagrama y SQL recreable | 2 | `BD/schema.sql`, `BD/MODELO_BD.md`, `BD/diagrama_bd.png`. |
| Obtener `n` metadata a JSON | 6 | Tres extractores en `Metadata/`; evaluar si dos endpoints de Open-Meteo cuentan como fuentes independientes según criterio docente. |
| Cargar metadata | 2 | `Metadata/cargar_*.py` y tablas `meta_*`. |
| Obtener `n` amenazas/fallas a JSON | 6 | Tres extractores en `Amenazas/`; los registros son indicadores, no fallas UAV observadas. |
| Cargar amenazas/fallas | 2 | `Amenazas/cargar_*.py` y tablas `amz_*`. |
| Explicar modelo de fallas | 3 | Discos espaciales sintéticos y descubrimiento local en `ruteo/fallas.py`. |
| Derivar pesos de fallas | 2 | `ruteo/pesos.py`, `BD/pesos.sql`; justificar la interpretación no probabilística. |
| Metadata como restricciones de usuario | 3 | Relieve/edificios y viento; zonas restringidas sin fuente efectiva cargada. |
| Preferencias por defecto | 2 | `ruteo/config.py` y formulario del sitio. |
| Nombrar algoritmo y paper | 4 | Yen (1971), más selección y replanificación propias. |
| Explicar funcionamiento | 6 | Pseudocódigo en `.tex` y `PROPUESTA_TECNICA.md`; implementación Python/pgRouting. |
| Al menos dos rutas con `pgr_dijkstra` y costo solo km | 4 | `comun/rutas.py`; atención al respaldo que multiplica costos por diez si excluir la primera ruta desconecta el par. |
| Al menos dos rutas con propuesta | 4 | `pgr_KSP` + selección; comprobar rutas distintas para los pares presentados. |
| Métrica de resiliencia de `k` rutas | 6 | `R_par`, `R_mision` y escenarios reproducibles. |
| Plataforma origen/destino, preferencias y mapa | 4 | FastAPI + Leaflet; falta una comprobación visual documentada de toda la interacción. |
| Diferencial de resiliencia | 2 | `ΔR` en puntos porcentuales; incluir también control Dijkstra con replanificación. |

El texto del enunciado describe una ruta Dijkstra de ejemplo y difiere en alcance de ciertos criterios de la rúbrica, que exigen **`k ≥ 2` rutas por método y diferencial de resiliencia**; el proyecto intenta cubrir la rúbrica completa. La [matriz detallada](05_T2/ENTREGA_TAREA2.md) indica qué archivo y qué evidencia mostrar en la presentación.

## 5. Modelo de misión e infraestructura

**Implementado:** un solo grafo físico `G=(V,E)`; `V` son puntos geolocalizados de navegación y `E`, segmentos candidatos de desplazamiento, no enlaces RF. La posición del UAV y la distancia ya recorrida son estados de simulación. La topología de referencia se mantiene, mientras que una arista puede quedar no admisible por restricciones previas o por una falla descubierta durante el avance. Así se representa un problema dinámico sin confundir los nodos con vehículos móviles.

La [configuración](05_T2/ruteo/config.py) usa un recorte urbano provisional de Mykolaiv y una malla sintética de **196 nodos y 618 aristas**: separación nominal de 0,5 km, hasta ocho vecinos, perturbación geométrica de 0,25 celdas y eliminación de 12 % de aristas sin desconectar la red (semilla 7). La primera corrida cargó 374,18 km de segmentos. La misión fija `A → P1 → P2 → P3 → B`, asociada a los nodos `[15, 131, 65, 151, 181]`; cada par consecutivo es un subproblema origen–destino y la longitud mínima total sin fallas es **`L* = 13,1637 km`**. Visitar esos tres puntos es una inspección **discreta**, no cobertura continua ni medición de superficie observada.

El modelo es **2,5D**: conserva posición horizontal, elevación del terreno y altura estimada de edificios, con una altura de vuelo fija respecto del punto de partida. Se excluye un tramo si `(terreno_máximo − elevación_origen) + altura_edificio_máxima ≥ altura_vuelo − margen`. El terreno se muestrea en extremos y punto medio; la altura de edificio procede de etiquetas OSM cercanas y suele faltar. La suma puede sobreestimar obstáculos si el DEM ya incorpora parte de la superficie construida, y el modelo no representa ascensos, maniobras, energía, permisos reales ni seguridad aeronáutica.

## 6. Arquitectura y archivos vigentes

```text
main.py (raíz)
  └─ Docker Compose: db (PostgreSQL/PostGIS/pgRouting), app (ETL), web
      └─ 05_T2/pipeline.py
          ├─ BD/crear_bd.py + BD/schema.sql
          ├─ Infraestructura/generar_infraestructura.py → JSON → cargador
          ├─ Metadata/{osm_edificios,elevacion,viento}.py → JSON → cargadores
          ├─ Amenazas/{gpsjam,incendios_guerra,ucdp_eventos}.py → JSON → cargadores
          ├─ BD/asignar_pesos.py + BD/pesos.sql
          ├─ BD/rutas_ejemplo.py: pgr_dijkstra / pgr_KSP + métricas
          └─ BD/diagrama_bd.py → PNG/SVG
      └─ 05_T2/SitioWeb/app.py + static/: FastAPI y Leaflet
```

La base tiene **13 tablas**: procedencia (`fuentes`), navegación (`nodos`, `aristas`, `mision`), tres `meta_*`, tres `amz_*`, parámetros, rutas y evaluaciones. `BD/schema.sql` habilita PostGIS y pgRouting. El núcleo Python de [`05_T2/ruteo/`](05_T2/ruteo/) usa la biblioteca estándar para grafo, Dijkstra, Yen, fallas, simulador y métricas; [`experimentos/run_experimentos.py`](05_T2/experimentos/run_experimentos.py) ejecuta comparaciones por semillas sin requerir Docker.

Cada JSON de infraestructura, metadata, amenaza y rutas de ejemplo tiene un `ESTRUCTURA_*.md` asociado. Las descargas crudas, `Metadata/salida/`, `Amenazas/salida/` y `BD/salida/` están excluidas de Git, mientras que `Infraestructura/salida/infraestructura.json` y los resultados de ajuste sí figuran en esta copia. Por ello, un clon nuevo puede necesitar descargar datos antes de usar `--sin-descarga`. No leer ni copiar archivos `.env` o credenciales al preparar nuevos informes.

**Ejecución histórica documentada:** el 19 de octubre de 2026, `python main.py` terminó con código 0 y **18/18 pasos** del pipeline en `ok`, con PostGIS 3.5.2, pgRouting 3.8.0 y seis fuentes externas respondidas; se registraron **28/28 pruebas** correctas localmente y en la imagen. Es evidencia de esa corrida, no una prueba realizada al escribir este traspaso. Overpass tardó 614 segundos tras un HTTP 502 del servidor principal y respondió un espejo. Las iteraciones posteriores de `BD/diagrama_bd.py` mejoraron el trazado del diagrama; no cambiaron el algoritmo de rutas.

**Cuidado al ejecutar:** `main.py` inicia servicios y el pipeline recrea el esquema y sobrescribe salidas; `--sin-descarga` presupone JSON locales. `run_experimentos.py` usa por defecto el conjunto **`evaluacion`**: para exploración debe indicarse explícitamente `--conjunto ajuste`, sin tocar las semillas reservadas hasta congelar parámetros.

## 7. Fuentes usadas y qué permiten concluir

| Clase | Fuente actual | Dato y uso implementado | Límite científico |
|---|---|---|---|
| Metadata 1 | OSM/Overpass | Huellas y etiquetas `height`/`building:levels`; estima obstáculos cercanos a aristas. Primera corrida: **33.593 edificios**, **1.022** con altura estimada. | Alturas muy incompletas; tres metros por nivel es supuesto. La geometría de un edificio no define sola una ruta aérea. |
| Metadata 2 | Open-Meteo Elevation, Copernicus GLO-90 | Elevación en nodos y puntos medios; **814 muestras** en la primera corrida. | Resolución aproximada de 90 m; no resuelve detalles de fachadas o seguridad 3D. |
| Metadata 3 | Open-Meteo Historical Weather | **720 horas** de viento para un punto; umbral de admisibilidad y costo según dirección. | Dato regional, no viento medido sobre cada tramo; el extractor no fija explícitamente el modelo meteorológico en la petición. |
| Amenaza 1 | GPSJam | **7 celdas H3** extraídas; fracción histórica de días con baja precisión GNSS reportada por aeronaves ADS-B. | Indicador indirecto de aviones en altura, no medición de jamming contra UAV ni enlace de comunicaciones. Falta de celda no significa ausencia de interferencia. |
| Amenaza 2 | Modelo *war-fire* de The Economist sobre NASA FIRMS | **41 focos**: 26 históricos y 15 del período posterior; los primeros contribuyen al puntaje y los segundos pueden centrar fallas sintéticas. | Un foco térmico o su clasificación no prueba cierre de un segmento de vuelo. |
| Amenaza 3 | UCDP GED, vía HDX | **65 eventos** georreferenciados; densidad histórica para puntaje contextual. | Incertidumbre espacial variable, en algunos registros de decenas de km; no es barrera aérea. |

Se consideraron **OpenTopography**, **OpenWeather**, **ACLED** y **OpenAIP** durante la Tarea 1 o la Fase 0, pero **no son las seis fuentes principales del pipeline Tarea 2**. OpenSky tampoco se usa como infraestructura UAV: sus aeronaves y altitudes no representan los vuelos bajos simulados. PostGIS es el sistema de almacenamiento y consulta, no una fuente original de datos. Hay que revisar si los dos productos de Open-Meteo satisfacen el criterio docente de fuentes independientes de metadata, aunque proporcionan variables y endpoints distintos.

### Registros, puntajes y cierres: tres niveles distintos

1. Los proveedores publican **registros geográficos o temporales** con cobertura y precisión limitadas.
2. El proyecto deriva **atributos o puntajes contextuales** para las aristas; en SQL, `r_eventos`, `r_incendios` y `p_gnss` se agregan como `1 − (1 − r_eventos)(1 − r_incendios)(1 − p_gnss)`. Ese número entre 0 y 1 **no es una probabilidad calibrada de fracaso**; no se ha demostrado independencia estadística entre fuentes.
3. El simulador crea **fallas espaciales sintéticas** y reproducibles; solo estas cierran aristas dentro del experimento. Un evento UCDP, una celda GPSJam o un foco FIRMS nunca bloquea automáticamente una ruta real.

Ante datos faltantes, el código deja neutra la condición correspondiente en lugar de cerrar el tramo; ello facilita la ejecución, pero no valida la seguridad. OpenAIP no aporta una capa cargada de restricciones en esta implementación, aunque la interfaz conserve la preferencia visual de respetarlas.

## 8. Fallas, parámetros y costos

Una falla sintética es un disco `f=(centro, radio, activación)`, con radio uniforme entre **0,25 y 0,60 km**; se activa después de que el UAV haya recorrido una distancia elegida en `[0, 0,8·L*]` y cierra los segmentos que intersectan el disco. Por defecto se generan **3 fallas por escenario**: con probabilidad **0,5** se centran cerca de un foco y, si no, en otra parte del área. Los discos que cubren puntos obligatorios se remuestrean, por lo que la tasa de éxito está condicionada a excluir esos casos imposibles para todos los métodos. El UAV solo descubre bloqueos en las aristas incidentes al nodo que alcanza, sin percepción lejana, falsos positivos ni comunicación con otros vehículos.

Los parámetros por defecto de [`ruteo/config.py`](05_T2/ruteo/config.py) son **altura 60 m** sobre el despegue, **margen vertical 10 m**, **viento máximo 12 m/s**, **velocidad de crucero 12 m/s**, **desvío máximo `α=0,35`**, **presupuesto extra `β=0,60`**, **peso de riesgo `w_R=1`**, **`K=8` candidatas Yen**, pesos de longitud y solape iguales a 1, separación espacial `d_sep=0,4 km`, radio de incertidumbre `ρ=0,6 km` y penalización `γ=3`. Todos son **supuestos de simulación**, no límites operativos certificados.

El presupuesto de misión es `L_max=(1+β)L*`. Para seleccionar rutas se usa un costo en kilómetros equivalentes `c(e,u→v)=L_e·f_viento(u,v)·(1+w_R·r_e)·π_e`, donde `π_e=1+γ` cerca de un bloqueo descubierto y vale 1 en otros segmentos; la distancia realmente recorrida se sigue midiendo con `L_e`. Entre pares candidatos `(p,q)` se minimiza `J(p,q)=w_L·[(L(p)+L(q))/(2L_min)−1] + w_S·S(p,q) + w_R·[R(p)+R(q)]/2`. `S` mide proximidad espacial de corredores, no solo aristas idénticas: dos caminos paralelos pueden fallar juntos bajo un disco.

## 9. Algoritmos y atribución correcta

| Código | Estrategia | Qué permite aislar |
|---|---|---|
| `A` | Dos Dijkstra por km preparados antes de salir; frente a un bloqueo intenta la alternativa fija. | Línea base exigida. |
| `B` | Dos rutas más cortas de Yen, también fijas. | Tener dos opciones de Yen no garantiza separación. |
| `D` | Dijkstra por km que recalcula desde la posición actual tras descubrir bloqueos. | Beneficio de replanificar sin selección contextual. |
| `C` | Yen genera candidatas; selección por longitud, solape y riesgo, más replanteamiento con penalización local y control de presupuesto. | Propuesta completa del grupo. |
| `C0` | `C` sin penalización del entorno. | Aporte de la penalización `π`. |
| `C1` | `C` sin control de presupuesto. | Aporte de controlar la holgura. |

Para la línea base en pgRouting, la primera consulta `pgr_dijkstra` usa **solo longitud en km** y la segunda excluye las aristas de la primera ruta. Si esa exclusión desconecta el par, el código tiene un *fallback* que multiplica por diez el costo de las aristas iniciales: **ese caso ya no satisface literalmente el costo exclusivamente kilométrico y debe declararse por separado**. Las rutas del método propuesto se obtienen mediante Yen/`pgr_KSP`; Yen solo enumera candidatos y no garantiza resiliencia. La selección `J`, la penalización espacial tras un bloqueo y el control de presupuesto son componentes diseñados en este proyecto, no resultados atribuidos al artículo de Yen o al de Luna.

En la simulación, la alternativa precalculada de `C` se usa para medir calidad del par, pero ante una falla `C` **recalcula un Dijkstra** y no necesariamente sigue aquella alternativa. Esto explica por qué la ventaja frente a `A` puede deberse a replantear en general; la comparación con `D` es necesaria para atribuir cualquier beneficio específico a la propuesta.

## 10. Protocolo y resultados conocidos

La métrica principal es **`R_mision`**, proporción de escenarios donde se visitan `P1`, `P2` y `P3` en orden y se llega a `B` dentro de `L_max`. **`R_par`** mide la proporción de tramos y escenarios en que al menos una de las dos rutas precalculadas permanece libre; no representa recuperación durante vuelo ni éxito de la misión completa. Se registran además km, sobrelongitud, replanificaciones, fracción de puntos alcanzados en fallidas y tiempo de cálculo. `ΔR=100·(R_C−R_A)` se informa en **puntos porcentuales** y la prueba exacta de McNemar usa escenarios pareados.

La separación de semillas en código es **ajuste `0–99`**, **evaluación reservada `10.000–10.299`** y **sitio `20.000–20.099`**. Los archivos de [`05_T2/resultados/`](05_T2/resultados/README.md) contienen solo ajuste: el simulador Python genera grafo, focos y eventos históricos **sintéticos** y evalúa los cuatro tramos de la misión. No se deben mezclar sus cifras con el ejemplo de PostGIS/pgRouting, que carga fuentes externas y consulta un par entre el primer y el último nodo de `mision`.

| Escenarios de ajuste (100 por fila; `prob_foco=0,5`) | `A` | `B` | `D` | `C` | Lectura |
|---|---:|---:|---:|---:|---|
| 3 fallas, `β=0,60` | 0,91 | 0,82 | 0,96 | 0,97 | `C` mejora al par fijo, casi empata con replanificación simple. |
| 5 fallas, `β=0,60` | 0,87 | 0,73 | 0,96 | 0,97 | `C−A=+10` pp (`p=0,01294`); `C−D=+1` pp (`p=1`). |
| 5 fallas, `β=0,20` | 0,75 | 0,72 | 0,94 | 0,90 | Con poca holgura, `D` supera a `C`. |
| 5 fallas, `β=0,10` | 0,70 | 0,71 | 0,91 | 0,84 | La diferencia `C−D` es −7 pp. |

Con cinco fallas y `β=0,60`, `R_par` fue **0,94 para C**, **0,9075 para A** y **0,875 para B**. `C` tardó unos **34,42 ms** de cálculo medio por misión, frente a **1,46 ms** de `A` y **0,75 ms** de `D` en esa corrida local. La evidencia respalda una mejor separación del par, pero no prueba que ella cause el aumento de `R_mision`; bajo presupuestos estrechos, el costo inicial de evitar riesgo puede consumir la holgura que luego se necesita para desviarse. La hipótesis principal frente a `A` es refutable y queda pendiente de la evaluación reservada; el aporte adicional frente a `D` tampoco está respaldado por el ajuste disponible.

### Hallazgo de la primera corrida con datos externos

La corrida completa inicial obtuvo rutas de ejemplo entre los nodos 15 y 181 y tasas de resiliencia, **pero esas tasas no deben presentarse como vigentes**. En `comun/resiliencia.py`, `focos_bd` buscaba focos de evaluación dentro del recorte estricto, mientras las descargas cubrían el recorte **más 5 km**; los 15 focos del período de evaluación quedaron en ese anillo y la búsqueda cayó a 3 focos **históricos**, que ya habían alimentado `r_incendios`. La consulta fue ampliada a `bbox(BUFFER_KM)` en el commit `abbfbc4`, por lo que falta regenerar y verificar `BD/salida/rutas_ejemplo.json` y las cifras del sitio.

**Discrepancia documental detectada:** `05_T2/README.md` dice que también los JSON de `resultados/` proceden de ese fallback histórico. El código de `experimentos/run_experimentos.py` muestra que esos JSON usan `generar_focos` sintético y **no llaman `focos_bd`**; la corrección de `comun/resiliencia.py` afecta al ejemplo de BD/sitio, no recalcula automáticamente los experimentos Python guardados. Conviene aclarar el README antes de entregar, sin borrar los resultados de ajuste.

## 11. Archivos de entrega y estado de Git

- **Informe:** [`05_T2/Informe_Tarea_2_Ruteo_Resiliente_UAV.tex`](05_T2/Informe_Tarea_2_Ruteo_Resiliente_UAV.tex), borrador actual con introducción, contexto, fuentes, restricciones, algoritmo, metodología, resultados preliminares, limitaciones y bibliografía. Mantener lenguaje académico en tercera persona; presentar los hallazgos del análisis sin atribuirlos a comentarios de corrección y usar transiciones fluidas entre ideas. El `.tex` no se compiló porque no había un ejecutable LaTeX disponible en este entorno; solo se revisaron estructura y citas de forma estática.
- **Presentación:** [`05_T2/entrega/`](05_T2/entrega/) contiene varias versiones `.pptx`, incluida una de 12 diapositivas. Conviene identificar una sola versión final, revisar visualmente sus cifras y capturas, y comprobar que la rúbrica se evidencia en la presentación.
- **Git:** la rama local `tarea-2` rastrea `origin/tarea-2` en GitHub. El `.tex`, la carpeta `05_T2/entrega/` y varios documentos de contexto aparecen **sin seguimiento** en el `git status` observado; no se ha creado aquí un commit ni un remoto GitLab UDP. El README de la raíz aún afirma que no hay remoto o implementación de Tarea 2 y está obsoleto.
- **Datos reproducibles:** el `.gitignore` excluye `.env`, credenciales, cachés y JSON externos voluminosos. Antes de publicar en GitLab UDP deben revisarse los archivos a añadir y la licencia/procedencia de datos o documentos externos, sin imprimir secretos.

## 12. Próximas decisiones y secuencia recomendable

1. **Acordar el alcance científico exacto:** mantener un UAV con inspección de puntos o ampliar explícitamente a varios vehículos y transferencia de alertas. La segunda opción no está implementada; afirmar una red mesh o cobertura poligonal completa con el código actual sería incorrecto.
2. **Congelar el método antes de evaluar:** decidir si se ajustan `w_R`, `γ` u otras reglas usando solo ajuste; conservar `D` como control y no ocultar un resultado desfavorable.
3. **Regenerar el ejemplo conectado a la BD** después del arreglo de focos, confirmar el origen temporal de los centros de falla, comparar rutas pgRouting con el núcleo Python y verificar que el fallback de la segunda ruta Dijkstra no se presente como costo solo km.
4. **Comprobar el sitio y la presentación:** interacción origen/destino, preferencias, capas, dos rutas por método, etiquetas correctas de `R_par` y `R_mision`, capturas de ETL y evidencia de cada criterio de la rúbrica.
5. **Ejecutar una sola evaluación reservada** (`10.000–10.299`) una vez fijados parámetros y código; registrar versión, semillas, resultados y cualquier desviación respecto de la hipótesis. Repetir solo si existe una razón metodológica documentada.
6. **Cerrar entrega:** armonizar README raíz y documentos técnicos desactualizados, decidir qué archivos `.pptx` compartir, añadir informe/presentación a Git y confirmar acceso, proyecto y ramas del GitLab UDP sin alterar silenciosamente el remoto GitHub.

## 13. Ruta de lectura para Claude

1. Leer este archivo y [`05_T2/README.md`](05_T2/README.md) para entender la implementación y su estado.
2. Leer el [enunciado/rúbrica](01_PROYECTO_ACTUAL/ENUNCIADO_Y_RUBRICA_TAREA_2.txt), [`05_T2/ENTREGA_TAREA2.md`](05_T2/ENTREGA_TAREA2.md) y el [informe `.tex`](05_T2/Informe_Tarea_2_Ruteo_Resiliente_UAV.tex).
3. Contrastar cualquier afirmación algorítmica con [`ruteo/config.py`](05_T2/ruteo/config.py), [`ruteo/algoritmos.py`](05_T2/ruteo/algoritmos.py), [`ruteo/fallas.py`](05_T2/ruteo/fallas.py), [`ruteo/simulador.py`](05_T2/ruteo/simulador.py), [`experimentos/run_experimentos.py`](05_T2/experimentos/run_experimentos.py) y los JSON conservados en `resultados/`.
4. Para la rama SQL/sitio, leer `BD/schema.sql`, `BD/pesos.sql`, `BD/MODELO_BD.md`, `comun/rutas.py`, `comun/resiliencia.py`, `comun/servicio.py`, `SitioWeb/app.py` y `SitioWeb/static/`.
5. Solo para historia del cambio de enfoque, consultar la [Tarea 1](03_TAREA_1/README.md), la [charla transcrita](02_REUNION_PROFESOR/Charla_profesor.txt), [V3](CONTEXTO_INTEGRAL_CODEX_RUTEO_UAV_2026_V3.md) y la [auditoría Fase 0](01_PROYECTO_ACTUAL/FASE_0_AUDITORIA_Y_FACTIBILIDAD.md), recordando que sus secciones de estado quedaron desactualizadas.

**Regla interpretativa final:** distinguir siempre (a) hechos documentados de Mykolaiv, (b) registros públicos descargados, (c) puntajes y restricciones derivados por reglas del grupo, (d) fallas y rutas simuladas y (e) resultados efectivamente ejecutados. La relación entre jamming y un cierre de ruta sigue siendo una **hipótesis abstracta de escenario**, no una observación demostrada en el caso de estudio.

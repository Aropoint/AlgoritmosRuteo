# Estado del proyecto de ruteo resiliente UAV y decisiones para la Tarea 2

**Fecha de revisión:** 17 de octubre de 2026  
**Propósito:** dejar en un solo lugar lo realizado en la Tarea 1, la retroalimentación recibida, el estado real del código y las decisiones necesarias antes de implementar la Tarea 2.

## 1. Conclusión principal

El proyecto nació como una extensión de **CLUN-LSR**, un protocolo de **ruteo de paquetes entre UAV** cuando el jamming afecta la comunicación. En ese modelo, cada dron es un nodo y las rutas indican por cuáles UAV viajan los datos. Este sigue siendo el antecedente científico de la Tarea 1, pero **la conversación posterior con el profesor cambió la dirección del proyecto**: usar la pérdida de reporte de un UAV como alerta para que los siguientes **modifiquen su trayectoria física**. El grupo eligió como misión **reconocer una zona delimitada**. La explicación y sus límites están en [Enfoque tras la charla con el profesor](ENFOQUE_TRAS_CHARLA_PROFESOR.md).

La Tarea 1 produjo un informe, scripts de consulta a fuentes externas, archivos de evidencia y una base PostGIS con capas espaciales. Eso demuestra acceso e integración de datos, **no valida todavía un algoritmo de ruteo resiliente**. La Tarea 2 exige construir y comparar rutas, medir resiliencia y exponer el resultado en una aplicación. Con el enfoque acordado, el grafo de pgRouting representa **puntos de paso y tramos de vuelo**, y la cobertura confirmada de la zona pasa a ser un resultado central. CLUN-LSR puede aportar la idea de usar información de comunicaciones para activar el cambio de ruta, pero **no debe presentarse como algoritmo de planificación física**.

## 2. Qué se hizo para la Tarea 1

### 2.1 Base científica y propuesta

Se escogió el artículo de Zheng y colaboradores, [*Cross-layer UAV network routing protocol for spectrum denial environments*](https://doi.org/10.1016/j.adhoc.2024.103702), como base de CLUN-LSR. El protocolo utiliza información espectral de una capa inferior para avisar a la capa de red sobre nodos afectados, actualizar vecinos y topología, y recalcular rutas. La implementación del artículo sobre MP-OLSR también contempla múltiples caminos.

La propuesta del grupo fue complementar esa lógica con topografía, edificaciones, clima y capas geoespaciales de riesgo. También se discutió un costo de enlace con penalizaciones espaciales y una regla para excluir enlaces inviables. **No hay una implementación ni una evaluación de ese costo con rutas en los archivos disponibles.** El artículo original sí considera movilidad y usa una simulación con propagación Two-Ray y *shadowing* constante; no conviene describirlo como una simple simulación estática o enteramente en espacio libre.

El repositorio conserva el PDF entregado y una fuente LaTeX corregida. **No consta en estos archivos que el ayudante haya reevaluado y aprobado esa fuente**. Su objetivo general continúa centrado en «diseñar y validar una infraestructura de datos geolocalizados», mientras que la retroalimentación pidió diseñar y validar el algoritmo.

### 2.2 Código, datos y resultados verificables

El directorio [`04_VALIDACION_TAREA_1/validacion_ruteo/`](../04_VALIDACION_TAREA_1/validacion_ruteo/README.md) contiene scripts de consulta para OpenSky, OpenTopography, OpenWeather, OpenCellID, OSM/Overpass, GPSJam, ACLED y OpenAIP. `run_all.py` los ejecuta y deja un resumen; otro script importa cuatro GeoJSON a PostgreSQL/PostGIS, y `postgis_evidence.py` registra consultas de comprobación. El [`main.py` de las pruebas iniciales](../03_TAREA_1/pruebas_iniciales/main.py) es anterior y **solo descarga un DEM**; no orquesta el flujo completo de la Tarea 2.

| Recurso | Resultado registrado | Qué demuestra y qué no |
|---|---|---|
| OpenSky | La consulta local a Santiago no entregó posiciones utilizables. El reintento global produjo 7.771 posiciones en el registro de ejecución; una versión del informe menciona 7.635. | Prueba acceso a estados de aeronaves. No demuestra posiciones de una flota UAV cooperativa ni enlaces entre drones. Las cifras de distintas ejecuciones deben fecharse y reconciliarse. |
| OpenTopography | DEM de 360 × 360 celdas para un sector de Santiago; cotas de terreno entre 440 y 1.881 m. | Aporta relieve. No entrega alturas de vuelo ni, por sí solo, línea de vista calculada entre UAV. |
| OpenWeather | Respuesta puntual de condiciones meteorológicas para Santiago. | Aporta contexto operacional; un punto no describe todo el espacio ni prueba degradación del enlace de datos. |
| OSM/Overpass | 236.791 polígonos simples de edificios exportados. | Aporta huellas de edificios; para bloqueo 3D se necesitan alturas fiables y una prueba geométrica tridimensional. |
| OpenCellID | Reintento con área menor: estimación de 2.333 celdas y 50 registros detallados. | Muestra infraestructura celular, no ocupación de un canal Wi-Fi ni jamming de la radio UAV. |
| GPSJam | 48.781 celdas H3 globales convertidas a polígonos; 509 con `percent_bad > 10` en la prueba. | Indica degradación de calidad GNSS inferida de ADS-B; no verifica jamming del enlace de comunicación entre UAV. |
| ACLED | 235 eventos de una fecha histórica disponible para Ucrania, como puntos. | Aporta eventos de conflicto contextual; no mide interferencia RF. Un radio o duración de efecto serían supuestos del modelo. |
| OpenAIP | 27 polígonos chilenos de espacios restringidos, peligrosos o prohibidos, filtrados de 36 registros. | Aporta restricciones operacionales de vuelo; cruzar el segmento de radio con un polígono horizontal no demuestra que el enlace esté bloqueado. |
| PostGIS | Cuatro tablas con SRID 4326 e índices espaciales; una línea de prueba intersectó un polígono OpenAIP. | Prueba carga y consulta espacial. La línea fue creada para validación: no es una ruta generada por un algoritmo. |

Los resultados numéricos proceden de las evidencias locales de septiembre de 2026 y describen **consultas puntuales**, no tasas de ocurrencia de jamming ni desempeño de CLUN-LSR. También mezclan zonas y tiempos: Santiago para relieve, edificios y clima; datos globales de OpenSky y GPSJam; Ucrania para ACLED. Antes de evaluar una ruta hay que seleccionar **una zona de estudio y una ventana temporal coherentes**.

El informe de la Biblioteca del Congreso Nacional, *Jamming: Caracterización y estatus legal en Chile y otros países* (junio de 2024), sirve como antecedente general sobre interferencia y usos delictuales contra GPS, telefonía y alarmas. **No acredita por sí mismo ataques a una red mesh de UAV en Chile.** Sus afirmaciones legales deben tratarse como información fechada en 2024, no como un estado normativo verificado para 2026.

### 2.3 Estado técnico al cierre de esta revisión

- **Hecho:** scripts de extracción y transformación para varias fuentes; evidencia guardada; PostGIS local con tablas de polígonos y puntos; prueba `ST_Intersects`.
- **Propuesto, pero no construido:** grafo de UAV y enlaces que cambian con el tiempo, enlace factible según alcance y línea de vista 3D, pesos derivados de metadatos/amenazas, integración operativa con CLUN-LSR.
- **No encontrado en el código revisado:** tablas de nodos/aristas de UAV para pgRouting, extensión pgRouting en Docker, llamadas a `pgr_dijkstra`, generación de dos rutas por alternativa, métrica implementada de resiliencia, sitio Leaflet y un proceso raíz que ejecute todo de extremo a extremo.
- **Pendiente de seguridad:** el `main.py` antiguo contiene una clave API incrustada y existen archivos de credenciales en el área de trabajo. Antes de compartir código, mover secretos a variables de entorno, excluirlos del repositorio y rotar los que se hayan divulgado. No copiar claves a la presentación ni al informe.

## 3. Qué significan los reparos de la primera entrega

La retroalimentación escrita del ayudante puede convertirse en las siguientes acciones. Se conservan los números indicados por el grupo para poder volver a los comentarios originales.

| Nº | Reparo | Corrección que debe verse en la siguiente entrega |
|---:|---|---|
| 1 | Se afirmó que la problemática ocurre sin indicar cuánto. | Citar cifras verificables del escenario escogido o formularlo expresamente como **riesgo experimental**, sin afirmar una frecuencia real no medida. Distinguir incidentes, equipos adquiridos y prevalencia. |
| 2 | Se calificó de «mucho tiempo» la reacción al jamming sin referencia. | Indicar protocolo, métrica, condiciones y valor de comparación. El artículo base reporta tiempos en sus experimentos; esos valores son del artículo, no una media universal de los UAV. |
| 3 | Se formuló un grafo estático para nodos móviles. | Usar `G(t) = (V(t), E(t))`: posiciones con marca temporal, enlaces que aparecen/desaparecen y recálculo por instantáneas o eventos. |
| 4 | La hipótesis «será posible estudiar» no era refutable. | Predecir un resultado medible frente a una línea base, en escenarios y condiciones declarados. Una hipótesis que no mejore la métrica elegida debe poder resultar falsa. |
| 5 | El objetivo general se centró en crear una base de datos. | Definir como producto principal un **algoritmo de ruteo resiliente implementado y validado**; la BD es una herramienta de apoyo. |
| 6 | Los objetivos quedaron limitados a la primera entrega. | Cubrir extracción, grafo, algoritmo, evaluación y comparación final. |
| 7 | Un objetivo era genérico para cualquier proyecto del curso. | Nombrar la red UAV, la amenaza concreta, el mecanismo de recálculo y la métrica del proyecto. |
| 8 | «Depurar APIs» es una tarea de desarrollo, no un objetivo científico. | Moverlo al plan de trabajo o a la metodología; reemplazarlo por un objetivo evaluable sobre rutas o resiliencia. |
| 9 | Un objetivo específico sí fue considerado válido. | Conservar su enfoque particular y conectarlo con resultados del algoritmo, sin repetir objetivos de infraestructura. |
| 10 | Se comparó la cota máxima de 1.881 m del DEM con la altura de un avión comercial. | Identificar 1.881 m como **altura del terreno** en el recorte, no como altitud de aeronave. Separar elevación sobre el nivel del mar y altura sobre el terreno. |
| 11 | Se cruzaron edificios de Santiago con vuelos comerciales muy altos de OpenSky. | Dejar de usar esas aeronaves como si fueran UAV a baja altura. Emplear posiciones UAV observadas si existen o movilidad simulada explícita; usar edificios solo cuando la altura y línea de vista los hagan relevantes. |
| 12 | Se habló de un modelo «real» representado solo en 2D. | Guardar posiciones 3D, alturas de edificios cuando existan, altitud de drones y límites verticales del espacio aéreo. Un mapa Leaflet 2D puede ser la interfaz, pero no sustituye el cálculo 3D. |
| 13 | Había contenido repetido. | Unificar explicación del modelo, eliminar repeticiones y priorizar método, resultados y límites. |
| 14 | Faltaron citas para afirmaciones, figuras y tablas. | Citar cada antecedente externo y cada fuente de datos; numerar figuras/tablas, indicar procedencia, fecha, área y si el dato es real o simulado. |

En las capturas de la rúbrica se observan resultados especialmente débiles para la **hipótesis**, la **problemática** y varios objetivos/elementos de infraestructura. Los buenos resultados parciales de factibilidad y metadatos **no equivalen a validación del problema ni del algoritmo**.

## 4. Cómo contextualizar mejor el proyecto

### El problema que hay que contar

La frase central ahora debe describir **qué zona se reconoce, qué información debe llegar a la estación de control, por qué hay varios UAV sucesivos y cómo cambia la trayectoria de los siguientes cuando se pierde el reporte de uno**. El jamming es una posible causa del evento, no una conclusión automática a partir del silencio. La red de comunicación sigue siendo necesaria para compartir la alerta, pero el producto principal es una **ruta de vuelo adaptada** y la cobertura conseguida.

Hay antecedentes chilenos sobre [drones que introducen contrabando en cárceles y uso de inhibidores para detenerlos](https://www.subinterior.gob.cl/noticias/2022/11/11/subsecretario-monsalve-detalla-medidas-para-combatir-el-crimen-organizado/), además de [inversiones en vigilancia y neutralización antidrones](https://www.subinterior.gob.cl/noticias/2023/12/01/gobierno-invierte-cerca-de-5-mil-millones-en-tecnologia-para-seguridad-carcelaria/). Sirven para mostrar que el jamming antidrones existe en Chile, pero **no prueban un caso de red UAV cooperativa que necesite reconectar rutas**. No conviene presentar ese escenario como si los inhibidores fueran usados por criminales para cegar una red de drones de vigilancia.

En México existe un antecedente más cercano al **adversario que interfiere vigilancia aérea**: [Intelligence Online informó en julio de 2025](https://www.intelligenceonline.com/americas/2025/07/02/skyfend-discreet-chinese-provider-of-anti-drone-tech-to-mexican-cartels,110471806-art) que fuerzas mexicanas incautaron en Durango equipos SkyFend vinculados al Cártel de Sinaloa, empleados para interferir drones tácticos del Ejército. [Milenio reportó](https://www.milenio.com/policia/mayiza-combate-fuerzas-armadas-equipo-anti-dron-elite), citando fuentes de seguridad, el uso de equipos de inhibición por la facción La Mayiza contra UAV de las fuerzas armadas. Por separado, la [Secretaría de Seguridad Pública de Sinaloa confirmó](https://www.sspsinaloa.gob.mx/post/cargadores-municiones-equipo-t%C3%A1ctico-y-bater%C3%ADas-para-dron-fueron-asegurados-por-el-grupo-interinst) la incautación de una batería de sistema antidrones SkyFend en San Ignacio. Esta confirmación oficial acredita el hallazgo de un componente, **no documenta por sí sola un ataque concreto ni su efecto sobre un enlace**. Ninguna de estas fuentes aporta una red mesh gubernamental, trazas de pérdida de paquetes o recuperación de rutas.

Para **rutas terrestres**, sí hay misiones de vigilancia con UAV: [CBP describe el uso de drones pequeños](https://www.cbp.gov/frontline/cbp-small-drones-program) para detectar y seguir, entre otros, a traficantes de droga en la frontera; el [Gobierno mexicano informó de drones desplegados en carreteras](https://www.gob.mx/presidencia/prensa/gobierno-de-mexico-presenta-estrategia-especial-cero-robos-para-carreteras-mexico-puebla-mexico-queretaro-y-culiacan-mazatlan?idiom=en), aunque ese operativo trata de **robos**, no acredita una ruta concreta de narcotráfico; y un [comunicado oficial de octubre de 2026](https://gabinetedeseguridad.gob.mx/contenido/9852/despliegan-500-efectivos-del-ejercito-y-guardia-nacional-con-el-apoyo-de-dos-helicopteros-de-la-fuerza-aerea-en-la-frontera-de-tamaulipas) menciona drones y equipos antidrones en una operación fronteriza contra tráfico de drogas y personas. En esta última, los **equipos antidrones los llevan las autoridades**. Los reportes sobre SkyFend en manos criminales respaldan por separado la amenaza contraria, pero **no hay prueba pública revisada de que una patrulla de UAV en esa ruta terrestre sufriera jamming criminal y recuperara comunicación mediante una red mesh**.

Como antecedente de **flota cooperativa**, el [ensayo británico de 20 UAV en RAF Spadeadam](https://www.gov.uk/government/news/swarming-drones-concept-flies-closer-to-reality) es especialmente pertinente. Los [requisitos oficiales del programa](https://www.gov.uk/government/publications/competition-many-drones-make-light-work-phase-3/competition-document-many-drones-make-light-work-phase-3) incluían una red mesh que se adaptara a interferencia accidental o deliberada. El informe público de la prueba **no confirma que se aplicara jamming en esa ejecución** y no aporta todas las trayectorias o mediciones RF necesarias para reproducirla.

### Qué contexto estudia realmente CLUN-LSR

El [artículo base](https://doi.org/10.1016/j.adhoc.2024.103702) motiva su propuesta en operaciones de UAV en un **entorno de conflicto con denegación del espectro**. No identifica una misión, ciudad, unidad operativa o ataque histórico concreto que el grupo pueda adoptar como caso de estudio. Los autores comparan protocolos en el simulador EXata con movilidad de UAV y jamming modelado. Esto respalda la **pertinencia técnica** del problema, pero no constituye una cifra de incidencia en una operación real.

La red se parece a una **malla ad hoc de múltiples saltos**: cada UAV conoce vecinos a su alcance y puede retransmitir datos de otro. Si una ruta `A → B → C` queda afectada, los paquetes pueden usar `A → D → C` **si esos enlaces alternativos existen**. El algoritmo cambia la ruta de los datos, no necesariamente el recorrido de vuelo. CLUN-LSR supone sensado espectral en la capa de enlace, difusión de un aviso por una antena de gestión, actualización de tablas de vecinos/topología y recálculo de rutas; su aplicación sobre MP-OLSR permite múltiples caminos. Una red completamente particionada no puede reconectarse solo cambiando el algoritmo.

### Investigación internacional y local acumulada

| Lugar y fecha | Hecho respaldado por fuentes | Relación y límite para el proyecto |
|---|---|---|
| **Chile, cárceles; 2018–2023** | [Gendarmería informó](https://html.gendarmeria.gob.cl/doc/cuenta_publica2018.pdf) del ingreso de drogas y objetos prohibidos mediante drones y planificó adquirir cuatro equipos portátiles antidrones. Una [cuenta pública posterior](https://html.gendarmeria.gob.cl/doc/CuentaPublica_InformeE_2023_.pdf) registra tres neutralizadores y dos drones de vigilancia en Arica. En una [sentencia sobre Santiago Sur](https://www.diarioconstitucional.cl/wp-content/uploads/2023/10/Fallo183-2023traficoCDPSantiagoSur.pdf183-2023.pdf), un funcionario describió una «pistola inhibidora» de Gendarmería. | Hay jamming antidrones documentado, pero la defensa neutraliza **drones intrusos**. No hay prueba de criminales interfiriendo una red mesh de UAV de vigilancia; tampoco una estadística pública de incidencia de ese supuesto. |
| **México, Durango y Sinaloa; 2025** | [Intelligence Online](https://www.intelligenceonline.com/americas/2025/07/02/skyfend-discreet-chinese-provider-of-anti-drone-tech-to-mexican-cartels,110471806-art) informó de equipos SkyFend incautados en Durango y usados para interferir drones tácticos del Ejército; [Milenio](https://www.milenio.com/policia/mayiza-combate-fuerzas-armadas-equipo-anti-dron-elite) atribuyó a La Mayiza inhibidores contra UAV militares. La [Secretaría de Seguridad Pública de Sinaloa](https://www.sspsinaloa.gob.mx/post/cargadores-municiones-equipo-t%C3%A1ctico-y-bater%C3%ADas-para-dron-fueron-asegurados-por-el-grupo-interinst) confirmó por separado la incautación de una batería antidrones SkyFend. | Es un contexto regional cercano de **interferencia criminal contra drones de autoridades**. Los reportes públicos no muestran una misión gubernamental con UAV en malla, tasas de fallas, telemetría del ataque ni evidencia de que se haya recuperado una ruta de datos; la incautación oficial de una batería tampoco verifica por sí sola el uso operativo. |
| **Ucrania, guerra; análisis publicados en 2025** | Un [análisis del Ejército de EE. UU.](https://www.army.mil/article/284546/adapting_to_multi_domain_battlefield_developing_emissions_control_sop) afirma que Rusia ha interferido enlaces de drones ucranianos con estaciones de control, dificultando obtención de información e identificación de objetivos. Un [estudio de CSIS](https://www.csis.org/analysis/lessons-ukraine-conflict-modern-warfare-age-autonomy-information-and-resilience), basado en entrevistas, describe interferencia localizada contra UAV de reconocimiento y ataque de ambos bandos. El [Ministerio de Defensa ucraniano](https://mod.gov.ua/en/news/raybird-a-small-birdie-with-the-capabilities-of-a-large-aircraft) presenta la guerra electrónica como amenaza para un UAV de reconocimiento en servicio. | Es la evidencia más directa de jamming contra **vigilancia/reconocimiento**. Las fuentes no demuestran que esos UAV formaran una red mesh entre aeronaves como la del paper. |
| **Reino Unido, RAF Spadeadam; ensayo informado en 2021** | Se [ensayó una flota cooperativa de 20 UAV](https://www.gov.uk/government/news/swarming-drones-concept-flies-closer-to-reality). El [programa oficial](https://www.gov.uk/government/publications/competition-many-drones-make-light-work-phase-3/competition-document-many-drones-make-light-work-phase-3) requería comunicaciones mesh adaptables a interferencia accidental y deliberada. | Coinciden el uso multi-UAV y la amenaza prevista; **no se confirmó públicamente que el ensayo concreto aplicara jamming**. |
| **Estados Unidos, Yuma; ensayo DARPA informado en 2019** | [DARPA informó](https://www.darpa.mil/news/2019/code-success) de seis UAV reales y otros virtuales que continuaron una misión cooperativa cuando las comunicaciones estaban fuera de servicio y el GPS no estaba disponible. | Prueba la relevancia de operar varios UAV bajo pérdida de comunicaciones; no prueba que CLUN-LSR se haya usado ni que la pérdida se causara por jamming real. |
| **Ensayo de campo académico publicado en 2025** | Un [artículo de IEEE](https://ieeexplore.ieee.org/document/10975949/) describe comunicación aérea multisalto y cambio automático de ruta tras fallas de enlace en drones reales. | Respalda que una **ruta de comunicación** entre UAV puede ser objeto de evaluación práctica; no es una prueba de jamming en ese ensayo. |
| **Letonia y Estados Unidos; ejercicios de 2025** | La [OTAN en Letonia](https://www.ncia.nato.int/newsroom/news/ncia-and-latvia-host-joint-exercise-to-enhance-defence-readiness-against-threats-on-latvian-border) entrenó defensa contra UAV adversarios de vigilancia/reconocimiento con técnicas de guerra electrónica. El [Ejército de EE. UU. en Fort Novosel](https://www.army.mil/article/283940/fort_novosel_doubles_down_on_drone_threat_in_dual_exercises) ejercitó la detección y neutralización de drones con inhibidores. | Muestran escenarios de entrenamiento actuales, **no combates documentados de una red mesh interferida**. |

**Interpretación de la evidencia:** hay casos reales de interferencia contra UAV de vigilancia y hay casos reales de flotas cooperativas y enlaces multisalto. Las fuentes públicas revisadas **no muestran conjuntamente** un caso operacional concreto con flota mesh, posiciones y enlaces observados, jammer documentado y registros de recuperación de rutas. Presentar esos elementos como un único hecho sería mezclar fuentes. Sí pueden combinarse como **motivación para diseñar un experimento declarado como tal**.

**Tres fenómenos distintos:** (1) jamming del enlace de control, video o datos, que puede cortar la comunicación que rutea CLUN-LSR; (2) interferencia GNSS, que afecta posicionamiento/navegación y no prueba que se haya cortado el video o el enlace de datos; y (3) interferencia de radar, que afecta otro sistema. Una pérdida de control tampoco implica siempre que el dron deje de registrar imágenes: el efecto sobre la vigilancia depende de cómo se obtienen y transmiten los datos.

### Opciones honestas para la siguiente formulación

1. **Aplicación civil chilena con estrés experimental:** escoger una operación plausible que requiera varios UAV y retransmisión de datos, por ejemplo una búsqueda coordinada o monitoreo de una zona extensa. La aplicación debe sustentarse con fuentes propias; el jamming se declara **amenaza simulada**, no incidente cotidiano demostrado. Usar geografía real y movilidad/mediciones RF observadas solo donde existan.
2. **Ensayo internacional como caso de referencia:** usar el programa británico para justificar una red multi-UAV en entorno de comunicaciones contestadas. La topología y el evento de interferencia usados en el trabajo serían un escenario de evaluación propio si no hay trazas públicas del ensayo.
3. **Escenario mexicano inspirado en un incidente documentado:** usar los reportes sobre inhibidores en poder de una facción del Cártel de Sinaloa para justificar la amenaza a drones gubernamentales. Proponer una misión de vigilancia con varios UAV como **diseño experimental hipotético**, sin afirmar que la red mesh o su recuperación de rutas hayan sido observadas en Durango o Sinaloa. Explicar por qué esa misión requiere retransmisión entre aeronaves.
4. **Replantear la amenaza, si el profesor exige frecuencia cotidiana documentada:** estudiar pérdida de enlaces por movilidad, relieve u obstrucción y dejar el jamming como un escenario adicional. Esto conserva el problema de ruteo de comunicaciones, pero cambia la hipótesis y obliga a explicar cuánto se aparta de CLUN-LSR.

**Actualización tras la reunión:** las cuatro opciones anteriores registran la exploración previa. El profesor orientó el proyecto hacia **ruteo físico de UAV después de una alerta de pérdida**; el grupo eligió reconocimiento de una zona. La elección de región, artículo de planificación física y modelo exacto de alerta siguen pendientes. Los casos de Chile, México y Ucrania son antecedentes posibles, no pruebas de que el experimento de rutas ocurrió allí.

## 5. Modelo y evaluación que sí responderían al curso

**Misión elegida:** varios UAV realizan vuelos sucesivos de reconocimiento de un polígono. El grafo de rutas físicas `G(t)=(V,E(t))` tiene **puntos de paso 3D** como vértices y **tramos de vuelo factibles** como aristas. La alerta sobre la pérdida de reporte de un UAV anterior modifica temporalmente el estado o costo de los tramos cercanos a su última posición conocida. El siguiente UAV puede tomar otro trayecto y seguir observando la zona. La pérdida de reporte señala **incertidumbre**; no identifica automáticamente un jammer ni demuestra que el UAV fue destruido.

Para comparar métodos en un alcance abordable, ambos deben cubrir el **mismo polígono** con la **misma secuencia de puntos de observación** y el mismo radio de observación supuesto. La línea base une esos puntos con `pgr_dijkstra` y costo de kilómetros. La alternativa adapta los tramos restantes al recibir una alerta. La secuencia de puntos puede ser fija al principio; optimizarla es una extensión distinta. La superficie «cubierta» debe ser la que el sensor observó **y cuya información alcanzó al sistema**, según la regla explícita de la simulación. Si no se modela transmisión, debe llamarse solo «superficie geométricamente observada».

**Hipótesis de trabajo, refutable:** «Bajo los mismos escenarios de pérdida simulada, una planificación que incorpora alertas recientes de UAV predecesores mantendrá una mayor proporción de área reconocida y reportada que la selección de tramos por distancia, sin superar un límite de recorrido adicional fijado previamente». La hipótesis falla si la cobertura no mejora o el desvío excede el límite. Los escenarios de falla deben generarse **independientemente del costo usado para seleccionar rutas**.

**Objetivo general propuesto:** diseñar, implementar y evaluar un algoritmo de ruteo físico resiliente para UAV que reconocen una zona delimitada, adaptando trayectorias tras pérdidas de reporte y comparándolo con rutas por distancia. La BD, el ETL y el mapa apoyan esa evaluación. Si se quiere medir PDR, *throughput* o tiempo de reconexión de datos, hace falta una simulación adicional de comunicaciones; la planificación espacial sola no produce esas métricas.

**Papel del artículo base:** CLUN-LSR sustenta la idea de que la capa de comunicaciones puede entregar alertas útiles de manera temprana. Su algoritmo no calcula trayectorias físicas. Para cumplir el requisito de «algoritmo elegido y paper» en el nuevo enfoque hay que fundamentar la **planificación espacial** en un artículo pertinente y explicar qué modificación propia se implementará. Un candidato cercano es [Luna et al. (2024)](https://doi.org/10.1002/rob.22342), que planifica cobertura poligonal con varios UAV y replanifica ante la pérdida de uno; sus autores [publicaron código](https://github.com/cvar-upm/coverage_path_planning). Ese artículo **no estudia jamming ni exactamente vuelos sucesivos ante una zona incierta**: habría que adaptar y acotar su método, no atribuirle el modelo nuevo.

## 6. Contraste directo con la Tarea 2

El enunciado exige entregar **presentación en Canvas** y modificar el proyecto del grupo en **GitLab UDP**. La presentación debe evidenciar el ETL y **cada criterio de la rúbrica**, no solo mostrar el sitio. La siguiente tabla contrasta lo solicitado con el trabajo local revisado:

| Requisito Tarea 2 | Estado actual | Trabajo pendiente |
|---|---|---|
| Docker con PostgreSQL, PostGIS y pgRouting | Hay `docker-compose.yml` con `postgis/postgis:16-3.4`; el SQL crea PostGIS. | Añadir pgRouting y probar su extensión en un contenedor reproducible. |
| Diagrama de BD y SQL de creación | Hay SQL de cuatro capas espaciales. | Añadir polígono de reconocimiento, puntos de observación, puntos de paso, tramos, alertas con marca temporal y rutas; entregar diagrama consistente con el SQL. |
| ETL de infraestructura, metadatos y amenazas a JSON/GeoJSON | Hay scripts de extracción para fuentes y evidencia parcial. | Crear el **grafo de trayectorias físicas**, documentar cada salida y separar datos reales de geometrías y eventos simulados. |
| Carga de cada JSON/GeoJSON a la BD | Hay un importador para cuatro GeoJSON espaciales. | Cubrir infraestructura y metadatos, o justificar y automatizar formalmente todas las cargas requeridas. |
| Modelo de fallas y pesos | Hay una fórmula propuesta para enlaces de comunicación. | Definir pérdida de reporte, incertidumbre espacial y temporal, efecto sobre tramos de vuelo y regla de caducidad; no trasladar directamente la fórmula de radio a kilómetros de vuelo. |
| Preferencias/restricciones del usuario y valores por defecto | Sin implementación encontrada. | Definir cobertura objetivo, límite de desvío y restricciones operacionales pertinentes, con valores por defecto. |
| Algoritmo elegido y paper | CLUN-LSR está documentado para rutas de datos. | Elegir un artículo de **planificación física** y explicar el algoritmo adaptativo que se implementará; mantener CLUN-LSR como antecedente de la alerta, sin atribuirle el ruteo de vuelo. |
| `k ≥ 2` rutas con `pgr_dijkstra` usando solo kilómetros | No se encontró. | Generar dos rutas **distintas** para el mismo par origen-destino; definir cómo se obtiene la segunda, ya que una llamada básica devuelve el camino mínimo. |
| `k ≥ 2` rutas con algoritmo elegido | No se encontró. | Calcular sobre las mismas instantáneas y pares de nodos que la línea base. |
| Métrica y diferencial de resiliencia | No se encontró. | Medir cobertura efectivamente observada y comunicada bajo los mismos escenarios, más costo adicional y tiempo de reacción; mostrar valor por alternativa y diferencia. |
| Sitio Leaflet | No se encontró. | Mostrar polígono de estudio, puntos de observación, alerta, preferencias y rutas físicas comparadas; identificar lo simulado. |
| `main` automatizado desde descarga hasta sitio | Hay `run_all.py` de validación y un `main.py` antiguo para DEM. | Crear un flujo integral, ejecutable en Docker, que genere/cargue datos, calcule rutas y habilite el sitio. |

**Ambigüedad del enunciado:** el punto narrativo 8 habla de una ruta `pgr_dijkstra` de ejemplo y dice que incorporar metadatos/amenazas será parte de la fase 3; la **rúbrica de la misma Tarea 2** exige `k ≥ 2` rutas tanto con Dijkstra como con el algoritmo elegido, una métrica de resiliencia y su comparación. Conviene seguir el criterio más exigente para planificar y pedir al profesor una aclaración explícita sobre el alcance de la fase actual.

Ahora `pgr_dijkstra` opera sobre el grafo **de vuelo**: el costo de referencia es la longitud recorrida en kilómetros. Para una misión de cobertura, una ruta completa puede concatenar caminos mínimos entre puntos de observación consecutivos. Ambos métodos deben visitar los mismos puntos para que la diferencia provenga del tratamiento de la alerta, no de que uno haya recibido una tarea más fácil. Una llamada básica a `pgr_dijkstra` da un camino mínimo; hay que documentar el procedimiento que produce otra ruta verdaderamente distinta si se sigue la rúbrica de `k ≥ 2`.

## 7. Preguntas que el grupo debe resolver

### Para el profesor

1. ¿La rúbrica de `k ≥ 2` rutas, algoritmo elegido y resiliencia aplica íntegra en la Tarea 2, pese a que el texto del punto 8 remite amenazas y metadatos a la fase 3? La reunión **no resolvió expresamente** esta contradicción.
2. Si se consulta de nuevo, mostrar un diseño concreto de reconocimiento de un polígono y preguntar si acepta como línea base la concatenación de `pgr_dijkstra` entre **puntos de observación obligatorios**.

### Para el diseño del grupo

1. ¿Qué polígono se reconocerá, qué puntos deberán observarse y con qué modelo de sensor se medirá la cobertura?
2. ¿Qué datos constituyen una observación **reportada** y cómo se tratará lo observado después de perder comunicación?
3. ¿Cuántos UAV harán vuelos sucesivos, qué evento dispara la alerta y cuánto tiempo se mantiene la incertidumbre sobre el sector de la última posición conocida?
4. ¿Cuál es la única zona y ventana temporal de evaluación? ¿Qué fuentes tienen cobertura allí y cuáles son solo antecedentes de otra región?
5. ¿Cómo se obtendrán dos trayectorias distintas por método, para la **misma misión** y restricciones?
6. ¿Qué artículo sustenta el algoritmo físico elegido y cuál será la modificación propia? ¿Cómo se explicará el papel acotado de CLUN-LSR?
7. ¿Qué métrica independiente del costo de selección refutaría la hipótesis y qué límite de desvío se aceptará?

## 8. Orden recomendado de trabajo

1. Fijar una **zona general de reconocimiento**, un polígono de prueba acotado y las fuentes utilizables allí. Distinguir hechos históricos de posiciones, eventos y parámetros simulados.
2. Definir una secuencia pequeña de puntos de observación, el modelo de cobertura y el criterio de «observado y reportado»; fijarlos para ambos métodos.
3. Leer y evaluar como candidato el artículo de Luna et al. (2024) sobre cobertura y replanificación; decidir qué algoritmo físico se implementará y escribir en una página qué se conserva de CLUN-LSR.
4. Diseñar BD y ETL alrededor de puntos de paso, tramos, polígono, alertas temporales, vuelos y rutas. Completar Docker con pgRouting.
5. Implementar la línea base por kilómetros, al menos dos trayectorias distintas si rige la rúbrica, y una métrica de cobertura/resiliencia independiente; luego implementar la variante adaptativa sobre los mismos escenarios.
6. Montar Leaflet y el `main` integral; registrar comandos, parámetros, resultados, límites y evidencias en la presentación.

## 9. Fuentes y archivos revisados

### Archivos locales del proyecto

- [`Charla_profesor.txt`](../02_REUNION_PROFESOR/Charla_profesor.txt) y [`ENFOQUE_TRAS_CHARLA_PROFESOR.md`](ENFOQUE_TRAS_CHARLA_PROFESOR.md): transcripción de la reunión e interpretación del nuevo enfoque, con puntos aún abiertos.
- [`CONTEXTO_PROYECTO_CODEX.md`](../03_TAREA_1/CONTEXTO_PROYECTO_CODEX.md): decisiones iniciales, explicación del artículo base y plan de fuentes.
- [`Informe_Ruteo_APO_DPC_AML_corregido.tex`](../03_TAREA_1/informes/Informe_Ruteo_APO_DPC_AML_corregido.tex) y [`Informe_Ruteo_APO_DPC_AML-1.pdf`](../03_TAREA_1/informes/Informe_Ruteo_APO_DPC_AML-1.pdf): fuente disponible y PDF de la entrega.
- [`VALIDACION_Y_CORRECCIONES.md`](../04_VALIDACION_TAREA_1/validacion_ruteo/VALIDACION_Y_CORRECCIONES.md), [`VALIDACION_COMPLETA.md`](../04_VALIDACION_TAREA_1/validacion_ruteo/VALIDACION_COMPLETA.md) y [`informe_pruebas.md`](../04_VALIDACION_TAREA_1/validacion_ruteo/evidencia/informe_pruebas.md): resultados y límites de las consultas.
- [`resumen_validacion.json`](../04_VALIDACION_TAREA_1/validacion_ruteo/evidencia/resumen_validacion.json), [`init_postgis.sql`](../04_VALIDACION_TAREA_1/validacion_ruteo/sql/init_postgis.sql) y [`docker-compose.yml`](../04_VALIDACION_TAREA_1/validacion_ruteo/docker-compose.yml): registro de ejecución y estado reproducible de la base.
- [`Tecnicas_de_Intercepcion_Telefonica.pdf`](../03_TAREA_1/referencias/Tecnicas_de_Intercepcion_Telefonica.pdf): archivo local cuyo contenido corresponde al informe de la Biblioteca del Congreso Nacional *Jamming: Caracterización y estatus legal en Chile y otros países* (junio de 2024).
- Retroalimentación del ayudante y capturas de rúbrica aportadas por el grupo; enunciado y rúbrica de la Tarea 2 aportados en la conversación.

### Antecedentes externos citados

- [Zheng et al., artículo base de CLUN-LSR](https://doi.org/10.1016/j.adhoc.2024.103702).
- [Luna et al., cobertura multi-UAV y replanificación durante el vuelo](https://doi.org/10.1002/rob.22342); [código publicado por los autores](https://github.com/cvar-upm/coverage_path_planning).
- [Ministerio del Interior de Chile, medidas contra crimen organizado y drones en cárceles](https://www.subinterior.gob.cl/noticias/2022/11/11/subsecretario-monsalve-detalla-medidas-para-combatir-el-crimen-organizado/).
- [Ministerio del Interior de Chile, tecnología de seguridad carcelaria](https://www.subinterior.gob.cl/noticias/2023/12/01/gobierno-invierte-cerca-de-5-mil-millones-en-tecnologia-para-seguridad-carcelaria/).
- [Intelligence Online, incautación de equipos SkyFend en Durango y uso contra drones tácticos del Ejército](https://www.intelligenceonline.com/americas/2025/07/02/skyfend-discreet-chinese-provider-of-anti-drone-tech-to-mexican-cartels,110471806-art).
- [Milenio, reportaje sobre equipos antidrones de La Mayiza](https://www.milenio.com/policia/mayiza-combate-fuerzas-armadas-equipo-anti-dron-elite).
- [Secretaría de Seguridad Pública de Sinaloa, incautación de batería antidrones SkyFend](https://www.sspsinaloa.gob.mx/post/cargadores-municiones-equipo-t%C3%A1ctico-y-bater%C3%ADas-para-dron-fueron-asegurados-por-el-grupo-interinst).
- [CBP, uso de drones pequeños para vigilancia fronteriza y seguimiento de traficantes](https://www.cbp.gov/frontline/cbp-small-drones-program).
- [Gobierno de México, drones desplegados en vigilancia de carreteras contra robos](https://www.gob.mx/presidencia/prensa/gobierno-de-mexico-presenta-estrategia-especial-cero-robos-para-carreteras-mexico-puebla-mexico-queretaro-y-culiacan-mazatlan?idiom=en).
- [Gabinete de Seguridad de México, drones y equipos antidrones en operativo fronterizo de Tamaulipas](https://gabinetedeseguridad.gob.mx/contenido/9852/despliegan-500-efectivos-del-ejercito-y-guardia-nacional-con-el-apoyo-de-dos-helicopteros-de-la-fuerza-aerea-en-la-frontera-de-tamaulipas).
- [Gobierno del Reino Unido, ensayo de 20 UAV cooperativos](https://www.gov.uk/government/news/swarming-drones-concept-flies-closer-to-reality).
- [Gobierno del Reino Unido, requisitos de red mesh e interferencia del programa](https://www.gov.uk/government/publications/competition-many-drones-make-light-work-phase-3/competition-document-many-drones-make-light-work-phase-3).
- [Gendarmería de Chile, Cuenta Pública 2018 y plan de equipos antidrones](https://html.gendarmeria.gob.cl/doc/cuenta_publica2018.pdf).
- [Gendarmería de Chile, Cuenta Pública 2023 y equipamiento en Arica](https://html.gendarmeria.gob.cl/doc/CuentaPublica_InformeE_2023_.pdf).
- [Sentencia judicial chilena sobre un dron con droga en Santiago Sur](https://www.diarioconstitucional.cl/wp-content/uploads/2023/10/Fallo183-2023traficoCDPSantiagoSur.pdf183-2023.pdf).
- [Ejército de EE. UU., guerra electrónica y recolección de información en Ucrania](https://www.army.mil/article/284546/adapting_to_multi_domain_battlefield_developing_emissions_control_sop).
- [CSIS, análisis de jamming contra UAV de reconocimiento y ataque en Ucrania](https://www.csis.org/analysis/lessons-ukraine-conflict-modern-warfare-age-autonomy-information-and-resilience).
- [Ministerio de Defensa de Ucrania, reconocimiento bajo amenaza de guerra electrónica](https://mod.gov.ua/en/news/raybird-a-small-birdie-with-the-capabilities-of-a-large-aircraft).
- [DARPA, ensayo CODE con UAV cooperativos y comunicaciones degradadas](https://www.darpa.mil/news/2019/code-success).
- [IEEE, ensayo de campo de comunicación multisalto y cambio de rutas entre drones](https://ieeexplore.ieee.org/document/10975949/).
- [OTAN, ejercicio Baltic Trust 25 contra UAV de vigilancia](https://www.ncia.nato.int/newsroom/news/ncia-and-latvia-host-joint-exercise-to-enhance-defence-readiness-against-threats-on-latvian-border).
- [Ejército de EE. UU., ejercicio antidrones en Fort Novosel](https://www.army.mil/article/283940/fort_novosel_doubles_down_on_drone_threat_in_dual_exercises).

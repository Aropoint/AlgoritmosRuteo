# Enfoque del proyecto tras la conversación con el profesor

**Fecha:** 17 de octubre de 2026. **Fuente:** [transcripción de la reunión](../02_REUNION_PROFESOR/Charla_profesor.txt). Es una transcripción automática con errores; este documento interpreta el sentido de la conversación y distingue sugerencias de decisiones tomadas.

## 1. Lo que entendimos de la orientación

El profesor propuso conservar la idea de **varios UAV que comparten información**, pero convertir la pérdida de un dron o de su señal en una razón para **cambiar el trayecto físico de los siguientes UAV**. El ejemplo fue: un primer dron deja de enviar un aviso periódico; otro, que iba a seguir una trayectoria similar, recibe o detecta la alerta y busca una ruta alternativa para cumplir la misma misión. Así el ruteo produce una decisión espacial observable, no solo una nueva ruta para paquetes.

Puntos expresados en la charla:

- Conviene **aprovechar el trabajo ya hecho** y acotar el problema; el profesor no pidió comenzar todo de cero.
- El caso necesita **una misión concreta y varios UAV**. Si no hay un dron posterior cuya decisión cambie, la información de la pérdida no aporta resiliencia al ruteo.
- Una pérdida de señal podría deberse a interferencia, derribo u otra falla. **El silencio de un beacon no identifica por sí mismo jamming ni localiza con precisión la amenaza**.
- La información debe propagarse a los UAV restantes; el curso podría limitarse a modelar que la alerta llega y evaluar el **cambio de ruta**. Diseñar un protocolo nuevo para propagarla puede quedar como trabajo futuro.
- El profesor sugirió usar un **escenario de conflicto**, mencionó Ucrania y pidió diferenciar entre llegar a un objetivo y reconocer una zona: la segunda misión requiere además una medida de cobertura del área observada. Es una sugerencia de contexto, no la confirmación de una zona ni de un incidente específico.
- Usar los drones adquiridos por la universidad es **opcional y no está evaluado** para este curso.

## 2. Cambio conceptual respecto de la propuesta anterior

| Antes de la reunión | Enfoque sugerido por la conversación |
|---|---|
| `V` = drones; `E` = enlaces de radio; la ruta es el camino de los datos. | `V` = posiciones o puntos de paso; `E` = tramos de vuelo permitidos; la ruta es una trayectoria física. Varios drones recorren o reutilizan ese espacio en distintos momentos. |
| CLUN-LSR decide por qué UAV retransmitir paquetes. | El estado de comunicaciones aporta una **alerta** al planificador físico. CLUN-LSR puede seguir como antecedente para detección/difusión de información, pero **no es por sí mismo un algoritmo de trayectorias de vuelo**. |
| Éxito = mantener camino de comunicación, PDR, *throughput* y tiempo de reconexión. | Éxito = completar la misión, evitar repetir una zona señalada como incierta, tiempo hasta replantear la ruta y costo adicional del desvío. PDR solo aplica si también se simula tráfico de datos. |
| Grafo móvil de enlaces entre UAV. | Grafo geoespacial de tramos con estado variable en el tiempo. Los UAV también se mueven, pero sus posiciones ya no son los vértices principales del grafo de rutas. |

**Precaución académica:** no atribuir al artículo CLUN-LSR la planificación física que no estudia. Si se mantiene como *paper base*, habrá que explicar con precisión el módulo nuevo que transforma una alerta de comunicación en una modificación de trayectoria y elegir un artículo adicional de planificación de rutas físicas que fundamente el algoritmo elegido. La misión de reconocimiento ya está escogida; faltan el algoritmo y la región de evaluación.

**Artículo candidato encontrado tras la reunión:** [Luna et al. (2024), *A multi-UAV system for coverage path planning applications with in-flight re-planning capabilities*](https://doi.org/10.1002/rob.22342), publicado en *Journal of Field Robotics* y disponible en acceso abierto. Planifica cobertura de áreas poligonales con varios UAV y **replanifica cuando se pierde una aeronave durante la misión**; presenta simulaciones y vuelos reales. Los autores [publicaron código](https://github.com/cvar-upm/coverage_path_planning). Encaja mejor que CLUN-LSR con la misión elegida, pero **no estudia jamming ni exactamente el caso de UAV sucesivos y zonas de incertidumbre**. Es una opción a leer y adaptar, no una elección aprobada ni una validación de nuestro diseño. Su método completo de cobertura y asignación de tareas puede ser más amplio que lo exigido en la Tarea 2.

## 3. Propuesta mínima para concretar el proyecto

**Misión elegida por el grupo:** reconocimiento de **una zona delimitada**, representada por un polígono. Varios UAV vuelan sucesivamente para cubrirla. Si se pierde el reporte periódico de un UAV predecesor, el siguiente no presupone una causa exacta: marca como incierto el entorno de su **última posición conocida**, recalcula el tramo de vuelo pendiente y continúa el reconocimiento. El resultado no se mide solo por llegar a un destino: importa qué porcentaje del polígono quedó **observado y reportado**.

**Forma acotada de compararlo en la Tarea 2:** fijar un origen, un destino y una secuencia pequeña de **puntos de observación obligatorios**, común a los dos métodos. La línea base une cada par consecutivo con `pgr_dijkstra` usando únicamente kilómetros. La alternativa usa la misma secuencia y los mismos datos iniciales, pero actualiza el costo o la factibilidad de los tramos después de una alerta. Se concatenan los tramos para obtener una ruta completa. Así se evita comparar una ruta que simplemente atraviesa el polígono con otra que sí intenta cubrirlo. Para la fase inicial pueden fijarse la secuencia y el radio de observación como supuestos experimentales; optimizar el orden de visita o el modelo de sensor puede quedar para una ampliación.

El evento puede denominarse **pérdida de reporte o de conectividad**. Un ensayo con jamming simulado puede ser un escenario de evaluación etiquetado como tal, pero la lógica del algoritmo no debe concluir «hubo jamming» solo por no recibir un beacon. No hace falta afirmar que un evento histórico ocurrió exactamente sobre el mapa usado en la prueba.

**Modelo mínimo:** grafo `G(t)=(V,E(t))` de puntos de paso tridimensionales y tramos factibles, con longitud en kilómetros; tramos excluidos o penalizados temporalmente por una alerta geolocalizada e incierta. El estado de alerta debe tener fuente, marca temporal y caducidad explícitas. El modelo puede usar varias instantáneas, una antes y otra después de la pérdida, para demostrar que una misma ruta inicial cambia. El DEM y las restricciones de espacio aéreo pueden ser insumos operacionales; OpenSky no representa una flota UAV; GPSJam, ACLED y clima no son medidas directas de la pérdida de radio entre esos drones.

**Experimento mínimo comparable:** fijar los mismos UAV, zona, puntos de observación, eventos de falla y horizonte de tiempo para ambas alternativas. Inyectar una pérdida en `t_f`, esperar el plazo de detección elegido y recién entonces permitir el recálculo. Registrar por separado **tiempo hasta detectar**, **tiempo de cálculo**, **cobertura confirmada** (área observada con reporte recibido dividida por área de estudio), kilómetros adicionales y cuántas misiones terminan. El período de beacon y el número de avisos perdidos que gatilla una alerta son **parámetros del experimento**, no un «promedio real» universal. Incluir al menos un evento de pérdida transitoria para comprobar si el método reacciona en exceso ante una falsa alarma.

**Hipótesis de trabajo, aún pendiente de fijar parámetros:** «En una misión de reconocimiento de una zona por vuelos sucesivos, una planificación que incorpora alertas recientes de pérdida de reporte alcanzará una mayor proporción de **área observada y comunicada** que las rutas seleccionadas solo por distancia, bajo los mismos escenarios de falla y con un límite predefinido de recorrido adicional». Se evalúa con fallas independientes de la fórmula de costo. La hipótesis puede refutarse si no mejora la cobertura confirmada o si excede el límite de desvío.

**Objetivo general propuesto:** diseñar y evaluar un algoritmo de **ruteo físico resiliente** para UAV que reconocen una zona delimitada, adaptando sus trayectorias tras una pérdida de reporte para mantener la cobertura observada y comunicada frente a rutas calculadas solo por distancia.

**Objetivos específicos propuestos:** (1) modelar el polígono de reconocimiento, los puntos de observación y el grafo geoespacial dinámico; (2) definir el evento de pérdida, su incertidumbre y la regla temporal con la que afecta tramos; (3) implementar rutas base y rutas adaptativas para la misma secuencia de puntos; (4) comparar cobertura observada y reportada, exposición a sectores fallidos, demora de reacción y costo del desvío en escenarios repetidos.

## 4. Encaje con la Tarea 2

La [consigna de la Tarea 2](ENUNCIADO_Y_RUBRICA_TAREA_2.txt) exige ETL, JSON documentados y cargados en BD, Docker con PostGIS y pgRouting, visualización Leaflet y una línea base con `pgr_dijkstra` cuyo costo es solo longitud en kilómetros. La rúbrica también pide **al menos dos rutas distintas por método**, restricciones por defecto, métrica de resiliencia y comparación. La charla aclaró el **sentido del caso**, pero no resolvió explícitamente la contradicción entre el punto 8 de la consigna (una ruta de ejemplo; amenazas en fase 3) y los criterios más exigentes de la rúbrica. Planificar según la rúbrica evita dejar criterios sin evidencia.

Con el nuevo enfoque, los vértices y aristas de pgRouting representan **posiciones y tramos de vuelo**, de modo que kilómetros, mapa y selección de origen-destino tienen un significado directo. Para `k ≥ 2`, una llamada básica a `pgr_dijkstra` produce un solo camino mínimo; el procedimiento para obtener otra ruta distinta debe explicarse y ejecutarse de forma reproducible. El algoritmo de la propuesta debe estar respaldado por un artículo que realmente trate planificación de trayectorias o adaptación espacial; CLUN-LSR puede justificar la señal de alerta, pero no sustituye ese requisito.

## 5. Decisiones pendientes del grupo

1. **Contexto:** ¿qué región general se usará como caso de estudio y qué datos públicos son verificables allí? No atribuir a un incidente real la posición de un jammer o de un UAV si la fuente no la publica.
2. **Cobertura:** ¿cuál será el polígono, qué radio de observación se supondrá y cuándo un sector se considera observado **y reportado**? Mantener la misma definición para ambos métodos.
3. **Evento:** ¿se medirá solo pérdida de reporte o también una causa conocida de interferencia? Fijar el intervalo de beacons, el tiempo de espera y la incertidumbre sin presentarlos como parámetros universales de UAV.
4. **Algoritmo y paper:** evaluar si la propuesta de Luna et al. (2024) se puede adaptar e implementar en el plazo; delimitar qué parte se toma de ese trabajo y qué parte del mecanismo anterior se conserva.
5. **Validación:** definir condiciones comparables, `k ≥ 2` rutas por alternativa, unidades y una métrica de resiliencia independiente del costo de selección.

## 6. Frases ambiguas de la transcripción

«METCH de web», «pay per», «yámero» y «comanan control» parecen referirse a *mesh de UAV*, *paper*, *jammer* y *command and control*. La referencia a que Chile «actualiza su jefe 15» no es inteligible y **no debe incorporarse como hecho**. Las cifras y maniobras improvisadas por el profesor en sus ejemplos no son datos experimentales ni requisitos del curso. Las decisiones centrales arriba se apoyan en pasajes reiterados de la conversación, no en esas frases dudosas.

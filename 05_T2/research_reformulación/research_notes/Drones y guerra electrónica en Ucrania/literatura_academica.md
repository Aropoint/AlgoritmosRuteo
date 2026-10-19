# Literatura académica: de la detección de jamming (CLUN-LSR) a la replanificación física resiliente multi-UAV

> Notas de investigación para el proyecto de ruteo resiliente de UAV (UDP, Chile). Fecha de corte: 2026-10-18.
> Cómo se verificó: todos los DOI que aparecen como "verificado" se resolvieron contra Crossref u OpenAlex (título, autores, revista, volumen y páginas coinciden). Los resúmenes de método salen del abstract oficial (OpenAlex/Crossref/arXiv) cuando estaba disponible. Si solo se vio el título o un fragmento de búsqueda, se dice explícitamente. No se pudo acceder al texto completo de los artículos de pago (ScienceDirect/IEEE devolvieron 403).

---

## 1. CLUN-LSR (Zheng et al.): qué detecta, cómo comparte la información de jamming, cómo se evalúa y quién lo cita

### Takeaway
CLUN-LSR es un protocolo **link-state** de capa de red. Lee de la capa de enlace el **estado del espectro en tiempo real** y usa el **número de vecinos a dos saltos** como métrica de selección de ruta para **evitar los nodos que están dentro del área de interferencia**. Según los autores, se puede aplicar a cualquier protocolo proactivo (table-driven). No mueve físicamente a los UAV. Pero su bibliografía ya cita trabajos de localización de jammers y de planificación de trayectorias anti-jamming, así que la extensión que propone el profesor (usar la alerta para cambiar trayectorias) tiene un anclaje directo en las fuentes del propio paper.

### Cited Findings
- **Cita completa (verificada):** Zheng, S., Zhu, X., Qin, Z., & Dong, C. "Cross-layer UAV network routing protocol for spectrum denial environments". *Ad Hoc Networks*, vol. 167, art. 103702. Publicado en línea el 2024-11-09; número impreso de febrero de 2025. DOI: 10.1016/j.adhoc.2024.103702. Afiliaciones: Nanjing University of Aeronautics and Astronautics (NUAA; Zhu es el autor de correspondencia) y Northwest Missouri State University (Qin). Acceso cerrado. — [Crossref](https://api.crossref.org/works/10.1016/j.adhoc.2024.103702); [OpenAlex](https://api.openalex.org/works/doi:10.1016/j.adhoc.2024.103702)
- **Qué hace, según el abstract** (visto solo como resumen del buscador, porque ScienceDirect devolvió 403): CLUN-LSR es un protocolo link-state que usa el estado del espectro en tiempo real obtenido de la capa de enlace. Toma el número de vecinos a dos saltos como métrica para elegir rutas y evita los nodos que están dentro del área de interferencia. Los autores dicen que todos los protocolos table-driven pueden adoptarlo para mejorar su desempeño. — [ScienceDirect (abstract)](https://www.sciencedirect.com/science/article/abs/pii/S1570870524003135)
- **Palabras clave temáticas asignadas por OpenAlex:** "Jamming attacks" (0.96), "Throughput" (0.93), "Link-state routing" (0.90), "UAV networks", "Cross-layer routing", "Packet transmission rate", "Military wireless communication", "Interference avoidance". Esto indica que se evalúa con throughput y tasa de transmisión de paquetes. — [OpenAlex](https://api.openalex.org/works/doi:10.1016/j.adhoc.2024.103702)
- **La bibliografía de CLUN-LSR (39 referencias, Crossref) ya contiene el puente hacia la capa física.** Entre otras:
  - Localización de jammers: "Exploiting jamming-caused neighbor changes for jammer localization", "Topology-based multi-jammer localization in wireless networks", "Mobile jammer localization and tracking in multi-hop wireless network", "An improved least-square based jammer localization algorithm", "Jamming source localization using augmented physics-based model".
  - Trayectorias anti-jamming: "Anti-jamming path planning for unmanned aerial vehicles with imperfect jammer information", "Radio map assisted path planning for UAV anti-jamming communications", "UAV relay flight path planning in the presence of jamming signal", "Anti-jamming 3D trajectory design for UAV-enabled wireless sensor networks under probabilistic LoS channel".
  - Ruteo: OLSRv2 y "Multipath optimized link state routing for mobile ad hoc networks".

  — [Crossref (lista de referencias)](https://api.crossref.org/works/10.1016/j.adhoc.2024.103702)
- **Trabajos que lo citan.** Semantic Scholar cuenta 6 citas, OpenAlex 7 y Crossref 8 (a oct. 2026). La continuación directa viene del mismo grupo de NUAA (Xiaojun Zhu, Chao Dong):
  - Zhang, K., Zhu, X., Dong, C., & Tian, C. (2026). "Defending Against Periodic Jamming: A Routing Protocol for UAV Networks with Neighborhood Collaboration". *IEEE Communications Magazine*. DOI: 10.1109/MCOM.001.2600062. Sin abstract disponible. El título indica colaboración entre vecinos frente a jamming periódico. — [OpenAlex](https://api.openalex.org/works?filter=doi:10.1109/mcom.001.2600062)
  - Wang, K., & Zhu, X. (2026). "Satellite-Assisted Routing Protocol for UAV Networks in Spectrum Denial Environments". *IEEE CSCWD 2026*. DOI: 10.1109/CSCWD68734.2026.11582096. Sin abstract disponible. — [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.adhoc.2024.103702?fields=citations.title)
  - Otros citantes: "Barrage Relay Network Assisted Multicast Routing Protocol for Spectrum Dissemination in UAV Networks" (ICC 2025, DOI 10.1109/ICC52391.2025.11161991); "Double DQN-Based Position Optimization for Improved Throughput in Multi-UAV Networks" (WSCE 2025, DOI 10.1109/WSCE68305.2025.11300679); "Q-CAR" (IWCMC 2026); y Dong et al. (2026), "Predictive-Q Learning Based Interference-and-Mobility Aware Dual-Path Routing for UAV Swarm Networks" (*CMC*, DOI 10.32604/cmc.2026.084301). Este último usa Q-learning con predicción de vida útil del enlace y abre un camino de respaldo condicional cuando el siguiente salto primario se vuelve poco fiable. Reporta más de 15 % de mejora en PDR sobre GPSR bajo interferencia fuerte. — [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.adhoc.2024.103702?fields=citations.title); [OpenAlex (Predictive-Q)](https://doi.org/10.32604/cmc.2026.084301)
- **Antecedente de ruteo resistente a jamming que sirve de baseline:** Pu, C. (2018). "Jamming-Resilient Multipath Routing Protocol for Flying Ad Hoc Networks" (JarmRout). *IEEE Access*, 6, 68472–68486. DOI 10.1109/ACCESS.2018.2879758 (verificado). Combina tres esquemas (calidad de enlace, carga de tráfico y distancia espacial entre caminos). Se evalúa en OMNeT++ contra DSR, OLSR y SMR, y mejora PDR, latencia y tasa de interrupción extremo a extremo. Limitación: solo opera en capa de red y no reubica a los UAV. — [DOI](https://doi.org/10.1109/ACCESS.2018.2879758)
- **Analogía industrial (patente, sin revisión por pares):** la patente US 9.088.903, "Dynamic routing under extreme cognitive jamming environments", cambia de modo de ruteo según el estado de jamming. Usa el costo link-state por defecto en operación normal, sube el costo cuando detecta jamming y añade reenvío redundante proactivo cuando el jamming es posible. — [USPTO](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9088903)

### Inferences
- Como CLUN-LSR ya trabaja con un "área de interferencia" y con conteos de vecinos a dos saltos, la información que produce es **espacial**: qué nodos están afectados y cuántos vecinos se perdieron. Eso es justo la entrada que usan los algoritmos de localización basados en cambios de vecindad (Liu et al. 2012, sección 3). Ese es el argumento técnico más fuerte para la extensión: la alerta de CLUN-LSR se convierte en (centro estimado, radio, incertidumbre) y alimenta el planificador del grafo geolocalizado.
- La continuación del mismo grupo hacia la "colaboración de vecindario" (IEEE ComMag 2026) apunta en la misma dirección que la propuesta del profesor: propagar información de jamming entre vecinos. Ellos lo aplican al ruteo de paquetes; el proyecto lo aplicaría a trayectorias.
- No se encontró ningún trabajo que cite CLUN-LSR y use su alerta para replanificar físicamente. Hasta donde llegó esta búsqueda, ahí está el hueco que el proyecto puede ocupar.

### Gaps
- No se pudo verificar el detalle interno de CLUN-LSR (formato de los mensajes, cómo se marca un nodo como "dentro del área", umbrales) ni el escenario de simulación (simulador, número de nodos, área, modelo de jammer, valores numéricos de throughput/PDR) porque el texto completo es de pago. Recomendación: el equipo debería extraer esto del PDF que ya tiene y citar páginas concretas.
- No hay abstract disponible para los dos trabajos de seguimiento de NUAA (ComMag 2026, CSCWD 2026), así que no se puede afirmar qué mecanismo exacto usan.

---

## 2. Planificación de trayectorias consciente de jamming y amenazas (jammers y radares como costos o regiones prohibidas)

### Takeaway
La literatura se divide en tres familias:
- **Optimización convexa o robusta de trayectoria** (SCA, BCD, S-procedure). Suele suponer conocimiento previo, aunque sea imperfecto, de la posición del jammer.
- **Búsqueda en grafo sobre mapas de costo o radio** (A*, Dijkstra, caminos de mínimo riesgo). Es la más compatible con el grafo geolocalizado del proyecto.
- **Aprendizaje** (DRL, GCN, active inference). Maneja jammers desconocidos o dinámicos descubiertos en línea, a cambio de perder garantías.

El trabajo que mejor encaja con la idea del proyecto es Duan et al. (2018): **detección → localización → evasión robusta**.

### Cited Findings
- **Duan, B., Yin, D., Cong, Y., Zhou, H., Xiang, X., & Shen, L. (2018).** "Anti-Jamming Path Planning for Unmanned Aerial Vehicles with Imperfect Jammer Information". *IEEE ROBIO 2018*, pp. 729–735. DOI 10.1109/ROBIO.2018.8665238 (verificado; CLUN-LSR lo cita).
  - **Método:** un UAV debe llegar a su destino manteniendo la calidad del enlace tierra-aire frente a un jammer cuya posición y potencia se desconocen al inicio. El marco tiene tres pasos: (i) detección combinando RSS y tasa de error de paquetes (PER); (ii) localización por RSS que estima a la vez la posición y la potencia del jammer; (iii) planificación robusta que garantiza el desempeño en el peor caso dentro de la incertidumbre de localización, de modo que la calidad de comunicación siempre supere un umbral. Se valida en NS-3.
  - **Aporte:** es la plantilla académica casi exacta de "alerta → zona incierta → evasión".
  - **Limitaciones:** un solo UAV, un solo jammer y sin cooperación entre UAV.

  — [DOI](https://doi.org/10.1109/ROBIO.2018.8665238)
- **Dong, Y., He, C., Wang, Z., & Zhang, L. (2022).** "Radio Map Assisted Path Planning for UAV Anti-Jamming Communications". *IEEE Signal Processing Letters*, 29, 607–611. DOI 10.1109/LSP.2022.3149374 (verificado; citado por CLUN-LSR).
  - **Método:** construye dos mapas de radio, uno de potencia de señal y otro de SINR, a partir de **datos topográficos reales** (pérdida de trayecto por relieve más interferencia de jammers). Sobre ellos aplica **A\*** en grafo para minimizar la distancia de vuelo cumpliendo la calidad de comunicación.
  - **Aporte:** muestra que un planificador de grafo clásico (A*/Dijkstra) con costos derivados de un mapa de interferencia es publicable y comparable. Es directamente transferible al grafo geolocalizado.
  - **Limitaciones:** supone jammers conocidos al construir el mapa y planifica offline, sin replanificación.

  — [DOI](https://doi.org/10.1109/LSP.2022.3149374)
- **Mah, M.-C., Lim, H. S., & Tan, A. W.-C. (2019).** "UAV Relay Flight Path Planning in the Presence of Jamming Signal". *IEEE Access*, 7, 40913–40924. DOI 10.1109/ACCESS.2019.2907962 (verificado; citado por CLUN-LSR). Optimiza la trayectoria de un UAV relé para maximizar el SINR, no el SNR, estimando los parámetros necesarios. Logra un desempeño cercano al óptimo ideal. Aporte: justifica usar el SINR, que incluye el jammer, como métrica de costo. Limitación: un solo relé y trayectoria continua, no un grafo. — [DOI](https://doi.org/10.1109/ACCESS.2019.2907962)
- **Wang, X., Gursoy, M. C., Erpek, T., & Sagduyu, Y. E. (2021).** "Jamming-Resilient Path Planning for Multiple UAVs via Deep Reinforcement Learning". *IEEE ICC Workshops 2021*, pp. 1–6. DOI 10.1109/ICCWorkshops50388.2021.9473587 (verificado; preprint arXiv:2104.04477).
  - **Método:** caminos sin colisión para varios UAV conectados a la red celular, con restricciones de conectividad con las estaciones base y un **jammer dinámico**. Un valor aprendido offline por TD modela la interacción UAV-UAV y UAV-entorno, y una DNN supervisada construye **en línea el mapa de SINR** que refleja el jammer.
  - **Métricas:** tasa de éxito, colisiones y brecha frente al caso con mapa SINR perfecto.
  - **Aporte:** es multi-UAV, maneja amenaza descubierta en línea y da métricas reutilizables.
  - **Limitaciones:** caja negra y dominio discreto pequeño.

  — [DOI](https://doi.org/10.1109/ICCWorkshops50388.2021.9473587); [arXiv](https://arxiv.org/abs/2104.04477)
- **Wu, Y., Fan, W., Yang, W., Sun, X., & Guan, X. (2020).** "Robust Trajectory and Communication Design for Multi-UAV Enabled Wireless Networks in the Presence of Jammers". *IEEE Access*, 8, 2893–2905. DOI 10.1109/ACCESS.2019.2962534 (verificado). Diseña conjuntamente trayectorias, scheduling y potencia de varios UAV frente a jammers con **ubicación imperfecta**. Usa BCD + SCA + S-procedure para modelar la región de incertidumbre. Aporte: formalismo de "zona incierta" en optimización robusta. Limitación: optimización centralizada offline. — [DOI](https://doi.org/10.1109/ACCESS.2019.2962534)
- **Wang, F., Zhang, Z., Zhou, L., Shang, T., & Zhang, R. (2024).** "Robust Multi-UAV Cooperative Trajectory Planning and Power Control for Reliable Communication in the Presence of Uncertain Jammers". *Drones*, 8(10), 558. DOI 10.3390/drones8100558 (verificado). Una unidad de control terrestre coordina varios UAV frente a varios jammers con ubicación y potencia imperfectas. Maximiza el **SINR promedio de peor caso** (problema semi-infinito no convexo) con S-procedure + SCA. Aporte: modelo multi-jammer con incertidumbre acotada. Limitación: centralizado y sin descubrimiento en línea. — [DOI](https://doi.org/10.3390/drones8100558)
- **Jeong, H. (2024).** "Anti-Jamming Path Planning Using GCN for Multi-UAV". arXiv:2405.00689 (preprint de un solo autor, sin venue). El enjambre agrega lo que mide cada UAV y una **red convolucional de grafos (GCN)** estima la posición y la intensidad de las áreas de jamming. Un control multiagente dispersa al enjambre para evitarlas y lo reagrupa en el objetivo. Aporte: idea de inteligencia colectiva para estimar la zona. Limitación: no revisado por pares y sin métricas cuantitativas en el abstract. — [arXiv](https://arxiv.org/abs/2405.00689)
- **Krayani, A., Sadati, S. F., Marcenaro, L., & Regazzoni, C. (2026).** "Bayesian Active Inference for Intelligent UAV Anti-Jamming and Adaptive Trajectory Planning". *IEEE CCNC 2026*, pp. 1–7. DOI 10.1109/CCNC65079.2026.11366598 (verificado). Planificación jerárquica (simbólica y de movimiento) que durante el despliegue hace inferencia en línea para anticipar interferencia, **localizar jammers sin conocimiento previo** y adaptar la trayectoria. Reduce interferencia y costo de misión frente a baselines de RL sin modelo. Limitación: requiere demostraciones expertas y es de un solo UAV. — [DOI](https://doi.org/10.1109/CCNC65079.2026.11366598)
- **Zhang, S., & Zhang, R. (2021).** "Radio Map-Based 3D Path Planning for Cellular-Connected UAV". *IEEE Trans. Wireless Communications*, 20(3), 1975–1989. DOI 10.1109/TWC.2020.3037916 (verificado). Minimiza la distancia de vuelo con una restricción de SINR esperado usando mapas de radio y búsqueda en grafo. Es la referencia base de planificación sobre radio map. No trata jamming. — [DOI](https://doi.org/10.1109/TWC.2020.3037916)
- **Zonas sin GNSS o con GNSS degradado:** Delamer, J.-A., Watanabe, Y., & Ponzoni Carvalho Chanel, C. (2021). "Safe path planning for UAV urban operation under GNSS signal occlusion risk". *Robotics and Autonomous Systems*, 142, 103800. DOI 10.1016/j.robot.2021.103800 (verificado). Predice oclusiones con un modelo georreferenciado y genera un **mapa de calidad y disponibilidad de posicionamiento**. Planifica con un POMDP resuelto por MCTS, evaluado sobre un mapa de elevación de San Diego. Aporte: tratar la degradación de navegación como capa de riesgo del mapa. Limitación: oclusión urbana, no jamming intencional. — [DOI](https://doi.org/10.1016/j.robot.2021.103800); [HAL](https://hal.archives-ouvertes.fr/hal-03336825)
- Un trabajo de la European Navigation Conference 2024 (sin DOI verificado) usa RL sobre mapas de dilución de precisión GNSS y reporta **36 % más de éxito de misión** al incorporar el desempeño GNSS en la planificación. — [Sciforum](https://sciforum.net/paper/19973)
- El grupo de Sabatini (Nottingham) incorpora a la evitación de colisiones restricciones de integridad GNSS, incluida la **evitación de jamming** cuando aplica. — [Nottingham ePrints](https://eprints.nottingham.ac.uk/34894/)
- **Clásicos de amenaza tipo radar o defensa aérea:**
  - Kim, J., & Hespanha, J. P. (2003). "Discrete approximations to continuous shortest-path: application to minimum-risk path planning for groups of UAVs". *42nd IEEE CDC*, vol. 2, pp. 1734–1740. DOI 10.1109/CDC.2003.1272863 (verificado). Reduce el camino de mínimo riesgo en dominio continuo (costo anisotrópico que depende de la posición y la dirección) a un **grafo finito** con muestreo "honeycomb" no uniforme. Lo aplica a grupos de UAV que minimizan el riesgo de ser derribados por defensas terrestres. Aporte: justifica discretizar el espacio en un grafo y usar caminos mínimos con costo de riesgo. — [DOI](https://doi.org/10.1109/CDC.2003.1272863)
  - Kabamba, P. T., Meerkov, S. M., & Zeitz, F. H. (2006). "Optimal Path Planning for Unmanned Combat Aerial Vehicles to Defeat Radar Tracking". *J. Guidance, Control, and Dynamics*, 29(2), 279–288. DOI 10.2514/1.14303 (verificado; abstract no disponible, solo se confirmó el título). Clásico de planificación óptima frente a seguimiento por radar. — [DOI](https://doi.org/10.2514/1.14303)
  - Jun, M., & D'Andrea, R. (2003). "Path Planning for Unmanned Aerial Vehicles in Uncertain and Adversarial Environments". En *Cooperative Systems* (Springer), pp. 95–110. DOI 10.1007/978-1-4757-3758-5_6 (verificado; contenido no revisado). — [DOI](https://doi.org/10.1007/978-1-4757-3758-5_6)
- **Amenazas emergentes ("pop-up") y replanificación:**
  - Un preprint de 2026 (arXiv:2606.12306) dispara la replanificación cada vez que un UAV detecta una nueva zona de amenaza, actualiza la capa de amenazas compartida y replanifica con **A\*** sobre un mapa de costo. Solo se vio un fragmento. — [arXiv](https://arxiv.org/pdf/2606.12306)
  - Una revisión de 2023 sobre métodos RRT distingue dos estrategias: replanificar en cuanto se detecta un cambio, o predecir el movimiento de la amenaza para replanificar menos. — [Springer, Complex & Intelligent Systems](https://link.springer.com/article/10.1007/s40747-023-01115-2)
- **Revisión de referencia:** Aggarwal, S., & Kumar, N. (2020). "Path planning techniques for unmanned aerial vehicles: A review, solutions, and challenges". *Computer Communications*, 149, 270–299. DOI 10.1016/j.comcom.2019.10.014 (verificado, más de 900 citas). — [DOI](https://doi.org/10.1016/j.comcom.2019.10.014)
- **Encuestas sobre anti-jamming:**
  - Pirayesh, H., & Zeng, H. (2022). "Jamming Attacks and Anti-Jamming Strategies in Wireless Networks: A Comprehensive Survey". *IEEE Communications Surveys & Tutorials*, 24(2), 767–809. DOI 10.1109/COMST.2022.3159185 (verificado). Cubre WLAN, celular, radio cognitiva, vehicular, GPS y sistemas con aprendizaje. — [DOI](https://doi.org/10.1109/COMST.2022.3159185)
  - Yang, J., Cui, M., Zhang, H., Ji, F., Lai, Z., & Wang, Y. (2025). "Agent-Based Anti-Jamming Techniques for UAV Communications in Adversarial Environments: A Comprehensive Survey". arXiv:2508.11687 (preprint). Organiza el campo en Percepción → Decisión → Acción (teoría de juegos y RL) y trata la localización de jammers como tarea de percepción del enjambre. — [arXiv](https://arxiv.org/abs/2508.11687)

### Inferences
- Para un grafo geolocalizado con Dijkstra/Yen, lo más defendible es seguir a Dong et al. (2022) y Kim & Hespanha (2003): convertir la zona de jamming en **penalización de aristas**, ya sea como costo de riesgo o SINR esperado, o en **eliminación de aristas** (zona prohibida) cuando la probabilidad de afectación supera un umbral. Los enfoques de DRL/GCN sirven como trabajo relacionado o futuro, no como base, porque cuesta reproducirlos en el plazo de un curso.
- Duan et al. (2018) y Wang F. et al. (2024) legitiman tratar la ubicación del jammer como **incierta y acotada**, con evasión de peor caso. Eso justifica inflar el radio de la zona según la incertidumbre de localización.

### Gaps
- No se encontró un paper revisado por pares que combine **D\* Lite con zonas de jamming descubiertas en línea por un enjambre** en un grafo geográfico. Parece un hueco real, y es justo la combinación que el proyecto puede presentar como contribución.
- El paper "Anti-jamming 3D trajectory design for UAV-enabled wireless sensor networks under probabilistic LoS channel", citado por CLUN-LSR, no se pudo verificar por DOI en esta sesión porque Crossref limitó las consultas.

---

## 3. Localización de jammers por UAV/enjambres: de la detección a una zona geolocalizada con radio de incertidumbre

### Takeaway
Hay métodos maduros para estimar la posición, y a veces la potencia, del jammer a partir de RSS, C/N0 o **cambios de vecindad**, incluso solo con información topológica de la red. Algunos trabajos recientes ya entregan **cotas de error y mapas de probabilidad**, que son lo que se necesita para construir una zona de evitación con radio de incertidumbre.

### Cited Findings
- **Liu, Z., Liu, H., Xu, W., & Chen, Y. (2012).** "Exploiting Jamming-Caused Neighbor Changes for Jammer Localization". *IEEE Trans. Parallel and Distributed Systems*, 23(3), 547–555. DOI 10.1109/TPDS.2011.154 (verificado; **citado por CLUN-LSR**).
  - **Método:** analiza cómo cambia el rango de comunicación de cada nodo según la posición y la potencia del jammer (modelo de espacio libre). Estima ese rango afectado **solo a partir de los cambios en la lista de vecinos** y resuelve la posición del jammer por **mínimos cuadrados (LSQ)** en un solo paso. Una variante adaptativa usa sombreado log-normal construido empíricamente.
  - **Aporte:** es el eslabón natural con CLUN-LSR, cuyas tablas link-state ya contienen los cambios de vecindad.
  - **Limitaciones:** redes de sensores estáticas y un solo jammer.

  — [DOI](https://doi.org/10.1109/TPDS.2011.154)
- **Ahmed, N., Winter, A., & Sokolova, N. (2021).** "Low Cost Collaborative Jammer Localization Using a Network of UAVs". *IEEE Aerospace Conference 2021*, pp. 1–8. DOI 10.1109/AERO50100.2021.9438441 (verificado). Usa un modelo de C/N0 en función de la distancia jammer-receptor con receptores GNSS de bajo costo. Compara (i) un arreglo sintético para un solo nodo, extendido a 3D, con (ii) la fusión de mediciones de todos los UAV cooperantes. Simula jammer dinámico y red dinámica en laboratorio. Aporte: está motivado explícitamente para que el sistema autónomo **"maniobre lejos de la región afectada"**. Limitación: validación de laboratorio. — [DOI](https://doi.org/10.1109/AERO50100.2021.9438441)
- **Koohifar, F., Guvenc, I., & Sichitiu, M. L. (2018).** "Autonomous Tracking of Intermittent RF Source Using a UAV Swarm". *IEEE Access*, 6, 15884–15897. DOI 10.1109/ACCESS.2018.2810599 (verificado). Un enjambre con sensores RSS omnidireccionales localiza y sigue un emisor intermitente. Compara un EKF basado en detección con un estimador bayesiano recursivo (este último gana por poco). Para planificar dónde medir, compara descenso por la cota posterior de Cramér-Rao con una heurística bioinspirada; la primera es un orden de magnitud mejor. Aporte: la incertidumbre de localización se puede cuantificar con la PCRLB. — [DOI](https://doi.org/10.1109/ACCESS.2018.2810599)
- **Aldosari, W., Moinuddin, M., Aljohani, A. J., & Al-Saggaf, U. M. (2020).** "Distributed Extended Kalman Filtering Based Techniques for 3-D UAV Jamming Localization". *Sensors*, 20(22), 6405. DOI 10.3390/s20226405 (verificado). Sigue un **UAV jammer** en 3D con EKF distribuido usando el modelo log-distancia P = Pt + k − 10n·log10(d) + Xσ. La variante con razón de distancias (DEKF-DR) tiene error 3D máximo menor a 0,6 m frente a 2,9 m del DEKF y 2,4 m del EKF centralizado, en simulación con 500 a 1000 corridas. Limitación: escenario a pequeña escala (decenas de metros) y sin cooperación multi-UAV real. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7697327/)
- **Liu, Z., Lo, S., Blanch, J., Chen, Y.-H., & Walter, T. (2025).** "Locating GNSS Interference Sources using ADS-B with Non-linear Least Squares". *NAVIGATION*, 72(3), navi.716. DOI 10.33012/navi.716 (verificado). Estima la potencia y la ubicación del interferente GNSS con reportes ADS-B públicos y mínimos cuadrados no lineales. En el evento de Denver de 2022 localiza dentro de **0,1° en latitud y longitud**. A diferencia de métodos anteriores, **cuantifica la incertidumbre con cotas de error y mapas de calor de probabilidad**. Aporte: modelo directo de "zona con incertidumbre". — [DOI](https://doi.org/10.33012/navi.716)
- **Schäfer, M., Sõeruer, S., Kippak, T., & Sadrak, E. (2023).** "Jammer on the Horizon: A Robust Method for GPS Jammer Localization Using ADS-B Data". *ION GNSS+ 2023*, pp. 4183–4196. DOI 10.33012/2023.19393 (verificado). Detecta jamming GPS a gran escala con ADS-B durante un año en la red europea (región báltica). Localiza la fuente **reconstruyendo el horizonte de radio del jammer**, lo que funciona incluso cuando la cobertura es parcial o el tráfico escaso. — [DOI](https://doi.org/10.33012/2023.19393). En presentaciones del autor ante la OACI se reporta una precisión de "algunas decenas de km" y detecciones en 287 de 365 días. — [ICAO (slides)](https://www.icao.int/MID/Documents/2024/EUR-MID%20Radio%20Navigation%20Symposium/8.1%20ADS-B%20to%20detect%20GNSS%20RFI_Matthias%20Schaefer.pdf)
- Duan et al. (2018) estiman **posición y potencia a la vez** por RSS tras detectar con RSS+PER, y planifican de forma robusta frente al ruido de localización (ver sección 2). — [DOI](https://doi.org/10.1109/ROBIO.2018.8665238)
- **Otros, no verificados por DOI:**
  - Guerra, Dardari & Djurić (EUSIPCO 2019): navegación distribuida de UAV con sensores RSS para minimizar la incertidumbre de la posición de la fuente, considerando NLOS y latencia. — [EURASIP PDF](https://www.eurasip.org/Proceedings/Eusipco/eusipco2019/Proceedings/papers/1570533708.pdf)
  - arXiv:2208.01227: localización pasiva por RSS con enjambre de drones (estimación por máxima verosimilitud y diseño óptimo de mediciones con restricciones de región). — [arXiv](https://arxiv.org/pdf/2208.01227)

### Inferences
- **Receta de conversión** (inferencia del equipo de investigación, apoyada en Duan 2018, Liu 2012, Aldosari 2020 y Liu 2025):
  1. **Centro** = posición estimada del jammer, por LSQ sobre cambios de vecindad o por RSS.
  2. **Radio efectivo de jamming** r_J = distancia a la que el SINR cae bajo el umbral del enlace, despejada del modelo log-distancia con la potencia estimada.
  3. **Margen de incertidumbre** = k·σ, donde σ sale de la covarianza del estimador (EKF o PCRLB) o de las cotas de error.
  4. **Zona de evitación** = disco de radio r_J + k·σ.

  Con k = 2 o 3 se obtiene una evitación "de peor caso" análoga a la robusta de Duan et al.
- Si solo un UAV detecta (sin triangulación), el centro queda muy incierto. En ese caso conviene modelar la zona como un **costo probabilístico decreciente con la distancia** en vez de un disco rígido, y reducir la incertidumbre a medida que más UAV reportan. Es una fusión incremental, en la línea de Koohifar et al.

### Gaps
- No se encontró un trabajo que use explícitamente la salida de un **protocolo de ruteo** (tablas link-state) como entrada para localizar jammers y luego **replanificar trayectorias**. Liu et al. (2012) localizan con vecindades, pero no replanifican.
- La mayoría de las validaciones son simulaciones o eventos civiles (Denver, Báltico). No hay validación pública en escenarios de conflicto activo.

---

## 4. Compartición cooperativa de amenazas y replanificación multi-UAV (incluida la pérdida de un UAV)

### Takeaway
Existe literatura directa sobre compartir amenazas detectadas entre UAV para replanificar. Un resultado contraintuitivo es que **compartir más información no siempre mejora la planificación**. También hay sistemas multi-UAV con replanificación en vuelo validados con vuelos reales (Luna et al., 2024) y marcos de asignación o planificación **resilientes a la pérdida o ataque de robots**. Para el algoritmo de replanificación incremental, la referencia canónica es D* Lite.

### Cited Findings
- **Luna, M. A., Molina, M., Da-Silva-Gomez, R., Melero-Deza, J., Arias-Perez, P., & Campoy, P. (2024).** "A multi-UAV system for coverage path planning applications with in-flight re-planning capabilities". *Journal of Field Robotics*, 41(5), 1480–1497. DOI 10.1002/rob.22342 (verificado).
  - **Método:** sistema multi-UAV para cubrir varias áreas separadas, con arquitectura **distribuida-centralizada** y heurísticas computacionalmente eficientes para planificar, replanificar y decidir durante la ejecución ante **eventos inesperados**. Se evalúa computacionalmente contra otras propuestas y con vuelos simulados y reales.
  - **Resultados:** reparte tareas de forma equitativa incluso a mitad de vuelo, con mayor eficiencia computacional que varias propuestas del estado del arte.
  - **Aporte:** referencia de arquitectura y de protocolo experimental (sim más vuelo real) para "replanificación en vuelo". Existe además la **tesis doctoral en español** del primer autor (UPM, 2024), "Planificación de Rutas de Cobertura de Área y Gestión Dinámica de Misiones para Sistemas Multi-UAV".
  - **Limitaciones:** los eventos son de misión (fallas, cambios) y no amenazas adversarias.

  — [DOI](https://doi.org/10.1002/rob.22342); [Tesis UPM](https://oa.upm.es/83836/1/MARCO_ANDRES_LUNA_AGUIRRE.pdf)
- **Zheng, Z., Liu, Y., & Zhang, X. (2016).** "The more obstacle information sharing, the more effective real-time path planning?". *Knowledge-Based Systems*, 114, 36–46. DOI 10.1016/j.knosys.2016.09.021 (verificado). Compartir la información de amenazas detectada por un UAV debería mejorar la planificación cooperativa, pero **no siempre lo hace**, por las diferencias en la información que tiene cada UAV. Proponen **tres estrategias adaptativas de compartición** y las validan sobre un planificador RRT en tiempo real en muchos escenarios. Aporte: justifica estudiar *qué* y *a quién* propagar la alerta, no solo propagarla. — [DOI](https://doi.org/10.1016/j.knosys.2016.09.021); [BUAA](https://research.buaa.edu.cn/en/publications/the-more-obstacle-information-sharing-the-more-effective-real-tim/)
- Un trabajo previo del mismo grupo (conferencia, 2011) planifica en tiempo real con UAV que detectan amenazas y **las comparten entre sí**, usando razonamiento difuso para los ángulos de giro. — [BUAA](https://research.buaa.edu.cn/en/publications/real-time-path-planning-for-multi-uavs-with-share-of-threats-info/)
- **Koenig, S., & Likhachev, M. (2005).** "Fast replanning for navigation in unknown terrain". *IEEE Trans. Robotics*, 21(3), 354–363. DOI 10.1109/TRO.2004.838026 (verificado). Versión de revista de **D\* Lite**, cuyo original es Koenig & Likhachev, AAAI-02, 2002, pp. 476–483 (URL/DOI de AAAI no verificado en esta sesión). Es una búsqueda heurística incremental que repara el camino más corto cuando cambian los costos de las aristas, sin replanificar desde cero. Aporte: algoritmo canónico para "el costo de una zona cambió porque llegó una alerta". — [DOI](https://doi.org/10.1109/TRO.2004.838026)
- **Choi, H.-L., Brunet, L., & How, J. P. (2009).** "Consensus-Based Decentralized Auctions for Robust Task Allocation". *IEEE Trans. Robotics*, 25(4), 912–926. DOI 10.1109/TRO.2009.2022423 (verificado, más de 1000 citas). Propone la asignación de tareas descentralizada por subasta más consenso (CBBA). Es la referencia estándar para **reasignar puntos de observación** cuando un UAV se pierde o queda incomunicado. — [DOI](https://doi.org/10.1109/TRO.2009.2022423)
- **Zhou, L., Tzoumas, V., Pappas, G. J., & Tokekar, P. (2019).** "Resilient Active Target Tracking With Multiple Robots". *IEEE Robotics and Automation Letters*, 4(1), 129–136. DOI 10.1109/LRA.2018.2881296 (verificado). Planifica de modo **resiliente a fallas o ataques de robots en el peor caso** (válido para cualquier número de fallas), con cotas de aproximación vía curvatura de funciones submodulares bajo restricciones de matroide. Simulado en MATLAB y Gazebo. Aporte: formalismo para "un UAV se silencia o se pierde". — [DOI](https://doi.org/10.1109/LRA.2018.2881296)
- Schlotfeldt, B., Tzoumas, V., Thakur, D., & Pappas, G. J. (2018). "Resilient Active Information Gathering with Mobile Robots". *IEEE/RSJ IROS 2018*, pp. 4309–4316. DOI 10.1109/IROS.2018.8593630 (verificado; contenido no revisado). — [DOI](https://doi.org/10.1109/IROS.2018.8593630)
- Duan, P., & Chen, D. (2025). "Distributed Cooperative Path Planning for Multi-UAV in Information-Rich and Dynamic Environments". *Drones*, 9(1), 38. DOI 10.3390/drones9010038 (verificado). Planificación colaborativa distribuida con información multifuente y objetivos dinámicos. — [DOI](https://doi.org/10.3390/drones9010038)
- Nigam, N. (2013). "Dynamic Replanning for Multi-UAV Persistent Surveillance". *AIAA GNC 2013*. DOI 10.2514/6.2013-4887 (verificado; solo título). — [DOI](https://doi.org/10.2514/6.2013-4887)

### Inferences
- Para el proyecto, el **"UAV que se silencia"** puede modelarse de dos formas compatibles:
  - (a) como **evidencia de jamming** cerca de su última posición conocida, al estilo de Liu et al. (2012), donde la pérdida de vecinos funciona como señal;
  - (b) como **pérdida de agente** que obliga a reasignar sus puntos pendientes, al estilo CBBA o Luna et al.

  Zhou et al. (2019) dan la justificación teórica para planificar *a priori* pensando en el peor caso de pérdidas.
- Zheng et al. (2016) sugieren un experimento interesante y barato: comparar "propagar la alerta a todos" contra "propagarla solo a los UAV cuya ruta futura cruza la zona", midiendo el costo y la tasa de misión completada.

### Gaps
- No se halló un paper que trate explícitamente **"silencio de radio de un UAV" como sensor de jamming** para replanificar a los UAV que vienen detrás. Es un hueco aprovechable.
- El contenido de Nigam (2013) y de Schlotfeldt et al. (2018) no se revisó más allá del título.

---

## 5. Ruteo resiliente: caminos disjuntos o geodiversos, ruteo averso al riesgo y métricas de resiliencia

### Takeaway
La resiliencia frente a fallas **regionales** (como una zona de jamming) se ha formalizado en redes de telecomunicaciones como **diversidad geográfica de caminos**: GeoDivRP, basado en Suurballe más una separación mínima d. En planificación con amenazas, el riesgo multiplicativo (probabilidad de supervivencia) se vuelve aditivo con la transformación −ln(1−p), lo que permite aplicar directamente Dijkstra y Yen. Las métricas estándar son la probabilidad de supervivencia del camino, la tasa de misión completada, el valor esperado de la misión y la diversidad de caminos.

### Cited Findings
- **Clásicos (todos verificados):**
  - Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs". *Numerische Mathematik*, 1, 269–271. DOI 10.1007/BF01386390. — [DOI](https://doi.org/10.1007/BF01386390)
  - Yen, J. Y. (1971). "Finding the K Shortest Loopless Paths in a Network". *Management Science*, 17(11), 712–716. DOI 10.1287/mnsc.17.11.712. — [DOI](https://doi.org/10.1287/mnsc.17.11.712)
  - Suurballe, J. W. (1974). "Disjoint paths in a network". *Networks*, 4(2), 125–145. DOI 10.1002/net.3230040204. Calcula pares o conjuntos de caminos disjuntos de costo total mínimo. — [DOI](https://doi.org/10.1002/net.3230040204)
- **Sterbenz, J. P. G., Hutchison, D., Çetinkaya, E. K., Jabbar, A., Rohrer, J. P., & Schöller, M. (2010).** "Resilience and survivability in communication networks: Strategies, principles, and survey of disciplines". *Computer Networks*, 54(8), 1245–1265. DOI 10.1016/j.comnet.2010.03.005 (verificado, unas 790 citas). Es el marco ResiliNets: estrategia D²R² + DR, es decir defender, detectar, remediar, recuperar, más diagnosticar y refinar. Aporte: vocabulario formal para estructurar el proyecto, donde detectar = CLUN-LSR, remediar = replanificar y recuperar = completar la misión. — [DOI](https://doi.org/10.1016/j.comnet.2010.03.005)
- **Rohrer, J. P., Jabbar, A., & Sterbenz, J. P. G. (2014).** "Path diversification for future internet end-to-end resilience and survivability". *Telecommunication Systems*, 56(1), 49–67 (en línea en 2013). DOI 10.1007/s11235-013-9818-7 (verificado). Propone la diversificación de caminos como mecanismo de resiliencia extremo a extremo, con métricas de diversidad de caminos. El detalle de las fórmulas no se revisó en el texto completo. — [DOI](https://doi.org/10.1007/s11235-013-9818-7)
- **GeoDivRP (ResiliNets, Universidad de Kansas):** aplica caminos mínimos de forma iterativa, al estilo de Suurballe, **penalizando las aristas ya usadas**. Una vez que tiene k caminos, elige el conjunto cuyos nodos están separados por más de una **distancia d**. Las capas superiores especifican la tupla (k, d, [h, t]), donde h son los saltos extra y t el desfase de retardo; los autores eligieron k = 3. — [ResiliNets](https://resilinets.org/geodivrp_geodiverse_multipath_routing_protocol.html)
- **Cheng, Y., Medhi, D., & Sterbenz, J. P. G. (2015).** "Geodiverse routing with path delay and skew requirement under area-based challenges". *Networks*, 66(4), 335–346. DOI 10.1002/net.21660 (verificado). Extiende GeoDivRP con un problema de flujo multicommodity de mínimo costo diverso y una optimización no lineal de retardo y desfase. Se implementa en ns-3 y supera a OSPF-ECMP en utilización de enlaces bajo **desafíos regionales**, como desastres o ataques. Variante con jitter: Cheng & Sterbenz, RNDM 2014, DOI 10.1109/RNDM.2014.7014949. — [DOI](https://doi.org/10.1002/net.21660)
- **Riesgo multiplicativo a costo aditivo:** un trabajo reciente sobre caminos con restricción de recursos define el costo de nodo como −ln(1 − riesgo). Así, minimizar la suma equivale a **maximizar el producto de las probabilidades de supervivencia** del camino, porque los solucionadores de caminos mínimos necesitan costos aditivos. El trabajo es sobre un UGV, pero las matemáticas son idénticas. — [arXiv:2511.18236](https://arxiv.org/pdf/2511.18236). Un trabajo coreano (en coreano) recuerda que el "most reliable path problem" se convierte en un problema de camino mínimo y compara algoritmos para la supervivencia de UAV. — [KoreaScience](https://koreascience.or.kr/article/JAKO201128563049638.pdf)
- **Sanjab, A., Saad, W., & Başar, T. (2017).** "Prospect theory for enhanced cyber-physical security of drone delivery systems: A network interdiction game". *IEEE ICC 2017*. DOI 10.1109/ICC.2017.7996862 (verificado). Plantea un juego de interdicción de suma cero en grafo: el operador elige el camino del UAV y el atacante elige dónde interceptar. Caracteriza el equilibrio de Nash y añade teoría prospectiva (percepciones subjetivas de la probabilidad de éxito del ataque). Aporte: la versión adversaria de "elegir un camino resiliente". Extensión en *IEEE Trans. Communications*, 68(11), 2020, DOI 10.1109/TCOMM.2020.3010289. — [DOI](https://doi.org/10.1109/ICC.2017.7996862)
- **JarmRout** (Pu, 2018; ver sección 1) incorpora la **distancia espacial entre caminos** en el ruteo multipath contra jamming. Es el análogo en capa de red de la geodiversidad. Sus métricas son PDR, latencia y tasa de interrupción extremo a extremo. — [DOI](https://doi.org/10.1109/ACCESS.2018.2879758)
- **Métricas de resiliencia usadas en la literatura revisada:**
  - Tasa de éxito y colisiones (Wang et al., 2021). — [DOI](https://doi.org/10.1109/ICCWorkshops50388.2021.9473587)
  - SINR de peor caso (Wang F. et al., 2024; Duan et al., 2018). — [DOI](https://doi.org/10.3390/drones8100558)
  - Distancia de vuelo con restricción de calidad de enlace (Dong et al., 2022). — [DOI](https://doi.org/10.1109/LSP.2022.3149374)
  - Información esperada recolectada con riesgo de detección (Badenbroek et al., 2024; sección 7). — [arXiv](https://arxiv.org/abs/2406.19001)
  - Utilización de enlaces bajo falla regional (Cheng et al., 2015). — [DOI](https://doi.org/10.1002/net.21660)
  - Mejora en éxito de misión al integrar el desempeño GNSS (36 %, ENC 2024). — [Sciforum](https://sciforum.net/paper/19973)

### Inferences
- El "par resiliente" que el proyecto ya implementa (Yen más una selección de par) queda bien justificado como **aproximación heurística a Suurballe y GeoDivRP**: generar k caminos con Yen y elegir el par que maximiza la separación geográfica mínima, o que minimiza las aristas compartidas, sujeto a un sobrecosto acotado. Conviene citar explícitamente la tupla (k, d) de GeoDivRP y reportar como métrica la **separación mínima entre los dos caminos** frente al radio típico de una zona de jamming. Si d es mayor que 2·(r_J + k·σ), una sola zona no puede cortar ambos caminos.
- Una métrica compuesta defendible es P_sup(camino) = ∏(1 − p_e), con costo de arista −ln(1 − p_e). Para el par: P(al menos uno sobrevive) = 1 − (1 − P₁)(1 − P₂) si son independientes. La geodiversidad hace razonable el supuesto de independencia. Sumar la **tasa de misión completada** en Monte Carlo y el **costo extra de replanificación** frente a Dijkstra sin información.

### Gaps
- No se halló un paper que aplique **GeoDivRP o Suurballe a trayectorias físicas de UAV** frente a jamming. Su uso documentado es en redes de fibra o telecomunicaciones. La transferencia es, por tanto, una contribución del proyecto y hay que presentarla así.
- No se revisaron las fórmulas exactas de diversidad de Rohrer et al. (2014). Se recomienda leer el PDF antes de citar una ecuación concreta.

---

## 6. Engaño y señuelos en sistemas multi-UAV o enjambres (resumen académico, sin orientación operativa)

### Takeaway
El engaño se estudia académicamente con tres lentes: **reconocimiento de objetivos** (planificar caminos que oculten el destino), **control cooperativo** (generar trazas fantasma ante radares) y **juegos o aprendizaje multiagente** (señuelos frente a sensores adversarios). Las métricas típicas son la probabilidad de que el observador identifique el objetivo, la distancia entre la amenaza y el activo protegido, y la degradación de la inferencia del adversario.

### Cited Findings
- **Masters, P., & Sardina, S. (2017).** "Deceptive Path-Planning". *IJCAI-17*, pp. 4368–4375. DOI 10.24963/ijcai.2017/610 (verificado). Formaliza la planificación engañosa como minimizar la probabilidad de que un observador identifique el destino antes de llegar. Introduce el **último punto engañoso** (LDP) para ordenar caminos según su potencial de engaño, junto con estrategias de *simulación* (mostrar lo falso) y *disimulación* (ocultar lo real), basadas en reconocimiento probabilístico de objetivos. Aporte: métrica formal y modelo en grafo. Limitación: un solo agente y observador pasivo. — [DOI](https://doi.org/10.24963/ijcai.2017/610)
- **Purvis, K. B., Chandler, P. R., & Pachter, M. (2006).** "Feasible Flight Paths for Cooperative Generation of a Phantom Radar Track". *J. Guidance, Control, and Dynamics*, 29(3), 653–661. DOI 10.2514/1.15563 (verificado). Estudia la factibilidad dinámica de que un equipo de vehículos cooperantes genere una **traza fantasma coherente** ante una red de radares, con cotas de condiciones iniciales y control cooperativo descentralizado (3 radares contra 3 vehículos). Aporte: ejemplo clásico de cómo el engaño impone restricciones de trayectoria coordinada. — [DOI](https://doi.org/10.2514/1.15563)
- **Bildik, E., Tsourdos, A., Perrusquía, A., & Inalhan, G. (2024).** "Swarm Decoys Deployment for Missile Deceive using Multi-Agent Reinforcement Learning". *ICUAS 2024*, pp. 256–263. DOI 10.1109/ICUAS60882.2024.10556889 (verificado). Usa MADDPG para aprender rutas de 6 señuelos en formación líder-seguidor (recompensa que favorece la formación triangular) que maximizan la distancia entre el misil y el blanco naval. Extensión en *Aerospace* 11(8):684, 2024, DOI 10.3390/aerospace11080684. Limitación: dominio naval y amenaza tipo misil. — [DOI](https://doi.org/10.1109/ICUAS60882.2024.10556889)
- **Mareschal de Charentenay, S. (2026).** Tesis doctoral "Swarm intelligence to deceive an adversary detection system", IMT Atlantique / Lab-STICC, defendida el 1 de junio de 2026. Modela (i) la amenaza estática como **riesgo de destrucción espacialmente correlacionado** entre miembros del enjambre, combinando planificación global con control local de formación para limitar la exposición, y (ii) el engaño frente a un adversario adaptativo como **juego estocástico parcialmente observable de suma cero** (OS-POSG). En simulación, el enjambre explota los límites de resolución de un radar para que este infiera mal su tamaño y distribución. — [IMT Atlantique](https://www.imt-atlantique.fr/en/events/stanislas-mareschal-de-charentenay-thesis-defence?page=1)
- El juego de interdicción de Sanjab et al. (2017) (sección 5) es el marco adversario de selección de caminos más cercano al grafo del proyecto. — [DOI](https://doi.org/10.1109/ICC.2017.7996862)

### Inferences
- Para el proyecto, el engaño solo debería aparecer como **trabajo relacionado o futuro**: por ejemplo, que la geodiversidad de caminos también reduce la predictibilidad de la ruta, lo que conecta con la métrica de Masters & Sardina. Basta con citar el modelo y la métrica, sin operativizarlo. El concepto de "riesgo espacialmente correlacionado" de la tesis de IMT Atlantique es útil para justificar que dos UAV en el mismo corredor no fallan de forma independiente.

### Gaps
- No se encontraron trabajos revisados por pares sobre "UAV señuelo que atrae jamming" en ruteo de comunicaciones. La literatura de señuelos se concentra en radar y misiles.

---

## 7. Modelos de misión ISR: visitar puntos de observación bajo amenaza (orienteering con riesgo)

### Takeaway
La misión "visitar puntos de observación bajo amenaza" tiene una formalización estándar como **problema de orienteering (OP)** con riesgo, en versiones robusta, multiobjetivo, con restricción de supervivencia o maximizando el valor esperado con probabilidad de detección. Esto permite justificar la definición de misión del proyecto con literatura de investigación de operaciones.

### Cited Findings
- **Evers, L., Dollevoet, T., Barros, A. I., & Monsuur, H. (2014).** "Robust UAV mission planning". *Annals of Operations Research*, 222(1), 293–315 (en línea en 2012). DOI 10.1007/s10479-012-1261-8 (verificado). Plantea la selección de objetivos de reconocimiento para UAV como **orienteering robusto** frente a la incertidumbre, por ejemplo en el consumo de combustible por clima. En su revisión de literatura menciona modelos que consideran la probabilidad de supervivencia según el tiempo en zonas de amenaza. — [DOI](https://doi.org/10.1007/s10479-012-1261-8); [TNO PDF](https://publications.tno.nl/publication/100738/lX6E6z/evers-2011-robust.pdf)
- **Daşdemir, E., Batta, R., Köksalan, M., & Tezcaner Öztürk, D. (2022).** "UAV routing for reconnaissance mission: A multi-objective orienteering problem with time-dependent prizes and multiple connections". *Computers & Operations Research*, 145, 105882. DOI 10.1016/j.cor.2022.105882 (verificado). OP multiobjetivo que equilibra recolección de información, duración y **seguridad de la misión**. Usa MIP para instancias pequeñas y un método híbrido para las grandes. — [DOI](https://doi.org/10.1016/j.cor.2022.105882); [METU](https://open.metu.edu.tr/handle/11511/98055)
- **Jorgensen, S., Chen, R. H., Milam, M. B., & Pavone, M. (2018).** "The Team Surviving Orienteers problem: routing teams of robots in uncertain environments with survival constraints". *Autonomous Robots*, 42, 927–952. DOI 10.1007/s10514-017-9694-1 (verificado; versión de conferencia en IRC 2017, DOI 10.1109/IRC.2017.49). Ruteo de **equipos** de robots en entornos inciertos con **restricciones de supervivencia**. El abstract no se recuperó; la descripción viene del título. — [DOI](https://doi.org/10.1007/s10514-017-9694-1)
- **Badenbroek, R., Jurrius, R., & Verlinde, L. (2024/2025).** "Optimal routing and transmission strategies for UAV reconnaissance missions with detection threats". arXiv:2406.19001, v2 de febrero de 2025 (preprint). Un UAV visita puntos de interés y decide en cada uno si transmite ya o difiere. Ambas opciones tienen **riesgo de detección**, que hace fracasar la misión. El objetivo es maximizar la **información esperada**. Prueban que el problema es NP-completo, dan una formulación ILP y un algoritmo genético para hasta 10 POI, con código como anexo. Aporte: conecta comunicación y ruta en el mismo modelo de riesgo, igual que el proyecto. — [arXiv](https://arxiv.org/abs/2406.19001)
- Manyam, S. G., Rasmussen, S., Casbeer, D. W., Kalyanam, K., & Manickam, S. (2017). "Multi-UAV routing for persistent intelligence surveillance & reconnaissance missions". *ICUAS 2017*, pp. 573–580. DOI 10.1109/ICUAS.2017.7991314 (verificado; solo título). — [DOI](https://doi.org/10.1109/ICUAS.2017.7991314)
- Un estudio coreano de VRP para UAV modela el nivel de amenaza combinando probabilidades de **detección y derribo**, y equilibra seguridad contra tiempo de misión. — [KoreaScience](https://koreascience.or.kr/article/JAKO201519262930576.pdf)

### Inferences
- La misión del proyecto puede definirse como un **OP de equipo con supervivencia**: maximizar los puntos de observación visitados (o la información esperada) sujeto a P_sup ≥ umbral por UAV, siguiendo a Jorgensen et al., con riesgo dinámico actualizado por las alertas de jamming. La métrica "puntos visitados / puntos planificados" en Monte Carlo es una **tasa de misión completada** directamente defendible.

### Gaps
- No se recuperaron los abstracts de Evers, Daşdemir ni Jorgensen. Antes de citar fórmulas, verificar en los PDF.

---

## 8. Uso de datos reales del conflicto en Ucrania (ACLED, GPSJam, líneas del frente) en planificación o modelado de riesgo

### Takeaway
**No se encontró ningún paper revisado por pares que use ACLED, GPSJam o líneas del frente de Ucrania como entrada de un planificador de rutas de UAV.** Sí hay literatura revisada por pares que usa **ADS-B colaborativo** (OpenSky) para cartografiar interferencia GNSS en Europa del Este desde febrero de 2022 y en zonas de conflicto en 2024. Esa es la fuente académicamente defendible para construir zonas de interferencia "realistas". GPSJam y ACLED son datasets públicos útiles, pero no son publicaciones científicas.

### Cited Findings
- **Figuet, B., Waltert, M., Felux, M., & Olive, X. (2022).** "GNSS Jamming and Its Effect on Air Traffic in Eastern Europe". *Engineering Proceedings*, 28(1), 12 (10th OpenSky Symposium). DOI 10.3390/engproc2022028012 (verificado). Usa ADS-B colaborativo para analizar la interferencia GNSS en Europa del Este entre **febrero y agosto de 2022**. Hubo días con **más de 1000 vuelos afectados (60 % del tráfico diario** del área analizada), y **las aeronaves a baja altitud se ven menos afectadas** que las que vuelan alto. — [DOI](https://doi.org/10.3390/engproc2022028012)
- **Felux, M., Figuet, B., Lenders, V., Monstein, R., & Strohmeier, M. (2025).** "Navigating Turbulence: Understanding New GNSS Risks in Conflict Zones". *17th Int. Conf. on Cyber Conflict (CyCon 2025)*, pp. 245–264. DOI 10.23919/CyCon65856.2025.11103718 (verificado). Con una herramienta basada en ADS-B identifican puntos calientes de jamming y spoofing en **2024**: Mar Negro, Mediterráneo oriental y frontera India-Pakistán. Las detecciones diarias llegaron a **1500 vuelos** y bajaron a unos 500 a fines de 2024. — [DOI](https://doi.org/10.23919/CyCon65856.2025.11103718)
- **Schäfer et al. (2023), ION GNSS+** (sección 3): un año de detección por ADS-B en la red europea, incluido el Báltico, y localización por horizonte de radio. — [DOI](https://doi.org/10.33012/2023.19393)
- **GPSJam.org** (no revisado por pares): mapa público construido con datos de ADS-B Exchange, que colorea zonas según la exactitud reportada por las aeronaves (parámetro NACp). ADS-B **no detecta la interferencia directamente**, sino su impacto en la aviación civil. — [Inside GNSS](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
- Material de Stanford (ION ITM 2026, sin DOI verificado) describe un spoofing en el Mar Negro en el que aeronaves parecían aproximarse a aeropuertos de Crimea; por ejemplo, el 25 de diciembre de 2023, con trayectorias falsas de aterrizaje en Belbek. — [Stanford PDF](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)
- Un artículo de *GPS Solutions* (2026, contenido no revisado) despliega un monitor GNSS de bajo costo en Gdynia (Polonia) y confirma interferencia en el Golfo de Gdansk. — [Springer](https://link.springer.com/article/10.1007/s10291-026-02061-5)
- **ACLED Ukraine Conflict Monitor:** datos casi en tiempo real de violencia política en Ucrania desde el 24 de febrero de 2022. Se publican cada miércoles y los eventos pasados se revisan. Las cifras de fatalidades son conservadoras. — [ACLED](https://acleddata.com/monitor/ukraine-conflict-monitor)
- **Contexto no académico** (declaración oficial, no revisada por pares): el viceprimer ministro ucraniano Fedorov afirmó que los drones cambian altitud, rutas y patrones según dónde se usan los equipos de guerra electrónica. Es evidencia anecdótica de que el problema de "replanificar según zonas de EW" es real. — [Ukrinform](https://www.ukrinform.net/rubric-defense/3924457-ukraine-actively-developing-antidrone-tech-vice-pm.html)

### Inferences
- Para un escenario "realista" defendible, conviene **derivar las zonas de interferencia de la literatura ADS-B revisada por pares** (Figuet 2022; Felux 2025) o de GPSJam, citado como dataset. Hay que dejar claro que ADS-B mide el **impacto en aeronaves a gran altitud**, y que Figuet et al. muestran menor afectación a baja altitud. Esto es una limitación explícita al extrapolar a drones pequeños.
- ACLED puede justificar la **densidad de amenaza** (eventos por celda), pero no la ubicación de jammers. Sería una capa de "riesgo general", separada de la capa de jamming.

### Gaps
- No se encontró ningún trabajo académico de planificación de rutas de UAV que use datos reales de Ucrania (ACLED, GPSJam o líneas del frente de DeepState u otros). La afirmación "no existe" está limitada por esta búsqueda.
- No se pudo extraer el texto del PDF de CyCon 2025 (binario). Las cifras citadas vienen del abstract oficial (OpenAlex).

---

## 9. Propuesta de encaje: qué papers sostienen mejor cada pieza de la extensión

### Takeaway
La cadena **CLUN-LSR (detección) → localización con incertidumbre → actualización de costos en el grafo → replanificación incremental o par geodiverso → métrica de supervivencia y misión** se puede respaldar pieza por pieza con literatura revisada por pares. La novedad defendible está en **unir** esas piezas (ruteo de paquetes y ruteo físico) en un sistema multi-UAV. No se encontró ningún trabajo que lo haga completo.

### Cited Findings
**(1) La detección de jamming como alerta (manteniendo CLUN-LSR)**
- Zheng et al. (2024/2025), CLUN-LSR. Usa el estado del espectro de la capa de enlace y los vecinos a dos saltos para evitar nodos en el área de interferencia. — [DOI](https://doi.org/10.1016/j.adhoc.2024.103702)
- Duan et al. (2018). Detección por RSS + PER como primera etapa de un marco detección-localización-evasión. — [DOI](https://doi.org/10.1109/ROBIO.2018.8665238)
- Liu et al. (2012), TPDS. Los cambios de vecindad causados por jamming son una señal medible y localizable. CLUN-LSR lo cita. — [DOI](https://doi.org/10.1109/TPDS.2011.154)
- Complementos: Pu (2018), JarmRout, como baseline de ruteo anti-jamming — [DOI](https://doi.org/10.1109/ACCESS.2018.2879758); y Zhang et al. (2026), ComMag, con colaboración de vecindario del mismo grupo — [DOI](https://doi.org/10.1109/MCOM.001.2600062).

**(2) Convertir la alerta en una zona de evitación con incertidumbre**
- Duan et al. (2018). Localización conjunta de posición y potencia por RSS más evasión robusta de peor caso. — [DOI](https://doi.org/10.1109/ROBIO.2018.8665238)
- Liu, Lo, Blanch, Chen & Walter (2025), NAVIGATION. Localización con **cotas de error y mapas de calor de probabilidad**. — [DOI](https://doi.org/10.33012/navi.716)
- Ahmed, Winter & Sokolova (2021). Localización colaborativa por una **red de UAV** para alejarse de la región afectada. — [DOI](https://doi.org/10.1109/AERO50100.2021.9438441)
- Wang F. et al. (2024), *Drones*. Jammers con ubicación y potencia imperfectas tratados con S-procedure, como región de incertidumbre acotada. — [DOI](https://doi.org/10.3390/drones8100558)

**(3) Algoritmo de replanificación**
- Koenig & Likhachev (2005). D* Lite para reparar caminos cuando cambian los costos de las aristas. — [DOI](https://doi.org/10.1109/TRO.2004.838026)
- Yen (1971) y Suurballe (1974), más GeoDivRP / Cheng et al. (2015), para el par de caminos geodiversos separados por una distancia d. — [Yen](https://doi.org/10.1287/mnsc.17.11.712); [Suurballe](https://doi.org/10.1002/net.3230040204); [Cheng 2015](https://doi.org/10.1002/net.21660)
- Dong et al. (2022). A* sobre mapas de radio y SINR construidos con topografía real. — [DOI](https://doi.org/10.1109/LSP.2022.3149374)
- Luna et al. (2024), JFR. Replanificación multi-UAV en vuelo con arquitectura distribuida-centralizada y vuelos reales. — [DOI](https://doi.org/10.1002/rob.22342)
- Zheng, Liu & Zhang (2016), KBS. Estrategias adaptativas de compartición de amenazas. — [DOI](https://doi.org/10.1016/j.knosys.2016.09.021)

**(4) Métrica de resiliencia**
- Kim & Hespanha (2003). Camino de mínimo riesgo frente a defensas terrestres sobre un grafo discretizado. — [DOI](https://doi.org/10.1109/CDC.2003.1272863)
- La transformación −ln(1−p): la suma de costos equivale al producto de supervivencias. — [arXiv:2511.18236](https://arxiv.org/pdf/2511.18236)
- Jorgensen et al. (2018). Orienteering de equipo con **restricción de supervivencia**, para la tasa de misión completada. — [DOI](https://doi.org/10.1007/s10514-017-9694-1)
- Sterbenz et al. (2010) y Rohrer et al. (2014). Marco ResiliNets (D²R² + DR) y diversidad de caminos. — [Sterbenz](https://doi.org/10.1016/j.comnet.2010.03.005); [Rohrer](https://doi.org/10.1007/s11235-013-9818-7)
- Wang, Gursoy, Erpek & Sagduyu (2021). Tasa de éxito y colisiones en multi-UAV con jammer dinámico. — [DOI](https://doi.org/10.1109/ICCWorkshops50388.2021.9473587)

### Inferences
- **Diseño experimental sugerido**, sintetizado a partir de los setups revisados:
  - **Escenarios:** grafo geolocalizado con k jammers ocultos, en posiciones aleatorias o derivadas de puntos calientes ADS-B reportados (Figuet 2022; Felux 2025).
  - **Revelado de amenazas:** cada jammer se descubre cuando un UAV entra en su radio (detección CLUN-LSR) o cuando un UAV "se silencia".
  - **Variantes comparadas:**
    - (i) Dijkstra sin información (baseline actual);
    - (ii) Dijkstra o A* con replanificación tras la alerta, con zona = disco r_J + k·σ;
    - (iii) D* Lite incremental;
    - (iv) par geodiverso Yen + separación d (estilo GeoDivRP) con conmutación al camino de respaldo.
  - **Métricas:**
    - tasa de misión completada, como fracción de puntos de observación visitados (Jorgensen; Badenbroek);
    - supervivencia esperada del camino, ∏(1 − p_e);
    - sobrecosto de distancia o tiempo frente al óptimo con información perfecta (Dong 2022; Wang 2021 lo usan como "ideal");
    - tiempo de cómputo de la replanificación (Luna 2024);
    - separación mínima del par frente al radio de zona (GeoDivRP);
    - opcionalmente, PDR y throughput de la capa de red (CLUN-LSR; JarmRout).
  - **Análisis de sensibilidad:** número de jammers, σ de localización, k del margen y latencia de propagación de la alerta.
- **Frase de justificación académica** (borrador): *"Siguiendo el marco detección-localización-evasión de Duan et al. (2018) y la estrategia D²R² + DR de Sterbenz et al. (2010), extendemos CLUN-LSR (Zheng et al., 2025) para que la detección de denegación de espectro, ya presente en su capa de red, se traduzca en zonas de evitación con incertidumbre (Liu et al., 2012; Liu et al., 2025) que actualizan los costos del grafo de vuelo y disparan replanificación incremental (Koenig & Likhachev, 2005) o la conmutación a un camino geodiverso (Suurballe, 1974; Cheng et al., 2015) en los UAV que aún no entran en la zona."*

### Gaps
- Falta confirmar en el PDF de CLUN-LSR el modelo de jammer y los parámetros de simulación, para que el escenario físico del proyecto sea coherente con el de la capa de red (mismo radio de jamming, misma potencia).
- No se verificaron en esta sesión los DOI de: el paper original de D* Lite (AAAI 2002); "Anti-jamming 3D trajectory design for UAV-enabled wireless sensor networks under probabilistic LoS channel"; y el paper de planificación jerárquica 4D DPRRT*/HAPF (*Drones*, 2023). Por eso se omitieron o se marcaron como no verificados.

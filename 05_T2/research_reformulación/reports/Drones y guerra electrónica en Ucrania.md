# La alerta de jamming redibuja la ruta

*Informe de investigación para actualizar la propuesta de la Tarea 2 del curso "Algoritmos de Ruteo Resiliente" (UDP). Fecha de corte de las fuentes: 18 de octubre de 2026. Solo fuentes abiertas; nivel descriptivo y de modelado de simulación, sin guía táctica ni operacional.*

## Resumen ejecutivo

La evidencia pública de la guerra de drones en Ucrania permite pasar de CLUN-LSR a un ruteo físico resiliente sin abandonar su base teórica. La idea que mejor sostiene ese paso es la **(a), reconocimiento con alerta**: el primer UAV que detecta interferencia avisa a los demás con el mecanismo de CLUN-LSR, el aviso se convierte en una zona con radio de incertidumbre y los UAV que todavía no entran en ella replanifican su trayectoria. Tres hechos la respaldan. La guerra electrónica (EW) es la causa de fracaso más citada: un registro de primera mano atribuye **31 % de las salidas FPV fallidas a la EW enemiga** ([War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)) y RUSI estima que **60–80 % de los FPV no llegan al blanco** por todas las causas ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). Los jammers tácticos tienen radios de **0,2–3 km**, así que esquivarlos por ruta es plausible. Y en la práctica ya hay oleadas en las que los primeros drones informan la ruta de los siguientes ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). La idea (a) encaja con el curso (un grafo, Dijkstra por km, Yen y una métrica de resiliencia) y con la base teórica, porque la bibliografía de CLUN-LSR ya cita trabajos de localización de jammers y de trayectorias anti-jamming ([Crossref](https://api.crossref.org/works/10.1016/j.adhoc.2024.103702)). También encaja con la sugerencia del profesor de que un UAV que va delante comunique las fallas. Además, corrige la debilidad de los resultados preliminares del grupo: hoy la selección resiliente no supera a un Dijkstra que replanifica, porque todo se descubre de forma local. La idea **(b), flota señuelo**, tiene mucha evidencia de uso: según la inteligencia ucraniana, cerca de la mitad de los drones que Rusia lanzó a fines de 2024 eran señuelos ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2024/11/11/7483868/)). Pero nadie ha medido de forma independiente su efecto, no hay literatura sobre señuelos que atraigan jamming en ruteo y exige modelar un adversario que se adapta, así que debe quedar como trabajo relacionado. Para los datos bastan seis fuentes abiertas: DeepStateMap, cobertura del suelo y relieve, viento a la altura de vuelo, GPSJam, el modelo de incendios de guerra de The Economist y ACLED (o sus respaldos). En cambio, **no existe ningún mapa público del jamming en el frente**. Esa capa tiene que ser sintética, con radios, bandas y latencias tomados de las fuentes, y declararse como supuesto. Por último, la zona de estudio debería salir del centro de Mykolaiv, a 50–70 km del frente, y pasar a un corredor Mykolaiv–Kherson que termine en la ribera derecha del Dnipro, donde la línea de contacto es un río estable desde noviembre de 2022.

## Un frente saturado de drones donde el reconocimiento ya es casi solo UAV

### Los tipos de drones forman capas por alcance y función

El campo de batalla de 2025–2026 funciona como un ecosistema de drones en capas. Según RUSI, el reconocimiento de ambos bandos "se ha realizado casi exclusivamente con UAV". Cada batallón ucraniano debe mantener **4 a 6 órbitas** simultáneas, y las unidades dedicadas a drones cubren tramos de **40 a 70 km** de frente ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). Solo las Fuerzas de Sistemas No Tripulados ucranianas (USF) operan **más de 250 modelos** distintos ([OSW](https://www.osw.waw.pl/en/publikacje/osw-commentary/2025-10-14/game-drones-production-and-use-ukrainian-battlefield-unmanned)).

En la capa de reconocimiento más cercana trabajan multirrotores tipo DJI Mavic, que observan, corrigen el tiro de artillería y sueltan granadas VOG-17 de 350 g ([CTC Sentinel](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/)). Más atrás operan drones de ala fija como Orlan-10, Zala, Leleka o Shark. Para el Shark, el fabricante declara más de 2 h de vuelo y 60 km de enlace ([Ukrainian News](https://ukranews.com/en/news/890883-ew-resistant-drone-that-can-adjust-himars-presented-in-ukraine-in-conditions-of-war)). En agosto de 2024, Rusia llegó a volar **1.000–1.500 órbitas diarias** de Orlan y Zala, según la defensa aérea ucraniana citada por RUSI ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)).

La capa de ataque táctico combina dos tipos de FPV. Los FPV por radio cargan unos 2 kg, alcanzan alrededor de 20 km y cuestan menos de USD 500 ([CTC Sentinel](https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/)). Los FPV por fibra óptica ya atacaban a más de 30 km del lado ruso en febrero de 2026, y un modelo ucraniano llegaba a unos 40 km ([Atlantic Council](https://www.atlanticcouncil.org/blogs/ukrainealert/fiber-optics-drones-have-emerged-as-critical-kit-for-both-russia-and-ukraine/)). La capa se completa con bombarderos pesados como el Vampire, que carga hasta 15 kg ([MoD Ucrania](https://mod.gov.ua/en/news/the-vampire-a-drone-that-terrifies-enemies-and-assists-ukrainians)) y se usa "predominantemente de noche" por su lentitud ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)), y con municiones merodeadoras tipo Lancet.

En el largo alcance, los drones de ataque unidireccional Shahed/Geran pasaron de unos 130 lanzamientos semanales antes de septiembre de 2024 a más de 1.000 en marzo de 2025 ([CSIS](https://www.csis.org/analysis/drone-saturation-russias-shahed-campaign)). En todo 2025 sumaron **54.538 lanzamientos** ([ISIS](https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine)). Completan el cuadro los interceptores, los relés y las "nodrizas", drones que transportan a otros. El Puhach, por ejemplo, suelta cuadricópteros a hasta 37 km ([Kyiv Independent](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)). Los señuelos se tratan en la comparación de misiones.

### Las capas forman un ciclo de reconocimiento y ataque que define la kill zone

Las capas se encadenan en un ciclo de reconocimiento y ataque. Los drones observadores transmiten video a los puestos de mando de batallón y brigada, y desde ahí se asigna cada blanco a FPV, bombarderos o artillería. RUSI distingue tres franjas según la distancia a la línea: una "transparencia" casi total en los **3 km** más próximos, una densidad de observación que va bajando hasta los **15 km** y reconocimiento asignable con latencia razonable hasta unos **40 km** ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)).

Esa transparencia es la "kill zone", el término que ya reemplaza a "zona gris". Las estimaciones de su profundidad difieren porque no miden lo mismo. Robert Brovdi, comandante de las USF, la sitúa en **25 km o más por lado**, según la regularidad y densidad de los ataques registrados ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2026/05/14/8034645/)). El subsecretario del Consejo de Seguridad ucraniano habla de unos 20 km, y de hasta 50 km en algunas áreas; el ISW sostiene que ningún bando puede concentrar fuerzas a menos de unos 30 km del frente ([Business Insider vía Yahoo](https://www.yahoo.com/news/world/articles/front-line-drone-kill-zone-110501096.html)). NPR reporta en octubre de 2026 una franja de 10–20 millas por lado, y el caso de un grupo que tardó **cuatro horas en recorrer 1 km** escondiéndose de los drones ([NPR](https://www.npr.org/2026/10/05/nx-s1-5925803/drones-buzz-overhead-troops-hunker-underground-in-ukraines-hellish-kill-zone)).

La interdicción logística llega más lejos. La unidad rusa Rubikon ataca la logística a **10–40 km** de la línea. Según un bloguero ruso citado por Jamestown, más de la mitad de sus blancos en 2025 fueron drones ucranianos o su infraestructura de antenas, radares y EW ([Jamestown](https://jamestown.org/rubicon-reveals-limits-of-russias-drone-centralization/)). Detectar tampoco basta, porque importa la latencia entre detectar y actuar: drones V-BAT encontraron 140 blancos rusos de alto valor, pero en más de 100 casos ningún dron de ataque pudo alcanzarlos a tiempo ([Kyiv Independent](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)).

### Implicancias para la simulación

Para el proyecto, la misión más representativa y "ruteable" es la de un dron de ala fija de reconocimiento, o la de un multirrotor, que visita puntos de observación y entrega la información con baja latencia al nodo de mando. De la evidencia salen tres consecuencias. Primero, el área de operación debe cubrir al menos **15–25 km desde la línea**, porque ahí se concentra la amenaza táctica, y el recorte urbano actual de unos 7 × 7 km no alcanza para representarla. Segundo, la latencia de entrega es una métrica legítima, no un detalle accesorio. Tercero, los drones, relés y antenas son en sí mismos blancos prioritarios, así que conviene modelar la pérdida de nodos y no solo el bloqueo de tramos.

## La guerra electrónica explica un tercio de los fracasos y obliga a cambiar de banda cada pocos meses

### Las pérdidas son altísimas y la EW es solo una parte de ellas

Los drones tácticos se pierden en enormes cantidades, y la EW es la causa individual más citada, aunque nunca la única. RUSI estima que **60–80 % de los FPV ucranianos no alcanzan su blanco**, según el sector y la pericia del operador, y que hay "largos períodos" en que la EW o el clima degradan mucho las operaciones ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). El único desglose de primera mano por causa que aparece en fuentes abiertas es el de un equipo FPV en Donbás, en 2024–2025 ([War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)). Las causas de las salidas fallidas se reparten así:

| Causa | Porcentaje |
|---|---|
| EW enemiga | 31 % |
| Fallos técnicos al despegar | ~25 % |
| No detonación | ~10 % |
| Jamming propio | ~3 % |
| Interferencia entre drones | ≥3 % |

Otro testimonio da una idea del desgaste: un instructor estima la vida operativa media de un Mavic en el frente en **unos 7 días** ([Militarnyi](https://militarnyi.com/en/news/on-the-front-lines-average-lifespan-of-mavic-drone-is-one-week-instructor-with-93rd-brigade/)).

Las cifras globales son menos fiables. La estimación de RUSI de "10.000 drones perdidos al mes" en 2023 venía de tres oficiales no identificados, y un experto la consideró "probablemente" sobreestimada ([Business Insider NL](https://www.businessinsider.nl/ukraine-is-losing-10000-drones-a-month-to-russian-electronic-warfare-systems-that-send-fake-signals-and-screw-with-their-navigation-researchers-say)). La cifra de OSW, "hasta 75 % neutralizados por interferencia en 2024", tiene una fuente primaria que no se pudo identificar ([OSW](https://www.osw.waw.pl/en/publikacje/osw-commentary/2025-10-14/game-drones-production-and-use-ukrainian-battlefield-unmanned)).

Contra los drones de largo alcance hay datos más sistemáticos. Según la Fuerza Aérea ucraniana, el porcentaje de Shahed "derribados o suprimidos" subió de **85,4 % a 93,3 %** entre enero y mayo de 2026, pero esa categoría no separa la EW de la intercepción cinética ([ISIS](https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine)). En el ataque del 1–2 de diciembre de 2024, 50 de 110 drones se dieron por "perdidos" por EW ([Euromaidan Press/ISW](https://euromaidanpress.com/2024/12/03/isw-ukrainian-ew-tech-increasingly-grounds-shahed-drones-complicating-russian-airstrikes/)).

Para el modelo, esto deja dos conclusiones. La probabilidad de que un jammer neutralice a un dron dentro de su zona debería rondar **0,6–0,7**, no 1; es lo que logran los fusiles inhibidores Kvertus según el instituto letón LIIA ([LIIA](https://liia.lv/en/publications/the-drone-revolution-lessons-from-ukraine-1476?get_file=1)). Y con datos públicos no se pueden calibrar por separado la falla por EW y la falla cinética, así que esa separación debe declararse como supuesto.

### Los drones y los jammers cambian de banda cada pocos meses

La EW contra drones es una carrera de saltos de banda que se mide en semanas o meses. Un manual del Estado Mayor ruso de 2024 fija el punto de partida: control en **390–490 MHz, 850–960 MHz, 1,2 GHz y 2,4 GHz**, y video en **2,4 y 5,8 GHz**. El mismo manual exige analizar la "situación radioelectrónica" con analizadores de espectro antes de cada salida, y avisar de las frecuencias propias a la EW amiga para no inhibir los propios drones ([Armada International](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/)).

Desde ahí, la migración ha sido continua. En abril–mayo de 2024, el fabricante ucraniano Kvertus detectaba FPV rusos en **720–1020 MHz**, además de 850–930 MHz, aunque estimaba que 65–70 % seguía usando frecuencias estándar ([Euromaidan Press](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/)). Del lado del inhibidor, un comandante de EW cuenta que en la primavera de 2024 el módulo estándar de 900 MHz ya no bastaba, porque los drones rusos operaban entre 750 y 1.050 MHz: en verano hacían falta 4–5 módulos y en otoño 7 ([Euromaidan Press](https://euromaidanpress.com/2025/06/26/ukraine-jamming-fails-fiber-drones-russia/)). En agosto de 2025, en un sector del frente, alrededor del 20 % de los drones rusos volaba en 400–490 MHz, el 30 % en 720–1020 MHz y el resto en 2,1–2,3 GHz, y algunos cambiaban de frecuencia de forma dinámica ([Ukrainska Pravda](https://www.pravda.com.ua/eng/articles/2025/08/08/7525279/)).

El video siguió el mismo camino. Pasó de 5,8 GHz a 1,2–1,3 GHz y 3,3 GHz ([Rubryka](https://rubryka.com/en/2024/06/13/retranslyator-vidlunnya-dlya-droniv/); [BlueBird](https://blue-bird.tech/en/products/bluebirds-chuyka-3-0-electronic-intelligence-device-5-8-ghz-3-3-ghz-1-2-ghz)). En 2026, el dron ruso Boomerang ya transmite en **6–7,2 GHz**, por encima del techo de unos 6 GHz de la mayoría de los detectores portátiles ([Militarnyi](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/)).

La congestión de frecuencias propias agrava el problema. En sectores calientes, hasta una docena de equipos comparten pocas frecuencias analógicas, y la espera antes de despegar puede llegar a 30 minutos ([War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)). Para el modelo, esto significa que un jammer solo afecta a los drones cuyas bandas cubre. La flota debería representarse como una mezcla de bandas que se redistribuye lentamente, no como un bloque homogéneo.

### Los jammers se ordenan en cuatro niveles de alcance

Los inhibidores atacan a la vez el posicionamiento satelital GNSS (L1, alrededor de 1559–1610 MHz; L2/L5, alrededor de 1176–1280 MHz), el enlace de control y el de video. Por ejemplo, el jammer direccional ucraniano Veres-2 cubre **1160–1280, 1560–1630, 2400–2500, 5160–5280 y 5725–5850 MHz**, con un alcance de 1–2 km según las unidades que lo usan ([Euromaidan Press](https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/)).

Con fuentes abiertas se pueden ordenar los sistemas en cuatro niveles. Los alcances son casi siempre afirmaciones de fabricante, ministerio o prensa, y pueden variar en un orden de magnitud: al Leer-3 se le atribuyen 6, 30 o 100 km según la fuente ([Defense News](https://www.defensenews.com/newsletters/unmanned-systems/2018/11/16/russian-drones-can-jam-cell-phones-60-miles-away/); [Army Recognition](https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2022/russian-troops-using-leer-3-able-to-jam-ukrainian-army-mobile-phone-signals-within-30-km); [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)), y al Volnorez, 600 m o más de 1 km ([Al Jundi](https://aljundi.ae/?p=36308); [Unmanned Airspace](https://www.unmannedairspace.info/counter-uas-systems-and-policies/russia-deploys-tank-mounted-volnorez-jammers-in-ukraine/)). Por eso el radio de cada nivel debe tratarse como un intervalo y someterse a análisis de sensibilidad.

| Nivel | Radio nominal | Ejemplos públicos | Bandas atacadas | Despliegue descrito | Fuentes |
|---|---|---|---|---|---|
| 1. Trinchera o personal | 0,2–0,8 km | ANTIFPV (200 m), Kvertus AD Counter FPV (300 m), Volnorez (600–800 m) | Control y video FPV (p. ej. 850–940 MHz en Kvertus; 900–2000 MHz en Volnorez) | Con la unidad o el vehículo; omnidireccional | [Euromaidan Press](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/); [Kyiv Defenders](https://kyivdefenders.com.ua/en/projects/reb-kvertus/); [Forbes vía online.ua](https://news.online.ua/en/russian-ew-systems-are-unable-to-cope-with-ukrainian-drones-forbes-873429); [Army Recognition](https://armyrecognition.com/focus-analysis-conflicts/army/defence-security-industry-technology/russia-unveils-portable-tank-mounted-drone-jammer-to-counter-ukrainian-attacks) |
| 2. Táctico o direccional | 1–3 km | Veres-2 (1–2 km), Stupor (2 km), Kupol-PRO (2,5 km) | GNSS, control y video | Sector de 90–120° o 360° | [Euromaidan Press](https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/); [Wikipedia, Stupor](https://en.wikipedia.org/wiki/Stupor_Anti-Drone_System); [AO Avtomatika](https://www.ao-avtomatika.ru/en/catalog/products/kupol-pro-portable-anti-drone-system/) |
| 3. Sistema mayor | 10–25 km | Zhitel (25 km), Bukovel (16–20 km), Pole-21 (≥25 km) | GNSS, enlaces, celular y satélite | ≥1 por cada 10 km de frente; 3–5 km detrás de la línea; ~10 km entre estaciones | [Wikipedia, Zhitel](https://en.wikipedia.org/wiki/R-330Zh_Zhitel); [Wikipedia, Bukovel](https://en.wikipedia.org/wiki/Bukovel_%28counter_unmanned_aircraft_system%29); [RUSI 2023](https://rusi.org/explore-our-research/publications/special-resources/meatgrinder-russian-tactics-second-year-its-invasion-ukraine); [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/) |
| 4. GNSS estratégico | ~250 km | Emisores en Kaliningrado | L1 y L5, todas las constelaciones | Fijo, regional | [Lo et al., Stanford](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf) |

### La interferencia GNSS opera a una escala que no se puede rodear

La interferencia del posicionamiento satelital GNSS opera a otra escala. RUSI la describe como "ubicua en toda la zona de combate" ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). Sus efectos sobre las armas guiadas están documentados: según un informe clasificado citado por la prensa, la tasa de acierto del proyectil Excalibur cayó de **55 % a 6 %** en 2023 ([Business Insider NL](https://businessinsider.nl/the-us-gave-up-sending-ukraine-excalibur-guided-artillery-shells-costing-100000-because-they-rarely-hit-their-target-report-says/)).

El spoofing, que hace creer al receptor que está en una posición falsa, también se usa contra drones. En noviembre de 2024, Ucrania desvió más de 100 Shahed hacia Rusia y Bielorrusia ([The Defense Post](https://thedefensepost.com/2024/12/05/ukraine-spoofs-shahed-drones/amp/)). Stanford observó en Rusia patrones de spoofing circulares de **2–11 km de diámetro**, recorridos a unos 200 km/h, una velocidad compatible con drones de ala fija. Desde Kaliningrado, el jamming llegó a unos 250 km de radio, y desde noviembre de 2024 se combina con spoofing ([Lo et al.](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)). En respuesta, Rusia montó en los Shahed antenas CRPA, antenas de arreglo que rechazan la interferencia, y pasó de 8 a 12 y luego a 16 elementos ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2025/02/18/7498968); [Militarnyi](https://militarnyi.com/en/news/new-chinese-crpa-antenna-found-on-russian-shahed/)).

La lección para el modelo es de escala. Una zona GNSS de decenas a cientos de kilómetros no se puede rodear: se soporta con robustez a bordo, y conviene modelarla como degradación de la navegación. Un jammer de enlace de 0,2–3 km, en cambio, sí se puede evitar por ruta, y ahí está el espacio donde el ruteo físico aporta.

Los dos fenómenos además se distinguen en el receptor. El jamming baja la relación portadora/ruido (C/N0) y la ganancia de control automático (AGC), mientras que el spoofing tiende a mantener o subir el C/N0 ([Android Developers](https://developer.android.com/develop/sensors-and-location/sensors/gnss-spoof-jam)). La secuencia "jamming y luego spoofing" sugiere una regla para el modelo: un UAV que detectó jamming debería desconfiar del GNSS durante un tiempo después de recuperarlo.

## Geometría, clima y terreno pesan tanto como la potencia del jammer

### La geometría del enlace decide si un jammer realmente afecta

El radio nominal de un jammer no basta para saber si afecta a un dron. También influyen la distancia entre el dron y su operador, la línea de vista y la altitud.

Los operadores FPV se acercan al frente porque la relación entre la señal del jammer y la del operador (J/S) empeora cuando el dron está lejos de su control ([drone-warfare.com](https://drone-warfare.com/counter-uas/electronic-warfare/), fuente divulgativa). El horizonte radioeléctrico también limita: con fibra se logran unos 20 km y con radio unos 30 km, y los módulos de autoapuntado empiezan el ataque a 3 km del objetivo y 800 m de altitud, donde recuperan línea de vista ([Kyiv Independent](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)). Cerca del suelo, edificios y colinas degradan el enlace, y los operadores trabajan hasta unos 10 km ([War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)). Los drones de radio que provee el Estado a menudo no operan más allá de 5–8 km de la línea ([The War Zone](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)).

La altitud tiene un efecto doble. Volar alto mejora la línea de vista con el operador, pero expone al dron a jammers más lejanos. Con datos ADS-B, Figuet et al. mostraron que las aeronaves a baja altitud sufren menos la interferencia GNSS que las que vuelan alto ([Figuet et al., 2022](https://doi.org/10.3390/engproc2022028012)). Un modelo que calcule la relación J/S a partir de las distancias dron–jammer y dron–operador captura mejor esta física que un disco binario. Para el alcance del curso basta el disco, siempre que su radio se trate como intervalo y se haga análisis de sensibilidad.

### El clima se puede expresar como variables aplicadas al vuelo

El clima tiene efectos documentados y se puede convertir en variables concretas del vuelo. El DJI Mavic 3 solo es eficaz entre −10 °C y +40 °C y con viento inferior a unos 12 m/s; el frío agota antes la batería y el hielo en las hélices reduce la sustentación ([Universidad de Portsmouth](https://www.port.ac.uk/news-events-and-blogs/blogs/security-and-risk/russia-turns-to-an-old-ally-in-its-war-against-ukrainian-drones-the-weather)). El ala fija Shark tolera viento de hasta 20 m/s, pero la lluvia o la nieve pueden dejarla en tierra (misma fuente).

El mal tiempo también se explota de forma deliberada. En octubre de 2025, la niebla, la lluvia y las nubes dejaron a los drones pequeños de reconocimiento "poco confiables o sin poder volar", y Rusia sincronizó asaltos con el mal tiempo ([Universidad de Portsmouth](https://www.port.ac.uk/news-events-and-blogs/blogs/security-and-risk/russia-turns-to-an-old-ally-in-its-war-against-ukrainian-drones-the-weather)). A fines de noviembre de 2025, la nieve, la lluvia helada y la niebla degradaron el uso ucraniano de drones mientras Rusia ganaba terreno cerca de Járkov y Pokrovsk ([Forbes](https://www.forbes.com/sites/vikrammittal/2025/11/28/russia-makes-advances-as-winter-weather-grounds-many-ukrainian-drones/)). RUSI anota que la artillería podía defender el frente cuando los UAV no podían volar ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)).

Para que el clima deje de ser "genérico", como se le criticó al grupo, hay que expresarlo como variables del vuelo: el viento a la altura de vuelo, su componente a lo largo de cada tramo, la visibilidad, la temperatura (por su efecto en la batería) y la estación con o sin hojas en los árboles. El umbral de 12 m/s que ya usa el simulador coincide con el límite publicado del Mavic 3.

### El terreno de franjas forestales y la zona de trincheras se modelan sintéticamente

El paisaje del frente es estepa agrícola cuadriculada por **franjas forestales lineales** ("lesosmugi"). Estas franjas son el refugio principal de posiciones, logística y antenas. En los campos abiertos, en cambio, las tropas que salen de cobertura suelen ser detectadas en minutos ([Forbes](https://www.forbes.com/sites/davidkirichenko/2026/03/04/excavators-are-building-ukraines-drone-era-fortifications/)).

El centro estonio ICDS describe el cambio doctrinal hacia una defensa dispersa: posiciones de 3–8 personas, líneas separadas por 400–600 m, al menos 50 % de emplazamientos señuelo y una profundidad defensiva total de 25–40 km ([ICDS](https://icds.ee/en/russias-war-in-ukraine-fortification-for-drone-warfare/)). Un veterano relata cómo, en una misma franja forestal cerca de Pokrovsk, una trinchera conocida cayó en menos de 24 horas y una posición oculta resistió diez días ([War on the Rocks](https://warontherocks.com/the-strange-transformation-of-the-front-line-in-ukraine/)).

Sobre qué está mapeado, la situación es desigual. Las fortificaciones rusas fueron mapeadas por OSINT a partir de imágenes satelitales, con un mapa público actualizado al menos hasta agosto de 2024 ([Brady Africk](https://read.bradyafrick.com/p/russian-field-fortifications-in-ukraine)). ISW publica capas con **5.963 puntos y 12.169 polilíneas**, pero sin licencia clara ([ISW ArcGIS](https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/RUAF_Field_Fortifications_Polylines/FeatureServer/0?f=json)). La geometría ucraniana no es pública, de forma intencional, y la doctrina de 2025–2026, con posiciones dispersas y ocultas, se presta mucho menos a ser mapeada.

Hay además un rasgo nuevo del terreno con dato público: los **corredores con malla antidron** sobre caminos. El Ministerio de Defensa reporta 887 km en los oblasts del frente desde inicios de 2026, 207 km de ellos en Kherson ([Euromaidan Press](https://euromaidanpress.com/2026/06/22/drones-hunt-anything-that-moves-near-front-ukraines-drone-proof-network-now-grows-9-kilometers-daily/), contenido marcado como publicitario).

Para el modelo, la "zona de atrincheramiento" se representa mejor como una franja de 0–2 km desde la línea de contacto, con líneas sintéticas generadas a partir de los parámetros del ICDS. Las franjas forestales y la densidad urbana actúan como modificadores de la ocultación y de la línea de vista. Ninguna fuente abierta documenta que los emisores de jamming se ubiquen específicamente en las franjas forestales; la evidencia es indirecta (allí se esconden posiciones y antenas) y debe tratarse como supuesto.

### Las contramedidas cambian dónde rinde rutear alrededor del jamming

Las contramedidas modifican el valor de rutear alrededor del jamming según el tipo de dron. La fibra óptica elimina la vulnerabilidad de radio. Aun así, en mayo de 2025 era menos del 5 % de la flota de un batallón, y su probabilidad de acierto rondaba el 50 %, frente a un 30 % de probabilidad de llegar para los drones de radio ([The War Zone](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)). El guiado terminal autónomo, con módulos como el TFL-1, neutraliza el jamming en los últimos **400–500 m** ([The Defense Post](https://gecici.thedefensepost.com/?p=117258)). Las antenas CRPA y la navegación visual protegen a los drones de largo alcance frente al jamming GNSS.

El resultado es que el ruteo físico consciente del jamming rinde sobre todo con **UAV de radio en el tramo de crucero**. Por eso el modelo debe incluir como parámetro la fracción de drones "inmunes" y mostrar cómo cae el beneficio cuando esa fracción crece.

## La literatura respalda cada eslabón de la extensión, aunque nadie los ha unido

### CLUN-LSR ya trabaja con un área de interferencia

CLUN-LSR (Zheng, Zhu, Qin y Dong, *Ad Hoc Networks* 167, 2025) es un protocolo de estado de enlace (link-state). Toma de la capa de enlace el **estado del espectro en tiempo real** y usa el **número de vecinos a dos saltos** como métrica para elegir rutas. Con eso **evita los nodos que quedan dentro del área de interferencia** ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1570870524003135); [DOI](https://doi.org/10.1016/j.adhoc.2024.103702)).

No mueve físicamente a los UAV. Pero su bibliografía, de 39 referencias, ya incluye trabajos de localización de jammers por cambios de vecindad y de planificación de trayectorias anti-jamming ([Crossref](https://api.crossref.org/works/10.1016/j.adhoc.2024.103702)). En otras palabras, el puente hacia la capa física está en las propias fuentes del paper.

El mismo grupo de la Universidad de Aeronáutica y Astronáutica de Nanjing (NUAA) publicó en 2026 una continuación sobre ruteo con "colaboración de vecindario" frente a jamming periódico ([Zhang et al., 2026](https://doi.org/10.1109/MCOM.001.2600062)). Esa dirección coincide con la del proyecto: ellos la aplican a paquetes, y el proyecto la aplicaría a trayectorias.

### Detectar y localizar el jamming tiene métodos maduros

La detección tiene cifras de laboratorio robustas, aunque ninguna validada en el frente:

| Trabajo | Método | Resultado |
|---|---|---|
| Li et al. (2022) | Red convolucional sobre espectrogramas | 99,79 % de exactitud y 0,03 % de falsa alarma ([Michigan Tech](https://digitalcommons.mtu.edu/michigantech-p/15739)) |
| Li et al. (2022) | Modelo de características | 92,20 % y 1,35 % (misma fuente) |
| Viana et al. (2022) | Detección por RSSI y SINR | Detecta un ataque **100 ms** después de su inicio ([arXiv 2207.10810](https://arxiv.org/abs/2207.10810)) |
| Detección colaborativa de GNSS | Datos de muchos receptores | Unos 10 s de tiempo medio y 1–2 % de falsos positivos ([Sciforum](https://sciforum.net/paper/view/25272)) |

Viana et al. advierten que la tasa de entrega de paquetes (PDR) solo delata el ataque después de una pérdida considerable de información.

Para pasar de la detección a una zona en el mapa existe una cadena de trabajos. Liu et al. (2012) localizan el jammer por mínimos cuadrados **solo a partir de los cambios en la lista de vecinos** de cada nodo ([DOI](https://doi.org/10.1109/TPDS.2011.154)); CLUN-LSR cita este trabajo, y sus tablas de estado de enlace ya contienen esa información. Duan et al. (2018) proponen el marco casi exacto que el proyecto necesita: detectar con la intensidad de señal (RSS) y la tasa de error de paquetes, localizar posición y potencia del jammer con RSS, y planificar de forma robusta para el peor caso dentro de la incertidumbre de localización ([DOI](https://doi.org/10.1109/ROBIO.2018.8665238)). El método de Liu, Lo, Blanch, Chen y Walter (2025) es el primero de esta línea que entrega **cotas de error y mapas de calor de probabilidad** de la posición del interferente ([DOI](https://doi.org/10.33012/navi.716)). Y Ahmed et al. (2021) localizan el jammer con una red de UAV cooperantes, con el fin explícito de que el sistema "maniobre lejos de la región afectada" ([DOI](https://doi.org/10.1109/AERO50100.2021.9438441)).

### Replanificar y medir la resiliencia ya tiene referencias en grafos

La replanificación y la resiliencia tienen referencias canónicas que encajan con el código del grupo. Para derivar costos de un mapa de interferencia, Dong et al. (2022) construyen mapas de potencia y de SINR a partir de topografía real y aplican A* para minimizar la distancia sujeta a calidad de enlace ([DOI](https://doi.org/10.1109/LSP.2022.3149374)). Kim y Hespanha (2003) justifican discretizar el espacio en un grafo con costo de riesgo ([DOI](https://doi.org/10.1109/CDC.2003.1272863)). Para la replanificación incremental, D* Lite repara el camino más corto cuando cambian los costos de las aristas, sin volver a calcular desde cero ([Koenig y Likhachev, 2005](https://doi.org/10.1109/TRO.2004.838026)). Luna et al. (2024) validan con vuelos reales un sistema multi-UAV que replanifica en vuelo ([DOI](https://doi.org/10.1002/rob.22342)). Sobre qué compartir, Zheng, Liu y Zhang (2016) demuestran que **compartir más información de amenazas no siempre mejora la planificación**, y proponen estrategias adaptativas para decidir qué compartir y con quién ([DOI](https://doi.org/10.1016/j.knosys.2016.09.021)).

Para el par resiliente que el grupo ya implementa, la referencia es Suurballe (1974) ([DOI](https://doi.org/10.1002/net.3230040204)). Su versión geográfica es GeoDivRP, que elige k caminos cuyos nodos están separados por más de una distancia d, con k = 3 ([ResiliNets](https://resilinets.org/geodivrp_geodiverse_multipath_routing_protocol.html); [Cheng et al., 2015](https://doi.org/10.1002/net.21660)). Si cada arista tiene una probabilidad de falla p, usar como costo −ln(1−p) hace que la suma de costos equivalga al producto de las probabilidades de supervivencia ([arXiv 2511.18236](https://arxiv.org/pdf/2511.18236)); así, Dijkstra y Yen maximizan directamente la supervivencia del camino.

Falta el vocabulario y la definición de misión. El marco ResiliNets organiza la resiliencia en defender, detectar, remediar y recuperar, más diagnosticar y refinar ([Sterbenz et al., 2010](https://doi.org/10.1016/j.comnet.2010.03.005)). En el proyecto, detectar sería CLUN-LSR, remediar sería replanificar y recuperar sería completar la misión. La misión de reconocimiento, por su parte, se formaliza como un problema de orienteering de equipo con restricción de supervivencia ([Jorgensen et al., 2018](https://doi.org/10.1007/s10514-017-9694-1)).

### Los huecos de la literatura son la contribución del proyecto

Hasta donde llegó la búsqueda, nadie ha unido estas piezas. Ningún trabajo usa la salida de un protocolo de ruteo (tablas de estado de enlace) para localizar jammers y replanificar trayectorias físicas. Ninguno trata el silencio de radio de un UAV como sensor de jamming para los que vienen detrás. Ninguno aplica GeoDivRP o Suurballe a trayectorias físicas de UAV frente a jamming. Y ningún planificador de UAV publicado usa datos reales de Ucrania (ACLED, GPSJam o líneas del frente). Ese hueco es la contribución que el grupo puede reclamar con honestidad: integrar piezas ya validadas por separado, no inventar un algoritmo nuevo.

## El reconocimiento con alerta encaja con CLUN-LSR; el señuelo exige modelar al adversario

### La idea (a) tiene precedente operativo directo, aunque incompleto

La idea (a) tiene precedentes públicos directos. RUSI describe que los Geran-2 y Gerbera rusos se lanzan en oleadas, "con datos devueltos por los primeros UAV para informar la ruta tomada por los siguientes", y agrega que rastrear las defensas EW "es un requisito absoluto" porque determina el plan de vuelo ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). Tras perder Starlink, Rusia pasó a redes mesh. Según un experto de la industria ucraniana, sus algoritmos ya permiten que unos drones redirijan a otros por rutas más seguras alrededor de zonas de EW o de defensa aérea, sobre todo en lanzamientos masivos ([Ukraine's Arms Monitor](https://ukrainesarmsmonitor.substack.com/p/drone-warfare-in-ukraine-ew-depth); [ASPI](https://www.aspistrategist.org.au/the-autonomous-arms-race-in-the-russia-ukraine-war/)). El viceprimer ministro Fedorov afirmó, por su parte, que los drones cambian altitud, rutas y patrones según dónde se usan los equipos de EW ([Ukrinform](https://www.ukrinform.net/rubric-defense/3924457-ukraine-actively-developing-antidrone-tech-vice-pm.html)).

El límite también debe declararse. No hay reportes verificados de drones tácticos pequeños que compartan entre sí mapas de interferencia de forma autónoma, y los detectores de EW documentados son portátiles y de tierra, no van a bordo. El aviso en vuelo es, por lo tanto, un supuesto del modelo que se apoya en la literatura y en la práctica de los drones de largo alcance.

### La idea (b) tiene más evidencia de uso, pero ninguna de efecto

La idea (b) está aún mejor documentada en cuanto a uso. Según la inteligencia militar ucraniana, cerca de la mitad de los drones lanzados por Rusia a fines de 2024 eran señuelos ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2024/11/11/7483868/)). En el primer semestre de 2026, entre 34 % y 37 % de los lanzamientos no eran Shahed/Geran, aunque esa categoría mezcla señuelos puros con Gerbera armados ([ISIS](https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine)). El valor del Gerbera, de unos USD 10.000, está en obligar a la defensa a elegir entre blancos ([Forbes](https://www.forbes.com/sites/vikrammittal/2024/11/25/the-latest-threat-to-ukrainian-air-defenses-the-russian-gerbera-drone/)). Ucrania, a su vez, produce "miles" de señuelos para que sus drones de largo alcance crucen la defensa más densa cerca del frente ([CEPA](https://cepa.org/article/the-phony-war-ukraine-and-russias-decoy-drones/)).

Pero **no hay ninguna medición independiente del efecto marginal de los señuelos** sobre la tasa de intercepción de los drones reales. La literatura académica tampoco ayuda mucho, porque trata casi siempre otro problema: trazas fantasma ante redes de radar ([Purvis et al., 2006](https://doi.org/10.2514/1.15563)), enjambres de señuelos frente a misiles ([Bildik et al., 2024](https://doi.org/10.1109/ICUAS60882.2024.10556889)), caminos que ocultan el destino ([Masters y Sardina, 2017](https://doi.org/10.24963/ijcai.2017/610)) o juegos con un observador que se adapta ([Mareschal de Charentenay, 2026](https://www.imt-atlantique.fr/en/events/stanislas-mareschal-de-charentenay-thesis-defence?page=1); [Sanjab et al., 2017](https://doi.org/10.1109/ICC.2017.7996862)). No se encontró ningún trabajo revisado por pares sobre UAV señuelo que atraigan jamming en el ruteo de comunicaciones.

### Comparación de las dos ideas

| Criterio | (a) Reconocimiento con alerta y cambio de ruta | (b) Ataque con flota señuelo previa |
|---|---|---|
| Relación con CLUN-LSR | Directa: se reutilizan la detección de denegación de espectro y el aviso a vecinos; solo cambia qué se hace con el aviso | Indirecta: CLUN-LSR no modela un adversario que reacciona ni la asignación de defensas |
| Sugerencia del profesor (fallas comunicadas por un UAV predecesor) | Coincide literalmente | Parcial: la flota real aprovecha lo que revela el señuelo, pero el foco está en provocar la reacción |
| Evidencia pública | Oleadas que informan rutas (RUSI); redes mesh que redirigen drones (2026). Falta evidencia en drones tácticos pequeños | Abundante sobre uso y proporciones. Ninguna sobre efecto medido |
| Literatura | Cadena completa detección → localización → replanificación → par geodiverso | Radar y misiles, engaño, juegos. Nada sobre señuelos que atraigan jamming |
| Modelo de simulación | Amenazas estáticas o semiestáticas que se revelan, con actualización de costos. Compatible con el simulador actual | Requiere un adversario adaptativo con recursos finitos y reglas de reacción inventadas. Es un juego, no un camino mínimo |
| Calibración | Radios, bandas, latencias y probabilidades con fuente | Ningún dato público del efecto; la respuesta enemiga sería supuesta |
| Métricas | `R_mision`, `R_par`, supervivencia del camino, latencia del aviso, ΔR frente a replanificación local | Supervivencia de la flota real frente al costo de la flota señuelo, dependiente del modelo del adversario |
| Riesgo ético | Bajo: dron genérico de observación en un entorno degradado | Alto: optimizar la saturación de defensas se acerca a guía táctica de ataque |
| Veredicto | **Recomendada como eje de la Tarea 2** | Trabajo relacionado o futuro, solo a nivel descriptivo |

### La alerta compartida corrige la debilidad de los resultados actuales

La recomendación por la idea (a) se apoya, además, en los resultados preliminares del propio grupo (PROPUESTA_TECNICA §9 del repositorio). La propuesta C supera a Dijkstra (A) en hasta **+22 pp** de misiones completadas, pero **no supera a la ablación D**, el Dijkstra que replanifica, porque ambas solo se enteran de una falla al llegar a ella; y la selección resiliente cuesta un 6–7 % de km fijos sin ganar información a cambio. La alerta propagada desde un UAV que va delante es precisamente el ingrediente que falta: información que llega **antes** de alcanzar la zona. Sin esa información, ninguna estrategia que decida con anticipación puede superar a una que replanifica en el momento.

La idea (b) se puede rescatar a nivel abstracto, sin ningún encuadre de ataque. RUSI anota que buena parte del valor de las oleadas está en los datos que obtienen al mapear la EW y la defensa aérea ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)). En la simulación, eso equivale a preguntarse **cuánto vale la información que obtiene un UAV que va delante**. Esa pregunta ya está contenida en (a), midiendo el compromiso entre la exposición del primer UAV y el éxito de los siguientes, y no hace falta modelar ni optimizar señuelos.

## Cómo actualizar la propuesta sin cambiarla completamente

### Qué se conserva de CLUN-LSR

Se conservan tres elementos: la detección de denegación de espectro en la capa de enlace como disparador; la noción de "área de interferencia", con los cambios en los vecinos a dos saltos como evidencia de esa área; y la difusión de estado de enlace como mecanismo de aviso entre UAV.

El grupo ya decidió no presentar la solución como una implementación de CLUN-LSR, y esta actualización no contradice esa decisión. La formulación correcta es que CLUN-LSR se **abstrae como el módulo de detección y aviso** de un sistema cuyo objeto de optimización es la trayectoria física. No se reimplementa el protocolo ni se miden sus métricas de paquetes, aunque la PDR y el throughput pueden reportarse como métricas secundarias opcionales. El borrador de justificación queda así:

> *Siguiendo el marco detección–localización–evasión de Duan et al. (2018) y la estrategia de defender, detectar, remediar y recuperar de Sterbenz et al. (2010), extendemos la detección de denegación de espectro de CLUN-LSR (Zheng et al., 2025) para que el aviso se traduzca en zonas de evitación con incertidumbre (Liu et al., 2012; Liu et al., 2025). Esas zonas actualizan los costos del grafo de vuelo y disparan, en los UAV que aún no entran en ellas, una replanificación (Koenig y Likhachev, 2005) o la conmutación a un camino geodiverso (Suurballe, 1974; Cheng et al., 2015).*

### Qué se agrega para pasar de paquetes a trayectorias

| Pieza nueva | Descripción | Fundamento |
|---|---|---|
| Flota de N UAV | 3–5 UAV con salidas escalonadas sobre la misma misión o sobre puntos de observación repartidos | Oleadas que informan rutas ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)); replanificación multi-UAV ([Luna et al.](https://doi.org/10.1002/rob.22342)) |
| Jammers sintéticos con huella espectral | Cada jammer tiene un nivel (radio), un subconjunto de grupos de bandas y una probabilidad de neutralización. Cada UAV tiene una banda de control y una de video, y solo le afecta un jammer que cubra alguna de ellas | Catálogo de bandas y tabla de niveles de este informe |
| Aviso con costo y retardo | El primer UAV que entra en la zona detecta con latencia `T_detect` y una exactitud dada, y difunde el aviso con una probabilidad que disminuye mientras más adentro de la zona esté, porque el primero en detectar suele ser el primero en perder el enlace | [Viana et al.](https://arxiv.org/abs/2207.10810); [Li et al.](https://digitalcommons.mtu.edu/michigantech-p/15739) |
| Silencio como evidencia | Si un UAV deja de reportar durante más de `T_silencio`, se marca un disco con mayor incertidumbre alrededor de su última posición conocida | Lógica de cambios de vecindad de [Liu et al., 2012](https://doi.org/10.1109/TPDS.2011.154) |
| Del aviso a la zona de evitación | Disco de radio `r_J + k·σ` (k = 2–3) alrededor del centro estimado. Las aristas que caen dentro se penalizan, o se eliminan si la probabilidad de afectación supera un umbral | [Duan et al.](https://doi.org/10.1109/ROBIO.2018.8665238); [Liu et al., 2025](https://doi.org/10.33012/navi.716) |
| Nuevas estrategias en el simulador | `D_A` (Dijkstra que replanifica con avisos compartidos) y `C_A` (propuesta C con avisos compartidos), para separar el valor del aviso del valor de la selección. También, avisar a todos frente a avisar solo a los UAV cuya ruta futura cruza la zona | [Zheng, Liu y Zhang, 2016](https://doi.org/10.1016/j.knosys.2016.09.021) |

### Mapeo a los criterios de la rúbrica

| Criterio (numeración de PROPUESTA_TECNICA) | Qué se conserva | Qué se agrega o cambia |
|---|---|---|
| Infraestructura JSON y BD (1; PostGIS/pgRouting) | Generador del grafo y esquema previsto | AOI ampliada al corredor Mykolaiv–Kherson; atributos por arista `d_front`, `banda_front`, `ocult`, `vis_front`, `w_par`, `p_gnss`, `p_kin`, `p_evt` |
| Metadata, n = 3 | Estructura ETL → JSON → cargador | M1 zonificación del frente (DeepState); M2 ocultación y visibilidad desde la línea (WorldCover + CHM + GLO-30); M3 viento a 80–120 m (Open-Meteo). Detalle en la sección de fuentes |
| Amenazas, n = 3 | Pipeline de fallas en tres niveles (registro → foco → falla con semilla) | T1 denegación GNSS (GPSJam + imputación en el frente); T2 incendios de guerra (The Economist/FIRMS); T3 ataques aéreos y de drones (ACLED, con UCDP, alertas o Bellingcat como respaldo) |
| Fallas (5.1) | Discos con radio, aparición diferida y descubrimiento local | Mezcla de niveles 1–3 de jammers, huella de bandas, descubrimiento por aviso compartido y por silencio |
| Pesos (5.2) | `c(e) = largo · f_viento · (1 + w_R·riesgo) · π(e)` | `p_e = 1 − ∏(1 − p_i)` y costo `L/v(viento) + κ·(−ln(1 − p_e))`, más un término `p_jam(t)` que solo se conoce tras un aviso |
| Preferencias (6.1/6.2) | Altura, zonas restringidas, viento máximo de 12 m/s, α, β | Fracción de UAV inmunes; tolerancia a cruzar la franja de 0–2 km; ventana de desconfianza del GNSS tras detectar jamming |
| Línea base (8) y k ≥ 2 rutas (9) | Dijkstra por km con `pgr_dijkstra`; segunda ruta excluyendo aristas | Sin cambios: la línea base sigue sin información de amenazas |
| Algoritmo publicado (7.1/7.2) | Yen (`pgr_KSP`) + selección del par | Citar Duan et al. (2018) como marco; D* Lite como replanificador incremental o Dijkstra recalculado; GeoDivRP para justificar la separación d |
| Métricas (10, 11.2) | `R_mision`, `R_par`, ΔR con McNemar, km extra | `ΔR(C_A − D)` y `ΔR(D_A − D)` como valor del aviso; supervivencia del camino ∏(1 − p_e); latencia entre detección y replanificación; fracción de puntos visitados antes de perder un UAV |
| Leaflet | Rutas por método y fallas | Capas de franjas de distancia al frente, jammers sintéticos con su disco `r_J + kσ`, cronología de avisos y rutas antes y después del aviso |

### Parámetros de simulación con respaldo público

Los valores que siguen son rangos para el análisis de sensibilidad, no constantes. Su confiabilidad se indica con los criterios de las notas de investigación.

| Parámetro | Valor o rango sugerido | Fundamento | Confiabilidad |
|---|---|---|---|
| Profundidad de la kill zone por lado | Escenarios 10 / 20 / 30 km; referencia 25 km | Brovdi, 25 km o más según densidad de ataques ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2026/05/14/8034645/)); ~20 km y hasta 50 km ([Business Insider vía Yahoo](https://www.yahoo.com/news/world/articles/front-line-drone-kill-zone-110501096.html)); 35–40 km ([ICDS](https://icds.ee/en/russias-war-in-ukraine-fortification-for-drone-warfare/)) | Oficial y analista; mide densidad, no alcance máximo |
| Franjas de distancia a la línea | 0–2 / 2–15 / 15–30 / >30 km | Transparencia en 3 km, decreciente hasta 15 km y asignable hasta 40 km ([RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf)) | Analista; la discretización es inferencia |
| Jammer nivel 1 | r = 0,2–0,8 km, omnidireccional | ANTIFPV, Kvertus, Volnorez (tabla de niveles) | Fabricante y secundaria |
| Jammer nivel 2 | r = 1–3 km, sector de 90–120° o 360° | Veres-2, Stupor, Kupol-PRO (tabla de niveles) | Testimonio y fabricante |
| Sistema EW mayor | r = 10–25 km; uno cada ~10 km; 3–5 km detrás de la línea | [RUSI 2023](https://rusi.org/explore-our-research/publications/special-resources/meatgrinder-russian-tactics-second-year-its-invasion-ukraine); [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/) | Analista y secundaria |
| Denegación GNSS regional | Capa de navegación degradada en toda la franja < 30 km; no se rodea | "Ubicua" según [RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf); radio de ~250 km en Kaliningrado ([Lo et al.](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)) | Analista y medición independiente fuera de Ucrania |
| Probabilidad de neutralización en la zona | 0,6–0,7 | Fusiles Kvertus ([LIIA](https://liia.lv/en/publications/the-drone-revolution-lessons-from-ukraine-1476?get_file=1)) | Analista |
| Fracaso por EW enemiga (calibración global) | ~31 % de las salidas fallidas; no llegada total del 60–80 % | [War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/); [RUSI](https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf) | Testimonio de primera mano y analista |
| Grupos de bandas de control | {400–490 MHz; 720–1020 MHz; 1,2–1,3 GHz; 2,1–2,5 GHz}, mezcla de referencia 20/30/50 % | [Armada International](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/); [Ukrainska Pravda](https://www.pravda.com.ua/eng/articles/2025/08/08/7525279/) | Secundaria y testimonio |
| Grupos de bandas de video | {1,2–1,3; 3,3; 5,1–5,9; 6–7,2 GHz} | [Rubryka](https://rubryka.com/en/2024/06/13/retranslyator-vidlunnya-dlya-droniv/); [Militarnyi](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/) | Fabricante y hecho documentado |
| Huella de un jammer táctico | 1160–1280, 1560–1630, 2400–2500, 5160–5280 y 5725–5850 MHz | Veres-2 ([Euromaidan Press](https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/)) | Testimonio y fabricante |
| Latencia de detección `T_detect` | 0,1–10 s | [Viana et al.](https://arxiv.org/abs/2207.10810); [Sciforum](https://sciforum.net/paper/view/25272) | Académica (simulación) |
| Exactitud y falsa alarma del detector | 85–99,8 % y 0,03–2 % | [Li et al.](https://digitalcommons.mtu.edu/michigantech-p/15739); [Viana et al.](https://arxiv.org/abs/2203.11373v1) | Académica (laboratorio) |
| Margen de incertidumbre de la zona | `r_J + k·σ`, k = 2–3 | [Duan et al.](https://doi.org/10.1109/ROBIO.2018.8665238); [Liu et al., 2025](https://doi.org/10.33012/navi.716) | Académica; la fórmula es inferencia |
| Separación del par geodiverso | `d > 2·(r_J + k·σ)`; k = 3 caminos candidatos | [GeoDivRP](https://resilinets.org/geodivrp_geodiverse_multipath_routing_protocol.html); [Cheng et al.](https://doi.org/10.1002/net.21660) | Académica más inferencia |
| Fracción de UAV inmunes (fibra o autonomía) | Barrido de 0–50 %; referencia < 5 % (mayo de 2025) | [The War Zone](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war) | Testimonio |
| Límites de la plataforma | Multirrotor: −10 a +40 °C, viento < 12 m/s. Ala fija: ~2 h, 60 km de enlace, viento ≤ 20 m/s | [Portsmouth](https://www.port.ac.uk/news-events-and-blogs/blogs/security-and-risk/russia-turns-to-an-old-ally-in-its-war-against-ukrainian-drones-the-weather); [Ukrainian News](https://ukranews.com/en/news/890883-ew-resistant-drone-that-can-adjust-himars-presented-in-ukraine-in-conditions-of-war) | Analista y fabricante |
| Alcance del enlace por radio | Hasta ~10 km del operador a baja altura | [War on the Rocks](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/); [The War Zone](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war) | Testimonio |
| Patrón de spoofing (zona de engaño) | Círculos de 2–11 km de diámetro | [Lo et al.](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf) | Medición independiente (Rusia, no el frente) |

Estos valores tienen dos consecuencias directas para `ruteo/config.py`. La primera es que el simulador actual solo representa jammers de nivel 1: los radios de falla de 0,25–0,60 km corresponden a ese nivel, y tanto la separación `d_separacion_km = 0,4` como el radio `ρ = 0,6 km` deberían derivarse de `r_J + k·σ`, no fijarse por separado. La segunda es que el AOI no alcanza para los niveles 2–3 ni para la kill zone. Representarlos exige una malla de varias decenas de kilómetros de profundidad, que sería manejable en pgRouting con resolución variable: 0,5 km en la franja de 0–15 km y 1–2 km más atrás.

### Hipótesis refutable y diseño experimental

La hipótesis principal actualizada es esta: con avisos difundidos desde el primer UAV que detecta, la tasa de misiones completadas de los UAV que vienen detrás con replanificación anticipada (`D_A` o `C_A`) supera a la de Dijkstra con descubrimiento solo local (D), con p < 0,05 (McNemar), y esa ventaja decrece tanto con `T_detect` como con la fracción de UAV inmunes. Se rechaza si no hay diferencia significativa, o si la ventaja no responde a esas dos variables.

La hipótesis secundaria, `C_A > D_A`, mide si la selección resiliente aporta algo por encima del aviso. Puede no cumplirse. Si no se cumple, el aporte defendible es el mecanismo de aviso derivado de CLUN-LSR, y debe informarse así.

## Seis fuentes abiertas alimentan el grafo, pero el mapa de jamming del frente no existe

### Qué se puede descargar y con qué restricciones

Para la zonificación del frente, la única fuente de control territorial diaria, descargable en GeoJSON y sin credenciales es DeepStateMap. Su API no documentada tiene snapshots desde el 3 de abril de 2022 ([DeepState API](https://deepstatemap.live/api/history/public)). Hay además dos derivados útiles: un espejo comunitario en GitHub con la capa "ocupado" ya disuelta, actualizado a diario desde julio de 2024 ([cyterat](https://github.com/cyterat/deepstate-map-data)), y un repositorio que publica la **línea de contacto** derivada de DeepState ([longlinecode](https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md)). El último snapshot de DeepState incluye también puntos de "dirección de ataque" y ubicaciones de unidades militares, que hay que descartar para quedarse solo con los polígonos ([DeepState API](https://deepstatemap.live/api/history/last)). Las capas de ISW se pueden consultar técnicamente, pero su licencia prohíbe usarlas sin consentimiento escrito ([ArcGIS ISW](https://www.arcgis.com/sharing/rest/search?q=owner:gbarros_understandingwar%20AND%20(title:VIEW_RussiaCoTinUkraine_V2%20OR%20title:AssessedRussianAdvanceInUkraine_V2)&f=json)).

Para la interferencia GNSS, GPSJam publica CSV diarios en celdas H3 de resolución 4, de unos **1.770 km²** cada una, desde febrero de 2022 ([GPSJam FAQ](https://gpsjam.org/faq)). Pero sobre el frente oriental **casi no tiene datos**: el 17 de octubre de 2026 había una sola celda con datos en el recuadro del frente, y ninguna roja ([GPSJam CSV](https://gpsjam.org/data/2026-10-17-h3_4.csv)). La razón es que allí no vuelan aviones civiles con ADS-B, y el propio GPSJam advierte que una celda vacía significa ausencia de tráfico, "como en zonas de guerra activas".

Para el combate cinético, el modelo de incendios de guerra de The Economist clasifica los focos de NASA FIRMS en celdas de 0,1°, con licencia CC BY 4.0, y se actualizó el mismo 18 de octubre de 2026 ([The Economist](https://github.com/TheEconomist/the-economist-war-fire-model)).

Para los eventos de ataque, ACLED tiene la mejor tipología, con los subtipos "Air/drone strike" y "Shelling". Su API, sin embargo, exige el nivel Research, y la licencia prohíbe redistribuir los datos y exige que los productos derivados sean transformativos ([ACLED EULA](https://acleddata.com/eula); [myACLED FAQ](https://acleddata.com/myacled-faqs)). Hay tres respaldos sin credenciales: UCDP GED vía HDX, hasta diciembre de 2024 ([HDX UCDP](https://data.humdata.org/api/3/action/package_show?id=ucdp-data-for-ukraine)); el dataset de alertas antiaéreas de Vadimkin, con licencia MIT y nivel de distrito (raion) desde diciembre de 2025 ([Vadimkin](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md)); y el JSON de Bellingcat, con 2.517 incidentes hasta julio de 2025 ([Bellingcat](https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json)).

Para el terreno y el clima, ESA WorldCover, la altura de dosel de Meta/WRI y el modelo de superficie Copernicus GLO-30 se descargan sin credenciales ([WorldCover](https://esa-worldcover.org/en/data-access); [Meta CHM](https://registry.opendata.aws/dataforgood-fb-forests/); [Copernicus DEM](https://registry.opendata.aws/copernicus-dem/)). Open-Meteo entrega el viento a 80 y 120 m bajo CC BY 4.0, para uso no comercial ([Open-Meteo](https://open-meteo.com/en/terms)).

Estos datos de relieve, cobertura y clima responden a la crítica de "metadata genérica" cuando la métrica se define respecto de la amenaza. En vez de la altura de un edificio, se usa la **fracción de cada tramo visible desde la línea de contacto**. En vez del "clima", se usa el **viento a la altura de vuelo proyectado sobre la arista**.

Las frecuencias de jamming que el encargo menciona como insumo para la detección temprana no existen como dataset. Existen como **catálogo de bandas** compilado de fuentes abiertas, el que ya resumen las tablas anteriores, y su uso correcto es como atributo de los jammers y los UAV sintéticos.

### Tabla de metadata y amenazas recomendadas

| Rol | Fuente | Acceso | Licencia | Atributo por arista o entidad | Advertencia |
|---|---|---|---|---|---|
| **M1** metadata | DeepStateMap: API, espejo cyterat y línea de longlinecode | Sin credenciales; GeoJSON diario | Sin licencia explícita (espejo GPL-3.0); atribuir © DeepStateMap.Live | `zona` ∈ {ocupado, gris, UA}; `d_front` (distancia del punto medio a la línea); `banda_front`; `r_front = exp(−d/λ)` | Solo polígonos; descartar puntos de unidades y direcciones de ataque; usar un snapshot histórico fijo |
| **M2** metadata | ESA WorldCover 10 m + CHM Meta/WRI + Copernicus GLO-30 | S3 sin firma | CC BY 4.0 / CC BY 4.0 / licencia Copernicus | `ocult`: % de cobertura arbórea en un buffer de 50–100 m; `h_dosel`; `vis_front`: fracción visible desde la línea (viewshed sobre el modelo de superficie) | No hay dataset de franjas forestales; el GLO-30 es un modelo de superficie que incluye vegetación y edificios |
| **M3** metadata | Open-Meteo (archivo e historical-forecast) | Sin clave; < 10.000 llamadas/día | CC BY 4.0, no comercial | `w_par = V·cos(θ_viento − θ_arista)` a 80–120 m; tiempo `L/(v + w_par)`; ráfagas; visibilidad; nubes bajas | Resolución gruesa (ERA5); declarar el viento uniforme por celda |
| Metadata de amenaza (catálogo) | Bandas de drones y jammers compiladas de fuentes abiertas | No es un dataset: compilación citada | Citas | `banda_ctrl`, `banda_video` por UAV; `bandas` por jammer; afectación solo si hay solapamiento | Instantáneas de 2024–2026; la mezcla cambia en semanas o meses |
| **T1** amenaza | GPSJam | CSV diario sin credenciales | Sin licencia explícita | `p_gnss`: fracción de días rojos en 30 días, o `pct_bad` medio de las celdas que toca la arista | Casi sin datos sobre el frente: imputar por franja de distancia; mide aeronaves en altura, no drones a 50–150 m |
| **T2** amenaza | Modelo de incendios de guerra de The Economist (sobre FIRMS) | CSV en GitHub; FIRMS por país sin clave | CC BY 4.0 (datos), MIT (código) | `fires_30d` en un buffer de 2–5 km → `p_kin` | Nubes y eventos sin calor quedan fuera; clasificación probabilística |
| **T3** amenaza | ACLED ("Air/drone strike", "Shelling") | myACLED; API solo desde el nivel Research | Licencia no comercial y sin redistribución | Densidad de eventos en 30 días → `p_evt` | Publicar solo la grilla transformada; respaldos: UCDP (CC BY-IGO, hasta 2024-12), alertas de Vadimkin (MIT) y Bellingcat |
| Respaldo temporal | Kaggle "Massive Missile Attacks on Ukraine" | Cuenta de Kaggle | CC BY-NC-SA 4.0 | Serie `not_reach_goal / launched` como intensidad nacional de EW | No espacial; la Fuerza Aérea dejó de reportar algunos tipos de misiles desde el 10 de agosto de 2026 ([Kaggle](https://www.kaggle.com/api/v1/datasets/view/piterfm/massive-missile-attacks-on-ukraine)) |
| **NO EXISTE** | Mapa abierto de jamming o EW de enlaces en el frente | — | — | Jammers sintéticos de niveles 1–3: 3–5 km detrás de la línea, ~10 km entre sistemas mayores, con preferencia por cobertura arbórea o urbana, bandas por mezcla; se revelan solo al detectarlos | Debe declararse como supuesto de escenario, con barrido de sensibilidad |
| **NO EXISTE** | Interferencia GNSS a nivel del suelo en Ucrania | — | — | `p_gnss` imputada por franja de distancia (alta o muy alta en < 30 km) | ADS-B y suelo no se correlacionan ni siquiera en el Báltico ([Safety4Sea](https://safety4sea.com/study-shows-gnss-interference-in-the-baltic-sea)) |
| **NO EXISTE** | Ocupación del espectro o mediciones de RF en Ucrania | — | — | Usar el catálogo de bandas | Esperable por razones de seguridad |
| **NO EXISTE (y no debe usarse)** | Posiciones reales de defensa aérea, EW o trincheras de 2025–2026 | — | — | Franja de "atrincheramiento" de 0–2 km con líneas sintéticas a 400–600 m ([ICDS](https://icds.ee/en/russias-war-in-ukraine-fortification-for-drone-warfare/)) | No reproducir geometrías reales |
| **NO EXISTE** | Dataset de franjas forestales de Ucrania | — | — | Derivar de WorldCover o CHM, u OSM `natural=tree_row` | OSM con ODbL obliga a compartir la base derivada |
| **NO EXISTE** | Corredores de Shahed por oblast | — | — | Solo pertinente si la zona es Mykolaiv ciudad; sintético | Las series diarias son nacionales |
| **NO EXISTE** | Desglose de pérdidas de drones por causa | — | — | Probabilidades con barrido (tabla de parámetros) | Solo hay testimonios y estimaciones |

### Cómo se combinan las capas en el costo

La combinación sugerida para pgRouting es:

```
p_e = 1 − (1 − p_gnss)(1 − p_kin)(1 − p_evt)(1 − p_jam(t))
costo_e = L_e / v_e(viento) + κ · (−ln(1 − p_e))
```

`p_jam(t)` vale cero hasta que llega un aviso, y κ y la imputación de EW en el frente son parámetros de escenario. Para que el experimento sea reproducible y no dependa de datos en tiempo real, conviene fijar un día de corte histórico (por ejemplo, una fecha de 2025) con ventanas de 30 días para T1–T3.

## Zona de estudio: del centro de Mykolaiv al corredor que termina en el Dnipro

La ciudad de Mykolaiv no representa el problema de reconocimiento bajo EW. El oblast queda a "menos de 70 km" del frente ([Kyiv Independent](https://kyivindependent.com/we-cannot-wait-for-peace-reluctant-at-first-denmark-takes-on-rebuilding-mykolaiv-oblast/)); la cifra de 50–70 km para la ciudad es una estimación geográfica, no un dato oficial, pero en cualquier caso la deja fuera de la kill zone de 25 km. Su amenaza dominante es de largo alcance: Shahed y misiles Iskander-M contra el puerto y la energía ([Kyiv Post](https://www.kyivpost.com/post/86866); [ISIS](https://isis-online.org/isis-reports/a-comprehensive-analytical-review-of-russian-shahed-type-uavs-deployment-against-ukraine-in-2025)). La costa sur del oblast, en cambio, sí sufre FPV, que cruzan un estuario de 10–15 km desde Kinburn ([Kyiv Post](https://www.kyivpost.com/post/68805)).

La ribera derecha del Dnipro en Kherson es el mejor compromiso. La línea de contacto es un río, estable desde noviembre de 2022. La Comisión de la ONU documentó ataques sistemáticos con drones en un tramo de más de 100 km desde julio de 2024 ([AP vía Yahoo](https://www.yahoo.com/news/un-commission-says-russian-drone-225500743.html)), y luego extendió la franja a **más de 300 km**, incluido el oblast de Mykolaiv ([ONU Ucrania](https://ukraine.un.org/en/304119-russian-authorities-committed-crimes-against-humanity-targeting-civilian-population-through)). Human Rights Watch documentó los mismos ataques de forma independiente ([HRW](https://www.hrw.org/report/2025/06/03/hunted-from-above/russias-use-of-drones-to-attack-civilians-in-kherson-ukraine)), y la ruta Kherson–Mykolaiv tiene corredores con malla antidron documentados ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2025/09/09/7530061/)).

| Opción | Distancia a la línea | Amenaza dominante | Estabilidad del frente | Representatividad para (a) | Recomendación |
|---|---|---|---|---|---|
| Mykolaiv ciudad (AOI actual) | ~50–70 km (estimación) | Largo alcance | No aplica (retaguardia) | Baja | Solo como base de retaguardia |
| **Corredor Mykolaiv–Kherson hasta la ribera derecha** | De 0 km (río) a >50 km | FPV y artillería en la ribera; largo alcance atrás | Muy alta en el río | Media-alta, con todas las franjas de distancia en un solo grafo | **Principal** |
| Sur del oblast (Ochakiv–Kinburn) | 10–15 km a través del estuario | FPV costeros | Alta | Media; frente marítimo atípico | Variante de continuidad |
| Eje Donetsk (Pokrovsk–Kramatorsk) | 0–30 km, línea móvil | FPV de radio y fibra, EW densa | Baja | Alta | Escenario de sensibilidad, solo con parámetros |

La recomendación es reemplazar el recorte urbano de Mykolaiv por un **corredor que vaya de la ciudad, como retaguardia y base de despegue, hasta la ribera derecha del Dnipro**. Esta elección conserva la continuidad con el trabajo ya hecho, pone en un mismo grafo todas las franjas de distancia al frente, usa una línea de contacto trivial de obtener (el curso del río) y contrastable con DeepState, y evita depender de un frente móvil. El eje de Donetsk queda como escenario de "EW alta y frente móvil", parametrizado con las cifras publicadas y sin reproducir posiciones. La evidencia de Kherson trata sobre todo de ataques contra civiles, así que su valor para el proyecto es solo geográfico (anchos de franja, distancias y línea), no táctico.

## Limitaciones éticas y de fuentes que el informe debe declarar

Las cifras de ambos bandos son afirmaciones, no hechos. Del lado ucraniano, el exministro Fedorov habla de que los drones realizan "más del 95 % de los ataques" ([Army Technology](https://www.army-technology.com/news/drones-accounting-for-over-95-of-strikes-ukraines-fedorov/)), y se afirma, sin una atribución clara, que 33.988 soldados rusos fueron muertos o gravemente heridos por UAV en marzo de 2026 ([Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2026/04/09/8029447/)). Del lado ruso, el Ministerio de Defensa asegura cerrar el ciclo entre detección y ataque "en minutos", y la propia nota admite que no es verificable ([www1.ru](https://www1.ru/en/news/2026/04/04/celeukazanie-za-minuty-orlan-10-zakryl-petliu-mezdu-obnaruzeniem-celi-i-artilleriiskim-udarom.amp.html)). Los conteos pro-rusos de LostArmour sobre el Lancet tienen un sesgo de supervivencia, porque los fallos rara vez se filman ([Wikipedia, ZALA Lancet](https://en.wikipedia.org/wiki/ZALA_Lancet)). Un fact-check concluyó que la cifra de "70–80 % de bajas por drones" proviene "principalmente de funcionarios ucranianos" ([Oklahoma Watch](https://oklahomawatch.org/2026/06/09/have-70-of-casualties-in-the-russia-ukraine-war-been-caused-by-drones-as-rep-tom-cole-claimed/)), mientras otras estimaciones ucranianas la sitúan entre un cuarto y la mitad ([Kyiv Post](https://www.kyivpost.com/post/67606)). Los alcances de los jammers difieren hasta en un orden de magnitud según la fuente. Ninguna de estas cifras debe entrar al modelo como constante, sino como un rango con su etiqueta de confiabilidad.

El proyecto no debe compilar ni publicar posiciones militares. Eso implica descartar los puntos de unidades y las direcciones de ataque de DeepState, no reproducir geometrías de fortificaciones ucranianas (que no se publican de forma intencional), usar un snapshot histórico en vez de feeds en tiempo real y no usar las APIs de alertas en vivo. El encuadre de la idea (b) debe quedar en el nivel descriptivo: optimizar la saturación de defensas con señuelos se acercaría a guía táctica, y este informe no lo hace.

Las licencias también imponen límites. ACLED prohíbe redistribuir los eventos crudos, e ISW es propiedad exclusiva y exige consentimiento escrito. GPSJam y DeepState no tienen licencia explícita, así que no conviene redistribuir los archivos crudos, sino publicar los scripts y los atributos derivados. Las fuentes CC BY-SA y ODbL contagian su cláusula de compartir a la base derivada.

Quedan además limitaciones sobre lo que los datos y la literatura pueden decir. ADS-B mide el efecto sobre aeronaves en altura, y Figuet et al. muestran que a baja altitud la afectación es menor, de modo que la capa GNSS en el frente es un supuesto y no una medición. La literatura de detección se valida en laboratorio, en simulación o en eventos civiles (Denver, el Báltico), no en combate. No se pudo leer el texto completo de CLUN-LSR, que está tras un muro de pago; el grupo debe extraer del PDF su modelo de jammer y sus parámetros, para que el radio de jamming físico sea coherente con el de la capa de red. Y como las zonas de EW serán sintéticas, cualquier resultado vale para el modelo de amenazas declarado, no para el frente real.

## Conclusión

La investigación cambia la naturaleza de la pregunta. Ya no se trata de si el jamming justifica rutear distinto, porque lo justifica, sino de **en qué escala espacial el ruteo físico es la respuesta correcta**. La denegación GNSS, de decenas a cientos de kilómetros, no se esquiva sino que se soporta a bordo, y la fibra y el guiado terminal anulan el jamming en los extremos de la misión. El espacio donde una alerta tipo CLUN-LSR tiene valor físico es, entonces, el de los **jammers tácticos de 0,2–3 km sobre UAV de radio en tramo de crucero**, y esa es la escala que la propuesta debe modelar y defender.

El hallazgo más útil para el grupo es que su propio resultado negativo, C empatando con D, no es un fracaso del método. Es lo que cabe esperar cuando no existe información anticipada. La alerta propagada es la variable que puede romper ese empate, y su efecto se puede refutar al barrer la latencia y la fracción de drones inmunes. Así, la contribución deja de ser "un Yen con penalizaciones" y pasa a ser una pregunta medible: **cuánto vale, en misiones completadas, que el primer UAV que sufre la interferencia hable a tiempo**.

## Bibliografía consolidada

*Fecha de consulta de todas las URL: 18-oct-2026, salvo que se indique otra cosa. "s/f" = sin fecha identificada.*

### Base teórica y literatura académica revisada por pares

- Zheng, S., Zhu, X., Qin, Z. y Dong, C. — "Cross-layer UAV network routing protocol for spectrum denial environments", *Ad Hoc Networks* 167, 103702 (en línea 9-nov-2024; número de feb-2025). https://doi.org/10.1016/j.adhoc.2024.103702 · resumen: https://www.sciencedirect.com/science/article/abs/pii/S1570870524003135 · referencias: https://api.crossref.org/works/10.1016/j.adhoc.2024.103702
- Zhang, K., Zhu, X., Dong, C. y Tian, C. — "Defending Against Periodic Jamming: A Routing Protocol for UAV Networks with Neighborhood Collaboration", *IEEE Communications Magazine* (2026). https://doi.org/10.1109/MCOM.001.2600062
- Duan, B. et al. — "Anti-Jamming Path Planning for Unmanned Aerial Vehicles with Imperfect Jammer Information", IEEE ROBIO, pp. 729–735 (2018). https://doi.org/10.1109/ROBIO.2018.8665238
- Dong, Y., He, C., Wang, Z. y Zhang, L. — "Radio Map Assisted Path Planning for UAV Anti-Jamming Communications", *IEEE Signal Processing Letters* 29, 607–611 (2022). https://doi.org/10.1109/LSP.2022.3149374
- Liu, Z., Liu, H., Xu, W. y Chen, Y. — "Exploiting Jamming-Caused Neighbor Changes for Jammer Localization", *IEEE TPDS* 23(3), 547–555 (2012). https://doi.org/10.1109/TPDS.2011.154
- Liu, Z., Lo, S., Blanch, J., Chen, Y.-H. y Walter, T. — "Locating GNSS Interference Sources using ADS-B with Non-linear Least Squares", *NAVIGATION* 72(3), navi.716 (2025). https://doi.org/10.33012/navi.716
- Ahmed, N., Winter, A. y Sokolova, N. — "Low Cost Collaborative Jammer Localization Using a Network of UAVs", IEEE Aerospace Conference (2021). https://doi.org/10.1109/AERO50100.2021.9438441
- Kim, J. y Hespanha, J. P. — "Discrete approximations to continuous shortest-path: application to minimum-risk path planning for groups of UAVs", 42nd IEEE CDC (2003). https://doi.org/10.1109/CDC.2003.1272863
- Koenig, S. y Likhachev, M. — "Fast replanning for navigation in unknown terrain", *IEEE Transactions on Robotics* 21(3), 354–363 (2005). https://doi.org/10.1109/TRO.2004.838026
- Luna, M. A. et al. — "A multi-UAV system for coverage path planning applications with in-flight re-planning capabilities", *Journal of Field Robotics* 41(5), 1480–1497 (2024). https://doi.org/10.1002/rob.22342
- Zheng, Z., Liu, Y. y Zhang, X. — "The more obstacle information sharing, the more effective real-time path planning?", *Knowledge-Based Systems* 114, 36–46 (2016). https://doi.org/10.1016/j.knosys.2016.09.021
- Suurballe, J. W. — "Disjoint paths in a network", *Networks* 4(2), 125–145 (1974). https://doi.org/10.1002/net.3230040204
- Cheng, Y., Medhi, D. y Sterbenz, J. P. G. — "Geodiverse routing with path delay and skew requirement under area-based challenges", *Networks* 66(4), 335–346 (2015). https://doi.org/10.1002/net.21660
- Sterbenz, J. P. G. et al. — "Resilience and survivability in communication networks: Strategies, principles, and survey of disciplines", *Computer Networks* 54(8), 1245–1265 (2010). https://doi.org/10.1016/j.comnet.2010.03.005
- Jorgensen, S., Chen, R. H., Milam, M. B. y Pavone, M. — "The Team Surviving Orienteers problem", *Autonomous Robots* 42, 927–952 (2018). https://doi.org/10.1007/s10514-017-9694-1
- Sanjab, A., Saad, W. y Başar, T. — "Prospect theory for enhanced cyber-physical security of drone delivery systems: A network interdiction game", IEEE ICC (2017). https://doi.org/10.1109/ICC.2017.7996862
- Masters, P. y Sardina, S. — "Deceptive Path-Planning", IJCAI-17, pp. 4368–4375 (2017). https://doi.org/10.24963/ijcai.2017/610
- Purvis, K. B., Chandler, P. R. y Pachter, M. — "Feasible Flight Paths for Cooperative Generation of a Phantom Radar Track", *J. Guidance, Control, and Dynamics* 29(3), 653–661 (2006). https://doi.org/10.2514/1.15563
- Bildik, E., Tsourdos, A., Perrusquía, A. e Inalhan, G. — "Swarm Decoys Deployment for Missile Deceive using Multi-Agent Reinforcement Learning", ICUAS, pp. 256–263 (2024). https://doi.org/10.1109/ICUAS60882.2024.10556889
- Figuet, B., Waltert, M., Felux, M. y Olive, X. — "GNSS Jamming and Its Effect on Air Traffic in Eastern Europe", *Engineering Proceedings* 28(1), 12 (2022). https://doi.org/10.3390/engproc2022028012
- Li et al. — detección de jamming en receptores OFDM de UAV, *IEEE Access* 10 (2022). https://digitalcommons.mtu.edu/michigantech-p/15739

### Preprints, tesis, actas y recursos académicos no revisados por pares

- Lo, S. et al. (Stanford GPS Lab) — "Observations of Spoofing…", ION ITM (2026). https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf
- Viana, J. et al. — detección de ataques sobre enlaces 5G de UAV con RSSI/SINR, arXiv 2207.10810 (2022). https://arxiv.org/abs/2207.10810
- Viana, J. et al. — "Two methods for jamming identification in UAV networks…", VTC 2022-Spring, arXiv 2203.11373 (2022). https://arxiv.org/abs/2203.11373v1
- Detección colaborativa de jamming GNSS (crowdsourcing y lógica difusa), Sciforum (s/f). https://sciforum.net/paper/view/25272
- Costo −ln(1−riesgo) en caminos con restricción de recursos, arXiv 2511.18236 (2025). https://arxiv.org/pdf/2511.18236
- ResiliNets, Universidad de Kansas — "GeoDivRP: Geodiverse Multipath Routing Protocol" (s/f). https://resilinets.org/geodivrp_geodiverse_multipath_routing_protocol.html
- Mareschal de Charentenay, S. — tesis "Swarm intelligence to deceive an adversary detection system", IMT Atlantique (defensa: 1-jun-2026). https://www.imt-atlantique.fr/en/events/stanislas-mareschal-de-charentenay-thesis-defence?page=1

### Think tanks, revistas de análisis y análisis especializado

- Watling, J. y Reynolds, N. (RUSI) — "Tactical Developments During the Third Year of the Russo-Ukrainian War" (14-feb-2025). https://static.rusi.org/tactical-developments-third-year-russo-ukrainian-war-february-2205.pdf
- Watling, J. y Reynolds, N. (RUSI) — "Meatgrinder: Russian Tactics in the Second Year of Its Invasion of Ukraine" (19-may-2023). https://rusi.org/explore-our-research/publications/special-resources/meatgrinder-russian-tactics-second-year-its-invasion-ukraine
- Nieczypor, K. y Matuszak, S. (OSW) — "Game of drones" (14-oct-2025). https://www.osw.waw.pl/en/publikacje/osw-commentary/2025-10-14/game-drones-production-and-use-ukrainian-battlefield-unmanned
- Jensen, B. y Atalan, Y. (CSIS) — "Drone Saturation: Russia's Shahed Campaign" (13-may-2025). https://www.csis.org/analysis/drone-saturation-russias-shahed-campaign
- Anokhin, I. (Institute for Science and International Security) — "Monthly Analysis of Russian Shahed-136 Deployment Against Ukraine" (7-jul-2026). https://isis-online.org/isis-reports/monthly-analysis-of-russian-shahed-136-deployment-against-ukraine
- Institute for Science and International Security — "A Comprehensive Analytical Review of Russian Shahed-type UAVs Deployment Against Ukraine in 2025" (2026). https://isis-online.org/isis-reports/a-comprehensive-analytical-review-of-russian-shahed-type-uavs-deployment-against-ukraine-in-2025
- Hambling, D. (CTC Sentinel, West Point) — "Moving Targets", vol. 18 n.º 7 (jul-2025). https://ctc.westpoint.edu/moving-targets-implications-of-the-russo-ukrainian-war-for-drone-terrorism/
- Sutea, V. (Atlantic Council) — "Fiber optics drones have emerged as critical kit for both Russia and Ukraine" (24-feb-2026). https://www.atlanticcouncil.org/blogs/ukrainealert/fiber-optics-drones-have-emerged-as-critical-kit-for-both-russia-and-ukraine/
- Sokolov, L. (Jamestown Foundation) — "Rubicon Reveals Limits of Russia's Drone Centralization" (~11-jun-2026). https://jamestown.org/rubicon-reveals-limits-of-russias-drone-centralization/
- ICDS / Sahaidachnyi Security Center — "Russia's War in Ukraine: Fortification for Drone Warfare" (9-sep-2025). https://icds.ee/en/russias-war-in-ukraine-fortification-for-drone-warfare/
- Kirichenko, D. (CEPA) — "The Phony War: Ukraine and Russia's Decoy Drones" (8-may-2025). https://cepa.org/article/the-phony-war-ukraine-and-russias-decoy-drones/
- Brown, H. (LIIA) — "The Drone Revolution: Lessons from Ukraine" (2025). https://liia.lv/en/publications/the-drone-revolution-lessons-from-ukraine-1476?get_file=1
- Jajcay, J. (War on the Rocks) — "I Fought in Ukraine and Here's Why FPV Drones Kind of Suck" (26-jun-2025). https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/
- Maurin, É. (War on the Rocks) — "The Strange Transformation of the Front Line in Ukraine" (9-sep-2026). https://warontherocks.com/the-strange-transformation-of-the-front-line-in-ukraine/
- Lee, P. (Universidad de Portsmouth / The Conversation) — "Russia turns to an old ally in its war against Ukrainian drones: the weather" (23-oct-2025). https://www.port.ac.uk/news-events-and-blogs/blogs/security-and-risk/russia-turns-to-an-old-ally-in-its-war-against-ukrainian-drones-the-weather
- Kirichenko, D. (ASPI The Strategist) — "The autonomous arms race in the Russia–Ukraine war" (4-ago-2026). https://www.aspistrategist.org.au/the-autonomous-arms-race-in-the-russia-ukraine-war/
- Kryzhanivska, O. (Ukraine's Arms Monitor) — "Drone warfare in Ukraine: EW depth" (28-feb-2026). https://ukrainesarmsmonitor.substack.com/p/drone-warfare-in-ukraine-ew-depth
- Defence Ukraine — "Russian EW architecture in Ukraine, 2026" (10-sep-2026; fuente secundaria). https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/
- drone-warfare.com — "Electronic warfare" (s/f; divulgativa). https://drone-warfare.com/counter-uas/electronic-warfare/
- Africk, B. — "Russian Field Fortifications in Ukraine" (Substack, s/f; mapa actualizado al menos hasta ago-2024). https://read.bradyafrick.com/p/russian-field-fortifications-in-ukraine
- Mittal, V. (Forbes) — "The Latest Threat To Ukrainian Air Defenses: The Russian Gerbera Drone" (25-nov-2024). https://www.forbes.com/sites/vikrammittal/2024/11/25/the-latest-threat-to-ukrainian-air-defenses-the-russian-gerbera-drone/
- Mittal, V. (Forbes) — "Russia Makes Advances As Winter Weather Grounds Many Ukrainian Drones" (28-nov-2025). https://www.forbes.com/sites/vikrammittal/2025/11/28/russia-makes-advances-as-winter-weather-grounds-many-ukrainian-drones/
- Kirichenko, D. (Forbes) — "Excavators Are Building Ukraine's Drone-Era Fortifications" (4-mar-2026). https://www.forbes.com/sites/davidkirichenko/2026/03/04/excavators-are-building-ukraines-drone-era-fortifications/

### Prensa y medios especializados

- Post, K. (Kyiv Independent) — "New Ukrainian strike drones are chasing Russian armor and EW past the radio horizon" (1-ago-2025). https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/
- Kyiv Independent — "'We cannot wait for peace': Denmark takes on rebuilding Mykolaiv Oblast" (~2024). https://kyivindependent.com/we-cannot-wait-for-peace-reluctant-at-first-denmark-takes-on-rebuilding-mykolaiv-oblast/
- Myre, G. (NPR) — "Drones buzz overhead, troops hunker underground in Ukraine's hellish kill zone" (5-oct-2026). https://www.npr.org/2026/10/05/nx-s1-5925803/drones-buzz-overhead-troops-hunker-underground-in-ukraines-hellish-kill-zone
- Ukrainska Pravda — Brovdi: la kill zone llega a 25 km o más (14-may-2026). https://www.pravda.com.ua/eng/news/2026/05/14/8034645/
- Ukrainska Pravda — interceptores y bajas por UAV en marzo de 2026 (9-abr-2026). https://www.pravda.com.ua/eng/news/2026/04/09/8029447/
- Ukrainska Pravda — distribución de bandas de drones rusos (8-ago-2025; leído en resumen de búsqueda). https://www.pravda.com.ua/eng/articles/2025/08/08/7525279/
- Ukrainska Pravda — HUR: la mitad de los drones lanzados son señuelos (11-nov-2024). https://www.pravda.com.ua/eng/news/2024/11/11/7483868/
- Ukrainska Pravda — antenas CRPA Kometa en drones rusos (18-feb-2025). https://www.pravda.com.ua/eng/news/2025/02/18/7498968
- Ukrainska Pravda — túneles antidron en Kherson y la ruta Kherson–Mykolaiv (9-sep-2025). https://www.pravda.com.ua/eng/news/2025/09/09/7530061/
- Business Insider vía Yahoo — "Front line drone kill zone" (12-jun-2026). https://www.yahoo.com/news/world/articles/front-line-drone-kill-zone-110501096.html
- Euromaidan Press — "Ukraine's jamming fails against fiber drones" (26-jun-2025). https://euromaidanpress.com/2025/06/26/ukraine-jamming-fails-fiber-drones-russia/
- Euromaidan Press — "The EW backpack revolution" (17-may-2024). https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/
- Euromaidan Press — "Ukraine deploys new Veres-2 anti-drone system" (25-ago-2025). https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/
- Euromaidan Press, citando a ISW — "Ukrainian EW tech increasingly grounds Shahed drones" (3-dic-2024). https://euromaidanpress.com/2024/12/03/isw-ukrainian-ew-tech-increasingly-grounds-shahed-drones-complicating-russian-airstrikes/
- Euromaidan Press — "Drones hunt anything that moves near front…" (22-jun-2026; marcado como publicitario). https://euromaidanpress.com/2026/06/22/drones-hunt-anything-that-moves-near-front-ukraines-drone-proof-network-now-grows-9-kilometers-daily/
- Militarnyi — "Russian Boomerang FPV drones shifted to frequencies unavailable to most detectors" (26-jul-2026). https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/
- Militarnyi — vida media de un Mavic en el frente: una semana (s/f, ~2025). https://militarnyi.com/en/news/on-the-front-lines-average-lifespan-of-mavic-drone-is-one-week-instructor-with-93rd-brigade/
- Militarnyi — nueva antena CRPA china en Shahed rusos (s/f, ~2025). https://militarnyi.com/en/news/new-chinese-crpa-antenna-found-on-russian-shahed/
- Withington, T. (Armada International) — "Check the Manual" (14-mar-2024). https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/
- Altman, H. (The War Zone) — "Inside Ukraine's fiber-optic drone war" (28-may-2025). https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war
- The Defense Post — "Ukraine spoofs Shahed drones" (5-dic-2024). https://thedefensepost.com/2024/12/05/ukraine-spoofs-shahed-drones/amp/
- The Defense Post — módulo TFL-1 de guiado terminal (19-nov-2025). https://gecici.thedefensepost.com/?p=117258
- Defense News — "Russian drones can jam cell phones 60 miles away" (16-nov-2018). https://www.defensenews.com/newsletters/unmanned-systems/2018/11/16/russian-drones-can-jam-cell-phones-60-miles-away/
- Army Recognition — Leer-3, 30 km (2022). https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2022/russian-troops-using-leer-3-able-to-jam-ukrainian-army-mobile-phone-signals-within-30-km
- Army Recognition — "Russia unveils portable tank-mounted drone jammer to counter Ukrainian attacks" (Volnorez; s/f). https://armyrecognition.com/focus-analysis-conflicts/army/defence-security-industry-technology/russia-unveils-portable-tank-mounted-drone-jammer-to-counter-ukrainian-attacks
- Al Jundi — Volnorez (s/f). https://aljundi.ae/?p=36308
- Unmanned Airspace — "Russia deploys tank-mounted Volnorez jammers in Ukraine" (s/f). https://www.unmannedairspace.info/counter-uas-systems-and-policies/russia-deploys-tank-mounted-volnorez-jammers-in-ukraine/
- Forbes vía online.ua — "Russian EW systems are unable to cope with Ukrainian drones" (s/f). https://news.online.ua/en/russian-ew-systems-are-unable-to-cope-with-ukrainian-drones-forbes-873429
- Business Insider NL — "Ukraine is losing 10,000 drones a month…" (2023). https://www.businessinsider.nl/ukraine-is-losing-10000-drones-a-month-to-russian-electronic-warfare-systems-that-send-fake-signals-and-screw-with-their-navigation-researchers-say
- Business Insider NL — Excalibur: caída de la tasa de acierto por jamming (s/f, ~2024). https://businessinsider.nl/the-us-gave-up-sending-ukraine-excalibur-guided-artillery-shells-costing-100000-because-they-rarely-hit-their-target-report-says/
- Rubryka — repetidor "Vidlunnia" (13-jun-2024). https://rubryka.com/en/2024/06/13/retranslyator-vidlunnya-dlya-droniv/
- Ukrinform — Fedorov: los drones cambian altitud, rutas y patrones según la EW (s/f). https://www.ukrinform.net/rubric-defense/3924457-ukraine-actively-developing-antidrone-tech-vice-pm.html
- Kyiv Post — ataques FPV en la costa de Mykolaiv (26-ene-2026). https://www.kyivpost.com/post/68805
- Kyiv Post — ataque con Iskander-M y Shahed contra Mykolaiv (2026; fecha por confirmar). https://www.kyivpost.com/post/86866
- Kyiv Post — estimaciones de bajas rusas causadas por drones (s/f). https://www.kyivpost.com/post/67606
- AP vía Yahoo — "UN commission says Russian drone attacks in Kherson are crimes against humanity" (28-may-2025). https://www.yahoo.com/news/un-commission-says-russian-drone-225500743.html
- Army Technology — "Drones accounting for over 95% of strikes: Ukraine's Fedorov" (28-sep-2026). https://www.army-technology.com/news/drones-accounting-for-over-95-of-strikes-ukraines-fedorov/
- Oklahoma Watch — fact-check sobre "70 % de bajas por drones" (9-jun-2026). https://oklahomawatch.org/2026/06/09/have-70-of-casualties-in-the-russia-ukraine-war-been-caused-by-drones-as-rep-tom-cole-claimed/
- www1.ru — afirmación del MoD ruso sobre Orlan-10 y "minutos" entre detección y ataque (4-abr-2026). https://www1.ru/en/news/2026/04/04/celeukazanie-za-minuty-orlan-10-zakryl-petliu-mezdu-obnaruzeniem-celi-i-artilleriiskim-udarom.amp.html
- Safety4Sea — estudio de interferencia GNSS en el Báltico (s/f, ~2025). https://safety4sea.com/study-shows-gnss-interference-in-the-baltic-sea
- Wikipedia — "ZALA Lancet" (consultada 18-oct-2026). https://en.wikipedia.org/wiki/ZALA_Lancet
- Wikipedia — "R-330Zh Zhitel" (consultada 18-oct-2026). https://en.wikipedia.org/wiki/R-330Zh_Zhitel
- Wikipedia — "Bukovel (counter unmanned aircraft system)" (consultada 18-oct-2026). https://en.wikipedia.org/wiki/Bukovel_%28counter_unmanned_aircraft_system%29
- Wikipedia — "Stupor Anti-Drone System" (consultada 18-oct-2026). https://en.wikipedia.org/wiki/Stupor_Anti-Drone_System

### Fuentes oficiales, organismos internacionales y ONG

- Ministerio de Defensa de Ucrania — "The Vampire: a drone that terrifies enemies…" (s/f). https://mod.gov.ua/en/news/the-vampire-a-drone-that-terrifies-enemies-and-assists-ukrainians
- ONU Ucrania / Comisión Internacional Independiente de Investigación — informe A/80/497 sobre crímenes de lesa humanidad con drones (27-oct-2025). https://ukraine.un.org/en/304119-russian-authorities-committed-crimes-against-humanity-targeting-civilian-population-through
- Human Rights Watch — "Hunted From Above: Russia's Use of Drones to Attack Civilians in Kherson" (3-jun-2025). https://www.hrw.org/report/2025/06/03/hunted-from-above/russias-use-of-drones-to-attack-civilians-in-kherson-ukraine
- Android Developers — "Detect GNSS jamming and spoofing" (s/f). https://developer.android.com/develop/sensors-and-location/sensors/gnss-spoof-jam

### Fabricantes

- Ukrspecsystems, vía Ukrainian News — dron Shark resistente a EW (2022). https://ukranews.com/en/news/890883-ew-resistant-drone-that-can-adjust-himars-presented-in-ukraine-in-conditions-of-war
- BlueBird Tech — detector Chuyka 3.0 (página de producto, s/f). https://blue-bird.tech/en/products/bluebirds-chuyka-3-0-electronic-intelligence-device-5-8-ghz-3-3-ghz-1-2-ghz
- AO Avtomatika — Kupol-PRO (página de producto, s/f). https://www.ao-avtomatika.ru/en/catalog/products/kupol-pro-portable-anti-drone-system/
- Kyiv Defenders — EW Kvertus (s/f). https://kyivdefenders.com.ua/en/projects/reb-kvertus/

### Datasets, APIs y documentación de datos

- DeepStateMap — API de historial y último snapshot (consultada 18-oct-2026). https://deepstatemap.live/api/history/public · https://deepstatemap.live/api/history/last
- cyterat — "deepstate-map-data", espejo diario GPL-3.0 (último commit 18-oct-2026). https://github.com/cyterat/deepstate-map-data
- longlinecode — "russo-ukrainian-front-daily", línea de contacto diaria (creado 1-sep-2026). https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md
- ISW — licencia de las capas ArcGIS de control territorial (ítems modificados en sep-2026). https://www.arcgis.com/sharing/rest/search?q=owner:gbarros_understandingwar%20AND%20(title:VIEW_RussiaCoTinUkraine_V2%20OR%20title:AssessedRussianAdvanceInUkraine_V2)&f=json
- ISW — capa "RUAF_Field_Fortifications_Polylines" (última edición 1-jul-2025). https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/RUAF_Field_Fortifications_Polylines/FeatureServer/0?f=json
- GPSJam — FAQ y metodología (s/f). https://gpsjam.org/faq · datos del 17-oct-2026: https://gpsjam.org/data/2026-10-17-h3_4.csv
- The Economist — "the-economist-war-fire-model" (último commit 18-oct-2026). https://github.com/TheEconomist/the-economist-war-fire-model
- ACLED — EULA (actualizada 8-jul-2025). https://acleddata.com/eula · FAQ de myACLED: https://acleddata.com/myacled-faqs
- HDX / UCDP — "UCDP data for Ukraine" (cobertura hasta 31-dic-2024). https://data.humdata.org/api/3/action/package_show?id=ucdp-data-for-ukraine
- Vadimkin — "ukrainian-air-raid-sirens-dataset", MIT (último commit 18-oct-2026). https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md
- Bellingcat — "Civilian Harm in Ukraine", JSON de TimeMap (registros hasta 9-jul-2025). https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json
- Ivaniuk, P. (Kaggle) — "Massive Missile Attacks on Ukraine", CC BY-NC-SA 4.0 (actualizado 17-oct-2026). https://www.kaggle.com/api/v1/datasets/view/piterfm/massive-missile-attacks-on-ukraine
- ESA — WorldCover, acceso a datos (versiones 2020/2021). https://esa-worldcover.org/en/data-access
- Meta / WRI — Global Canopy Height (AWS Registry, s/f). https://registry.opendata.aws/dataforgood-fb-forests/
- Copernicus DEM GLO-30 (AWS Registry, s/f). https://registry.opendata.aws/copernicus-dem/
- Open-Meteo — términos de uso (s/f). https://open-meteo.com/en/terms

### Documentos internos del proyecto (sin URL pública)

- Grupo del curso — `05_T2/PROPUESTA_TECNICA.md`, v2 (18-oct-2026): estrategias A/B/C/C0/C1/D y resultados preliminares (§9).
- Grupo del curso — `05_T2/CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md` (18-oct-2026): decisión de no presentar la solución como una implementación de CLUN-LSR.
- Grupo del curso — `05_T2/ruteo/config.py`: AOI de Mykolaiv y parámetros de fallas, malla y algoritmo.

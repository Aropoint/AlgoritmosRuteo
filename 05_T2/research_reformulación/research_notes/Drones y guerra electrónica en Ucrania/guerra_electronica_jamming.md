# Guerra electrónica (EW) contra drones en la guerra Rusia–Ucrania: jamming, spoofing GNSS, bandas de frecuencia y contramedidas (2022–2026)

> Notas de investigación basadas solo en fuentes abiertas, para parametrizar una simulación académica de ruteo resiliente de UAV inspirada en CLUN-LSR. El nivel de detalle es descriptivo, el que aparece en prensa y literatura académica. Etiquetas de fiabilidad usadas en cada afirmación: **[H]** hecho documentado o medición independiente; **[OF]** afirmación oficial (gobierno o ministerio); **[FAB]** afirmación de fabricante o promotor; **[AN]** estimación de analista o think tank; **[TEST]** testimonio de combatientes o unidades; **[SEC]** fuente secundaria, de menor calidad o contenido que solo pude ver en el resumen de un buscador porque la página bloqueó la descarga. Fecha de corte de la búsqueda: 18-oct-2026.

## 1. ¿Qué bandas de frecuencia usan los enlaces de control y video de los drones en esta guerra, y cómo han cambiado al abandonar las bandas interferidas?

### Takeaway
Las bandas de control han ido bajando y dispersándose: primero 868/915 MHz y 2,4 GHz (2023–24), luego 720–1020 MHz y 400–490 MHz, y después 2,1–2,3 GHz (2025). En paralelo, el video analógico ha migrado desde 5,8 GHz hacia 1,2–1,3 GHz, 3,3 GHz y, en 2026, 6–7,2 GHz, por encima del techo de ~6 GHz de muchos detectores e inhibidores. Es una carrera de saltos de banda, que se mide en semanas o meses, y no hay ninguna banda segura de forma estable.

### Cited Findings
**Línea base 2023–2024 (manual ruso de FPV)**
- **[SEC/OF]** Un manual del Estado Mayor ruso sobre empleo táctico de FPV (2024), analizado por Thomas Withington, indica control en **390–490 MHz, 850–960 MHz, 1,2 GHz y 2,4 GHz**, y bajada de video en **2,4 GHz y 5,8 GHz**. Su tabla por modelo da, por ejemplo: Boomerang con control en 433/868/915 MHz y video en 5,8 GHz; Courier y XL-10 con control en 868/915 MHz y 2,4 GHz y video en 5,8 GHz; Piranha-7/10 y PVC-1 con control en 868/915 MHz y video en 5,8 GHz. — [Armada International, "Check the Manual", 14-mar-2024](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/)
- **[SEC/OF]** El mismo manual exige que los pilotos notifiquen sus frecuencias a las unidades EW propias para evitar el auto-bloqueo (fratricidio electromagnético), y que analicen la "situación radioelectrónica" con analizadores de espectro antes de cada salida para elegir la frecuencia de control. — [Armada International, 14-mar-2024](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/)

**Primer desplazamiento documentado del control (2024)**
- **[TEST/FAB]** Kvertus, fabricante ucraniano de EW, afirmó en abril-mayo de 2024 que los FPV rusos pasaron de **850–930 MHz** a usar también **720–1020 MHz**, combinando ataques en ambas bandas. Según su cofundador Yaroslav Filimonov, "65–70% de los drones aún usan frecuencias estándar". — [Euromaidan Press, 17-may-2024](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/)

**Video en 1,2–1,3 GHz y 3,3 GHz (2024–2025)**
- **[FAB]** El repetidor ucraniano "Vidlunnia" (junio de 2024) baja el video a tierra en **1,3 GHz**. El video por defecto del dron es **5,8 GHz** y el control usa módulos TBS Crossfire o ELRS. — [Rubryka, 13-jun-2024](https://rubryka.com/en/2024/06/13/retranslyator-vidlunnya-dlya-droniv/)
- **[SEC]** Los detectores de video ucranianos trabajaban sobre todo en **1,2 y 5,8 GHz**, y los fabricantes añadieron **3,3 GHz** cuando se extendieron los drones en esa banda. — [Mezha/Oboronka (comparativa de detectores; página bloqueada, visto en resumen de búsqueda)](https://oboronka.mezha.ua/en/cukorok-chuyka-dziga-tinysa-whoover-yak-obrati-detektor-droniv-304569/)
- **[FAB]** El detector BlueBird "Chuyka 3.0" se comercializa para interceptar video en 1,2, 3,3 y 5,8 GHz, con barrido en **900–1800, 2870–4080 y 4860–6060 MHz**. — [BlueBird Tech (página de producto)](https://blue-bird.tech/en/products/bluebirds-chuyka-3-0-electronic-intelligence-device-5-8-ghz-3-3-ghz-1-2-ghz)

**Dispersión y saltos de frecuencia (2025)**
- **[TEST/SEC]** En agosto de 2025, en un sector del frente, un experto observó que ~**20%** de los drones rusos volaba en **400–490 MHz**, ~**30%** en **720–1020 MHz** y el resto en **2,1–2,3 GHz**. Algunos drones cambian de frecuencia de forma dinámica, usan amplificadores y siguen navegando tras perder el enlace. — [Ukrainska Pravda, 8-ago-2025 (página bloqueada, visto en resumen de búsqueda)](https://www.pravda.com.ua/eng/articles/2025/08/08/7525279/)
- **[TEST]** Una operadora ucraniana citó **5,2 GHz** como ejemplo de banda no inhibida que el enemigo podría explotar. Resume la dinámica así: "No puedes inhibir todo a la vez; solo funciona en ciertas bandas". — [Euromaidan Press (D. Kirichenko), 10-ago-2025](https://euromaidanpress.com/2025/08/10/when-the-beeping-starts-someones-drone-is-about-to-die/)
- **[SEC]** Se informa que operadores rusos reprogramaron drones para operar en frecuencias ucranianas, presumiblemente "protegidas" por la EW amiga ucraniana. La cita es de US Army Military Review, recogida por un portal secundario. — [Defence Ukraine, 10-sep-2026](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)

**Por encima de 6 GHz (2025–2026)**
- **[SEC]** Una fuente de origen ruso (~2025) afirma haber hallado transmisores de video de **6,7 GHz y 7,2 GHz** en restos de FPV ucranianos. No lo pude corroborar. — [Militär Aktuell (página bloqueada, visto en resumen de búsqueda)](https://militaeraktuell.at/en/ukraine-opens-next-round-in-drone-frequency-war/)
- **[H/TEST]** Un Boomerang ruso capturado, analizado por el especialista ucraniano Serhii "Flash", transmite video en **6–7,2 GHz**. Sus antenas de telemetría tienen líneas de corte para reajustar la banda en campo. La mayoría de los detectores portátiles FPV tienen techo en **~6 GHz**; los más nuevos añaden un cuarto canal de 7,2 GHz o más. — [Militarnyi, 26-jul-2026](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/)

**Congestión propia y otros enlaces**
- **[TEST]** En sectores calientes hasta una docena de equipos de drones comparten unas pocas frecuencias analógicas sin cifrar, y la espera por frecuencia antes del despegue puede llegar a 30 minutos. — [War on the Rocks (J. Jajcay), 26-jun-2025](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)
- **[AN]** Con FPV pilotados por radio es difícil concentrar varios drones en tiempo y espacio porque interfieren entre sí. — [RUSI, Watling & Reynolds, "Tactical Developments During the Third Year...", feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[SEC/OF]** Enlaces satelitales y celulares: los Molniya-2 rusos con antenas Starlink atacaban entre 20 y 80 km tras las líneas ucranianas, hasta que en febrero de 2026 la "lista blanca" de Starlink cortó los terminales no registrados. — [NV, feb-2026](https://english.nv.ua/nation/russian-field-operations-crippled-after-starlink-cut-50581450.html); [Kyiv Post](https://www.kyivpost.com/amp/post/69255)
- **[H]** Fase temprana (2022): el ministro Fedorov acusó a Rusia de usar una versión extendida de DJI AeroScope, que revela la posición del dron y del piloto, para localizar operadores ucranianos. Es una acusación no confirmada. DJI dejó de producir AeroScope hacia marzo de 2023. — [Mezha, 6-mar-2023](https://mezha.ua/en/2023/03/06/dji-has-quietly-discontinued-the-aeroscope-drone-detection-system-that-could-have-been-used-by-the-russians/)

### Inferences
- Para la simulación conviene modelar al menos estos grupos de bandas: control {400–490 MHz, 720–1020 MHz (incluye 868/915), 1,2–1,3 GHz, 2,1–2,5 GHz} y video {1,2–1,3 GHz, 3,3 GHz, 5,8 GHz (5,1–5,9), 6–7,2 GHz}. Cada dron usaría una banda de control y una de video, y un jammer afectaría a un subconjunto de grupos.
- La migración es un proceso adaptativo con retardo. Los datos de 2024 (65–70% aún en banda "estándar") y de 2025 (20/30/50%) sugieren modelar la población de drones como una mezcla de bandas que se redistribuye hacia las menos inhibidas en horizontes de semanas o meses, no de minutos.
- Que existan radios con salto dinámico (2025) implica que una parte de la flota tiene "agilidad" y otra no. Esa distinción importa para decidir quién debe cambiar de ruta física cuando se detecta jamming y quién puede limitarse a cambiar de canal.

### Gaps
- No encontré datos cuantitativos sistemáticos (series temporales) de la distribución de bandas por frente. Solo hay instantáneas de fabricantes o expertos.
- No hallé fuentes primarias fiables sobre las bandas de los enlaces digitales (por ejemplo, sistemas tipo DJI o video digital) usados en 2025–2026, ni sobre la proporción analógico/digital.
- La afirmación de 6,7/7,2 GHz en drones ucranianos es de origen ruso y no está corroborada.

## 2. ¿Qué bandas atacan los inhibidores y qué especificaciones públicas tienen los principales sistemas EW rusos y ucranianos?

### Takeaway
Los inhibidores atacan a la vez las bandas GNSS (L1 ~1559–1610 MHz y L2/L5 ~1176–1280 MHz), las de control (400 MHz–1 GHz, 2,4 GHz) y las de video (1,2, 3,3 y 5,8 GHz), además de las celulares y satelitales. Las especificaciones públicas son casi siempre afirmaciones de fabricante o ministerio, a menudo contradictorias: los "alcances" de prensa difieren hasta en un orden de magnitud.

### Cited Findings
**Bandas GNSS como objetivo**
- **[SEC]** Pole-21 está pensado para combatir GPS, GLONASS, Galileo y BeiDou, cuyas señales están entre **1176,45 y 1575,42 MHz**. — [WPS (2016)](https://en.wps.ru/articles/def-sec/military-industries-conversion-defense-ministry-will-suppress-gps-from-cellular-communication-towers/)
- **[H]** Monitoreo a bordo de un barco cerca de Kaliningrado (junio–octubre de 2025) identificó **cuatro transmisores coordinados**: un spoofer de GPS L1, un jammer chirp de banda baja (GPS, Galileo, BeiDou), un jammer chirp de banda alta (solo GLONASS) y un jammer de tipo analógico sobre **toda la banda L1 de 60 MHz**. — [Inside GNSS (D. Goward), 8-dic-2025](https://insidegnss.com/kaliningrad-jamming-and-spoofing-up-close/)
- **[H]** Una estación de bajo costo de Stanford en Gdynia (mayo de 2025) registró interferencia procedente de Kaliningrado en **L1 y L5**, que afectaba también a Galileo, BeiDou y GLONASS. — [Lo et al., Stanford, ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)

**Ejemplo de jammer táctico que cubre GNSS, control y video**
- **[TEST/FAB]** El ucraniano Veres-2 (2025) es direccional y trabaja en **5 bandas: 1160–1280 MHz, 1560–1630 MHz, 2400–2500 MHz, 5160–5280 MHz y 5725–5850 MHz**, con alcance de **1–2 km** según las unidades que lo usan. — [Euromaidan Press, 25-ago-2025](https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/)

**Sistemas rusos (todas son afirmaciones de fabricante, ministerio o prensa salvo que se indique)**
- **Pole-21** (GNSS):
  - **[SEC]** 20 W por unidad y hasta **80 km** de alcance, con despliegue en torres celulares. — [Strategypage, 21-sep-2016](https://www.strategypage.com/htmw/htecm/20160921.aspx); [WPS](https://en.wps.ru/articles/def-sec/military-industries-conversion-defense-ministry-will-suppress-gps-from-cellular-communication-towers/)
  - **[SEC]** Para Pole-21M, "al menos 25 km" y 300–1000 W. Es un foro, de fiabilidad baja. — [armedconflicts.com](https://origin.armedconflicts.com/Pole-21M-t272048)
  - **[SEC/OF]** Según el manual del MoD ruso, sus postes de antena suprimen la navegación satelital a **no menos de 25 km**. — [Defence Ukraine, 10-sep-2026](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
- **R-330Zh Zhitel**:
  - **[SEC/OF]** Reconocimiento en **0,1–2 GHz**. Su objetivo declarado es detectar e inhibir Inmarsat, Iridium, GSM-1900 y GPS. Alcance de bloqueo de **hasta 25 km** contra comunicaciones terrestres y **50 km** contra aeronaves. — [Wikipedia, R-330Zh Zhitel](https://en.wikipedia.org/wiki/R-330Zh_Zhitel)
  - **[H/AN]** Oryx contaba un mínimo de **25 Zhitel** perdidos a septiembre de 2026 (dato recogido por un tercero). — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
  - **[TEST]** Un Zhitel fue destruido a ~55 km del frente. — [Euromaidan Press](https://euromaidanpress.com/?p=424218)
- **Krasukha-2/-4**:
  - **[SEC]** Son jammers de radar, no de enlaces de drones pequeños. Krasukha-2 trabaja en banda S y se le atribuyen ~250 km contra aviones AWACS. Krasukha-4 trabaja en bandas X y Ku, con ~300 km contra radares aerotransportados y satélites LEO. Ucrania capturó un Krasukha-4 cerca de Kiev en 2022. — [Wikipedia, Krasukha](https://en.wikipedia.org/wiki/Krasukha)
- **Leer-3 (RB-341V)**, carga de EW en el dron Orlan-10 contra redes celulares GSM:
  - **[OF]** El MoD afirmó en 2018 un alcance de **100 km**. — [Defense News, 16-nov-2018](https://www.defensenews.com/newsletters/unmanned-systems/2018/11/16/russian-drones-can-jam-cell-phones-60-miles-away/)
  - **[SEC]** Army Recognition habla de **30 km** y de ~2.000 abonados suprimidos. — [Army Recognition, 2022](https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2022/russian-troops-using-leer-3-able-to-jam-ukrainian-army-mobile-phone-signals-within-30-km)
  - **[AN]** US Army ODIN da un radio de denegación celular de **~6 km** (recogido por un tercero). — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
- **Tobol** (contra Starlink): **[SEC/OF]** un documento de inteligencia estadounidense filtrado (marzo de 2023) dice que Moscú llevaba meses probando Tobol contra Starlink en Ucrania, sin indicar si tuvo éxito. Es incierto si actúa sobre el enlace de subida o el de bajada. — [Stars and Stripes / Washington Post, 18-abr-2023](https://stripes.com/theaters/europe/2023-04-18/russia-secretive-weapon-spacex-starlink-ukraine-9841092.html)
- **Volnorez** (jammer en tanque o vehículo, contra FPV):
  - **[SEC]** La mayoría de las fuentes dan **900–2000 MHz**; Army Recognition dice 900–3000 MHz. — [Army Recognition](https://armyrecognition.com/focus-analysis-conflicts/army/defence-security-industry-technology/russia-unveils-portable-tank-mounted-drone-jammer-to-counter-ukrainian-attacks)
  - **[SEC]** Alcance de **600 m** según fuentes rusas. — [Al Jundi](https://aljundi.ae/?p=36308)
  - **[SEC]** **800 m**, con un cono muerto sobre el vehículo. — [Forbes vía online.ua](https://news.online.ua/en/russian-ew-systems-are-unable-to-cope-with-ukrainian-drones-forbes-873429)
  - **[SEC]** Más de 1 km. — [Unmanned Airspace](https://www.unmannedairspace.info/counter-uas-systems-and-policies/russia-deploys-tank-mounted-volnorez-jammers-in-ukraine/)
- **Otros sistemas tácticos rusos**:
  - **[FAB]** Kupol-PRO (portátil): "al menos 2,5 km". — [AO Avtomatika](https://www.ao-avtomatika.ru/en/catalog/products/kupol-pro-portable-anti-drone-system/)
  - **[OF/SEC]** Stupor (fusil): hasta **2 km**. — [Wikipedia, Stupor](https://en.wikipedia.org/wiki/Stupor_Anti-Drone_System)
  - **[FAB]** Repellent-Patrol: hasta **20 km**, según Rosoboronexport. — [The Defense Post, 23-feb-2021](https://thedefensepost.com/2021/02/23/russia-counter-drone-systems-idex-2021/amp/)
  - **[FAB/SEC]** Prototipo Tishina (2026): siete amplificadores de 50 W y 10 km de detección y supresión declarados, no demostrados de forma independiente (Armada International, citada por un tercero). — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
- **Escala de producción**: **[SEC]** hacia finales de 2024 Rusia producía ~**5.000 dispositivos C-UAS ligeros al mes**, según US Army Military Review a partir de catálogos del Estado Mayor ruso. — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)

**Sistemas ucranianos**
- **Bukovel / Bukovel-AD** (Proximus):
  - **[SEC/FAB]** Detección de 70–100 km, inhibición del enlace de datos a 16–20 km y bloqueo de GPS, GLONASS, Galileo y BeiDou. — [Wikipedia, Bukovel](https://en.wikipedia.org/wiki/Bukovel_(counter_unmanned_aircraft_system))
  - **[SEC]** Las listas de bandas publicadas se contradicen: de 30 MHz a 6 GHz en sub-bandas según una fuente rusa, 290/320–6000 MHz según otras hojas. — [TopWar (fuente rusa)](https://en.topwar.ru/217358-rjeb-kotoryj-protiv-nas-bukovel-ad.html)
- **Nota** (Tritel según Janes; RADION según Defence Blog): **[SEC/FAB]** detecta e inhibe UAV hasta **20 km** y bloquea la red celular a 1 km. — [Janes, 4-mar-2022](https://www.janes.com/defence-news/c4isr-command-tech/latest/ukraine-conflict-ukraines-electronic-warfare-systems-in-focus); [Defence Blog](https://defence-blog.com/army/radion-unveils-advanced-electronic-warfare-system-not)
- **Kvertus**:
  - **[FAB]** Mochila EW de **720–1050 MHz**, con una "cúpula de varios cientos de metros", 2 h de autonomía y un precio de US$7.000. — [Euromaidan Press, 17-may-2024](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/)
  - **[FAB]** Cúpula "AD Counter FPV" de **850–940 MHz**, con alcance efectivo de **300 m**. — [Kyiv Defenders](https://kyivdefenders.com.ua/en/projects/reb-kvertus/)
  - **[FAB]** Jammer autónomo "Mirage" de **0–6000 MHz** con hasta 20 h de autonomía, y plan de un "muro" EW de **1.500 km**. — [Euromaidan Press, 10-ago-2025](https://euromaidanpress.com/2025/08/10/when-the-beeping-starts-someones-drone-is-about-to-die/)
- **Piranha**: **[SEC]** el Piranha AVD 360, montado en vehículo, crea una cúpula de hasta **600 m**. Los sistemas mayores de Piranha Tech afirman cubrir entre 5 y 20 km. Esto se vio en un resumen de búsqueda de Rubryka; no pude confirmar qué artículo contiene cada dato. — [Rubryka](https://rubryka.com/en/?p=592409); [Rubryka](https://rubryka.com/en/?p=669794)
- **Otros jammers ucranianos**:
  - **[FAB]** Cúpula ANTIFPV (Obrii Miltek): **200 m**, US$1.400. — [Euromaidan Press, 17-may-2024](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/)
  - **[TEST]** Damba: de ~200 m a 2–3 km. — [Euromaidan Press, 10-ago-2025](https://euromaidanpress.com/2025/08/10/when-the-beeping-starts-someones-drone-is-about-to-die/)

### Inferences
- Para la simulación, los sistemas públicos se agrupan en tres clases de "huella espectral":
  - **jammers GNSS puros**, de tipo Pole-21: L1, L2 y L5;
  - **jammers de enlaces FPV portátiles o vehiculares**: 400 MHz–6 GHz en sub-bandas, típicamente 720–1050 MHz más 2,4 y 5,8 GHz;
  - **sistemas multi-propósito**, de tipo Zhitel, Bukovel o Veres-2: GNSS más control y video, o también celular y satélite.
- Krasukha no es pertinente para modelar la denegación contra drones pequeños: es un sistema anti-radar.
- La disparidad de alcances, por ejemplo 600 m frente a más de 1 km para el mismo Volnorez o 6 frente a 100 km para Leer-3, obliga a tratar el radio como un parámetro con intervalo y a correr análisis de sensibilidad, no a fijar un valor único.

### Gaps
- No encontré especificaciones públicas fiables de Shipovnik-Aero. Un fragmento secundario no verificado menciona ~25 s para identificar e interrumpir el enlace y posible toma de control, pero no pude confirmar la fuente. Tampoco encontré especificaciones de "trench jammers" rusos concretos más allá de Volnorez y Saniya.
- No hallé hojas técnicas oficiales de Nota ni de Piranha con bandas en MHz.
- No hay datos de potencia radiada para la mayoría de los sistemas tácticos, salvo Tishina (7×50 W, prototipo) y Pole-21 (20 W en prensa).

## 3. ¿Qué alcances efectivos tienen los inhibidores contra drones y cómo influyen el terreno y la altitud?

### Takeaway
Las fuentes abiertas apoyan una jerarquía de tres o cuatro niveles. Los jammers personales o de trinchera cubren unos 200–800 m. Los vehiculares y direccionales tácticos, ~1–3 km. Los sistemas EW "mayores", del orden de 10–25 km, desplegados a ~1 por cada 10 km de frente. Los sistemas GNSS estratégicos alcanzan cientos de kilómetros. La geometría (distancia dron–operador frente a dron–jammer), la línea de vista y la altitud determinan el efecto real tanto como el radio nominal.

### Cited Findings
**Jammers personales y de trinchera (cientos de metros)**
- **[FAB]** ANTIFPV: 200 m. Kvertus AD Counter FPV: 300 m. Mochila Kvertus: "varios cientos de metros". Piranha AVD 360: 600 m (dato de Rubryka, visto en resumen de búsqueda). — [Euromaidan Press, 2024](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/); [Kyiv Defenders](https://kyivdefenders.com.ua/en/projects/reb-kvertus/); [Rubryka](https://rubryka.com/en/?p=669794)
- **[SEC]** Volnorez: 600 m–1 km (ver sección 2). — [Al Jundi](https://aljundi.ae/?p=36308); [Unmanned Airspace](https://www.unmannedairspace.info/counter-uas-systems-and-policies/russia-deploys-tank-mounted-volnorez-jammers-in-ukraine/)

**Jammers tácticos y direccionales (~1–3 km)**
- **[TEST]** Veres-2: 1–2 km. Damba: 0,2–3 km. — [Euromaidan Press, 25-ago-2025](https://euromaidanpress.com/2025/08/25/ukraine-deploys-new-veres-2-anti-drone-system-that-jams-uavs-at-2km-range/); [Euromaidan Press, 10-ago-2025](https://euromaidanpress.com/2025/08/10/when-the-beeping-starts-someones-drone-is-about-to-die/)
- **[FAB]** Kupol-PRO: 2,5 km. Stupor: 2 km. — [AO Avtomatika](https://www.ao-avtomatika.ru/en/catalog/products/kupol-pro-portable-anti-drone-system/); [Wikipedia, Stupor](https://en.wikipedia.org/wiki/Stupor_Anti-Drone_System)

**Sistemas mayores (10–25 km) y su densidad**
- **[OF/FAB/SEC]** Zhitel: 25 km contra objetivos terrestres. Bukovel: 16–20 km. Nota: 20 km. Pole-21: ≥25 km. — [Wikipedia, Zhitel](https://en.wikipedia.org/wiki/R-330Zh_Zhitel); [Wikipedia, Bukovel](https://en.wikipedia.org/wiki/Bukovel_(counter_unmanned_aircraft_system)); [Janes, 2022](https://www.janes.com/defence-news/c4isr-command-tech/latest/ukraine-conflict-ukraines-electronic-warfare-systems-in-focus)
- **[AN]** RUSI (trabajo de campo de 2023) estima "al menos un sistema mayor cubriendo cada 10 km de frente". — [RUSI, "Meatgrinder", Watling & Reynolds, 19-may-2023](https://rusi.org/explore-our-research/publications/special-resources/meatgrinder-russian-tactics-second-year-its-invasion-ukraine)
- **[SEC/OF]** Según un manual C-UAS del MoD ruso de 2023 (citado por un tercero), las estaciones se sitúan **3–5 km detrás de la línea, ~10 km entre sí**, con sectores direccionales de **~90–120°** (R-934BMV, Palantin-U) y reubicación rápida tras emitir. — [Defence Ukraine, 10-sep-2026](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)

**Ubicuidad en la zona de combate**
- **[AN]** RUSI (febrero de 2025): "la interferencia de navegación es ubicua en toda la zona de combate"; la interferencia de frecuencias de mando "también está extendida"; y "la mayoría de los vehículos que entran en la zona de combate llevan jammers", dirigidos sobre todo a enlaces de mando y video para reducir la precisión terminal de los FPV. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)

**Geometría, terreno y altitud**
- **[SEC]** Los operadores FPV se acercan al frente porque la proximidad dron–operador reduce la relación jamming/señal (J/S). Con unos 500 m entre controlador y dron, la J/S cae fuertemente. El ejemplo es ilustrativo y procede de una fuente divulgativa. — [drone-warfare.com](https://drone-warfare.com/counter-uas/electronic-warfare/)
- **[TEST]** El enlace de radio se degrada cerca del suelo por obstáculos, y la falta de línea de vista por edificios o colinas puede impedir un ataque. Los operadores trabajan hasta a ~10 km. — [War on the Rocks, 26-jun-2025](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)
- **[TEST]** Una unidad ucraniana configura su jammer contra FPV que vuelan a ~150 m (ajuste "160"). — [Euromaidan Press, 10-ago-2025](https://euromaidanpress.com/2025/08/10/when-the-beeping-starts-someones-drone-is-about-to-die/)
- **[SEC]** Las antenas del Volnorez dejan una "zona muerta" en el cono superior. — [Forbes vía online.ua](https://news.online.ua/en/russian-ew-systems-are-unable-to-cope-with-ukrainian-drones-forbes-873429)
- **[H]** Horizonte radioeléctrico: los FPV baratos pierden el enlace de video más allá del horizonte por la curvatura terrestre. Hay módulos de autoapuntado que inician el ataque a ~3 km del objetivo y 800 m de altitud, donde recuperan línea de vista. — [Kyiv Independent (K. Post), 1-ago-2025](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)
- **[H]** Un monitor GNSS a nivel del mar en Gdynia, a ~90 km de Kaliningrado, no debería recibir esa interferencia según el modelo de horizonte 4/3 de la Tierra, pero la recibe a veces por inversiones atmosféricas. En cambio, aeronaves hasta ~36.000 ft sí resultan afectadas. Es decir, la altitud amplía la exposición a jammers lejanos. — [Lo et al., ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf); [Spire, oct-2024](https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/)
- **[TEST]** Los drones de radio provistos por el Estado a menudo no operan más allá de 5–8 km de la línea de contacto. — [The War Zone (H. Altman), 28-may-2025](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)

### Inferences
- **Parametrización sugerida**, con fundamento público y para usar con barrido de sensibilidad:
  - **nivel 1**, jammer de trinchera o personal: R ≈ 0,2–0,8 km, omnidireccional, bandas de control y video FPV;
  - **nivel 2**, vehicular o direccional: R ≈ 1–3 km, sector de 90–120° o 360°, control, video y GNSS L1/L2/L5;
  - **nivel 3**, sistema mayor: R ≈ 10–25 km, separados ~10 km y a 3–5 km tras la línea, GNSS más enlaces;
  - **nivel 4**, GNSS estratégico: R ≈ 100–250 km (ver sección 4).
- La altitud tiene un efecto doble. Volar alto mejora la línea de vista con el operador, pero expone el receptor GNSS y el enlace a jammers más lejanos. Volar bajo reduce la exposición a jammers lejanos, pero degrada el enlace con el operador por obstáculos y horizonte. Un modelo físico simple (pérdida en espacio libre más horizonte radioeléctrico, J/S en función de las distancias dron–jammer y dron–operador) captura mejor este efecto que un disco binario.
- Es más realista modelar la zona de jamming como dependiente de la relación J/S que como un círculo fijo. El mismo jammer "alcanza" más lejos contra un dron cuyo operador está lejos y menos contra uno con el operador o el repetidor cerca.

### Gaps
- No hay curvas públicas de alcance frente a altitud o terreno para jammers concretos. Los datos son anecdóticos.
- No encontré mediciones independientes de potencia ni de alcance de jammers de trinchera en campo.

## 4. Interferencia y spoofing GNSS: escala, efectos sobre drones e incidentes documentados

### Takeaway
La interferencia GNSS es ubicua en el frente y se ha extendido a escala regional. Desde Kaliningrado, el jamming medido en ADS-B cubre un radio de ~250 km y afecta L1 y L5 en todas las constelaciones; desde finales de 2024 se combina con spoofing ("jam then spoof"). Contra drones y municiones guiadas, la interferencia GNSS degradó fuertemente la precisión (Excalibur, HIMARS), y en respuesta se adoptaron antenas CRPA en drones de largo alcance como el Shahed.

### Cited Findings
**Frente ucraniano y municiones**
- **[AN]** "La interferencia de navegación es ubicua en toda la zona de combate" (febrero de 2025). Los misiles de crucero rusos se rutean para evitar las defensas EW antes de la fase terminal, y el Kh-101 mejoró su seguimiento visual del terreno para evitar la EW en esa fase. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[SEC]** Excalibur: evaluaciones ucranianas confidenciales muestran que la tasa de acierto cayó de más del 50% a menos del 10% en varios meses, y atribuyen la caída al jamming de GPS ruso. — [Washington Post vía Stars and Stripes, 24-may-2024](https://www.stripes.com/theaters/europe/2024-05-24/russian-jamming-high-tech-weapons-ukraine-13964032.html)
- **[SEC]** Otra cobertura de un informe clasificado da una caída de 55% (enero de 2023) a 6% (agosto de 2023), con unos 3.000 disparos. — [Business Insider](https://businessinsider.nl/the-us-gave-up-sending-ukraine-excalibur-guided-artillery-shells-costing-100000-because-they-rarely-hit-their-target-report-says/)
- **[TEST]** Un directivo de Shield AI afirma que la precisión de los cohetes HIMARS bajo EW rusa cayó de ~90% a ~20%. — [Kyiv Independent, 1-ago-2025](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)

**Spoofing documentado contra drones**
- **[SEC]** Ucrania desvió más de 100 Shahed hacia Rusia y Bielorrusia en noviembre de 2024 mediante EW (dato de Le Monde). — [The Defense Post, 5-dic-2024](https://thedefensepost.com/2024/12/05/ukraine-spoofs-shahed-drones/amp/)
- **[AN]** ISW informa que la EW ucraniana hace que los Shahed cambien de rumbo y caigan sin combustible. La Fuerza Aérea ucraniana reporta a diario drones "perdidos localmente" o "desaparecidos del radar" por EW. — [Euromaidan Press (ISW), 3-dic-2024](https://euromaidanpress.com/2024/12/03/isw-ukrainian-ew-tech-increasingly-grounds-shahed-drones-complicating-russian-airstrikes/)
- **[H]** Patrones de spoofing en Rusia (marzo de 2025): círculos, semicírculos y endecágonos de **2–11 km de diámetro**, recorridos a **~200 km/h**, comparable al crucero del Shahed-136 (185 km/h). Los autores infieren que están dirigidos contra misiles de crucero o drones de ala fija, no contra drones de consumo. — [Lo et al., Stanford, ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)
- **[H]** Spoofing sobre el mar Negro y los Balcanes (por ejemplo, el 6-dic-2023): las posiciones falsas se concentran en el aeropuerto de Belbek, en Crimea. En Smolensk se observan trayectorias circulares falsas. — [Inside GNSS (Liu, Lo et al., Stanford), 26-mar-2024](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)

**Contramedida rusa: antenas CRPA**
- **[OF/H]** Inteligencia ucraniana (HUR, febrero de 2025) informó que Rusia usa antenas CRPA "Kometa" de 12 canales junto a las Kometa-M de 8 canales. — [Ukrainska Pravda, 18-feb-2025](https://www.pravda.com.ua/eng/news/2025/02/18/7498968)
- **[OF/H]** Después aparecieron antenas chinas de 16 elementos en Shahed. Un portavoz de la Fuerza Aérea dijo: "si antes eran 8 canales, ahora son 16". — [Business Insider](https://www.businessinsider.nl/russia-is-leveling-up-its-shahed-drones-with-new-chinese-antennae-to-defeat-kyivs-jammers-ukrainians-say); [Militarnyi](https://militarnyi.com/en/news/new-chinese-crpa-antenna-found-on-russian-shahed/)

**Escala regional: Báltico y Kaliningrado**
- **[H]** El jamming desde Kaliningrado comenzó de forma ocasional hacia 2022–23 y creció en potencia y extensión. El 5-mar-2025 parecía omnidireccional y se extendía unos **250 km de radio**. El spoofing regular empezó hacia el **9-nov-2024**. — [Lo et al., ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)
- **[H]** La interferencia en el Báltico aumentó desde el 25-dic-2023, concentrada sobre todo entre las 00:00–05:00 y las 21:00–24:00 UTC, y algunos días casi todo el día. La elipse estimada del emisor incluye la región de Kaliningrado. — [Inside GNSS, 26-mar-2024](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
- **[H]** GPSPatron y la Universidad Marítima de Gdynia midieron:
  - en tierra, en Gdańsk: más de 84 h de interferencia en ~9 meses, con eventos de más de 7 h e indicios de fuentes móviles;
  - a bordo, entre junio y octubre de 2025: todos los eventos combinaban jamming multiconstelación y spoofing de L1; en una ventana de 48 h hubo 30 h activas; la señal era hasta 15 dB más fuerte mar adentro.
  — [Inside GNSS, 8-dic-2025](https://insidegnss.com/kaliningrad-jamming-and-spoofing-up-close/)
- **[H]** Spire detecta la interferencia combinando RF desde satélites LEO con datos ADS-B. En octubre de 2024 registró disrupciones de hasta 7 h en las cuatro constelaciones y errores de posición de más de 30 m, y atribuyó una fuente probable a un jammer móvil embarcado. — [Spire, Parte 1](https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/)
- **[SEC]** Un informe báltico-nórdico registra que **122.607 vuelos** de 365 aerolíneas sufrieron interferencia GNSS entre enero y abril de 2025: ~27,4% de los vuelos en abril y más del 42% en algunas áreas. — [EU Today](https://eutoday.net/russian-gnss-interference-disrupted-123000-flights/)
- **[OF/H]** Polonia (Instituto Nacional de Telecomunicaciones), en 2026: disrupción en **todas las bandas GNSS** el ~70% de los días de mayo y junio, y el 63% de los días del 1 al 19 de agosto. Pomerania sumó ~90 h en julio, en L1. Los drones recreativos y comerciales pierden posición fiable. — [Euronews, 25-ago-2026](https://www.euronews.com/my-europe/2026/08/25/phones-drones-and-ships-running-blind-as-gps-malfunctions-across-poland)
- **[OF]** Lituania (2026): las antenas de spoofing en Kaliningrado pasaron de unas pocas a "varias decenas", con un alcance de spoofing de hasta 450 km según esa afirmación oficial. — [Euronews, 25-ago-2026](https://www.euronews.com/my-europe/2026/08/25/phones-drones-and-ships-running-blind-as-gps-malfunctions-across-poland)

### Inferences
- Para drones, la interferencia GNSS se manifiesta de dos formas que la simulación debería distinguir:
  - **jamming**: pérdida de solución GNSS, con caída de C/N0 y del indicador de integridad (NIC); el dron pasa a navegación inercial o deriva;
  - **spoofing**: saltos de posición o trayectorias falsas coherentes, con C/N0 normal o alto; es más peligroso porque no siempre se detecta.
- La secuencia "jam then spoof" observada en Kaliningrado sugiere que la detección de jamming puede ser un precursor útil del spoofing: un dron que detecta jamming debería desconfiar del GNSS durante un tiempo tras recuperarlo.
- Las zonas GNSS son mucho mayores (de decenas a cientos de km) que las de jamming de enlaces (de cientos de m a pocos km). Rodear físicamente una zona GNSS es a menudo inviable, y la respuesta habitual es la robustez a bordo (CRPA, navegación inercial o visual). En cambio, para jammers de enlace tácticos, la evasión por ruta sí es plausible.

### Gaps
- No encontré mediciones públicas sistemáticas del jamming GNSS en la línea del frente ucraniana (radios o potencias), solo afirmaciones cualitativas (RUSI) y datos indirectos (ADS-B, que casi no tiene cobertura sobre el frente porque allí no vuelan aviones civiles).
- No hallé estadísticas mensuales oficiales de drones "perdidos localmente" por EW. Habría que agregar los partes diarios de la Fuerza Aérea ucraniana.
- La cifra lituana de 450 km es una afirmación oficial sin metodología publicada.

## 5. ¿Cómo detectan el jamming un dron o su operador, qué detectores se usan y qué dice la literatura académica sobre tiempos y precisión de detección?

### Takeaway
En campo, la detección temprana de EW se basa en análisis de espectro antes del vuelo, en detectores RF portátiles (sobre todo de video analógico, con techo de ~6 GHz) y en síntomas de enlace (pérdida de video o control, modo RXLOSS) y de GNSS (caída de C/N0 y de la ganancia automática AGC, saltos de posición). La literatura académica reporta detectores de jamming para UAV con 92–99,99% de exactitud en laboratorio o simulación y latencias mínimas de ~100 ms, pero sin validación pública en el frente.

### Cited Findings
**Práctica operativa**
- **[SEC/OF]** El manual ruso pide analizar la situación radioelectrónica con analizadores de espectro antes de cada salida para detectar ataque electrónico en curso y elegir frecuencias. — [Armada International, 14-mar-2024](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/)
- **[AN]** RUSI: "rastrear las defensas EW es un requisito absoluto para operar UAV con éxito, porque afecta al plan de vuelo y al momento de lanzamiento". La radiogoniometría se usa para orientar las órbitas de los UAV. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[AN]** Los Geran-2 y Gerbera rusos se lanzan en oleadas, y los datos que devuelven los primeros UAV informan la ruta de los siguientes. El valor de estos ataques está tanto en mapear la EW y la defensa aérea como en el daño causado. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[SEC]** Un video de un FPV ucraniano con guiado terminal muestra entradas repetidas en el modo **RXLOSS** (pérdida de señal) antes de completar el ataque. Es la manifestación típica del jamming en el enlace. — [Euromaidan Press, 29-may-2025](https://euromaidanpress.com/2025/05/29/new-footage-shows-ukraines-fpv-drone-bypasses-jamming-in-autonomous-strike/)
- **[TEST]** El jamming propio impedía despegar, a veces durante horas, o derribaba drones; el ~3% de las salidas fallaron por jamming amigo sin aviso. — [War on the Rocks, 26-jun-2025](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)

**Detectores RF portátiles en unidades**
- **[OF/SEC]** Chuika 3.0 (BlueBird): intercepta el video analógico del FPV y muestra hasta 3 fuentes y sus frecuencias, según Brave1. Prensa: alcance de hasta ~4 km; barrido de 900–1680, 3060–3700 y 4990–6000 MHz según United24, mientras la página del fabricante da 900–1800, 2870–4080 y 4860–6060 MHz. — [Ukrainska Pravda, 28-may-2025](https://www.pravda.com.ua/eng/news/2025/05/28/7514494); [United24](https://united24media.com/es/war-in-ukraine/con-esta-tecnologia-ucraniana-podras-espiar-drones-rusos-15687); [BlueBird](https://blue-bird.tech/en/products/bluebirds-chuyka-3-0-electronic-intelligence-device-5-8-ghz-3-3-ghz-1-2-ghz)
- **[SEC]** Tsukorok: detector pasivo de enlaces de control en **865–885, 902–928 y 970–1020 MHz**, con módulo opcional de 2,4 GHz y alcance de 6–16 km según terreno. Otras fuentes dicen que detecta alas de reconocimiento y no FPV. — [Xataka Brasil](https://www.xataka.com.br/diversos/este-pequeno-dispositivo-e-um-aliado-poderoso-da-ucrania-os-drones-russos)
- **[FAB]** Pluton (Infozakhyst): detecta drones a hasta 70 km y puede disparar contramedidas, pero no inhibe. — [Euromaidan Press, 17-may-2024](https://euromaidanpress.com/2024/05/17/the-ew-backpack-revolution-how-ukrainian-portable-tech-jams-russian-drones/)
- **[H/TEST]** Limitación: muchos detectores portátiles tienen techo de ~6 GHz, lo que deja ciegos a los videos de 6–7,2 GHz. — [Militarnyi, 26-jul-2026](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/)

**Indicadores GNSS (C/N0 y AGC)**
- **[H]** En general, el jamming reduce C/N0 y la ganancia AGC; el spoofing tiende a elevar C/N0 y reducir la AGC. — [Android Developers, "Detect GNSS jamming and spoofing"](https://developer.android.com/develop/sensors-and-location/sensors/gnss-spoof-jam)
- **[H]** Advertencia: C/N0 y AGC indican perturbación, pero no prueban por sí solos que haya un jammer. — [Virginia Tech, análisis tiempo-frecuencia de jamming en autopistas](https://www.aoe.vt.edu/content/dam/aoe_vt_edu/people/faculty/joerger/publications/Time-Frequency%20Analysis%20of%20GNSS%20Jamming%20Events%20Detected%20on%20US%20Highways_v3.pdf)
- **[H]** En ADS-B, un NIC menor que 7 indica anomalía, probablemente interferencia (NIC 7 equivale a un radio de contención de 370,4 m). — [Inside GNSS, 26-mar-2024](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
- **[H]** Lo et al. observaron con un receptor u-blox la AGC y el C/N0 máximo en L1 y L5 durante interferencia procedente de Kaliningrado: degradación de C/N0 "algo, pero no severa" a ~90 km. — [Lo et al., ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)

**Literatura académica: detectores y tiempos**
- **[H]** SINTEF propone un detector de jamming con filtro de Kalman sobre el C/N0, integrado con navegación inercial asistida, para UAV, y lo prueba con datos de un evento abierto de jamming. — [SINTEF](https://sintef.no/en/publications/publication/2279833)
- **[H]** Una tesis de la Universidad de Vaasa (2025) aplica XGBoost e Isolation Forest sobre características de la AGC, con datos de un ensayo controlado de jamming en Noruega, y concluye que los umbrales fijos fallan en escenarios dinámicos. — [Univ. Vaasa, 2025](https://osuva.uwasa.fi/bitstream/10024/19843/2/Uwasa_2025_Ashika_Ruwanthi.pdf)
- **[H]** Detección colaborativa (crowdsourcing y lógica difusa): tiempo medio de detección de ~10 s y falsos positivos de ~1–2%. No es específico de UAV. — [Sciforum](https://sciforum.net/paper/view/25272)
- **[H]** Li et al., IEEE Access vol. 10 (2022), receptores OFDM para UAV con datos SDR y cuatro tipos de jamming (barrage, protocol-aware, single-tone, pulsos sucesivos):
  - CNN sobre espectrogramas: **99,79%** de exactitud y **0,03%** de falsa alarma;
  - modelo de características (SNR, umbral de energía, parámetros OFDM): **92,20%** y **1,35%**.
  — [Michigan Tech Digital Commons](https://digitalcommons.mtu.edu/michigantech-p/15739)
- **[H]** Viana et al., VTC 2022-Spring, con datos sintéticos simulados:
  - un método estadístico de series temporales detecta el **84,38%** de los ataques con el jammer a 30 m;
  - una red profunda logra ~**99,99%** con potencias altas y jammer a corta distancia (menos de ~200 m).
  — [UCC Research Profiles](https://research.ucc.ie/en/publications/two-methods-for-jamming-identification-in-uav-networks-using-new/); [arXiv 2203.11373](https://arxiv.org/abs/2203.11373v1)
- **[H]** Viana et al. (arXiv, 2022) detectan ataques sobre enlaces 5G de UAV usando RSSI y SINR: el tiempo mínimo tras el inicio del ataque es de **100 ms**, la potencia mínima detectable de 2 dBm y detectan atacantes móviles a 500 m. Señalan que PDR y RSSI, los indicadores clásicos, solo detectan el ataque tras una pérdida considerable de información. — [arXiv 2207.10810](https://arxiv.org/abs/2207.10810)
- **[H]** Greco et al. (Northeastern) proponen un detector distribuido a bordo para redes de drones con throughput, PDR y RSSI como características. El desempeño mejora con ventanas de muestreo de paquetes más cortas. — [Greco et al., 2021](https://www.ece.neu.edu/fac-ece/basagni/papers/GrecoPF21.pdf)
- **[H]** Una comparación de cinco arquitecturas de deep learning da un RNN con ~93% de exactitud. — [Taylor's University](https://expert.taylors.edu.my/file/rems/publication/109566_14414_1.pdf)
- **[H]** Metadatos de la base teórica del proyecto: "Cross-layer UAV network routing protocol for spectrum denial environments", de Siyue Zheng, Xiaojun Zhu, Zhengrui Qin y Chao Dong, *Ad Hoc Networks* vol. 167, artículo 103702. Crossref lo registra como publicado en febrero de 2025; la versión en línea es probablemente de 2024. — [Crossref API](https://api.crossref.org/works/10.1016/j.adhoc.2024.103702)

### Inferences
- **Latencia de detección para la simulación**: con fundamento académico, el rango es de ~0,1 s (RSSI/SINR con deep learning, simulación) a ~10 s (detección colaborativa de GNSS). Detectar mediante PDR o pérdida de paquetes es más lento porque requiere que la pérdida ya haya ocurrido. Un parámetro razonable es T_detect ∈ [0,1; 10] s, con exactitud de 85–99% y falsas alarmas de 0,03–2%, más un término de degradación con la distancia y la J/S.
- **Correspondencia con CLUN-LSR**: el aviso temprano que el proyecto quiere propagar tiene precedente operativo real. RUSI describe oleadas de Geran cuyos primeros drones informan la ruta de los siguientes, y misiles que se rutean evitando las defensas EW. Esto apoya conceptualmente el uso de la detección de jamming como señal para que otros UAV cambien su ruta física.
- El dron que detecta primero suele ser el que ya está dentro o en el borde de la zona. Su valor para el enjambre depende de poder transmitir el aviso, por ejemplo por otra banda o a través de relés, antes de perder el enlace. Conviene modelar una probabilidad de que el aviso se difunda en función de la intensidad del jamming.

### Gaps
- No encontré reportes públicos fiables de detectores de espectro montados a bordo de drones ucranianos o rusos para alertar de EW en vuelo. Los detectores documentados son portátiles, de tierra y de infantería.
- No hay datos públicos del frente sobre con cuántos segundos de antelación un operador percibe el jamming antes de perder el dron.
- No pude acceder al texto completo de CLUN-LSR para contrastar su mecanismo de detección con estas cifras.

## 6. Contramedidas (salto de frecuencia, radios multibanda, fibra óptica, autonomía terminal, navegación inercial o visual, relés, CRPA) y cómo cambian el valor de "rutear alrededor del jamming"

### Takeaway
Ninguna contramedida domina por sí sola. La fibra óptica, adoptada por Rusia desde la primavera de 2024 y luego por Ucrania, elimina la vulnerabilidad RF en 10–25 km o más, pero con penalizaciones de carga, maniobra y enredo. La autonomía terminal neutraliza los jammers de los últimos 400 m–3 km. Las CRPA y la navegación inercial o visual protegen los drones de largo alcance frente al GNSS. Los relés y "nodrizas" amplían el alcance de radio más allá del horizonte. El ruteo evasivo conserva valor sobre todo para la flota de radio (aún mayoritaria) y frente a jammers tácticos de radio limitado.

### Cited Findings
**Salto de frecuencia y radios ágiles**
- **[TEST/SEC]** Hay drones rusos que cambian de frecuencia de forma dinámica y usan amplificadores (agosto de 2025). — [Ukrainska Pravda, 8-ago-2025 (resumen de búsqueda)](https://www.pravda.com.ua/eng/articles/2025/08/08/7525279/)
- **[H]** El Boomerang ruso de 2026 tiene recepción por diversidad y antenas reajustables en campo para cambiar de banda. — [Militarnyi, 26-jul-2026](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/)

**Fibra óptica**
- **[AN]** RUSI (febrero de 2025): con carretes de cable los FPV son "inmunes a la disrupción electrónica". Los operadores ucranianos citan como desventajas peores prestaciones de vuelo, un alcance limitado de ~10 km y riesgo de enredo, pero la fibra permite penetrar zonas de jamming intenso de GPS y radio. Ucrania aún no la usaba ampliamente, y sus ataques dependían de huecos en la protección electrónica, abiertos con artillería o con pausas planificadas del jamming propio. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[TEST]** The War Zone, mayo de 2025, Azov:
  - Rusia empezó a usar FPV de fibra en la primavera de 2024;
  - Ucrania los usa con eficacia hasta 15 km y hay casos de 20 km; Rusia ya llega a 30 km;
  - son menos del 5% de la flota del batallón;
  - un dron de fibra plenamente funcional tiene ~50% de probabilidad de acertar, frente a ~30% de probabilidad de llegar para los de radio;
  - cuestan ~US$1.200 para 10 km, con listas de espera de 2–3 meses.
  — [The War Zone, 28-may-2025](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)
- **[TEST/H]** Hay unos 20 km prácticos con fibra y carretes de hasta 40 km. — [Kyiv Independent, 1-ago-2025](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)
- **[OF]** El comandante en jefe Syrskyi dijo en junio de 2025 que Rusia tenía ventaja en cantidad y alcance de drones de fibra. — [Ukrainska Pravda, 22-jun-2025](https://www.pravda.com.ua/eng/news/2025/06/22/7518207)
- **[OF]** Brave1 probó FPV de fibra de 20 km en abril de 2025. — [Defence Connect](https://www.defenceconnect.com.au/joint-capabilities/15814-ukrainian-military-begins-testing-on-20km-fibre-optic-fpv-drones)
- **[SEC]** Los alcances de fibra rusos eran de 15–25 km a principios de 2026. — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
- **[FAB]** Ptashka afirma alcanzar 50 km (video de diciembre de 2025). — [Euromaidan Press](https://euromaidanpress.com/?p=383666)
- **[TEST]** Un modelo de fibra de 10 km cuesta ~2 veces lo que uno de radio de alcance similar. — [War on the Rocks, 26-jun-2025](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)

**Autonomía y guiado terminal**
- **[AN]** Los FPV incorporan guiado terminal autónomo, lo que también los hace inmunes a la disrupción en la fase final. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[SEC/FAB]** El módulo TFL-1 (~US$100) da guiado autónomo en los últimos **400–500 m** bajo jamming intenso. — [The Defense Post, 19-nov-2025](https://gecici.thedefensepost.com/?p=117258)
- **[FAB]** Los módulos de autoapuntado de WarBirds permiten iniciar el ataque desde ~3 km y 800 m de altitud sin más intervención del operador. — [Kyiv Independent, 1-ago-2025](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)
- **[H]** El Boomerang ruso incorporó guiado terminal a principios de 2025, lo que reduce mucho el efecto de la EW portátil. — [Militarnyi, 26-jul-2026](https://militarnyi.com/en/news/russian-boomerang-fpv-drones-shifted-to-frequencies-unavailable-to-most-detectors/)
- **[AN/SEC]** El guiado de última milla alcanzó escala "masiva" en verano de 2025, pero con despliegue desigual. — [New Geopolitics, 28-dic-2025](https://www.newgeopolitics.org/2025/12/28/ukraines-deftech-at-the-end-of-2025-from-drone-mass-to-systems-warfare/)

**GNSS robusto (CRPA y navegación visual)**
- **[OF/H]** Los Shahed han pasado de CRPA de 8 elementos a 12 (Kometa) y 16 (china). — [Ukrainska Pravda, 18-feb-2025](https://www.pravda.com.ua/eng/news/2025/02/18/7498968); [Militarnyi](https://militarnyi.com/en/news/new-chinese-crpa-antenna-found-on-russian-shahed/)
- **[AN]** El Kh-101 mejoró su seguimiento visual del terreno en la fase terminal. — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)

**Relés, repetidores y "nodrizas"**
- **[FAB]** El repetidor Vidlunnia afirma cubrir 30 km a 500 m de altitud durante 60 min. — [Rubryka, 13-jun-2024](https://rubryka.com/en/2024/06/13/retranslyator-vidlunnya-dlya-droniv/)
- **[OF]** Brave1 probó repetidores de más de 30 empresas en enero de 2024. — [Militarnyi](https://militarnyi.com/en/news/brave1-tests-tools-to-increase-drone-communication-range/)
- **[SEC]** Drones "reina" de 2024 retransmiten la señal a ~10 FPV. — [DroneDJ, 28-ene-2024](https://dronedj.com/2024/01/28/video-describes-ukraine-queen-drones-leading-fpv-swarm-attacks/)
- **[TEST/FAB]** El guiado por radio con repetidores llega a ~30 km, y la nodriza Puhach de WarBirds suelta cuadricópteros a 37 km. — [Kyiv Independent, 1-ago-2025](https://kyivindependent.com/new-ukrainian-strike-drones-are-chasing-russian-armor-and-ew-past-the-radio-horizon/)
- **[AN]** Las antenas reales y señuelo se colocan en puntos altos para dificultar la localización por inteligencia de comunicaciones. — [Armada International, 2024](https://www.armadainternational.com/2024/03/russian-fpv-drone-manual-milcom/)

**Contra-contramedidas**
- **[TEST]** Hay drones rusos que cortan fibras ucranianas con las hélices. — [The War Zone, 28-may-2025](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)
- **[SEC]** El sistema ruso Lesochek permite marcar como "prohibidas" (no inhibir) las frecuencias amigas. — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)
- **[FAB/SEC]** Rusia afirma producción en masa del sistema Volna Kupol Garant contra terminales Starlink (septiembre de 2026), algo no verificado; analistas de The Insider lo consideran exagerado. — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)

### Inferences
- **Valor de rutear alrededor del jamming, por tipo de dron**:
  - **(a) FPV o UAV de radio sin autonomía**, la mayoría en 2024–2025: alto valor, porque evitar las zonas de jammers de nivel 1 y 2 o pasar por corredores con línea de vista hacia un relé es la principal defensa;
  - **(b) drones con guiado terminal**: el jamming de los últimos cientos de metros pierde importancia, y el valor del ruteo se traslada al tramo de crucero (llegar al punto de enganche);
  - **(c) fibra óptica**: el ruteo por jamming es irrelevante, y las restricciones pasan a ser físicas (obstáculos para el cable, longitud del carrete);
  - **(d) largo alcance con CRPA o navegación inercial o visual**: el ruteo evita sobre todo defensas EW y antiaéreas fuertes, como hacen los misiles rusos según RUSI.
- **Implicación para CLUN-LSR adaptado**: la red de UAV que se simula, con enlaces RF entre UAV, es el caso en que el aviso temprano y el cambio de ruta física tienen máximo valor. Conviene parametrizar la fracción de UAV "inmunes" (fibra o autónomos) para mostrar cómo decrece el beneficio del protocolo al aumentar esa fracción.
- Los relés y nodrizas convierten el problema en uno de ruteo multi-salto con nodos aéreos expuestos. Un relé en altura amplía la cobertura (más línea de vista), pero también su exposición a jammers lejanos. Es un compromiso que un protocolo de ruteo consciente de la denegación espectral puede explotar.

### Gaps
- No encontré cifras públicas fiables de la proporción de fibra óptica frente a radio en el total de ataques FPV de 2025–2026, más allá de testimonios de unidad (por ejemplo, menos del 5% en Azov en mayo de 2025).
- No hay datos públicos de que haya redes malladas (mesh) operativas en el frente con protocolos de ruteo específicos. Lo documentado son repetidores y nodrizas punto a punto o punto a multipunto.
- No encontré información verificable sobre navegación visual o por correlación de terreno en drones tácticos pequeños.

## 7. ¿Existen conjuntos de datos o mapas abiertos de jamming o actividad EW?

### Takeaway
Hay buenas fuentes abiertas para la interferencia GNSS regional: GPSJam, el mapa de Flightradar24 y rfi.stanford.edu, todas inferidas del indicador NIC en ADS-B, más monitores terrestres (GPSPatron/GMU, Instituto de Telecomunicaciones de Polonia) y conjuntos de ensayo (Jammertest, Noruega). Para el jamming de enlaces de drones en el frente prácticamente no existen datos abiertos. Los conjuntos de datos académicos de detección de jamming en UAV son de laboratorio o sintéticos.

### Cited Findings
- **[H]** **Flightradar24 GPS jamming map**:
  - no mide RF directamente, sino que infiere interferencia cuando muchos vuelos de una zona reportan NIC bajo;
  - solo usa áreas con suficientes vuelos y receptores;
  - tiene resolución de 6 o 24 h y se actualiza cada 6 h;
  - no distingue jamming de spoofing.
  — [Flightradar24](https://www.flightradar24.com/data/gps-jamming); [Soporte FR24](https://support.fr24.com/support/solutions/articles/3000125401-gps-jamming-what-is-it-and-where-can-i-see-the-updated-map)
- **[H]** **GPSJam** (John Wiseman): usa ADS-B de aeronaves en todo el mundo, con el campo de integridad como indicador. — [Gigazine, 22-mar-2024](https://wbgsv0a.gigazine.net/gsc_news/en/20240322-gps-jam)
- **[H]** Advertencia metodológica: estos mapas usan NIC y NACp, y no representan las condiciones RF a nivel del suelo ni una cobertura completa de amenazas. — [Inside GNSS, "ADS-B Data Analysis for GNSS Interference Mapping"](https://insidegnss.com/?p=197872)
- **[H]** **rfi.stanford.edu** (Stanford GPS Lab): detecta y marca eventos de spoofing desde ADS-B. Es solo GPS L1, con huecos de cobertura, y complementa con AIS de barcos y monitores de bajo costo. — [Lo et al., ION ITM 2026](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Lo_ION_ITM_2026_Observations_of_Spoofing.pdf)
- **[H]** El artículo de la ION *Navigation* "Locating GNSS Interference Sources using ADS-B with Non-linear Least Squares" estima la ubicación y la potencia del jammer a partir del NIC. — [NAVIGATION (ION)](https://navi.ion.org/content/72/3/navi.716)
- **[H]** Hay monitoreo comercial y académico: Spire (RF desde LEO más ADS-B) y GPSPatron con la Universidad Marítima de Gdynia (sensores terrestres y embarcados). — [Spire](https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/); [Inside GNSS, 8-dic-2025](https://insidegnss.com/kaliningrad-jamming-and-spoofing-up-close/)
- **[OF]** El Instituto Nacional de Telecomunicaciones de Polonia publica estadísticas de días con disrupción GNSS por banda. — [Euronews, 25-ago-2026](https://www.euronews.com/my-europe/2026/08/25/phones-drones-and-ships-running-blind-as-gps-malfunctions-across-poland)
- **[H]** Jammertest (Andøya, Noruega) es un ensayo abierto con un catálogo de jammers por banda y modulación, y sus datos se reutilizan en investigación. — [GPSPatron, "Jammertest 2022 Jammer overview"](https://gpspatron.com/wp-content/uploads/2022/10/Jammertest-2022-Jammer-overview-%E2%80%93-frequency-bands-and-modulations.pdf); [Univ. Vaasa, 2025](https://osuva.uwasa.fi/bitstream/10024/19843/2/Uwasa_2025_Ashika_Ruwanthi.pdf)
- **[H]** Conjuntos de datos académicos de jamming en UAV:
  - Li et al. (IEEE Access, 2022) publicaron sus conjuntos de datos y modelos (proyecto NSF 2006662);
  - Viana et al. (VTC 2022) crearon un conjunto sintético.
  — [CPS-VO](https://archive.cps-vo.org/node/86514); [arXiv 2203.11373](https://arxiv.org/abs/2203.11373v1)
- **[H/AN]** Oryx es una lista de pérdidas verificadas con foto o video. A septiembre de 2026 registraba ≥107 sistemas EW rusos (25 Zhitel, 22 de la familia Borisoglebsk, 10 Sinitsa, 1 Krasukha-4). Sirve para estimar la presencia de sistemas, no su actividad. — [Defence Ukraine](https://www.defenceukraine.com/en/insights/russian-ew-architecture-ukraine-2026/)

### Inferences
- Para la simulación, GPSJam, Flightradar24 y rfi.stanford.edu permiten calibrar el tamaño y la variabilidad temporal de zonas GNSS reales: radios de unos 250 km, intermitencia con picos nocturnos y duraciones de horas. No sirven para el jamming de enlaces de drones.
- Los conjuntos de datos de Li et al. y Viana et al. pueden servir para entrenar o validar un detector de jamming en la capa física de los UAV simulados.

### Gaps
- No encontré "SkAI" ni ningún mapa abierto de actividad EW contra drones en el frente ucraniano. Tampoco informes ucranianos abiertos de espectro.
- ADS-B casi no cubre la zona de combate (no hay vuelos civiles), por lo que los mapas abiertos subrepresentan el frente.

## 8. ¿Qué proporción de las pérdidas de drones se atribuye a la EW?

### Takeaway
Las cifras públicas son heterogéneas y no comparables entre sí. RUSI estimó ~10.000 drones ucranianos perdidos al mes en 2023, con la EW como causa principal, una cifra luego cuestionada como posiblemente sobreestimada. Un registro de primera mano de 2024–2025 atribuye el 31% de las salidas fallidas a la EW enemiga. RUSI (2025) da un 60–80% de FPV que no llegan al objetivo por todas las causas.

### Cited Findings
- **[AN]** RUSI (mayo de 2023): "las pérdidas de UAV ucranianos se mantienen en aproximadamente 10.000 al mes". La EW rusa sigue siendo potente, con ~1 sistema mayor cada 10 km, y está "fuertemente orientada a derrotar UAV". — [RUSI, "Meatgrinder", 19-may-2023](https://rusi.org/explore-our-research/publications/special-resources/meatgrinder-russian-tactics-second-year-its-invasion-ukraine)
- **[AN]** La cifra procede de entrevistas con tres oficiales ucranianos no identificados, y no está claro cuántos drones fueron destruidos frente a inutilizados. — [Task & Purpose](https://taskandpurpose.com/news/ukraine-10000-drone-losses); [Business Insider](https://www.businessinsider.nl/ukraine-is-losing-10000-drones-a-month-to-russian-electronic-warfare-systems-that-send-fake-signals-and-screw-with-their-navigation-researchers-say)
- **[AN]** El experto James Patton Rogers considera la cifra "probablemente" sobreestimada y señala que la mayoría de las pérdidas son drones comerciales baratos. — [Futurezone](https://futurezone.at/amp/digital-life/ukraine-10000-drohnen-abschiessen-russland-verlust-rusi-james-patton-rogers/402458547)
- **[AN]** RUSI (noviembre de 2022, febrero–julio de 2022): "el 90% de los UAS empleados se pierden"; la EW es el principal medio contra-UAS; "el espectro electromagnético difícilmente se deniega, pero se disrumpe continuamente". — [RUSI, "Preliminary Lessons...", 30-nov-2022](https://rusi.org/explore-our-research/publications/special-resources/preliminary-lessons-conventional-warfighting-russias-invasion-ukraine-february-july-2022)
- **[AN]** RUSI (febrero de 2025): entre el 60% y el 80% de los FPV ucranianos no alcanzan su objetivo, según el sector del frente y la pericia del operador. Hay largos periodos en que la EW o el clima degradan mucho las operaciones. Aun así, los UAV tácticos causan el 60–70% de los sistemas rusos dañados o destruidos. La EW también provoca fratricidio y hace que las operaciones propias sean "periódicas, no continuas". — [RUSI, feb-2025](https://nllp.jallc.nato.int/iks/sharing%20public/tactical-developments-third-year-russo-ukrainian-war-february-2205%20(1).pdf)
- **[TEST/H]** Datos de primera mano de un equipo FPV ucraniano en Donbás (2024–2025):
  - 43% de las salidas aciertan, o 20–30% si se cuentan los abortos antes del lanzamiento;
  - causas de fallo: **EW enemiga 31%**, fallos técnicos al despegar ~25%, no detonación ~10%, jamming amigo ~3% e interferencia de otros drones ≥3%.
  — [War on the Rocks (J. Jajcay), 26-jun-2025](https://warontherocks.com/i-fought-in-ukraine-and-heres-why-fpv-drones-kind-of-suck/)
- **[TEST]** Los drones de radio pueden caer a ~30% de probabilidad de llegar por saturación de frecuencias y otros factores, frente a ~50% de acierto para los de fibra. — [The War Zone, 28-may-2025](https://twz.com/news-features/inside-ukraines-fiber-optic-drone-war)
- **[AN]** CSIS: los operadores reportan un 10–15% de éxito típico en misiones FPV baratas, y un 30–50% para operadores muy hábiles. — [CSIS](https://www.csis.org/analysis/ukraines-future-vision-and-current-capabilities-waging-ai-enabled-autonomous-warfare)
- **[AN]** LIIA (Riga, 2025): los fusiles inhibidores Kvertus neutralizan FPV solo el 60–70% de las veces, y el gran defecto de la EW son sus elevadas necesidades de energía. — [LIIA, H. Brown, "The Drone Revolution", 2025](https://liia.lv/en/publications/the-drone-revolution-lessons-from-ukraine-1476?get_file=1)

### Inferences
- Para parametrizar, una base defendible es que entre un cuarto y un tercio de las misiones FPV de radio fracasan por EW enemiga en sectores disputados (31% según Jajcay). La tasa global de no llegada, por todas las causas, es del 60–80% (RUSI). La probabilidad de que un jammer de nivel 1 o 2 neutralice un FPV que entra en su zona puede fijarse en ~0,6–0,7 (LIIA, para Kvertus), no en 1.
- La cifra de 10.000 al mes (2023) sirve como orden de magnitud histórico, no como tasa actual ni como pérdidas atribuibles exclusivamente a la EW.

### Gaps
- No encontré un desglose oficial y sistemático de pérdidas de drones por causa (EW, cinética, técnica) para 2024–2026, ni cifras rusas equivalentes.
- No hallé estimaciones públicas actualizadas (2025–2026) del total mensual de drones perdidos por EW.

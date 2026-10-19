# Datasets globales de interferencia GNSS, drones y eventos de conflicto: inventario y cobertura comparada fuera de Ucrania

Estado: 18 de octubre de 2026. Todas las verificaciones de URL (código HTTP) y las descargas se hicieron el 2026-10-18 con `curl` desde un directorio temporal fuera del proyecto. "Verificado 200" significa que la URL respondió con contenido sin credenciales. Los scripts y datos quedaron en `C:\Users\ArNaxex\AppData\Local\Temp\claude\E--Github-AlgoritmosRuteo\43ac050e-1474-4025-8c7f-cdf4f139500a\scratchpad\xglobal_cov_7f3a\` (subcarpetas `dl_gpsjam`, `dl_stanford`, `dl_misc` y `scripts`; script principal `scripts\gpsjam_zones.py`).

## 1. Datasets de interferencia GNSS: ¿cuáles son libres y descargables sin credenciales?

### Takeaway
Hay tres fuentes que se pueden descargar a nivel global sin credenciales y que son directamente útiles: **GPSJam** (CSV diario en H3 res-4, histórico desde el 2022-02-14), el **Stanford GPS Lab / rfi.stanford.edu** (JSON diario y horario en H3 res-4, con capas separadas de jamming y spoofing, CC BY-NC 4.0) y los **datos crudos de ADS-B con NIC/NACp** (API abierta y volcados diarios de adsb.lol, más una muestra gratuita de ADS-B Exchange el día 1 de cada mes). Flightradar24 y GPSwise solo sirven para mirar en pantalla, porque no ofrecen descarga. El histórico de OpenSky exige una cuenta aprobada y se limita a investigación sin fines de lucro. AIS marítimo y RFI satelital (HawkEye 360, Windward) son comerciales. SMOS y Sentinel-1 publican RFI, pero en bandas que no son GNSS.

### Cited Findings

**GPSJam (gpsjam.org)**
- Muestra la agregación de 24 h de la precisión de navegación que reportan las aeronaves por ADS-B, en un mapa hexagonal. Verde significa que más del 98 % de las aeronaves reportó buena precisión, amarillo que entre 2 % y 10 % reportó baja precisión y rojo que más del 10 % la reportó baja — [GPSJam FAQ](https://gpsjam.org/faq)
- **Umbral rojo verificado:** la fórmula oficial es `percent_bad_aircraft = 100 * (num_bad_aircraft - 1) / (num_good_aircraft + num_bad_aircraft)`. El autor resta 1 al conteo de aeronaves "malas" para reducir falsos positivos en hexágonos con poco tráfico, y advierte que eso sesga el mapa en contra de mostrar interferencia donde hay pocos datos. Por lo tanto, el criterio `bad/(good+bad) > 0.1` de la consigna **no** coincide exactamente con el rojo de GPSJam. El criterio correcto es `(bad-1)/(good+bad) > 0.10` — [GPSJam FAQ](https://gpsjam.org/faq)
- Fuente de datos: posiciones de **airplanes.live** y **ADS-B Exchange**, deduplicadas por aeronave cuando se usan ambas — [GPSJam FAQ](https://gpsjam.org/faq). El `manifest.csv` muestra que la columna `source` dice `adsbexchange` desde el 2022-02-14 y cambia a `merged` desde el **2026-08-27**: 1 653 días de una sola fuente y 52 días fusionados al 2026-10-17, con 16 días marcados `suspect=true` — [manifest GPSJam](https://gpsjam.org/data/manifest.csv) (descargado, cálculo propio)
- Actualización diaria poco después de medianoche UTC, con fechas en UTC. No hay datos antes del 2022-02-14 y hay días incompletos documentados (2022-06-08/09, 2022-10-13/14, 2024-01-28/30, 2024-07-14/15, 2025-01-08/09, etc.) — [GPSJam FAQ](https://gpsjam.org/faq)
- Los huecos sin hexágono corresponden a zonas sin aeronaves con ADS-B ("por ejemplo, en una zona de guerra activa") o sin receptores que alimenten las redes — [GPSJam FAQ](https://gpsjam.org/faq)
- Zonas que el autor ve con interferencia frecuente: mar Negro/Crimea, Báltico (Polonia, Lituania, Letonia, Estonia, Finlandia, Suecia, partes de Alemania), Mediterráneo oriental y Medio Oriente (Irak, Líbano, Chipre, Turquía, Israel, Egipto, Siria), golfo Pérsico y estrecho de Ormuz, y partes de Asia del Sur (alrededores de Lahore y de Yangón, "probablemente relacionado con la guerra de drones"). El rojo en el suroeste de EE. UU. (Texas) proviene de aviones de entrenamiento militar en maniobras y no de jamming — [GPSJam FAQ](https://gpsjam.org/faq)
- Formato verificado: `https://gpsjam.org/data/YYYY-MM-DD-h3_4.csv` con columnas `hex,count_good_aircraft,count_bad_aircraft`, unas 47 600–48 300 filas por día y unos 190 KB comprimido. Responde 200 sin credenciales (usar `curl --compressed`) — [CSV 2026-10-17](https://gpsjam.org/data/2026-10-17-h3_4.csv)
- La celda H3 de resolución 4 mide en promedio **1 770 km²**, con lados de unos **26 km**. Medidas propias: unos 2 003 km² en el Líbano, 1 649 km² en Yemen y 1 511 km² en Kaliningrado — cálculo con la librería [h3 4.5.0](https://pypi.org/project/h3/)
- No encontré ninguna declaración de licencia para los CSV en la FAQ, en /about ni en la portada — [GPSJam FAQ](https://gpsjam.org/faq)

**Stanford GPS Lab: GNSS Interference Monitoring (rfi.stanford.edu)**
- Publica datos de jamming y spoofing derivados de ADS-B en JSON, que se descargan con un downloader en Python. Licencia **CC BY-NC 4.0**; el uso comercial requiere una licencia aparte con la oficina de transferencia de Stanford. La página menciona como proveedores en distintas etapas a ADS-B Exchange, OpenSky, Airplanes.live y AirNav Systems, y AirNav es el "Current Data Provider". Última actualización: agosto de 2026 — [Stanford RFI resources](https://rfi.stanford.edu/resources)
- Estructura de los datos (README del downloader `rfi-fileparser`): `jamming/AAAA/MM/DD/heatmap.json` con un heatmap diario y otro **horario** (`/HHMM/heatmap.json`) por `h3Index`, con `lowQualityCount` (aeronaves con NIC bajo) y `totalAircraftCount`. También `event.json`, con eventos de jamming (centroide, `startTime` y `endTime`). En spoofing hay heatmap por evento con `spoofedFlightCount` y archivos `beforeAndDuringSpoofing.json` y `duringAndAfterSpoofing.json` con la última posición normal y la primera falsificada de cada vuelo — [README gist](https://gist.github.com/liu1322/a2ef320432990ed4383f576e2a228615); [PyPI rfi-fileparser](https://pypi.org/project/rfi-fileparser/)
- **Verificado:** el endpoint real (tomado del código del paquete) es `https://waas-nas.stanford.edu/data/<jamming|spoofing>/AAAA/MM/DD/<archivo>.json`. El heatmap de jamming del 2026-10-15 (7,7 MB, 41 590 celdas, todas H3 **res-4**, granularidad DAILY) responde 200. También responden 200 los heatmaps del 2023-01-15 y del 2024-06-15, de modo que hay histórico al menos desde 2023. El heatmap de spoofing del 2026-10-15 (18 eventos y 193 celdas) y `beforeAndDuringSpoofing.json` responden 200. Los `event.json` de jamming y de spoofing devolvieron **404** en las fechas probadas (2025-04-24, 2026-10-14 y 2026-10-15). Los propios JSON traen la licencia CC BY-NC 4.0 y la atribución "Data from rfi.stanford.edu, Stanford GPS Laboratory" — [heatmap jamming 2026-10-15](https://waas-nas.stanford.edu/data/jamming/2026/10/15/heatmap.json); [heatmap spoofing 2026-10-15](https://waas-nas.stanford.edu/data/spoofing/2026/10/15/heatmap.json)

**Flightradar24: mapa de GPS jamming**
- Calcula la interferencia a partir del NIC (Navigation Integrity Category) que difunden las aeronaves en ADS-B. Muestra resolución de 6 h o 24 h y solo cubre áreas con suficientes vuelos y receptores terrestres de FR24 — [FR24 blog](https://www.flightradar24.com/blog/gps-jamming-map/); [FR24 data page](https://www.flightradar24.com/data/gps-jamming)
- "Recibimos NICs con cada actualización ADS-B y los datos de esta página se actualizan cada 6 horas". El gris significa poca o ninguna cobertura o vuelos — [FR24 support](https://support.fr24.com/support/solutions/articles/3000125401-gps-jamming-what-is-it-and-where-can-i-see-the-updated-map)
- No encontré ninguna opción de descarga o exportación. La página respondió 200 a `curl`, pero con un desafío anti-bot ("Just a moment…") — [FR24 data page](https://www.flightradar24.com/data/gps-jamming)

**ADS-B Exchange**
- Los productos empresariales (API, streaming gRPC y descarga diaria completa vía S3) son de pago. Para uso personal o no comercial existe una "Community API" — [ADSBx data products](https://www.adsbexchange.com/data-products/)
- **Verificado:** la muestra gratuita `readsb-hist` del **día 1 de cada mes** se descarga sin credenciales: 2026-10-01 y 2026-09-01 responden 200, mientras que 2026-09-02 y 2026-09-15 responden 404. La muestra trae los campos `nic`, `nac_p`, `sil`, `nic_baro` y `gva` por aeronave — [muestra ADSBx 2026-10-01](https://samples.adsbexchange.com/readsb-hist/2026/10/01/000000Z.json.gz)

**adsb.lol y airplanes.live (redes comunitarias)**
- **Verificado:** la API abierta de adsb.lol (`/v2/point/lat/lon/radio`) devolvió 59 aeronaves alrededor de Israel (32N 35E, 250 nm) sin clave, con los campos `nic`, `nac_p`, `sil`, `gpsOkBefore`, `gpsOkLat` y `gpsOkLon` (estos tres últimos marcan la última posición con GPS bueno) — [API adsb.lol](https://api.adsb.lol/v2/point/32.0/35.0/250)
- adsb.lol publica en GitHub volcados diarios del historial global ("Openly licensed"). La release `v2026.10.17-planes-readsb-prod-0` se publicó el 2026-10-18, partida en tars de unos 2 GB más 1,5 GB — [globe_history_2026](https://github.com/adsblol/globe_history_2026); [API releases](https://api.github.com/repos/adsblol/globe_history_2026/releases)
- La API de airplanes.live devolvió **403** a `curl` (Cloudflare) y su página `api-guide` dio 404 — [API airplanes.live](https://api.airplanes.live/v2/point/32.0/35.0/250)

**OpenSky Network**
- Licencia: uso limitado a "investigación sin fines de lucro y educación sin fines de lucro". Cualquier entidad con fines de lucro necesita una licencia escrita, igual que cualquier uso operativo de la REST API, incluso para entidades sin fines de lucro. No se pueden redistribuir los datos a terceros fuera de la institución. Hay que citar Schäfer et al. 2014 — [OpenSky Terms of Use](https://opensky-network.org/about/terms-of-use)
- **Verificado:** la REST API anónima `/api/states/all` con bbox responde 200 (vuelos sobre Israel), pero los state vectors no traen NIC/NACp. Sus campos son icao24, callsign, país, posición, altitudes, velocidad, rumbo, squawk y fuente de posición — [OpenSky REST](https://opensky-network.org/api/states/all?lamin=29&lomin=34&lamax=34&lomax=36)
- El histórico se consulta vía **Trino** (Impala quedó deprecado en junio de 2024) con autenticación. `pyopensky` expone `history()` sobre `state_vectors_data4` y `rawdata()` sobre `rollcall_replies_data4` (mensajes crudos) — [pyopensky Trino](https://mode-s.org/pyopensky/trino.html); [PyPI pyopensky](https://pypi.org/project/pyopensky/)
- Hay literatura que usa OpenSky para detectar jamming por NACp y NIC: un trabajo de 2019 que se presenta como el primero en usar métricas de calidad ADS-B — [EasyChair](https://easychair.org/publications/paper/Mp3x); el análisis de unos 135,5 millones de mensajes de OpenSky sobre Texas (octubre de 2022), con un umbral de NIC < 7 — [InsideGNSS](https://insidegnss.com/?p=191777); un método que compara NACp con el HDOP del almanaque GPS — [Aeronautical Journal](https://www.cambridge.org/core/journals/aeronautical-journal/article/gnss-interference-detection-methodology-utilising-adsb-nacp-indicator-and-gps-almanac-data/72FEBF7BFE1541D7BF146B14BFAA4AB8); y un trabajo de machine learning (LightGBM) que advierte que los umbrales de NIC pierden eventos intermitentes — [even3 PDF](https://static.even3.com/anais/1239773.pdf)

**SkAI / GPSwise**
- `spoofing.skai-data-services.com` redirige a **gpswise.aero** (verificado). El sitio se describe como "Live GPS Jamming & Spoofing Map" con "datos ADS-B de la OpenSky Network" y "tendencias históricas". Es una SPA (aplicación de una sola página) con autenticación y no encontré descarga — [GPSwise](https://gpswise.aero/). La página "how-gpswise-works" devolvió 404 — [GPSwise how it works](https://gpswise.aero/how-gpswise-works)

**Datasets académicos abiertos (RF crudo y campañas de jamming)**
- Jammertest 2024 (Noruega): dataset de campo con receptores GNSS, no ADS-B — [arXiv 2510.27576](https://arxiv.org/pdf/2510.27576)
- Tampere (Zenodo, mayo de 2025): grabaciones de laboratorio GPS E1 con 9 escenarios, falsificados y auténticos — [Zenodo 15490403](https://zenodo.org/records/15490403). GATEMAN (2019): grabaciones de campo de jamming y spoofing — [Zenodo 3532660](https://zenodo.org/record/3532660)
- White paper de abril de 2026 sobre detección de spoofing en aviación con ADS-B, alojado por Aireon (ADS-B satelital, comercial) — [PDF Aireon](https://aireon.com/wp-content/uploads/2026/04/White-Paper-GNSS-Spoofing-Detection-in-Aviation-1.0-1-1.pdf)

**AIS marítimo (spoofing de buques)**
- Windward (comercial) reportó más de 330 buques afectados por spoofing o jamming a inicios de 2025, más de 12 000 incidentes que afectaron a más de 3 000 buques durante el conflicto con Irán del 13 al 24 de junio de 2025 y más de 13 000 buques en el segundo trimestre de 2025 — [Windward 2025 stress test](https://windward.ai/blog/2025-maritime-stress-test/). Describe el patrón de buques "en círculos geométricos" sobre aeropuertos o tierra — [Windward glossary](https://windward.ai/glossary/what-is-ais-spoofing/)
- Una fuente secundaria cifra en más de 1 650 los buques perturbados en el golfo a inicios de marzo de 2026 (no es un dataset primario) — [gisresources](https://gisresources.com/gnss-jamming-crisis-at-the-strait-of-hormuz-exposes-maritime-navigation-vulnerabilities/)
- Global Fishing Watch tiene APIs públicas (la página responde 200), pero no verifiqué que expongan un indicador de spoofing — [GFW APIs](https://globalfishingwatch.org/our-apis/)

**RFI satelital**
- HawkEye 360 (comercial): en julio de 2025 anunció un algoritmo de interferencia GNSS que incorpora detección de spoofing de GPS y geolocalización ajustada al terreno — [GPS World](https://www.gpsworld.com/hawkeye-360-launches-advanced-gnss-interference-detection-capabilities/). En diciembre de 2023 compró RF Solutions a Maxar; RF Solutions provenía de la adquisición de Aurora Insight — [Virginia Business](https://virginiabusiness.com/hawkeye-360-acquires-rf-solutions/); [SEC S-1](https://www.sec.gov/Archives/edgar/data/1750704/000162828026024593/hawkeye360-sx1.htm). **Verificado:** `aurorainsight.com` redirige a `he360.com` (403 anti-bot)
- SMOS (ESA, banda L de 1,4 GHz): el portal RFI ofrece mapas de probabilidad de RFI por país o región para cualquier fecha desde 2017 (ventana de 15 días) — [SMOS RFI portal](https://rfi.smos.eo.esa.int/rfimanager/public.jsp); [ESA LPS 2022](https://earth.esa.int/living-planet-symposium-2022-presentations/26.05.Thursday/H2-17/1330-1510/02_Uranga_LPSP22-ERMITlessons_v3.pdf)
- Sentinel-1 (banda C): desde la versión 3.40 del IPF (procesador), los productos anotan si se detectó y si se mitigó RFI — [nota técnica ESA S-1 RFI](https://sentinel.esa.int/documents/247904/0/DI-MPC-OTH-0540-1-1-RFI-Tech-Note/1e327218-18f3-c1f9-cbab-5d3af11ac793); también hay monitoreo de RFI en banda C a partir del ruido de S-1 — [ESA LPS 2022 Franceschi](https://earth.esa.int/living-planet-symposium-2022-presentations/23.05.Monday/Bangkok/1330-1510/03_Franceschi.pdf)
- SMAP: el RFI se marca en el procesamiento L1B. Hay estudios con CNN (redes convolucionales) para clasificar RFI global, pero no encontré un producto público de mapa de probabilidad — [NSF PAR](https://par.nsf.gov/servlets/purl/10399371)

### Inferences
- **Sin credenciales y con cobertura global:** GPSJam (CSV), Stanford RFI (JSON, CC BY-NC), API y volcados de adsb.lol (crudos, con NIC/NACp) y la muestra mensual de ADSBx. **Con registro o licencia:** OpenSky Trino (solo investigación sin fines de lucro, sin redistribución) y ADSBx completo (pago). **Solo visualización:** Flightradar24 y GPSwise. **Comerciales:** HawkEye 360, Windward y Aireon.
- Para el simulador, Stanford RFI aporta dos cosas que GPSJam no tiene: heatmaps **horarios** y una capa de **spoofing** separada, ambos en la misma grilla H3 res-4 que GPSJam. Se cargan en PostGIS con `h3` o con `h3-pg` sin cambiar la resolución.
- SMOS (1 400–1 427 MHz) y Sentinel-1 (banda C) **no miden L1/L2 GNSS** (1 575/1 227 MHz). Sirven como indicador de emisores fuertes, pero no como verdad de terreno del jamming GNSS. Esta es una inferencia basada en las bandas que documentan las fuentes.
- La fusión de airplanes.live en GPSJam (desde el 2026-08-27) significa que las series anteriores y posteriores a esa fecha no son estrictamente comparables. El efecto global medido es pequeño (ver sección 2).

### Gaps
- No pude confirmar qué tablas de OpenSky Trino exponen NIC/NACp ya decodificados. La página de Trino devolvió 403 a WebFetch y la documentación de pyopensky no lista columnas. Lo probable es decodificar mensajes crudos con pyModeS, pero queda sin verificar.
- No encontré datos abiertos de Spire Aviation sobre interferencia GNSS, ni un catálogo abierto de spoofing AIS (por ejemplo, el reporte C4ADS de 2019), porque no los busqué en detalle.
- No verifiqué la cobertura geográfica oficial ni la fecha de inicio del histórico de Stanford RFI. Solo comprobé que hay datos del 2023-01-15 y que los `event.json` dan 404.
- Licencia de los CSV de GPSJam: no encontrada.

## 2. Verificación empírica: cobertura de GPSJam (y Stanford) por zona candidata

### Takeaway
En la semana del 11 al 17 de octubre de 2026, GPSJam tiene **cobertura densa y señal de interferencia fuerte** en el Báltico, en Israel/Líbano/Siria, en la frontera India–Pakistán, en Myanmar y en el golfo Pérsico. Tiene **cobertura densa sin interferencia** en Corea, Colombia, México e Irak (útiles como zonas de control). Tiene **cobertura prácticamente nula** en Yemen/mar Rojo sur, Sudán, la RDC oriental y el Sahel. Esas cuatro zonas reproducen el mismo hueco que el frente ucraniano, donde solo hay datos en un promedio de 5 de 158 celdas y ninguna en rojo.

### Cited Findings
- **Método:** se descargaron los CSV diarios de GPSJam del 2026-10-11 al 2026-10-17 (7 días), más 2025-10-17, 2026-08-20, 2026-09-17 y 2026-10-01 para comparar — [patrón de URL, ejemplo 2026-10-17](https://gpsjam.org/data/2026-10-17-h3_4.csv). Cada celda se asignó a una zona según si su centroide (`h3.cell_to_latlng`) cae dentro de un bbox. El total de celdas por bbox se obtuvo con `h3.polygon_to_cells`, usando [h3 4.5.0](https://pypi.org/project/h3/). "Roja GJ" significa `(bad-1)/(good+bad) > 0.10`, la fórmula oficial ([GPSJam FAQ](https://gpsjam.org/faq)). "Roja raw" significa `bad/(good+bad) > 0.10`, el criterio pedido en la consigna. "Amarilla GJ" significa entre 0,02 y 0,10.
- **Bboxes (lon_min, lat_min, lon_max, lat_max):** Israel/Líbano/Siria (34.0, 29.4, 42.5, 37.4); mar Rojo sur/Yemen/golfo de Adén (36, 11, 54, 20); Irak (38.8, 29.0, 48.6, 37.4); golfo Pérsico/Ormuz (47.5, 23.5, 57.5, 30.5); Irán (44, 25, 63.3, 39.8); Báltico (12, 53.5, 30, 60.5); Kaliningrado (19.4, 54.3, 22.9, 55.4); península coreana (124, 33, 131, 43); India–Pakistán (68, 23, 78, 35.5); Myanmar (92.2, 9.8, 101.2, 28.5); Sudán (21.8, 8.7, 38.6, 22); RDC oriental (26, −5, 31.3, 4); Sahel (−12, 10, 16, 20); Colombia (−79, −4.2, −66.8, 12.5); México (−117.2, 14.5, −86.7, 32.7); Ucrania frente E/SE (33, 46, 40.2, 50.5); Ucrania completa (22, 44.3, 40.2, 52.4). Los rectángulos incluyen territorio vecino: Jordania y el sur de Turquía en el Levante; el sur de Suecia y Finlandia, el norte de Polonia y el oeste de Rusia en el Báltico; Moldavia, Rumania, Belarús, Rusia y el mar Negro en "Ucrania completa".

**Tabla A. GPSJam, día 2026-10-17** (fuente: [CSV 2026-10-17](https://gpsjam.org/data/2026-10-17-h3_4.csv); cálculo propio)

| Zona | Celdas H3 en bbox | Celdas con datos | % cobertura | Σ aeronaves | Roja raw | Roja GJ | Amarilla GJ |
|---|---|---|---|---|---|---|---|
| Israel/Líbano/Siria | 362 | 200 | 55,2 | 13 060 | 28 | 21 | 22 |
| Mar Rojo sur/Yemen | 1 214 | 2 | 0,2 | 2 | 0 | 0 | 0 |
| Irak | 472 | 115 | 24,4 | 5 246 | 2 | 1 | 8 |
| Golfo Pérsico/Ormuz | 467 | 337 | 72,2 | 38 090 | 37 | 22 | 36 |
| Irán (completo) | 1 662 | 534 | 32,1 | 39 457 | 42 | 22 | 41 |
| Báltico | 586 | 552 | 94,2 | 24 168 | 154 | 91 | 86 |
| Kaliningrado | 19 | 16 | 84,2 | 119 | 11 | 8 | 0 |
| Península coreana | 537 | 246 | 45,8 | 26 366 | 0 | 0 | 0 |
| India–Pakistán | 729 | 561 | 77,0 | 33 793 | 63 | 49 | 38 |
| Myanmar | 968 | 395 | 40,8 | 15 497 | 55 | 39 | 26 |
| Sudán | 1 399 | 10 | 0,7 | 46 | 6 | 3 | 0 |
| RDC oriental | 298 | 0 | 0,0 | 0 | 0 | 0 | 0 |
| Sahel (Malí/Burkina/Níger) | 2 004 | 14 | 0,7 | 90 | 0 | 0 | 0 |
| Colombia | 1 385 | 569 | 41,1 | 15 238 | 2 | 2 | 1 |
| México | 3 119 | 1 911 | 61,3 | 152 522 | 2 | 1 | 3 |
| **Ucrania frente E/SE** | 158 | 2 | 1,3 | 3 | 1 | 0 | 0 |
| Ucrania completa (con vecinos) | 697 | 174 | 25,0 | 19 546 | 72 | 35 | 54 |

**Tabla B. GPSJam, promedio de 7 días (2026-10-11 a 2026-10-17)** (fuente: CSV diarios, por ejemplo [2026-10-11](https://gpsjam.org/data/2026-10-11-h3_4.csv) a [2026-10-17](https://gpsjam.org/data/2026-10-17-h3_4.csv); cálculo propio)

| Zona | Celdas con datos (media) | Roja GJ/día media (mín–máx) | Amarilla GJ/día | Celdas con datos algún día | Celdas roja GJ algún día |
|---|---|---|---|---|---|
| Israel/Líbano/Siria | 211 | 24,1 (13–39) | 34,1 | 263 | 53 |
| Mar Rojo sur/Yemen | 0 | 0 (0–0) | 0 | 3 | 0 |
| Irak | 107 | 0,9 (0–4) | 3,1 | 203 | 6 |
| Golfo Pérsico/Ormuz | 326 | 14,1 (2–55) | 55,0 | 403 | 68 |
| Irán (completo) | 489 | 13,0 (2–42) | 52,0 | 716 | 60 |
| Báltico | 537 | 81,4 (74–91) | 89,4 | 581 | 178 |
| Kaliningrado | 13 | 7,3 (5–9) | 0,3 | 19 | 13 |
| Península coreana | 263 | 0,3 (0–2) | 3,4 | 308 | 2 |
| India–Pakistán | 586 | 53,3 (39–71) | 42,1 | 662 | 103 |
| Myanmar | 384 | 30,6 (24–39) | 23,6 | 474 | 60 |
| Sudán | 8 | 0,6 (0–3) | 0,1 | 15 | 3 |
| RDC oriental | 0 | 0 | 0 | 0 | 0 |
| Sahel | 14 | 0 | 0 | 23 | 0 |
| Colombia | 554 | 0,3 (0–2) | 1,6 | 647 | 2 |
| México | 1 953 | 0,9 (0–2) | 8,4 | 2 150 | 4 |
| **Ucrania frente E/SE** | 5 | 0 | 0 | 28 | 0 |
| Ucrania completa | 183 | 36,7 (33–43) | 48,7 | 327 | 99 |

- **Global:** entre 47 602 y 48 142 celdas con datos por día en esa semana. Hay entre 461 y 569 rojas GJ por día, frente a entre 905 y 1 089 rojas raw: la resta de 1 aproximadamente **reduce a la mitad** el conteo de celdas rojas — [CSV 2026-10-16](https://gpsjam.org/data/2026-10-16-h3_4.csv) (cálculo propio)
- **Comparación interanual (2025-10-17, solo ADSBx, contra 2026-10-17, fusionado):** las celdas globales con datos pasaron de 46 108 a 47 602 (+3 %). Por zona: el golfo Pérsico pasó de 0 a 22 rojas GJ, India–Pakistán de 2 a 49, Israel/Líbano/Siria de 29 a 21, el Báltico de 98 a 91 y Kaliningrado de 13 a 8; Sudán siguió en 23→10 celdas con datos — [CSV 2025-10-17](https://gpsjam.org/data/2025-10-17-h3_4.csv) (cálculo propio)
- **Variabilidad mensual (rojas GJ el 2026-08-20, 2026-09-17 y 2026-10-01):** Israel/Líbano/Siria 14, 18 y 30; golfo Pérsico 19, 7 y 2; India–Pakistán 3, 19 y 53; Myanmar 7, 27 y 18; Báltico 108, 71 y 81 — [CSV 2026-08-20](https://gpsjam.org/data/2026-08-20-h3_4.csv); [CSV 2026-09-17](https://gpsjam.org/data/2026-09-17-h3_4.csv); [CSV 2026-10-01](https://gpsjam.org/data/2026-10-01-h3_4.csv) (cálculo propio)

**Tabla C. Stanford GPS Lab, heatmap diario de jamming del 2026-10-15** (H3 res-4; ">10 % raw" = `lowQualityCount/totalAircraftCount > 0.10`; ">10 % denoised" = `(low-1)/total > 0.10`) — [heatmap Stanford 2026-10-15](https://waas-nas.stanford.edu/data/jamming/2026/10/15/heatmap.json) (cálculo propio)

| Zona | Celdas con datos | >10 % raw | >10 % denoised | Σ aeronaves |
|---|---|---|---|---|
| Israel/Líbano/Siria | 222 | 79 | 65 | 13 530 |
| Mar Rojo sur/Yemen | 15 | 8 | 5 | 56 |
| Irak | 198 | 18 | 7 | 5 495 |
| Golfo Pérsico/Ormuz | 266 | 45 | 32 | 33 978 |
| Báltico | 516 | 252 | 188 | 26 985 |
| Kaliningrado | 6 | 6 | 5 | 28 |
| Península coreana | 247 | 0 | 0 | 31 912 |
| India–Pakistán | 598 | 36 | 20 | 36 611 |
| Myanmar | 278 | 59 | 43 | 15 726 |
| Sudán | 45 | 23 | 11 | 349 |
| RDC oriental | 35 | 9 | 2 | 150 |
| Sahel | 19 | 1 | 0 | 50 |
| Colombia | 581 | 22 | 15 | 14 453 |
| México | 1 815 | 154 | 111 | 175 825 |
| Ucrania frente E/SE | 0 | 0 | 0 | 0 |

- En total, Stanford tuvo 41 590 celdas ese día y 2 518 con más de 10 % raw — [heatmap Stanford 2026-10-15](https://waas-nas.stanford.edu/data/jamming/2026/10/15/heatmap.json)
- Spoofing de Stanford el 2026-10-15: 18 eventos globales y 193 celdas. Por zona: Israel/Líbano/Siria, 1 evento en 62 celdas; Irak, 1 evento en 8 celdas; Báltico, 2 eventos en 4 celdas; Kaliningrado, 1 evento en 1 celda; India–Pakistán, 1 evento en 5 celdas; Myanmar, 1 evento en 10 celdas — [heatmap spoofing 2026-10-15](https://waas-nas.stanford.edu/data/spoofing/2026/10/15/heatmap.json) (cálculo propio)

### Inferences
- **Grupo A, con datos e interferencia** (permiten calibrar zonas de jammer sintéticas con datos reales): Báltico/Kaliningrado, Israel/Líbano/Siria, India–Pakistán, Myanmar y golfo Pérsico/Irán. **Grupo B, con datos y sin interferencia** (sirven como línea base o control): Corea, Colombia, México e Irak. **Grupo C, sin datos** (mismo hueco que el frente ucraniano, solo admiten jammer sintético): Yemen/mar Rojo sur, Sudán, RDC oriental y Sahel.
- En el Grupo C, la falta de celdas no indica ausencia de jamming. Indica que no hay tráfico ADS-B ni receptores, el mismo mecanismo que explica el hueco en Ucrania según la FAQ de GPSJam. Para el simulador conviene representarlo como "sin observación" (NULL) y no como 0.
- Stanford detecta más celdas "altas" que GPSJam en zonas de poco riesgo (México: 111 contra 1, con ruido similar en Sudán y la RDC con muy pocas aeronaves). Los umbrales de NIC "bajo" de ambas fuentes no son equivalentes y los conteos pequeños generan falsos positivos. Si se usa Stanford, conviene exigir un mínimo de aeronaves por celda o aplicar la resta de 1 de GPSJam.
- La celda res-4 tiene unos 26 km de lado. Una zona de jammer sintética del simulador puede anclarse a 1–7 celdas (el anillo k=1 tiene unos 12 400 km²). Para resolución táctica hay que bajar de escala con un modelo de propagación, porque el dato observado solo ofrece mesoescala.
- La celda "Ucrania completa" con 36 rojas por día corresponde probablemente al perímetro (mar Negro, Moldavia, Rumania y Belarús/Rusia), no al frente, que no tiene datos. Es una inferencia basada en los bboxes.

### Gaps
- No calculé los conteos con polígonos de país, sino con rectángulos. Las cifras incluyen celdas de países vecinos.
- No descargué las series largas (por ejemplo, 2022–2026) por zona. Solo se tomaron 11 días.
- No encontré la definición exacta de "lowQualityCount" (umbral NIC) en Stanford.

## 3. Datasets de eventos de conflicto con cobertura global y subtipo "dron"

### Takeaway
**ACLED** es la única fuente global con un subtipo que nombra a los drones ("Air/drone strike"). Ese subtipo no separa drones de aviones tripulados, y lo específico del dron solo aparece en `notes` cuando la fuente lo reporta. Además, el acceso a datos a nivel de evento depende del nivel myACLED asignado por el dominio del correo. **UCDP GED/Candidate** es CC BY 4.0 y mensual, pero sin subtipo de arma, y desde febrero de 2026 su API exige token. **GDELT** es libre y se actualiza cada 15 minutos, pero con mucho ruido. Airwars, TBIJ y New America cubren ataques aéreos y con drones en pocos países, con licencias poco claras o proyectos cerrados.

### Cited Findings

**ACLED**
- myACLED reemplaza a las Access Keys y tiene cuatro niveles: **Open, Research, Partner y Enterprise**. Según la tabla de la FAQ, mal alineada en la extracción: Open recibe datos en "tiempo real" en el Explorer, sin API; Research recibe datos agregados, API y nuevas categorías; Partner agrega datos de eventos con rezago (lagged) y archivos curados descargables; Enterprise recibe datos desagregados semanales. Los correos genéricos (gmail.com) quedan en Open y se recomienda registrarse con el dominio institucional. Los keys API antiguos tuvieron una transición hasta el 15 de septiembre de 2025, y el nuevo acceso usa cookies u OAuth. Se restringe "monetizar productos" y generar "productos secundarios o sustitutos" — [myACLED FAQ](https://acleddata.com/myacled-faqs)
- **Verificado:** la API (`/api/acled/read`) responde 403 "authentication required" sin credenciales — [ACLED API](https://acleddata.com/api/acled/read?limit=1). Los términos están en [ACLED terms and conditions](https://acleddata.com/terms-and-conditions) (200)
- Definición: "Air/drone strike" es "cualquier ataque aire-tierra por aeronaves o drones, en ausencia de otro enfrentamiento". No existe campo ni tag de dron. La información de drones "puede registrarse a veces en la columna Notes" y "no se reporta sistemáticamente". Se recomienda filtrar `notes` por "drone" y buscar también "airstrike/drone" en eventos tipo Battles. Además, se agrupan en un solo evento todos los ataques con la misma fecha, lugar y actores (página del 24 de junio de 2026) — [ACLED FAQ air/drone strikes](https://acleddata.com/faq/how-does-acled-code-air-and-drone-strike-events)
- "Shelling/artillery/missile attack" corresponde a armas de base terrestre o naval, frente al ataque aire-tierra del subtipo de drones — [ACLED FAQ air/drone strikes](https://acleddata.com/faq/how-does-acled-code-air-and-drone-strike-events); el codebook tiene 6 tipos y 25 subtipos de evento — [ACLED Codebook](https://acleddata.com/methodology/acled-codebook)
- **Inicio de cobertura por país:** Israel, Palestina, Líbano, Irak, Irán e India desde 1/2016; Siria desde 1/2017; Yemen y Arabia Saudí desde 1/2015; Pakistán y Myanmar desde 1/2010; Sudán, RDC, Malí, Burkina Faso y Níger desde 1/1997; Rusia, Corea del Norte y del Sur, Colombia, México y Ucrania desde 1/2018; Estonia, Letonia, Lituania y Polonia desde 1/2020 — [ACLED country/time coverage](https://acleddata.com/knowledge-base/country-time-period-coverage)

**UCDP**
- **GED Global 26.1** cubre 1989–2025. El **GED Candidate** es mensual, con "no más de un mes de rezago"; la última versión listada es la 26.0.8 (agosto de 2026). Ambos son gratuitos bajo **CC BY 4.0** y se ofrecen en CSV y Excel. La página no menciona drones — [UCDP downloads](https://ucdp.uu.se/downloads/)
- **Verificado:** la API responde 401 "API token required. Add header: x-ucdp-access-token". Según la documentación, el token se introdujo en febrero de 2026, es gratuito y se pide por correo describiendo el proyecto — [UCDP API](https://ucdpapi.pcr.uu.se/api/gedevents/25.1?pagesize=1); [UCDP API docs](https://ucdp.uu.se/apidocs/)

**GDELT**
- Todos los datasets están disponibles para "uso ilimitado y sin restricciones para cualquier uso académico, comercial o gubernamental, sin costo", y se pueden redistribuir — [GDELT about](https://www.gdeltproject.org/about.html)
- **Verificado:** `lastupdate.txt` apunta a exportaciones con marca 20261018224500, es decir, actualización cada 15 min — [GDELT lastupdate](http://data.gdeltproject.org/gdeltv2/lastupdate.txt)

**Airwars**
- El sitio responde 200. Los filtros de investigación incluyen Yemen (unas 141 entradas), Somalia (160), Siria (140), territorios palestinos (24), Türkiye (6) y Ucrania (22). Su base de Yemen sigue las acciones antiterroristas de EE. UU. con fuentes locales mayoritariamente en árabe — [Airwars](https://airwars.org/); [Airwars research](https://airwars.org/research/page/3)

**ISW/CTP y Liveuamap**
- `understandingwar.org`, `criticalthreats.org` y `liveuamap.com` devolvieron **403** (anti-bot) a `curl` — [ISW](https://www.understandingwar.org/); [CTP](https://www.criticalthreats.org/); [Liveuamap](https://liveuamap.com/)
- Precios de la API de Liveuamap según un competidor (no verificado): plan Pro de 150 USD al mes por 200 solicitudes diarias y Enterprise desde 1 000 USD al mes, con licencia propietaria — [World Monitor (competidor)](https://www.worldmonitor.app/compare/worldmonitor-vs-liveuamap/)

**Proyectos específicos de ataques con drones**
- TBIJ siguió entre 2010 y 2020 los ataques con drones y otras acciones encubiertas de EE. UU. en Pakistán, Afganistán, Yemen y Somalia. El proyecto está cerrado — [TBIJ Drone War](https://www.thebureauinvestigates.com/projects/drone-war)
- New America, "America's Counterterrorism Wars": mapa y lista de ataques (Pakistán desde 2004, además de Yemen y Somalia). La URL antigua `/future-security/reports/world-of-drones/` da 404 y la nueva `/insights/americas-counterterrorism-wars/` da 200 — [New America CT Wars](https://www.newamerica.org/insights/americas-counterterrorism-wars/); hay un PDF archivado con datos hasta junio de 2016 — [Just Security PDF](https://www.justsecurity.org/wp-content/uploads/2016/10/NAF-Airstrikes-Data-Pakistan-Yemen-Somalia.pdf)

### Inferences
- Para un estudiante con correo `udp.cl`, el nivel probable es **Research** (datos agregados y API). Si no hay acceso a eventos desagregados, hay que solicitarlo a ACLED. Esto debe confirmarse con la cuenta, porque la FAQ es ambigua.
- Para el rubro "amenaza", el subtipo ACLED `Air/drone strike` más un filtro `notes ILIKE '%drone%'` es el único proxy global de "ataque con dron". Hay que documentar que mezcla aviación tripulada y que la agregación diaria por lugar y actor subcuenta los ataques.
- UCDP es la opción con licencia más limpia (CC BY 4.0) para publicar JSON derivados, pero no distingue el tipo de arma.

### Gaps
- No encontré los términos de licencia de los mapas de ISW/CTP ni datos de API de Liveuamap en fuentes primarias, porque los sitios bloquearon el acceso automatizado.
- No verifiqué la metodología completa de Airwars ni si ofrece descargas en CSV.
- No investigué PAX (no encontré un dataset de incidentes descargable en esta pasada).

## 4. Capas globales de terreno, cobertura y clima

### Takeaway
Las cuatro capas que ya se usan para Ucrania funcionan en todas las zonas candidatas sin credenciales: WorldCover (10 m, CC BY 4.0), Copernicus DEM GLO-30, Meta canopy height (1 m) y Open-Meteo/ERA5. Hay tres salvedades verificadas. **GLO-30 no cubre Armenia ni Azerbaiyán**, donde hay que usar GLO-90. La precisión de WorldCover es de alrededor de 76–77 %, también en África. Y las imágenes de Meta datan de 2009–2020, por lo que no reflejan la deforestación ni la destrucción recientes.

### Cited Findings
- **ESA WorldCover:** **verificado** que la tile `ESA_WorldCover_10m_2021_v200_N33E033_Map.tif` (Levante, 31 MB) se descarga desde S3 sin credenciales — [tile WorldCover](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N33E033_Map.tif); [ESA WorldCover](https://esa-worldcover.org/en). La precisión global de 2021 v200 es de 76,7 %, validada por Wageningen e IIASA — [worldcover2021.esa.int](https://worldcover2021.esa.int). Para África es de 76,5 % ±1,3 en 2021 (73,6 % en 2020), con menor precisión en arbustos, humedales herbáceos y musgo/liquen — [Digital Earth Africa](https://docs.digitalearthafrica.org/en/latest/data_specs/ESA_WorldCover_specs.html); [PVR v2.0](https://pure.iiasa.ac.at/18981/1/WorldCover_PVR_V2.0.pdf)
- **Copernicus DEM:** **verificado** que la tile GLO-30 `N33_00_E035_00` (Líbano) da 200. La tile GLO-30 `N40_00_E044_00` (Armenia) da **404**, mientras que la GLO-90 de la misma tile da 200 — [GLO-30 Líbano](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N33_00_E035_00_DEM/Copernicus_DSM_COG_10_N33_00_E035_00_DEM.tif); [GLO-30 Armenia (404)](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N40_00_E044_00_DEM/Copernicus_DSM_COG_10_N40_00_E044_00_DEM.tif); [GLO-90 Armenia](https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_N40_00_E044_00_DEM/Copernicus_DSM_COG_30_N40_00_E044_00_DEM.tif). GLO-30 es libre en todo el mundo "con excepción de Armenia y Azerbaiyán" — [GEE catalog](https://developers.google.cn/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30?hl=es-419); ASF rellena con GLO-90 — [ASF HyP3](https://hyp3-docs.asf.alaska.edu/dems/); afecta a unas 40 tiles — [EMD wiki](https://help.emd.dk/mediawiki/index.php/Copernicus_DEM)
- **Meta/WRI canopy height (1 m):** **verificado** que `tiles.geojson` se descarga del bucket público de AWS (15 MB) — [AWS Registry](https://registry.opendata.aws/dataforgood-fb-forests/); [tiles.geojson](https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/tiles.geojson). El MAE es de 2,8 m, con imágenes de 2009–2020 (80 % de 2018–2020) — [Meta sustainability](https://sustainability.atmeta.com/?p=5573). Una validación en los Alpes italianos encontró que subestima la altura máxima y no estima bien el número ni la posición de los árboles — [unibz](https://bia.unibz.it/esploro/outputs/journalArticle/Evaluating-the-reliability-of-the-1-meter/991007384663701241). Un CHMv2 (DINOv3) aparece con fecha del 6 de marzo de 2026 en fuentes secundarias (no verificado) — [listing CHMv2](https://theresanaiforthat.com/model/canopy-height-maps-v2/)
- **Open-Meteo:** **verificado** que las APIs de pronóstico y de archivo (ERA5) responden 200 para Saná (Yemen) — [forecast](https://api.open-meteo.com/v1/forecast?latitude=15.35&longitude=44.2&current=wind_speed_10m,cloud_cover); [archive](https://archive-api.open-meteo.com/v1/archive?latitude=15.35&longitude=44.2&start_date=2026-10-01&end_date=2026-10-02&hourly=wind_speed_10m). La API gratuita es solo para uso no comercial, con menos de 10 000 llamadas diarias, 5 000 por hora y 600 por minuto, y los datos son CC BY 4.0 — [Open-Meteo terms](https://open-meteo.com/en/terms)
- **OSM/Geofabrik:** la página de extractos de África responde 200 — [Geofabrik África](https://download.geofabrik.de/africa.html)
- **NASA FIRMS:** la página de la API responde 200 y lista un endpoint para configurar `MAP_KEY` — [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/)

### Inferences
- Para las zonas del Grupo C (Sudán, Sahel, RDC), la capa de terreno sí está disponible. Lo que falta es la capa de amenaza GNSS, así que el simulador puede usar terreno real con jammer sintético.
- Si se agregara el Cáucaso (Armenia/Azerbaiyán), habría que bajar a GLO-90 o fusionar con otro DEM.

### Gaps
- No encontré fuentes primarias sobre la completitud de OSM por país (Sahel, RDC, Myanmar). Queda como pendiente.
- No verifiqué si FIRMS exige `MAP_KEY` para todas las consultas, aunque la página lo sugiere.

## 5. Datasets de incidentes de drones y contra-drones, y datasets RF útiles como parámetros

### Takeaway
No existe un dataset global y abierto de "incidentes de drones en conflicto" aparte de ACLED (subtipo mixto). Los proyectos específicos (TBIJ y New America) cubren solo los ataques de EE. UU. en Pakistán, Yemen, Somalia y Afganistán y están cerrados o desactualizados. Drone Wars UK cubre al Reino Unido, y la FAA solo avistamientos en EE. UU. Para parametrizar el simulador (detección RF y firma de enlace) sí hay datasets abiertos de señales RF de drones comerciales: DroneRF, DroneRFa y RFUAV.

### Cited Findings
- **Drone Wars UK:** el sitio responde 200. Su menú incluye "Who has Armed Drones?", "British Drone Strike Stats" y "List of UK air/drone strikes on ISIS" — [Drone Wars UK](https://dronewars.net/)
- **New America "World of Drones":** sigue qué países y actores no estatales poseen, desarrollan o usaron drones armados. Más de diez países realizaron ataques con drones: EE. UU., Israel, Reino Unido, Pakistán, Irak, Nigeria, Irán, Turquía, Azerbaiyán, Rusia y EAU — [New America World of Drones](https://www.newamerica.org/insights/world-drones/); [press release](https://www.newamerica.org/insights/new-americas-international-security-program-launches-database-of-global-drone-imports/)
- **TBIJ** (2010–2020, cerrado) — [TBIJ](https://www.thebureauinvestigates.com/projects/drone-war)
- **FAA UAS Sightings Report** (EE. UU.): la página responde 200 — [FAA](https://www.faa.gov/uas/resources/public_records/uas_sightings_report)
- **DroneRF** (Data in Brief, 2019): 227 grabaciones RF de 3 drones en distintos modos (apagado, encendido, hover, vuelo, video) más fondo sin drones. Está en Mendeley Data (DOI 10.17632/f4c2b4n755.1) y responde 200 — [Mendeley](https://data.mendeley.com/datasets/f4c2b4n755/1); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6727013)
- **RFUAV** (2025): integra DroneRF y DroneRFa y cubre más de 54 tipos de drones. DroneRFa tiene unos 25 tipos — [arXiv 2503.09033](https://arxiv.org/html/2503.09033v1). Hay otro dataset multi-escenario de 2026 — [arXiv 2603.00106](https://arxiv.org/html/2603.00106v1)

### Inferences
- Para el modelo de detección y alerta tipo CLUN-LSR, DroneRF y RFUAV sirven para fijar parámetros de enlace (bandas de 2,4 y 5,8 GHz y firmas de control y video). La geografía del jamming sale de GPSJam y Stanford. Son capas complementarias: unas dan la física del enlace y otras dónde ocurre.
- Los datasets de "incidentes de drones" con cobertura multi-país y actual se reducen en la práctica a ACLED (con filtro en `notes`). Las fuentes de nicho sirven para validación cualitativa.

### Gaps
- No encontré un dataset abierto de incidentes contra-drones (por ejemplo, interceptaciones o jamming de C-UAS) fuera de bases comerciales. No investigué PAX ni bases de aeropuertos europeos (EUROCONTROL), aunque `eurocontrol.int` responde 200 — [EUROCONTROL](https://www.eurocontrol.int/)

## 6. Matriz comparativa de cobertura por zona candidata

### Takeaway
Los candidatos que cumplen las tres capas (eventos con proxy de dron, GNSS observado y terreno/clima) son **Israel/Líbano/Siria, Báltico/Kaliningrado, India–Pakistán, Myanmar y golfo Pérsico**. **Yemen, Sudán, RDC y Sahel** tienen eventos ACLED desde 1997 o 2015, pero **ninguna observación GNSS**, el mismo problema que Ucrania. Corea, Colombia, México e Irak sirven como controles con tráfico denso y poca interferencia.

### Cited Findings
- Valores de cobertura GNSS: tablas A, B y C de la sección 2 — [GPSJam CSV](https://gpsjam.org/data/2026-10-17-h3_4.csv); [Stanford heatmap](https://waas-nas.stanford.edu/data/jamming/2026/10/15/heatmap.json)
- Inicio de cobertura ACLED por país — [ACLED coverage](https://acleddata.com/knowledge-base/country-time-period-coverage); el subtipo de dron no tiene campo propio — [ACLED FAQ](https://acleddata.com/faq/how-does-acled-code-air-and-drone-strike-events)
- Licencias: ACLED con myACLED por niveles y restricción de productos secundarios — [myACLED FAQ](https://acleddata.com/myacled-faqs); UCDP CC BY 4.0 — [UCDP](https://ucdp.uu.se/downloads/); Stanford CC BY-NC 4.0 — [Stanford](https://rfi.stanford.edu/resources); OpenSky solo para investigación sin fines de lucro — [OpenSky ToU](https://opensky-network.org/about/terms-of-use); Open-Meteo no comercial, CC BY 4.0 — [Open-Meteo](https://open-meteo.com/en/terms); GLO-30 con excepción de Armenia y Azerbaiyán — [ASF](https://hyp3-docs.asf.alaska.edu/dems/)

### Inferences
Matriz construida con los hallazgos citados arriba. "Frente/zona" se refiere a la disponibilidad de un mapa abierto de control territorial verificado en esta investigación. En todos los casos se puede usar ACLED o UCDP como proxy de puntos de evento; los mapas de control específicos quedan para las notas regionales.

| Zona | Frente/zona (mapa de control abierto) | Eventos con subtipo dron | GNSS GPSJam (7 días): % celdas con datos; rojas/día | GNSS Stanford 15-oct: celdas; >10 % denoised | Terreno/clima | Licencias/restricciones | Uso en simulador |
|---|---|---|---|---|---|---|---|
| Israel/Líbano/Siria | No verificado (ISW/CTP y Liveuamap bloquean el acceso automatizado) | ACLED desde 2016 (Siria 2017), Air/drone strike + notes; Airwars (Siria, Palestina); UCDP | 58 %; 24,1 (13–39) **alta** | 222; 65 (+ spoofing: 1 evento, 62 celdas) | Completo | ACLED por nivel; Stanford NC | **A: calibrar jammer real** |
| Mar Rojo sur/Yemen | No verificado | ACLED desde 2015; Airwars, TBIJ (hasta 2020) y New America (EE. UU.) | 0 %; 0 **sin datos** | 15; 5 (56 aeronaves, ruido) | Completo | AIS spoofing solo comercial (Windward) | C: solo sintético |
| Irak | No verificado | ACLED desde 2016; UCDP | 23 %; 0,9 | 198; 7 (+ spoofing: 1 evento) | Completo | — | B/A débil |
| Golfo Pérsico/Ormuz (+ Irán) | No aplica (marítimo); Irán no verificado | ACLED Irán 2016, Arabia Saudí 2015 | 70 %; 14,1 (2–55) **alta y variable** | 266; 32 | Completo | AIS comercial | **A** |
| Báltico/Kaliningrado | No aplica (sin frente terrestre) | ACLED países bálticos y Polonia 2020, Rusia 2018 (pocos eventos armados; inferencia) | 92 %; 81,4 **muy alta**; Kaliningrado 68 %; 7,3 | 516; 188 (+ spoofing: 2 eventos) | Completo | — | **A (mejor señal GNSS del mundo)** |
| Península coreana | DMZ estática (inferencia) | ACLED desde 2018 | 49 %; 0,3 | 247; 0 | Completo | — | B: control |
| India–Pakistán | LoC estática (inferencia) | ACLED Pakistán 2010, India 2016; New America/TBIJ (Pakistán, histórico) | 80 %; 53,3 (39–71) **alta** | 598; 20 (+ spoofing: 1 evento) | Completo | — | **A** |
| Myanmar | No verificado | ACLED desde 2010 | 40 %; 30,6 (24–39) **alta** | 278; 43 (+ spoofing: 1 evento) | Completo | — | **A** |
| Sudán | No verificado | ACLED desde 1997 | 0,6 %; 0,6 **sin datos** | 45; 11 (349 aeronaves, ruido) | Completo (WorldCover África 76,5 %) | — | C |
| RDC oriental | No verificado | ACLED desde 1997 | 0 %; 0 **sin datos** | 35; 2 | Completo | — | C |
| Sahel | No verificado | ACLED desde 1997 | 0,7 %; 0 **sin datos** | 19; 0 | Completo | — | C |
| Colombia | No verificado | ACLED desde 2018 | 40 %; 0,3 | 581; 15 | Completo | — | B: control |
| México | No verificado | ACLED desde 2018 | 63 %; 0,9 | 1 815; 111 (umbral ruidoso) | Completo | — | B: control |
| **Ucrania frente (contraste)** | DeepStateMap (ya en uso) | ACLED desde 2018 | 3 %; 0 **sin datos** | 0; 0 | Completo | — | Hueco conocido |

- Para cumplir la rúbrica (3 fuentes de metadatos y 3 de amenaza, cargables en JSON/PostGIS) en una zona fuera de Ucrania, la combinación más robusta y sin credenciales es: **metadatos** = WorldCover + Copernicus GLO-30 + Open-Meteo (o Meta CHM); **amenaza** = GPSJam CSV + Stanford RFI JSON + UCDP GED/Candidate CSV, con ACLED como complemento si la cuenta institucional lo permite. Las seis fuentes usan o se convierten a lat/lon o H3 res-4.
- **Recomendación para el caso de estudio:** el Báltico, o Israel/Líbano, como zona con interferencia observada y cobertura de casi 60–95 % de las celdas. Sudán o el Sahel como segundo caso, para mostrar que el hueco de observación de Ucrania es estructural (sin ADS-B civil) y no exclusivo de ese frente.

### Gaps
- La columna "frente/zona" no se pudo completar con fuentes primarias. ISW, CTP y Liveuamap devolvieron 403 y la búsqueda de mapas de control por país corresponde a las notas regionales.
- No se calculó la serie histórica 2022–2026 por zona. La semana analizada puede no ser representativa: por ejemplo, el golfo Pérsico varía entre 2 y 55 celdas rojas por día.

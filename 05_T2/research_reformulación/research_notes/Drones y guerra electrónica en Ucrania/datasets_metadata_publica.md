# Catálogo de fuentes públicas de "metadata" aplicada y de "amenazas/fallas" para ruteo resiliente de UAV (guerra Rusia–Ucrania)

Fecha de verificación de todas las entradas: **2026-10-18**, salvo que se indique otra cosa. "Verificado" significa que en esta sesión se descargó o consultó el endpoint, o se leyó la página oficial. Las afirmaciones que no se pudieron comprobar están en "Gaps".

Criterio de seguridad aplicado: solo se catalogan datos agregados y publicados (polígonos de control con retraso diario, celdas de interferencia de 24 h, eventos ya codificados, alertas históricas). **No** se recomienda usar capas de posiciones de unidades ni flujos en tiempo real. Ver la nota sobre DeepState en la sección 1.

---

## 1. Frente / control territorial: ¿qué fuentes descargables existen y cuáles se pueden usar legalmente?

### Takeaway
La única fuente de control territorial que es **diaria, descargable en GeoJSON y sin credenciales** es DeepStateMap: tiene una API no documentada con historial desde 2022-04-03 y un espejo comunitario en GitHub con snapshots diarios desde 2024-07-08. Los servicios ArcGIS de ISW/Critical Threats sí se pueden consultar técnicamente, pero su licencia **prohíbe usarlos sin consentimiento escrito de ISW**, así que no sirven para un proyecto que se publique.

### Cited Findings

**1.1 DeepStateMap: API no documentada (fuente primaria)**
- Endpoints verificados el 2026-10-18:
  - `https://deepstatemap.live/api/history/public` devuelve la lista de snapshots: 1.788 entradas, desde 2022-04-03 hasta 2026-10-17.
  - `https://deepstatemap.live/api/history/last` devuelve el último FeatureCollection.
  - `https://deepstatemap.live/api/history/{id}/geojson` devuelve un snapshot histórico. Se probó con id=1713995636, que corresponde a abril de 2024, y respondió HTTP 200 con 578 KB. — [DeepState API history/public](https://deepstatemap.live/api/history/public); [DeepState API last](https://deepstatemap.live/api/history/last)
- Contenido del último snapshot, analizado en esta sesión: 524 features. Los polígonos se nombran en ucraniano e inglés separados por "///":
  - "Окуповано /// Occupied" (ocupado)
  - "Звільнено /// Liberated" (liberado)
  - "Статус невідомий /// Unknown status" (estado desconocido, 31 polígonos; funciona como "zona gris")
  - "ОРДЛО /// CADR and CALR"
  - "Окупований Крим" (Crimea ocupada)
  - **Además trae Points de "Напрямок удару /// Direction of attack" (60) y ubicaciones de unidades militares concretas** (por ejemplo, "138-ма окрема мотострілецька бригада"). — [DeepState API last](https://deepstatemap.live/api/history/last)
- Coordenadas en EPSG:4326 con una tercera coordenada 0 (Z). — [DeepState API last](https://deepstatemap.live/api/history/last)
- No se encontró licencia ni términos de uso publicados en el sitio. — [deepstatemap.live](https://deepstatemap.live/)

**1.2 Espejo comunitario cyterat/deepstate-map-data (GitHub)**
- Contenido: GeoJSON diario con la capa "Occupied" disuelta en un MultiPolygon. El script filtra los nombres 'CADR and CALR', 'Occupied' y 'Occupied Crimea' y luego aplica `union_all()`. Toma los datos de `https://deepstatemap.live/api/history/last`. — [download-geojson.py](https://raw.githubusercontent.com/cyterat/deepstate-map-data/main/scripts/download-geojson.py)
- Archivos: `data/deepstatemap_data_<YYYYMMDD>.geojson`, más un consolidado `deepstate-map-data.geojson.gz` con columnas `id`, `date` y `geometry`. Se actualiza a diario cerca de las 03:00 UTC mediante GitHub Actions. Licencia del repositorio: GPL-3.0. — [cyterat/deepstate-map-data](https://github.com/cyterat/deepstate-map-data)
- Verificado: hay 826 archivos diarios entre `deepstatemap_data_20240708.geojson` y `deepstatemap_data_20261018.geojson`, y el último commit es del 2026-10-18 a las 07:47 UTC. — [GitHub API contents](https://api.github.com/repos/cyterat/deepstate-map-data/contents/data)
- Advertencia del autor: los features se solapan mucho y cambian poco de un día a otro, así que conviene filtrar por `date`. — [cyterat/deepstate-map-data](https://github.com/cyterat/deepstate-map-data)

**1.3 longlinecode/russo-ukrainian-front-daily (GitHub, creado el 2026-09-01)**
- Publica el feed `data/latest.geojson` con tres elementos: el área bajo control ruso, la **línea de contacto** (`kind: contact_line`, "derived from DeepStateMap") y el territorio ruso en manos ucranianas (geometría esquemática basada en ISW). Se actualiza a diario a las 04:10 UTC. — [README](https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md)
- Fuentes por período:
  - Desde 2024-07-08: DeepState, a través del espejo de cyterat.
  - Entre 2022-02-24 y 2024-07-07: solo 16 fechas clave, reconstruidas a partir de ISW/Critical Threats, con una precisión de unos 5–10 km. — [README](https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md)
- Sesgos que declara el autor:
  - ISW cartografía la máxima extensión del avance y por eso **sobreestima** el control ruso frente a tácticas de infiltración.
  - DeepState **retrasa la publicación de avances ucranianos** por seguridad operacional.
  - Entre ambas fuentes hay una diferencia de unos 1.400 km².
  - "Infiltración no es control".
  - Algunos sectores no tienen una línea continua. — [README](https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md)
- El repositorio no declara licencia (la API de GitHub devuelve `license: null`) y pide atribuir los datos a "© DeepStateMap.Live". — [GitHub API repo](https://api.github.com/repos/longlinecode/russo-ukrainian-front-daily); [README](https://raw.githubusercontent.com/longlinecode/russo-ukrainian-front-daily/main/README.md)

**1.4 ISW / Critical Threats: servicios ArcGIS públicos, con licencia restrictiva**
- La organización ArcGIS `services5.arcgis.com/SaBe5HMtmnbqSWlu` tiene 326 servicios. Entre ellos:
  - `VIEW_RussiaCoTinUkraine_V3`, capa 49 "Assessed Russian-controlled Ukrainian Territory"
  - `AssessedRussianAdvanceInUkraine_V2_view`
  - `ClaimedRussianTerritoryinUkraine_V2_view` (82 polígonos)
  - `MDS_AssessedRussianInfiltrationAreasinUkraine_V3_view`
  - Varias capas mensuales, por ejemplo `Assessed_Russian_Advances_in_May_2026_view`. — [ArcGIS REST directory ISW](https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services)
- Los ítems `VIEW_RussiaCoTinUkraine_V2` (modificado el 2026-09-23) y `AssessedRussianAdvanceInUkraine_V2 view` (2026-09-13) tienen el owner `gbarros_understandingwar` y esta licencia: **"This geodata is the exclusive intellectual property of the Institute for the Study of War (ISW). You may not use this geodata without the written consent of ISW."** — [ArcGIS Online search API](https://www.arcgis.com/sharing/rest/search?q=owner:gbarros_understandingwar%20AND%20(title:VIEW_RussiaCoTinUkraine_V2%20OR%20title:AssessedRussianAdvanceInUkraine_V2)&f=json)
- La capa "AssessedRussianAdvance" está rotulada explícitamente como "This is not CoT" (no es control del terreno). — [ArcGIS Online search API](https://www.arcgis.com/sharing/rest/search?q=owner:gbarros_understandingwar%20AND%20(title:VIEW_RussiaCoTinUkraine_V2%20OR%20title:AssessedRussianAdvanceInUkraine_V2)&f=json)
- Servicios antiguos como `OCTclaim` (editado en noviembre de 2022) admiten consultas en JSON, GeoJSON y PBF, en Web Mercator. — [OCTclaim layers](https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/OCTclaim/FeatureServer/layers)

**1.5 Fortificaciones**
- ISW publica en ArcGIS dos servicios de fortificaciones:
  - `Russian_Field_Fortifications`: 5.963 puntos, ítem modificado el 2025-01-02.
  - `RUAF_Field_Fortifications_Polylines`: 12.169 polilíneas. Sus campos (Name, FolderPath, SymbolID, AltMode, PopupInfo…) indican que provienen de KML. Última edición: 2025-07-01.
  - En la búsqueda, el campo licenseInfo de estos ítems aparecía vacío. — [ArcGIS REST ISW](https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/RUAF_Field_Fortifications_Polylines/FeatureServer/0?f=json); [ArcGIS Online search](https://www.arcgis.com/sharing/rest/search?q=title:%22Field%20Fortifications%22&f=json)
- Brady Africk: Texty publica un mapa interactivo de las fortificaciones rusas basado en sus datos satelitales, que se actualizan con regularidad. El autor advierte que **no es un inventario completo**, que no distingue barreras de trincheras y que parte de las posiciones ya no están ocupadas. No se encontró una descarga directa. — [Texty.org.ua](https://texty.org.ua/fragments/109478/interaktyvna-karta-ukriplen-rosijskyh-okupantiv-v-ukrayini/)

**1.6 Wikimedia**
- `File:2022 Russian invasion of Ukraine.svg` tiene licencia CC BY-SA 4.0 y su última revisión es del 2026-04-24. Es un SVG cartográfico, no un dato vectorial georreferenciado. — [Commons API](https://commons.wikimedia.org/w/api.php?action=query&titles=File:2022_Russian_invasion_of_Ukraine.svg&prop=imageinfo&iiprop=extmetadata|timestamp&format=json)

**1.7 Productos derivados en HDX**
- NRC "Frontline hromada buffer analysis": XLSX por hromada con bandas de distancia al frente, publicado cada dos semanas entre 2024-08 y 2025-12. El último archivo es `NRC_Frontline_Buffer_data_01_December_2025.xlsx`. Licencia CC BY.
  - Metodología: "ARCGIS Frontline Data (Aligned with ISW and AEI's Critical Threat Project)" combinado con los shapefiles de OCHA.
  - Advertencia del propio dataset: solo para planificación. — [HDX package_show nrc-frontline-hromada-buffer-analysis](https://data.humdata.org/api/3/action/package_show?id=nrc-frontline-hromada-buffer-analysis)

### Inferences
- **Fuente recomendada para la "zona operacional":** el espejo de cyterat (MultiPolygon diario ya limpio, sin Points) o la API de DeepState **filtrando solo los Polygons**. Se descartan explícitamente los Points de unidades y "direcciones de ataque", para no compilar posiciones militares.
- Para el proyecto basta un **snapshot histórico fijo** (por ejemplo, una fecha de 2025) y no hace falta un pipeline en tiempo real. Eso además cumple la restricción de no usar datos de targeting.
- **Atributos por arista en PostGIS:**
  - Clasificación de zona: `ST_Intersects(arista, ocupado)` da "ocupado", `ST_Intersects(arista, desconocido)` da "gris" y el resto es "control UA".
  - Distancia de cada arista a la línea de contacto: `d_front = ST_Distance(ST_LineInterpolatePoint(edge,0.5)::geography, contacto::geography)`. La línea se puede usar tal como viene en longlinecode o derivarse con `ST_Boundary(ocupado)` y recortarse con el borde internacional.
  - Riesgo derivado: por ejemplo, `r_front = exp(-d_front/λ)`, con λ como parámetro de escenario sometido a análisis de sensibilidad.
- La zona gris ("Unknown status") se puede modelar como un multiplicador de riesgo mayor, o como un tramo prohibido para un dron de reconocimiento propio.
- Por licencia, los datos de ISW (y el NRC, que deriva de ellos) sirven solo como validación cualitativa. No deben cargarse ni redistribuirse sin permiso de ISW. El NRC está en CC BY en HDX, pero su insumo es ISW, una zona legal gris.

### Gaps
- No hay términos de uso explícitos de DeepStateMap. Tampoco está claro si la GPL-3.0 del espejo puede cubrir datos de terceros. Recomendación: atribuir "© DeepStateMap.Live", no redistribuir en bloque y publicar solo productos derivados (distancias o zonas).
- No se verificó "Ukraine Control Map" (sitio de Suriyak u otros) ni su licencia.
- No se encontró un dataset descargable de Brady Africk/AEI. Las capas de fortificaciones de ISW no tienen una licencia clara.

---

## 2. Interferencia GNSS (jamming/spoofing): ¿qué datos abiertos hay y cubren el frente?

### Takeaway
GPSJam publica **CSV diarios sin credenciales**: celdas H3 de resolución 4, con conteos de aeronaves con NACp bueno o malo, desde 2022-02-14 y al día. Es la única fuente diaria descargable de interferencia GNSS. Pero el análisis propio de esta sesión muestra que **sobre el frente oriental casi no hay datos**, porque no hay tráfico ADS-B: el espacio aéreo civil ucraniano está cerrado. Sirve como capa regional (mar Negro, Moldavia/Rumania, Belarús/Polonia, Crimea), y el frente debe imputarse por escenario.

### Cited Findings

**2.1 GPSJam (gpsjam.org)**
- **Datos verificados:**
  - Descarga diaria: `https://gpsjam.org/data/{YYYY-MM-DD}-h3_4.csv`. El contenido viene comprimido en gzip aunque la extensión sea .csv.
  - Columnas: `hex,count_good_aircraft,count_bad_aircraft`.
  - Manifiesto: `https://gpsjam.org/data/manifest.csv`, con fechas hasta el 2026-10-17.
  - Archivo del 2026-10-17: 47.602 celdas a nivel mundial. — [GPSJam CSV 2025-10-01](https://gpsjam.org/data/2025-10-01-h3_4.csv); [GPSJam manifest](https://gpsjam.org/data/manifest.csv)
- **Resolución H3 4** (verificada con `h3.get_resolution`): área media de 1.770,3 km² por hexágono y arista media de 26,07 km. — [H3 resolution table](https://h3geo.org/docs/core-library/restable/)
- **Metodología:**
  - Usa el NACp que reportan las aeronaves por ADS-B, agregado en 24 h.
  - Fuentes: airplanes.live y ADS-B Exchange, deduplicadas por aeronave.
  - Fórmula: `percent_bad = 100*(bad-1)/(good+bad)`. Se resta 1 para evitar falsos positivos en celdas con poco tráfico.
  - Umbrales: verde >98 % bueno, amarillo 2–10 % malo, rojo >10 % malo. — [GPSJam FAQ](https://gpsjam.org/faq)
- **Cobertura temporal y actualización:**
  - Datos desde 2022-02-14 (el primer día está incompleto), con huecos documentados: 2022-06-08/09, 2022-10-13/14, 2024-07-14/15, 2025-01-08/09 y otros.
  - Se actualiza cada 24 h, poco después de medianoche UTC. — [GPSJam FAQ](https://gpsjam.org/faq)
- **Sesgos declarados:**
  - El NACp no indica qué sistema de navegación se degradó.
  - Un NACp bajo no siempre significa jamming.
  - Una interferencia breve puede bastar para pintar un día de rojo.
  - Las aeronaves "ven" más fuentes que un receptor en tierra.
  - Una celda vacía indica que no hubo tráfico ni receptores, "such as in active war zones". — [GPSJam FAQ](https://gpsjam.org/faq)
- **Licencia:** la FAQ no declara licencia ni términos. Solo dice que el sitio es gratuito y pide donaciones. — [GPSJam FAQ](https://gpsjam.org/faq)
- **Análisis propio de esta sesión** (h3-py sobre los CSV del 2025-10-01 y del 2026-10-17):
  - En el recuadro aproximado del frente (34–40°E, 46–51°N) solo hubo 2 y 1 celdas con datos, respectivamente, con 1–2 aeronaves cada una y 0 celdas rojas.
  - En el recuadro amplio de Ucrania (22–40,3°E, 44,3–52,4°N) hubo 204 y 174 celdas con datos. El 2026-10-17 se marcaron 35 rojas: 33 al oeste de 30°E (Rumania, Moldavia, la frontera Polonia–Belarús) y 2 en la costa de Crimea, cerca de Sebastopol. — [GPSJam CSV 2026-10-17](https://gpsjam.org/data/2026-10-17-h3_4.csv)

**2.2 Flightradar24, mapa de GPS jamming**
- Se basa en el NIC de ADS-B y se muestra en ventanas de 6 h o 24 h. Solo usa áreas con suficientes vuelos y receptores, y por eso Ucrania apareció sin color en la cobertura inicial.
- No se encontró ninguna opción de descarga. — [FR24 blog](https://www.flightradar24.com/blog/inside-flightradar24/gps-jamming-map/); [Maproom blog](https://www.maproomblog.com/2024/03/flightradar24s-map-of-gps-interference/)

**2.3 SkAI Data Services (spin-off de ZHAW)**
- Tracker gratuito en `spoofing.skai-data-services.com`. Usa ADS-B de OpenSky para marcar aeronaves con posible spoofing y muestra hexágonos de posible jamming de las últimas horas.
- En mayo de 2024, uno de sus hotspots principales era Sebastopol (mar Negro). Su red tiene menos cobertura que otros sitios ADS-B.
- No se encontró descarga. — [OPSGROUP "Where is the spoofing today"](https://ops.group/blog/where-is-the-spoofing-today/)

**2.4 OpenSky Network: datos crudos para calcular interferencia propia**
- **Licencia:** uso limitado, no exclusivo, intransferible, "solely for the purpose of non-profit research and non-profit education".
- Las entidades comerciales (incluidos contratistas gubernamentales y militares) necesitan licencia escrita.
- El uso "operacional" de la REST API, incluso en sistemas internos automatizados, requiere un acuerdo escrito previo. — [OpenSky Terms of Use](https://opensky-network.org/about/terms-of-use)
- **Receta académica (Felux et al., 2024, *NAVIGATION* 71(3), navi.657, open access CC BY 4.0):**
  - Usaron las tablas `state_vectors_data4` y `operational_status_data4` (NACp) de OpenSky con la librería `traffic`.
  - Marcaron como afectado un vuelo con NACp=0 durante más de 1 min dentro del área de interés y NACp>7 durante más de 1 min en el resto del período.
  - Período: febrero a diciembre de 2022. En el área Rumania/Bulgaria/Moldavia/mar Negro occidental quedaron afectados 27.911 de 432.290 vuelos.
  - Los autores advierten que la red terrestre de receptores ve solo un subconjunto de los vuelos y usaron gpsjam.org para contrastar. — [Felux et al. 2024](https://navi.ion.org/custom-print/150266)
- **Contraste a nivel de suelo:** un estudio de GPSPATRON y la Universidad Marítima de Gdynia (junio–noviembre de 2024, costa polaca) registró 84 h de interferencia, sobre todo jamming, y **no encontró correlación con las detecciones basadas en ADS-B**. Durante los eventos, el error de posición subió de 3–5 m a más de 35 m. — [Shipping Telegraph](https://shippingtelegraph.com/shipping-reports/gnss-interference-became-a-growing-challenge-in-baltic-sea/); [Safety4Sea](https://safety4sea.com/study-shows-gnss-interference-in-the-baltic-sea)

### Inferences
- **Paso de GPSJam a atributos por zona o arista:**
  - Cargar las celdas H3 como polígonos, ya sea con `h3.cell_to_boundary` en Python al exportar a GeoJSON o con la extensión h3-pg de PostgreSQL (verificar disponibilidad).
  - Calcular por celda `p_red_30d`, la fracción de días rojos en una ventana de 30 días, y `pct_bad_medio`, recortando valores negativos a 0.
  - Por arista: el máximo, o la media ponderada por longitud, de las celdas que intersecta.
- **Imputación obligatoria en el frente:** para celdas sin datos situadas a menos de X km de la línea de contacto de DeepState, asignar una `p_jam` de escenario (por ejemplo, alta o muy alta). Para celdas sin datos en la retaguardia, usar el valor regional o el vecino más cercano. Hay que documentar que **la capa GNSS en el frente es un supuesto y no una medición**. Ese es el argumento honesto para la "falla" de EW.
- La escala de H3 res 4 (unos 26 km de arista) es gruesa frente a drones tácticos. Conviene presentarla como "probabilidad regional de denegación GNSS", no como huella de un jammer.
- Por la falta de correlación entre ADS-B y suelo en el Báltico, la capa ADS-B (tomada a altitud de crucero) **no representa directamente** lo que vive un dron a 50–150 m de altura. Debe tratarse como un indicador de presencia de EW, no de intensidad local.
- Calcular la interferencia desde OpenSky es viable para la academia (licencia de investigación sin fines de lucro), pero sobre Ucrania tendría la misma falta de tráfico que GPSJam. No aporta cobertura extra en el frente.

### Gaps
- GPSJam no tiene licencia explícita. Se recomienda no redistribuir los CSV crudos y publicar el script de descarga junto con productos derivados, o escribir al autor (el contacto figura en la FAQ).
- No se verificaron el proceso actual ni la elegibilidad para acceder a OpenSky Trino (la página dio 403).
- No se encontró un dataset abierto de interferencia GNSS **a nivel de suelo** sobre Ucrania, ni un paper 2024–2025 específico de Ucrania con datos liberados.

---

## 3. Eventos de conflicto (ataques con drones, artillería, misiles): ¿qué datasets sirven y con qué licencias?

### Takeaway
ACLED es la fuente con mejor tipología: incluye el subtipo "Air/drone strike" y "Shelling/artillery/missile attack". Pero los datos por evento exigen una cuenta myACLED, la API solo está disponible desde el nivel "Research" (correo institucional) y la EULA **prohíbe redistribuir** y exige que los derivados sean transformativos. Las alternativas sin credenciales son UCDP GED vía HDX (CSV, hasta 2024-12), el JSON de Bellingcat (2.517 incidentes georreferenciados, hasta 2025-07) y el dataset de Kaggle de ataques masivos con misiles y drones (CC BY-NC-SA, actualizado al 2026-10-17, con resolución por oblast o ciudad objetivo).

### Cited Findings

**3.1 ACLED**
- **API:**
  - Base `https://acleddata.com/api/`, endpoint `/api/acled/read`.
  - Autenticación OAuth: `POST https://acleddata.com/oauth/token` con `grant_type=password`, `client_id=acled`, `scope=authenticated` y el usuario y contraseña de myACLED. El token dura 24 h y el refresh token, 14 días.
  - Formato JSON por defecto o CSV con `_format=csv`. Por defecto devuelve 5.000 filas y admite paginación. — [ACLED API getting started](https://acleddata.com/api-documentation/getting-started)
  - El sistema anterior de claves dejó de funcionar el 15 de septiembre de 2025. — [ACLED myACLED FAQ](https://acleddata.com/myacled-faqs)
- **Niveles de acceso:** Open, Research, Partner y Enterprise. El nivel se asigna según el dominio del correo, y un correo genérico como gmail recibe Open. **La API solo está disponible para Research, Partner y Enterprise.** Según la tabla, Research recibe "Aggregated Data + Event Data (lagged)". — [ACLED myACLED FAQ](https://acleddata.com/myacled-faqs)
- **EULA (actualizada el 8 de julio de 2025):**
  - Licencia "for non-commercial purposes".
  - Prohíbe "provide, permit, or allow direct access to any of the Licensed Content".
  - Los materiales externos "must be transformative, such that they cannot be reverse engineered". No basta con complementar, reordenar o mostrar en un dashboard propio.
  - Prohíbe el scraping.
  - Al terminar la licencia hay que borrar los datos. — [ACLED EULA](https://acleddata.com/eula)
- **Tipología:** "Air/drone strike" se define como cualquier ataque aire-tierra con aeronaves o drones sin otro enfrentamiento. Se registra un solo evento por fecha, lugar y actores. — [ACLED FAQ air/drone strikes](https://acleddata.com/faq/how-does-acled-code-air-and-drone-strike-events)
  - Los subtipos de "Explosions/Remote violence" incluyen air/drone strike, shelling/artillery/missile attack y remote explosive/landmine/IED. — [EUAA (cita del codebook ACLED)](https://www.euaa.europa.eu/print/pdf/node/28988)
- **En HDX, ACLED solo publica agregados** por país-año y país-mes (XLSX de eventos de violencia política, ataques contra civiles y manifestaciones). Cobertura de Ucrania: 2018-01-01 a 2026-10-09, con actualización semanal. — [HDX ukraine-acled-conflict-data](https://data.humdata.org/api/3/action/package_show?id=ukraine-acled-conflict-data)

**3.2 UCDP GED**
- **HDX:** el CSV `conflict_data_ukr.csv` cubre 2014-01-22 a 2024-12-31. HDX lo lista como CC BY-IGO. Son eventos de violencia organizada geocodificados hasta nivel de aldea y desagregados por día. — [HDX ucdp-data-for-ukraine](https://data.humdata.org/api/3/action/package_show?id=ucdp-data-for-ukraine)
- **API:**
  - URL: `https://ucdpapi.pcr.uu.se/api/gedevents/<versión>`. La versión GED más reciente es 26.1 y existen versiones Candidate mensuales (por ejemplo 26.0.8).
  - **Requiere un token** en el header `x-ucdp-access-token`, que se pide por email al mantenedor indicando nombre, afiliación, rol y uso previsto. La respuesta tarda 3–5 días hábiles.
  - Límite de 5.000 requests/día. Gratis. — [UCDP API docs](https://ucdp.uu.se/apidocs/)

**3.3 Kaggle "Massive Missile Attacks on Ukraine" (Petro Ivaniuk)**
- Licencia CC BY-NC-SA 4.0, última actualización 2026-10-17, 916 KB. — [Kaggle API metadata](https://www.kaggle.com/api/v1/datasets/view/piterfm/massive-missile-attacks-on-ukraine)
- Contenido: misiles y drones lanzados y derribados en ataques masivos desde octubre de 2022. Se construye a mano a partir de los reportes de la Fuerza Aérea y del Estado Mayor ucranianos.
- Columnas de `missile_attacks_daily.csv`:
  - `time_start`, `time_end`, `model`, `launch_place`, `target`, `launched`, `destroyed`
  - **`not_reach_goal`** (desde julio de 2024), que incluye entre sus causas "(3) active counteraction by electronic warfare (EW) systems", además de pérdida en radar, señuelos, defectos y falta de combustible
  - `affected_region`, `num_hit_location`
- Hay una tabla auxiliar `missiles_and_uavs.csv` con guiado, costo y otros atributos.
- Aviso del autor: **"The Ukrainian Air Force has stopped reporting the number of some kind of missiles launched and intercepted since August 10, 2026"**. — [Kaggle API metadata](https://www.kaggle.com/api/v1/datasets/view/piterfm/massive-missile-attacks-on-ukraine)
- Repositorio hermano (MIT): pérdidas rusas de personal y equipo según el Estado Mayor ucraniano y Oryx. No tiene geometría. — [PetroIvaniuk/2022-Ukraine-Russia-War-Dataset](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset)

**3.4 Bellingcat "Civilian Harm in Ukraine" (TimeMap)**
- Endpoint JSON verificado: `https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json`. Contiene 2.517 registros entre 2022-02-24 y 2025-07-09, con los campos `impact, weapon_system, sources, id, description, date, location, latitude, longitude, graphic`. — [Bellingcat api.json](https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json)
- Las coordenadas publicadas se difuminan **dentro de 150 m**. Solo incluye incidentes filmados o publicados en línea, así que subestima el total. — [Bellingcat civilian harm map](https://ukraine.bellingcat.com/?id=CIV0139); [Bellingcat methodology article](https://www.bellingcat.com/news/2022/03/17/hospitals-bombed-and-apartments-destroyed-mapping-incidents-of-civilian-harm-in-ukraine/)

**3.5 Otros en HDX**
- Insecurity Insight publica datos de ataques contra la ayuda humanitaria, la educación y la salud en Ucrania (XLSX, CC BY-SA, actualizados el 2026-10-12). — [HDX search](https://data.humdata.org/api/3/action/package_search?q=ukraine%20explosive%20ordnance&rows=6)

### Inferences
- **Por arista o zona:**
  - Construir una densidad de kernel (o un conteo por hexágono H3 res 6–7) de eventos de "Air/drone strike" y "Shelling/artillery/missile attack" en una ventana de 30 días, normalizada a [0,1].
  - Asignar a cada arista el valor medio o máximo de su buffer, por ejemplo de 1–2 km.
  - Pasar ese valor a probabilidad de falla `p_kin` y luego a costo aditivo `c = -ln(1 - p)`, de modo que el camino más corto maximice la probabilidad de supervivencia.
- **ACLED y el repositorio público:** no se pueden subir los eventos crudos a GitHub, porque la EULA lo prohíbe. Lo que sí se puede publicar es la grilla de riesgo agregada y transformada, junto con el script (que pide credenciales en `.env`).
- El nivel de acceso que recibiría un correo `@mail.udp.cl` es incierto. Si cae en Open, no hay API.
- **Kaggle no tiene coordenadas por evento**, solo oblast o ciudad objetivo y lugar de lanzamiento. Sirve como **serie temporal de intensidad aérea y de EW a nivel nacional u oblast**: por ejemplo, `not_reach_goal / launched` es un proxy de la efectividad de la EW ucraniana contra drones de largo alcance. Es metadata temporal aplicada, no una capa espacial fina.
- UCDP vía HDX se descarga sin token, pero termina en 2024-12. Sirve como respaldo histórico.

### Gaps
- No se verificó qué desfase exacto tiene el nivel Research de ACLED (ACLED solo dice "lagged") ni si un estudiante UDP calificaría.
- El JSON de Bellingcat no tiene una licencia explícita, y el endpoint no está documentado (es el que usa la app TimeMap).
- No se revisaron los datasets de KSE/Texty ni los incidentes geolocalizados de CIR (Eyes on Russia), cuyo acceso parecía restringido o a pedido.
- La descarga de Kaggle requiere una cuenta y un token de la API de Kaggle (no se verificó en esta sesión; la metadata se obtuvo sin autenticación).

---

## 4. Alertas antiaéreas: ¿qué granularidad espacial tienen y cómo se obtienen?

### Takeaway
Existe un dataset histórico abierto, con licencia MIT y actualización diaria, con alertas oficiales a nivel de oblast, raion y hromada desde 2022-03-15. Desde diciembre de 2025 las alertas son mayoritariamente por **raion**. Se puede unir a los límites administrativos COD-AB de OCHA (CC BY-IGO, GeoJSON). Las APIs en vivo (alerts.in.ua y ukrainealarm) requieren un token que se pide por formulario.

### Cited Findings

**4.1 Vadimkin/ukrainian-air-raid-sirens-dataset (GitHub, MIT)**
- **Dataset oficial:** archivos `datasets/official_data_en.csv` (31 MB) y `official_data_uk.csv`, desde 2022-03-15. — [datasets/README.md](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md)
  - Columnas: `oblast,raion,hromada,level,started_at,finished_at,source`. Tiempos en UTC; `level` puede ser oblast o hromada, entre otros valores. — [official_data_en.csv](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/official_data_en.csv)
  - "Since December, 2025th there is mostly air raid alerts on raion (district) level… before sirens were applied to the whole oblast". — [datasets/README.md](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md)
- **Dataset de voluntarios:** proviene de eTryvoga, cubre desde 2022-02-25 y **solo a nivel de oblast**. Cuando falta el mensaje de fin, se marca `naive=True` con una duración fija de 30 min. — [datasets/README.md](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md)
- **Exclusiones:** dos alertas permanentes no aparecen en los datos: Luhansk (desde el 2022-04-04) y Crimea (desde el 2022-12-10). — [datasets/README.md](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md)
- **Actualización y regeneración:** el último commit es del 2026-10-18 a las 03:42 UTC. Para regenerar los datos se necesitan un app id y un hash de Telegram. — [GitHub API commits](https://api.github.com/repos/Vadimkin/ukrainian-air-raid-sirens-dataset/commits?per_page=1); [repo](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset)

**4.2 alerts.in.ua (API)**
- **Token:** se pide por formulario en `alerts.in.ua/api-request` o por correo a api@alerts.in.ua. — [alerts-in-ua-py](https://github.com/alerts-ua/alerts-in-ua-py); [PyPI alerts-in-ua](https://pypi.org/project/alerts-in-ua/0.2.3/)
- **Granularidad y tipos:** `location_type` puede ser oblast, raion, hromada o city. Tipos de alerta: air_raid, artillery_shelling, urban_fights, chemical y nuclear. Tipos de amenaza: drones, misiles balísticos y de crucero, bombas guiadas, aviación, entre otros.
- **Historial:** `get_alerts_history(..., period='week_ago'|'month_ago')`.
- **Límites:** existe un `RateLimitError`, pero no se publican umbrales. — [alerts-in-ua-py](https://github.com/alerts-ua/alerts-in-ua-py)
- La página devs.alerts.in.ua devolvió 403 por Cloudflare. — [devs.alerts.in.ua](https://devs.alerts.in.ua/)

**4.3 ukrainealarm.com (API oficial de la app "Повітряна тривога")**
- Requiere una API key que se pide por formulario. — [PyPI ua-alarm](https://pypi.org/project/ua-alarm/1.3.9/)
- Categorías: air, artillery, chemical, nuclear, urban fights y unknown. La integración de Home Assistant limita el polling a 10 s y a 5 regiones para respetar el rate limit. — [Home Assistant ukraine_alarm](https://home-assistant.io/integrations/ukraine_alarm)
- El swagger devolvió 403 por Cloudflare. — [api.ukrainealarm.com](https://api.ukrainealarm.com/swagger/index.html)

**4.4 Límites administrativos COD-AB Ucrania (OCHA, HDX)**
- Versión 05, con 27 oblasts, 139 raions, 1.769 hromadas y 29.706 asentamientos (cobertura parcial). Licencia CC BY-IGO. Archivo `ukr_admin_boundaries.geojson.zip`. Revisado el 2025-12-18.
- Advertencia: hay P-codes inconsistentes en Sebastopol y Crimea. — [HDX cod-ab-ukr](https://data.humdata.org/api/3/action/package_show?id=cod-ab-ukr)

### Inferences
- **Atributo por zona:** horas de alerta por día o semana en cada raion u hromada. Para fechas anteriores a diciembre de 2025, las alertas a nivel oblast se propagan a todos sus raions.
- **Paso a aristas:** cada arista hereda el valor del polígono que intersecta; si cruza varios, se pondera por longitud con `ST_Intersection`.
- Hay que hacer un **mapeo de nombres**: el CSV trae nombres transliterados (por ejemplo "Umanska terytorialna hromada") y COD-AB usa P-codes. Hace falta una tabla de equivalencias en el ETL.
- Cerca del frente la señal **discrimina poco**: hay alertas casi continuas y las alertas permanentes de Luhansk y Crimea están excluidas. La capa es más útil para la amenaza aérea en la retaguardia (Shahed y misiles) que para el combate táctico. Debe complementarse con FIRMS/Economist y ACLED.
- Para el proyecto basta el CSV histórico (sin credenciales). Las APIs en vivo no hacen falta y además rozan la restricción de no usar tiempo real.

### Gaps
- No se pudieron leer los términos de uso de alerts.in.ua ni de ukrainealarm (Cloudflare 403), ni sus límites numéricos.
- No está claro de qué canal o fuente exacta proviene el dataset "oficial" de Vadimkin; el README solo dice "official" y menciona Telegram.

---

## 5. Daño a edificaciones: ¿qué evaluaciones abiertas existen?

### Takeaway
Hay dos fuentes con licencia abierta y formato listo para PostGIS. Las evaluaciones UNOSAT en HDX son puntuales por ciudad (SHP/GDB, CC BY-SA o CC BY-IGO). El dataset nacional de Dietrich et al. (2025, Zenodo, CC BY 4.0) estima daño a partir de Sentinel-1 e incluye GeoJSON agregados por hromada (ADM3) y las etiquetas UNOSAT.

### Cited Findings

**5.1 Zenodo 14811504 (Dietrich et al., 2025, *Communications Earth & Environment*)**
- Licencia CC BY 4.0, publicado el 2025-02-05. Archivos:
  - `unosat_labels.geojson` (7,4 MB)
  - `unosat_aois.geojson`
  - `n_buildings_damaged_adm3_t0_655.geojson` (60,7 MB, edificios dañados por región administrativa)
  - `buildings_preds.db` (4,35 GB, huellas de Overture con estimaciones por período)
  - `ukraine_final_preds_22_23_masked.tif` (17,9 GB, mapa de calor nacional agregado de febrero de 2022 a febrero de 2024) — [Zenodo API 14811504](https://zenodo.org/api/records/14811504)
- El código es MIT y usa Sentinel-1 en Google Earth Engine, etiquetas UNOSAT y huellas de Overture Maps. DOI 10.1038/s43247-025-02183-7. — [prs-eth/ukraine-damage-mapping-tool](https://github.com/prs-eth/ukraine-damage-mapping-tool)

**5.2 UNOSAT en HDX**
- Evaluaciones de daño disponibles: Kremenchuk (2023-02-09, CC BY-SA), Mariupol (rápida de 2022-04-01, CC BY-SA, y distrito Livoberezhnyi de 2022-03-18, CC BY-IGO), ciudad de Kherson (junio de 2023, CC BY-SA) y Solontsi/Pidlisne (2023-06-15). Formatos SHP y Geodatabase.
- También hay extensión de inundación tras la rotura de Kakhovka (junio de 2023). — [HDX package_search ukraine unosat](https://data.humdata.org/api/3/action/package_search?q=ukraine%20unosat&rows=8); [HDX package_search ukraine damage assessment](https://data.humdata.org/api/3/action/package_search?q=ukraine%20damage%20assessment&rows=8)

### Inferences
- `n_buildings_damaged_adm3` permite crear un atributo por hromada, "intensidad histórica de combate o destrucción" (edificios dañados por km² o como proporción). Es un proxy de **zonas de combate sostenido**, útil como metadata de contexto, y se puede cargar directo con `ogr2ogr`.
- Las evaluaciones UNOSAT son demasiado puntuales y antiguas (2022–2023) para el frente actual. Sirven para validar.
- Ojo con la CC BY-SA: si se combinan datos UNOSAT CC BY-SA en una base que se redistribuye, el derivado hereda la cláusula share-alike.

### Gaps
- No se encontró un dataset de Microsoft AI for Good sobre daño en Ucrania en HDX (sí los hay para otros desastres).
- No se identificaron los códigos EMSR de Copernicus EMS para Ucrania; la API pública de activaciones no devolvió resultados utilizables.

---

## 6. Incendios y explosiones como proxy de combate (NASA FIRMS / The Economist)

### Takeaway
Son las mejores fuentes de "amenaza cinética" **sin credenciales y con licencia abierta**. FIRMS publica CSV anuales por país sin MAP_KEY, y su API con MAP_KEY gratuita da datos casi en tiempo real. El modelo de The Economist (CC BY 4.0) ya clasifica qué focos son "war-related", en celdas de 0,1°, y se actualizó en el repositorio el mismo 2026-10-18.

### Cited Findings

**6.1 NASA FIRMS**
- **CSV anual por país sin clave**, verificado con HTTP 200: `https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/2024/viirs-snpp_2024_Ukraine.csv`. Columnas: `latitude, longitude, bright_ti4, scan, track, acq_date, acq_time, satellite, instrument, confidence, version, bright_ti5, frp, daynight, type`. — [FIRMS country CSV Ukraine 2024](https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/2024/viirs-snpp_2024_Ukraine.csv)
- **API de área:** `/api/area/csv/[MAP_KEY]/[SOURCE]/[west,south,east,north]/[DAY_RANGE 1–5]/[DATE]`.
  - Fuentes disponibles: MODIS_NRT/SP, VIIRS_SNPP_NRT/SP, VIIRS_NOAA20_NRT/SP y VIIRS_NOAA21_NRT.
  - La MAP_KEY es gratuita. Límite de 5.000 transacciones cada 10 min. — [FIRMS API area](https://firms.modaps.eosdis.nasa.gov/api/area/)

**6.2 The Economist, war-fire model**
- **Método:**
  - Celdas de 0,1° × 0,1° por día. Un día de una celda se considera "de guerra" si su exceso de incendios tiene menos de 5 % de probabilidad en un año normal y se repite: dos eventos a menos de 50 km, separados por entre 7 y 180 días.
  - Precisión aproximada de 500 m por evento.
  - Al 19 de junio de 2024 sumaba 93.834 eventos. — [TheEconomist/the-economist-war-fire-model](https://github.com/TheEconomist/the-economist-war-fire-model)
- **Archivos:** `output-data/ukraine_war_fires.csv` y `ukraine_fires.csv`, con columnas como `LATITUDE, LONGITUDE, date, ACQ_TIME, war_fire, war_fire_restrictive, in_ukraine_held_area` y unas 30 en total.
- **Licencia:** datos CC BY 4.0 y código MIT.
- **Limitaciones:**
  - Muchos eventos no generan calor detectable, y las nubes ocultan otros.
  - La clasificación es probabilística.
  - No clasifica en olas de calor; por ejemplo, del 4 al 11 de abril de 2023 no hay eventos clasificados. — [repo README](https://github.com/TheEconomist/the-economist-war-fire-model)
- Último commit: 2026-10-18 a las 18:22 UTC, "Update FIRMS data 2026-10-18 18:22 UTC". — [GitHub API commits](https://api.github.com/repos/TheEconomist/the-economist-war-fire-model/commits?per_page=1)

### Inferences
- **Atributo por arista:** `fires_30d`, el conteo de `war_fire==1` en un buffer de 2–5 km o en las celdas de 0,1° que toca la arista durante los últimos 30 días, normalizado y convertido en `p_kin`.
- La columna `in_ukraine_held_area` permite separar el fuego del lado ruso del ucraniano.
- Es la capa de amenaza más defendible para el curso: es abierta, se descarga con `requests` en un CSV, está documentada y tiene metodología publicada.
- FIRMS crudo, sin el filtro de The Economist, mezcla quemas agrícolas. Si se usa, conviene filtrar por `confidence`, por época del año o por cercanía al frente (menos de 30 km de la línea de contacto).

### Gaps
- No se verificó una licencia explícita de FIRMS (en general, los datos de NASA son abiertos con cita).
- La resolución nominal de VIIRS (unos 375 m) y de MODIS (1 km) no se comprobó en esta sesión.
- No se midió el tamaño actual de `ukraine_war_fires.csv`.

---

## 7. Minas y contaminación por explosivos

### Takeaway
**No se encontró ningún dataset abierto descargable** (SHP, GeoJSON o API) de áreas peligrosas en Ucrania. Los mapas oficiales (el del NMAC sobre IMSMA y el del Servicio Estatal de Emergencias) solo se pueden consultar en web o en app, y son parciales.

### Cited Findings
- El National Mine Action Centre (Ministerio de Defensa) publica un mapa sobre IMSMA (GICHD) con tierras despejadas, áreas sospechosas y áreas confirmadas. Según Bellingcat, los datos son significativos pero parciales: cubren solo el lado ucraniano y la franja de unos 20 km desde el frente es inaccesible para los desminadores. — [Bellingcat 2025](https://www.bellingcat.com/news/2025/07/02/ukraines-contaminated-land-clearing-landmines-with-rakes-tractors-and-drones/)
- El Servicio Estatal de Emergencias mantiene un mapa interactivo y una app (Android e iOS) con lugares donde se encontraron peligros explosivos y su grado de amenaza. — [Gobierno de Ucrania (KMU)](https://www.kmu.gov.ua/en/news/v-ukraini-stvorena-interaktyvna-mapa-potentsiinoi-minnoi-nebezpeky-1)
- Un experto estima unos 140.000 km² potencialmente contaminados. — [Interfax-Ukraine](https://en.interfax.com.ua/news/blog/1054968.html)
- Las búsquedas en HDX de "ukraine landmine", "mine action" y "explosive ordnance" no devolvieron capas de contaminación en Ucrania. — [HDX package_search](https://data.humdata.org/api/3/action/package_search?q=ukraine%20landmine&rows=6)

### Inferences
- Para un dron, las minas son poco relevantes como falla de vuelo; solo importan para el aterrizaje o la recuperación. Si se quiere incluir, se puede modelar la "zona contaminada" como un buffer de N km desde la línea de contacto, como supuesto documentado.

### Gaps
- No se confirmó si IMSMA o el NMAC ofrecen descargas para investigadores bajo solicitud.

---

## 8. Espacio aéreo (OpenAIP, NOTAM, EASA)

### Takeaway
Todo el espacio aéreo civil de Ucrania está cerrado: las 6 FIR están cerradas por NOTAM A0021/26 y EASA mantiene el CZIB-2022-01R14 vigente hasta el 2027-01-31. Una capa de espacio aéreo civil sería **constante** en todo el país y aporta poco a la diferenciación de aristas. OpenAIP exige registro o API key y su licencia, según una fuente secundaria, es CC BY-NC.

### Cited Findings
- EASA CZIB-2022-01R14 (24 de julio de 2026): extiende la validez hasta el 31 de enero de 2027 sin cambios. Cubre todas las altitudes de las FIR de Lviv, Kyiv, Kyiv UTA, Dnipro, Simferopol y Odesa, y cita el NOTAM ucraniano A0021/26 que las cierra a la aviación civil. — [EASA Conflict Zones](https://www.easa.europa.eu/conflict-zone-information-bulletin-czibs); [EASA Airspace of Ukraine](https://www.easa.europa.eu/node/136057)
- OpenAIP:
  - La API core devuelve 403 "No authenticated user found" sin credenciales (verificado).
  - El bucket público de exportaciones por país en GCS ahora es "requester pays" (verificado).
  - Un tercero indica que la licencia es CC BY-NC 4.0. — [api.core.openaip.net](https://api.core.openaip.net/api/airspaces?country=UA&limit=1); [Airfield Directory FAQ](https://airfield.directory/pages/faq)
- OCHA publica en HDX la lista de aeródromos certificados de Ucrania (XLSX, CC BY, 2026-06-08). — [HDX search](https://data.humdata.org/api/3/action/package_search?q=ukraine%20mine%20action&rows=6)

### Inferences
- En el modelo se puede asumir "espacio aéreo segregado o militar en todo el país" sin cargar una fuente.
- Si el curso exige una capa, conviene usar aeródromos y zonas restringidas como **puntos de despegue o recuperación** y no como costo.

### Gaps
- No se verificaron las restricciones específicas para drones civiles en Ucrania (Servicio Estatal de Aviación, app "Air Space") ni si tienen datos descargables.

---

## 9. Cobertura del suelo, ocultamiento y línea de vista

### Takeaway
ESA WorldCover (10 m, CC BY 4.0), la altura de dosel de Meta/WRI (CC BY 4.0) y el Copernicus DEM GLO-30 (un DSM que incluye vegetación y edificios) se descargan sin credenciales desde AWS, y se verificaron teselas sobre Donetsk y Luhansk. **No existe un dataset abierto de franjas forestales (lesosmugi) de Ucrania.** La "aplicación" consiste en convertir estos datos genéricos en ocultamiento y enmascaramiento del enlace respecto de la línea de contacto.

### Cited Findings
- **ESA WorldCover:**
  - Versiones 2020 (v100) y 2021 (v200), unos 10 m, 11 clases, licencia CC BY 4.0.
  - Descarga: `s3://esa-worldcover/v200/2021/map` con `--no-sign-request`. Formato COG en teselas de 3×3°, EPSG:4326. — [ESA WorldCover data access](https://esa-worldcover.org/en/data-access)
  - Verificado: la tesela `ESA_WorldCover_10m_2021_v200_N48E036_Map.tif` responde HTTP 200. — [S3 tile](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N48E036_Map.tif)
- **Copernicus DEM:**
  - GLO-30 (30 m) en el bucket `copernicus-dem-30m` y GLO-90. Es un **DSM** (incluye edificios, infraestructura y vegetación), en COG.
  - Se rige por la licencia Copernicus. — [AWS Registry Copernicus DEM](https://registry.opendata.aws/copernicus-dem/)
  - Verificado: la tesela N48 E037 responde HTTP 200. — [S3 tile](https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N48_00_E037_00_DEM/Copernicus_DSM_COG_10_N48_00_E037_00_DEM.tif)
- **Altura de dosel Meta/WRI:**
  - Cobertura global, resolución submétrica, licencia CC BY 4.0.
  - Ruta: `s3://dataforgood-fb-data/forests/v1/alsgedi_global_v6_float/`. Formato GeoTIFF o COG, sin cuenta AWS.
  - Las imágenes de origen son de Maxar (© 2016 según el registro). — [AWS Registry Meta/WRI CHM](https://registry.opendata.aws/dataforgood-fb-forests/)
- **Franjas forestales:** no hay un dataset publicado. Un paper sugiere como trabajo futuro "mapping shelterbelts using classification methods". El proyecto de IAMO (financiado por la fundación alemana para la investigación de la paz) planea documentar las franjas en 6 regiones del sureste ucraniano. — [EarthDoc](https://www.earthdoc.org/content/papers/10.3997/2214-4609.2025510130); [Bundesstiftung Friedensforschung](https://bundesstiftung-friedensforschung.de/en/2026/03/16/assessment-of-war-damage-and-strategy-for-restoration/)

### Inferences
- **Índice de ocultamiento por arista:** `% de píxeles WorldCover clase 10 (Tree cover)` en un buffer de 50–100 m, más la media de altura de dosel (Meta). Las franjas forestales lineales (tree rows) aparecen en WorldCover y en el CHM aunque no exista un dataset específico. OSM `natural=tree_row` es otra opción (ODbL, share-alike en la base).
- **Exposición o línea de vista:** calcular un viewshed sobre el DSM GLO-30 desde puntos muestreados de la línea de contacto (por ejemplo, con GRASS `r.viewshed` o `gdal_viewshed`) y asignar a cada arista la fracción visible. Eso aproxima la exposición a la detección visual o por radar y a la EW con línea de vista. También puede modelar la pérdida de enlace con la estación terrena (GCS), calculando el viewshed desde la GCS.
- Así, una fuente "genérica" (DEM o cobertura) se vuelve **aplicada**, porque la métrica se define respecto de la amenaza: visibilidad desde el frente y enmascaramiento del enlace.

### Gaps
- No se verificó la cobertura de Ucrania en el HRL Tree Cover de Copernicus. Probablemente no la tiene, porque el HRL cubre los países EEA38 más el Reino Unido, pero hay que confirmarlo.
- No se verificó el ETH Global Canopy Height 10 m.
- Tampoco el año exacto de las imágenes del CHM de Meta para Ucrania.

---

## 10. Datasets académicos de RF y jamming para drones (no espaciales)

### Takeaway
Hay datasets abiertos de señales RF de drones y de jamming o spoofing GNSS: DroneRF, UAV Attack Dataset, TEXBAT, OAKBAT y grabaciones IQ de LINKS en Zenodo. **Ninguno es geoespacial ni de Ucrania.** Sirven para parametrizar los modelos de falla (probabilidad de pérdida de GNSS o de enlace), no como capa del grafo. **No se encontraron datos públicos de ocupación del espectro en Ucrania.**

### Cited Findings
- **DroneRF:** Mendeley Data, DOI 10.17632/f4c2b4n755.1, publicado el 2019-03-02 por la Universidad de Qatar. Contiene 227 segmentos de 3 drones más el fondo RF. Licencia CC BY 4.0 (verificada en la página). — [Mendeley DroneRF](https://data.mendeley.com/datasets/f4c2b4n755/1); [Data in Brief (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6727013/)
- **UAV Attack Dataset:** IEEE DataPort, DOI 10.21227/00dg-0d12, de acceso abierto. Incluye logs de vuelo simulados y reales con spoofing y jamming en una instalación blindada. Última actualización: diciembre de 2023. — [IEEE DataPort](https://ieee-dataport.org/open-access/uav-attack-dataset)
- **GPS Spoofing Detection on UAS:** Mendeley, DOI 10.17632/z7dj3yyzt8.3, de octubre de 2022, de la Universidad de Dakota del Norte. Solo cubre spoofing. — [Mendeley](https://data.mendeley.com/datasets/z7dj3yyzt8/3)
- **TEXBAT:** grabaciones de spoofing GPS L1 C/A (25 Msps, 20 MHz, 16 bits). — [UT Radionavigation Lab public datasets](https://radionavlab.ae.utexas.edu/research/public-datasets-and-code/)
- **OAKBAT:** ORNL, 2020, DOI 10.13139/ORNLNCCS/1664429. Hoy exige registro. — [ORNL OAKBAT](https://impact.ornl.gov/en/datasets/oak-ridge-spoofing-and-interference-test-battery-oakbat-pure-tone/); [arXiv 2511.00491](https://arxiv.org/pdf/2511.00491)
- **LINKS Foundation (Zenodo 14859481):** grabaciones IQ de la banda L1 con jamming triangular a 10 MHz, int8 complejo, unos 19,8 GB. Licencia CC BY 4.0, publicadas el 2025-02-12. — [Zenodo 14859481](https://zenodo.org/records/14859481)

### Inferences
- **Uso en el proyecto:** como fuente bibliográfica o empírica para fijar funciones de falla, por ejemplo la probabilidad de pérdida de fix GNSS en función de la relación jamming/señal o de la distancia al jammer. Luego esas funciones se aplican espacialmente usando la capa de zonas EW (sección 2) y la distancia al frente (sección 1).
- No conviene contarlos como una de las "3 fuentes de amenaza" del curso, porque no producen atributos por arista.

### Gaps
- No se encontró ningún dataset público de ocupación del espectro ni de mediciones RF en Ucrania. Es lo esperable por razones de seguridad.

---

## 11. Meteorología aplicada al vuelo (Open-Meteo / ERA5)

### Takeaway
Open-Meteo entrega viento histórico sin clave: a 10 m y 100 m (archivo basado en ERA5) y a 80, 120 y 180 m (APIs forecast e historical-forecast), con licencia CC BY 4.0 y un nivel gratuito no comercial que admite investigación pública y uso educativo.

### Cited Findings
- **Archivo:** `archive-api.open-meteo.com/v1/archive` devolvió `wind_speed_10m`, `wind_speed_100m`, `wind_gusts_10m`, `cloud_cover_low` y `visibility` para 48,6°N 37,8°E el 2025-08-01 (verificado). — [Open-Meteo archive query](https://archive-api.open-meteo.com/v1/archive?latitude=48.6&longitude=37.8&start_date=2025-08-01&end_date=2025-08-01&hourly=wind_speed_10m,wind_speed_100m,wind_gusts_10m,cloud_cover_low,visibility&wind_speed_unit=ms)
- **Historical-forecast:** devolvió `wind_speed_80m` y `wind_speed_120m` para la misma fecha y lugar (verificado). — [Open-Meteo historical-forecast query](https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=48.6&longitude=37.8&start_date=2025-08-01&end_date=2025-08-01&hourly=wind_speed_80m,wind_speed_120m)
- **Términos:**
  - Datos bajo CC BY 4.0.
  - Nivel gratuito: menos de 10.000 llamadas al día, 5.000 por hora y 600 por minuto, solo para uso no comercial.
  - Se mencionan como permitidos "Public research conducted at public institutions" y "Use in educational content". — [Open-Meteo terms](https://open-meteo.com/en/terms)

### Inferences
- Para que no se lea como el "clima genérico" que se les criticó, hay que **aplicarlo al dron**: viento a la altura de vuelo (80–120 m), su componente a lo largo de cada arista (`w_par = V·cos(θ_viento − θ_arista)`), el tiempo y la energía (`t = L/(v_aire + w_par)`), y umbrales de ráfaga u operabilidad para drones pequeños. Las nubes bajas y la visibilidad modulan la detección óptica.

### Gaps
- Open-Meteo no permite elegir el modelo (ERA5 o ERA5-Land) para la altura de 100 m en todas las consultas; habría que revisar la documentación del archivo.

---

## 12. Shortlist recomendada (3 de metadata + 3 de amenaza) para "dron de reconocimiento bajo EW cerca del frente"

### Takeaway
**Metadata aplicada:** (M1) zonificación del frente con DeepStateMap, (M2) ocultamiento y exposición combinando WorldCover, el CHM de Meta y el DSM GLO-30 respecto de la línea de contacto, y (M3) viento a la altura de vuelo con Open-Meteo. **Amenazas:** (T1) denegación GNSS con GPSJam más imputación en el frente, (T2) intensidad de fuego de combate con el modelo de The Economist sobre FIRMS, y (T3) eventos de ataques aéreos, con drones y de artillería de ACLED, con UCDP GED o las alertas de Vadimkin como respaldo. M1, M2, M3, T1 y T2 no requieren credenciales.

### Cited Findings

| # | Fuente | Rol | Credenciales | Licencia | Resolución / frecuencia |
|---|---|---|---|---|---|
| M1 | DeepStateMap (API o espejo cyterat) | Zona (ocupado / gris / UA) y distancia a la línea de contacto | No | Sin licencia explícita; espejo GPL-3.0 | Polígonos vectoriales, diario, historial desde 2022-04 — [API](https://deepstatemap.live/api/history/public), [espejo](https://github.com/cyterat/deepstate-map-data) |
| M2 | ESA WorldCover + Meta CHM + Copernicus GLO-30 | Ocultamiento y visibilidad desde el frente | No (S3 sin firma) | CC BY 4.0 / CC BY 4.0 / licencia Copernicus | 10 m / submétrica / 30 m, estáticos — [WorldCover](https://esa-worldcover.org/en/data-access), [CHM](https://registry.opendata.aws/dataforgood-fb-forests/), [DEM](https://registry.opendata.aws/copernicus-dem/) |
| M3 | Open-Meteo (viento a 80–120 m, ráfagas) | Penalización de tiempo y energía por arista | No | CC BY 4.0, no comercial | Horario — [términos](https://open-meteo.com/en/terms) |
| T1 | GPSJam | Probabilidad regional de denegación GNSS | No | Sin licencia explícita | H3 res 4 (~1.770 km²), diario desde 2022-02-14 — [FAQ](https://gpsjam.org/faq) |
| T2 | Economist war-fire (FIRMS) | Probabilidad de falla cinética (fuego de combate) | No | Datos CC BY 4.0 | 0,1°, ~500 m por evento, actualización diaria — [repo](https://github.com/TheEconomist/the-economist-war-fire-model) |
| T3 | ACLED (Air/drone strike, Shelling) | Densidad de ataques por zona | Sí (myACLED; API desde Research) | EULA no comercial y sin redistribución | Evento georreferenciado, semanal — [API](https://acleddata.com/api-documentation/getting-started), [EULA](https://acleddata.com/eula) |

**Respaldos si no hay credenciales**
- **T3 sin ACLED (opción a):** UCDP GED Ucrania en HDX. CSV sin token, CC BY-IGO, hasta 2024-12. — [HDX UCDP](https://data.humdata.org/api/3/action/package_show?id=ucdp-data-for-ukraine)
- **T3 sin ACLED (opción b):** alertas antiaéreas de Vadimkin. MIT, sin credenciales, por raion y hromada, al día; se unen a COD-AB. — [Vadimkin README](https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/README.md); [COD-AB](https://data.humdata.org/api/3/action/package_show?id=cod-ab-ukr)
- **T3 sin ACLED (opción c):** JSON de Bellingcat. Sin credenciales, 2.517 incidentes con `weapon_system`, hasta 2025-07. — [Bellingcat api.json](https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json)
- **T2 sin MAP_KEY:** CSV anual por país de FIRMS. — [FIRMS country CSV](https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/2024/viirs-snpp_2024_Ukraine.csv)
- **M3 alternativa más "aplicada":** daño por hromada de Dietrich et al. (CC BY 4.0, GeoJSON), como proxy de intensidad histórica de combate. — [Zenodo 14811504](https://zenodo.org/api/records/14811504)
- **Metadata temporal de EW:** la serie `not_reach_goal` del dataset de Kaggle (CC BY-NC-SA) como indicador nacional de la efectividad de la EW contra drones. — [Kaggle metadata](https://www.kaggle.com/api/v1/datasets/view/piterfm/massive-missile-attacks-on-ukraine)

### Inferences
- **Justificación del conjunto:** cada fuente responde una pregunta distinta del problema.
  - M1: ¿dónde está el frente?
  - M2: ¿qué tan expuesto está el dron o su enlace?
  - M3: ¿cuánto le cuesta físicamente cada tramo?
  - T1: ¿dónde se pierde el GNSS?
  - T2: ¿dónde hay combate activo?
  - T3: ¿dónde hay ataques aéreos o de drones?
- Esto responde directamente a la crítica de "metadata genérica": M2 y M3 usan datos de base, pero las métricas se definen respecto de la amenaza (visibilidad desde la línea de contacto y viento a la altura de vuelo).
- **Modelo de costo sugerido en pgRouting:**
  - Probabilidad de falla de cada arista: `p_e = 1 − (1−p_gnss)(1−p_kin)(1−p_evt)`.
  - Costo aditivo: `cost = L_e/v_e(viento) + κ·(−ln(1−p_e))`, para que Dijkstra o A* equilibre tiempo y supervivencia. κ y la imputación de EW en el frente son parámetros de escenario, de modo que la resiliencia se evalúa con análisis de sensibilidad.
- **Base temporal común:** fijar un día de corte histórico (por ejemplo, una fecha de 2025) y ventanas de 30 días para T1 a T3. Eso hace el experimento reproducible y evita los datos en tiempo real.
- **Legal y repositorio:**
  - No subir datos crudos de ACLED (EULA), de ISW (propiedad exclusiva), de GPSJam ni de DeepState (sin licencia explícita).
  - Sí subir los scripts ETL, que descargan a JSON o GeoJSON y cargan con `ogr2ogr` o `psycopg`, junto con los atributos derivados por arista.
  - Las fuentes CC BY (Economist, WorldCover, CHM, Open-Meteo, Dietrich) se pueden redistribuir con atribución.

### Gaps
- No se puede garantizar que un correo `@mail.udp.cl` reciba el nivel Research de ACLED. Hay que pedirlo temprano, o planificar con UCDP o Vadimkin desde el inicio.
- No se confirmaron los términos de DeepStateMap ni de GPSJam. Convendría escribir a ambos autores pidiendo permiso para uso académico (los contactos están en sus sitios).
- La capa T1 no tiene datos medidos sobre el frente oriental. Su valor allí será siempre un supuesto de escenario, y eso debe declararse en el informe.

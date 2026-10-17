# Contexto del proyecto: Ruteo resiliente de UAV bajo denegación de espectro

> **Documento histórico de la Tarea 1.** Tras la [reunión con el profesor](../02_REUNION_PROFESOR/Charla_profesor.txt), el grupo eligió reconocimiento de una zona mediante **rutas físicas de UAV que se adaptan a pérdidas de reporte**. Las «decisiones de enfoque», el grafo de enlaces entre drones y las tareas pendientes descritas más abajo registran el plan anterior y no deben ejecutarse como plan vigente. Véanse el [enfoque actualizado](../01_PROYECTO_ACTUAL/ENFOQUE_TRAS_CHARLA_PROFESOR.md) y el [resumen del proyecto](../01_PROYECTO_ACTUAL/RESUMEN_PROYECTO_Y_TAREA_2.md).

Documento pensado para dárselo a un asistente de código (Codex) y que pueda continuar el trabajo sin contexto previo. Idioma de trabajo: español (informe y comentarios), código en Python.

---

## 1. Qué es esto

Tarea 1 grupal de un curso de **ruteo resiliente** (Chile). Grupo de **3 integrantes (n=3)**: Aarón Pozas Oyarce, Diego Pérez Carrasco, Alex Marambio Leyton.

La Tarea 1 es el **sustento** de la Tarea 2 (final), donde se deberán elegir distintas rutas entre un par de puntos para dar resiliencia. Por eso lo que se define ahora (grafo + metadata + amenazas) debe poder alimentar un algoritmo de ruteo después.

Entregables Tarea 1: **presentación + informe** (el informe se escribe en LaTeX, formato IEEEtran). Presentaciones a partir del 4 de septiembre; el feedback sirve para complementar el informe de la Tarea 2.

### Qué exige el enunciado (secciones del informe)
1. Problemática identificada
2. Hipótesis que la solucione mediante ruteo resiliente
3. Objetivo general y específicos (mínimo 3 específicos)
4. Infraestructura: red **geolocalizada** (no necesariamente de telecomunicaciones), nodos y aristas; indicar de dónde y cómo se obtiene la información y que es factible obtenerla
5. Metadata (características) a incorporar a la infraestructura: **mínimo n=3 APIs/BD distintas**
6. Fallas/eventos geolocalizados externos que puedan afectar la infraestructura: **mínimo n=3 APIs/BD distintas**
7. En total, **al menos 1 API y 1 base de datos geoespacial que use polígonos**

### Rúbrica (60 pts), resumen
Problemática real (6), hipótesis con ruteo resiliente (6), objetivo general (2), ≥3 objetivos específicos (2), infraestructura: fuente (4) + factibilidad (4), metadata: importancia (6) + fuente (4) + factibilidad (4), amenazas: importancia (6) + fuente (4) + factibilidad (4), ≥1 API (4), ≥1 BD con polígonos (4). Cada criterio: bien logrado / faltan correcciones / no logrado. **La factibilidad se evalúa explícitamente**, por eso importa mostrar pruebas reales de cada fuente.

---

## 2. Paper base

**"Cross-layer UAV network routing protocol for spectrum denial environments"**, S. Zheng, X. Zhu, Z. Qin, C. Dong. *Ad Hoc Networks* 167 (2025) 103702. DOI: 10.1016/j.adhoc.2024.103702. Propone **CLUN-LSR** (Cross-Layer UAV Link State Routing).

### Problema que ataca
En redes ad hoc de UAV bajo jamming, los protocolos proactivos (OLSR, OSPF, MP-OLSR) se recuperan lento: la capa física/enlace intenta "reparar" (cambio de canal, spectrum switching, varios reintentos) y solo si falla la capa de red se entera. Mientras tanto la capa de red sigue enviando por la ruta rota y hay pérdida de paquetes. OLSR además debe esperar un HELLO/TC nuevo para actualizar el link set.

### Solución
- Cada UAV tiene **2 antenas**: de servicio (datos) y de gestión de espectro/control (siempre puede sensar y enviar info espectral).
- Un módulo de sensado espectral en la capa de enlace detecta interferencia y genera un **mensaje spectrum-aware** (direcciones de nodos + *jamming flag*, Fig. 6), que se difunde por la antena de control.
- Al recibirlo, cada nodo saca los nodos interferidos de su tabla de vecinos de 1 salto (N) y 2 saltos (N2), actualiza la tabla de topología (TP), el grafo G y recalcula rutas con Dijkstra (Algoritmo 1). No altera los periodos de HELLO/TC.
- Es "cross-layer" porque la capa de red lee directo el estado espectral sin esperar la reparación de las capas inferiores. Aplicable a cualquier protocolo table-driven; lo implementan sobre **MP-OLSR** → **CLUN-MPOLSR** (Algoritmo 2).

### Modelo del grafo y métrica
- Grafo dirigido ponderado `G=(V,E,W)`. **Cada nodo = un UAV**, cada arista = enlace directo entre dos UAV en rango.
- Peso de arista: `w_il = f(v_l) = 1/m_l`, con `m_l` = número de vecinos de 2 saltos alcanzables a través de `v_l`. Si `m_l = 0` y el nodo es el destino se usa como último salto; si es intermedio, `w_il = 999`. Menos vecinos ⇒ más cerca de la zona de interferencia ⇒ mayor peso ⇒ ruta menos deseable.

### Modelo de jamming (analítico, sección 3.2)
Supuestos: misma frecuencia, jammer omnidireccional con propagación en espacio libre, zonas de jamming sin traslape.
- Potencia de comunicación (1): `P_sr1 = P_t·G_tr·G_rt·λ² / (4π d_c)²`
- Potencia del jammer en el receptor (2): `P_jr1 = P_j·G_jr·G_rj·λ² / (4π d_j)²`
- JSR (3): `JSR = P_jr1/P_sr1 = (P_j G_jr G_rj)/(P_t G_tr G_rt) · (d_c/d_j)²`
- Con pérdidas por polarización `L_a` (≈1) y ancho de banda `L_b = B_r/B_j` (4), (5): `JSR = (P_j G_jr)/(P_t G_tr) · (d_c/d_j)² · L_a · L_b`
- Condición (6): `(d_j/d_c)² = c`; jamming efectivo si `d_j/d_c < √c`.
- Con jammer en el origen y transmisor en (d,0): (7) `x²+y² = c((x−d)²+y²)`. Si `c=1` la zona es un semiplano (x = d/2); si `c≠1` es un **círculo** (8): centro `(c·d/(c−1), 0)`, radio `d·√c/|c−1|`.
- Flag de jamming: 1 inicialmente, 0 cuando el nodo cae dentro de la zona.

### Experimentos del paper (EXata 5.1)
- Tabla 1: área 5000×1500 m, altura 100 m, 30 UAV, 60 s y 120 s, potencia 4 dBm, CBR (3 flujos), paquetes 512 B cada 0.5 s, UDP, IPv4, **802.11b**, 2.4 GHz, 2 Mbps, noise factor 10, **path loss Two-Ray**, **shadow model Constant**.
- Tabla 2: HELLO 2 s, TC 5 s, neighbor hold 6 s, topology hold 15 s, duplicate hold 30 s, fp=3, fe=2, 3 caminos (MP-OLSR).
- Comparan OLSRv1, OLSRv2, MP-OLSR y CLUN-MPOLSR con PDR, throughput y recovery time.
- Toy example (Fig. 8, 30 s): recovery time 7.16 s (MP-OLSR) vs 2.24 s (CLUN-MPOLSR) → **4.92 s más rápido**; PDR 28.74% vs 77.84%; throughput 574.8 vs 1556.8 kbps.
- Variaciones: nº de nodos jammeados (2,4,6,8; PDR decrece al aumentar), velocidad (10–30 m/s, jammer en (1000,600), radio 120 m, 120 s), nº de UAV (10–50, jammer en el centro que afecta 2 UAV).
- Overhead comparable (mensajes pequeños, poco frecuentes, por radio/canal separados).

### Limitaciones del paper (la brecha que justifica nuestro trabajo)
Importante ser **preciso**: el paper NO usa solo el modelo analítico de espacio libre; las simulaciones corren en EXata con Two-Ray + shadowing constante y con movilidad. Aun así:
1. **Sin terreno real** (Two-Ray asume superficie plana; sin obstrucción/línea de vista real).
2. **Sin ruido espectral civil de fondo** (la única interferencia es el jammer).
3. **Sin clima/atenuación atmosférica variable.**
4. **Zona de jamming arbitraria**: círculo de radio fijo en coordenadas elegidas por los autores, sin contraste con datos reales de interferencia/conflicto.

---

## 3. Decisión de enfoque del grupo

- El paper es **inspiración**; se mantiene el contexto de **conflicto/militar** para que metadata y amenazas estén bien definidas.
- Propuesta: **extender/validar con datos reales** el escenario del paper (terreno, congestión espectral, clima como metadata; interferencia GPS, conflicto y espacio aéreo restringido como amenazas), reemplazando la zona de jamming circular idealizada por zonas empíricas/polígonos.
- Se descartó (como ejemplo ilustrativo) la idea de dron vigilando colegios por narcotráfico; no es el contexto del trabajo.
- Distinción conceptual clave:
  - **Infraestructura** = el grafo (nodos/aristas).
  - **Metadata** = atributos estructurales/recurrentes que describen cómo es un nodo/arista normalmente y alimentan el peso `w_il`.
  - **Amenaza** = evento externo puntual/variable en el tiempo que degrada o inhabilita nodos/aristas y gatilla recálculo de rutas.
- Decisión de diseño abierta: **Opción A** (nodo = UAV individual, fiel al paper) vs **Opción B** (un dron, nodos = waypoints). El paper usa A; el informe actual asume A.

---

## 4. Fuentes de datos (versión definitiva, según plan del grupo)

| Rol | Fuente | Qué aporta | Autenticación / cuota | Estado |
|---|---|---|---|---|
| Infraestructura | **OpenSky Network** `GET https://opensky-network.org/api/states/all?lamin&lomin&lamax&lomax` | Posiciones (icao24, lat, lon, altitud, velocidad, rumbo) → nodos; aristas por proximidad | **OAuth2 client credentials** (token Bearer, ~30 min). Anónimo 400 créditos/día, registrado 4.000, con receptor 8.000 | Pendiente de probar |
| Metadata #1 | **OpenTopography** `GET https://portal.opentopography.org/API/globaldem` (demtype=SRTMGL3, bbox, outputFormat=GTiff) | DEM → elevación y línea de vista (Fresnel) | API Key; 200 req/24h cuenta académica | ✅ **Probado** (main.py + terreno.py) |
| Metadata #2 | **OpenCelliD** `GET https://opencellid.org/cell/getInArea` / `getInAreaSize` (BBOX=latmin,lonmin,latmax,lonmax) | Densidad de antenas celulares → proxy de congestión espectral civil / ruido de fondo | API Key; 1.000 req/día; getInAreaSize 2 créditos, getInArea 1 crédito por celda | Pendiente de probar |
| Metadata #3 | **OpenWeatherMap** `GET https://api.openweathermap.org/data/2.5/weather?lat&lon&appid&units=metric` | `rain.1h`, `wind.speed`, `visibility` → atenuación | API Key; ~1.000 llamadas/día | ✅ **Probado** (OpeanWeather.py) |
| Amenaza #1 | **GPSJam** (gpsjam.org) | Interferencia GPS real (hexágonos H3, derivado de ADS-B) | **No tiene API por bbox**: CSV diario descargable | Pendiente (descarga manual del CSV) |
| Amenaza #2 | **ACLED** `GET https://api.acleddata.com/acled/read?key&email` (modo clásico; migrando a OAuth) | Eventos de conflicto geolocalizados (event_date, event_type, lat, lon, notes) | Registro + **aprobación de cuenta (no inmediata)** | Pendiente: registrarse ya |
| Amenaza #3 | **NOTAM / OpenAIP** `GET https://api.openaip.net/api/airspaces` (header `x-openaip-api-key`) | Polígonos GeoJSON de espacios RESTRICTED/PROHIBITED/DANGER | API Key; OpenAIP global, NOTAM por API solo FAA (EE.UU.), DGAC Chile sin API abierta | Pendiente de probar |

Columnas "Metadata #4" y "Amenaza #4" del plan del grupo están vacías (con 3+3 se cumple el mínimo).

### Cumplimiento de requisitos
- ≥1 API: varias.
- ≥1 BD geoespacial con **polígonos**: espacios aéreos de OpenAIP (GeoJSON `Polygon` nativo) y/o zonas de GPSJam/ACLED convertidas a polígonos (PostGIS o GeoJSON + Shapely/Turf.js).

### Correcciones que salieron de verificar la documentación (importante no revertirlas)
- OpenSky **ya no usa Basic Auth**: OAuth2 client credentials.
- GPSJam **no es una API consultable**; es una base de datos descargable (CSV diario). Se documenta como limitación real de factibilidad. Alternativa más ambiciosa: derivar un proxy propio desde ADS-B (indicadores NIC/NACp).
- La **ITU Spectrum Database fue descartada** (sin API pública general); por eso la congestión espectral se toma de OpenCelliD.
- NOTAM tiene cobertura de API desigual por país; OpenAIP lo complementa.
- La afirmación inicial de que el paper usaba un modelo "totalmente idealizado" fue **corregida**: usa EXata con Two-Ray + shadowing (ver sección 2).

---

## 5. Extensión matemática propuesta (para el informe / Tarea 2)

Partiendo de la Ec. (5) del paper:

1. **Terreno** (OpenTopography): incluir `L_terrain ∈ (0,1]` en `P_sr1` (y análogamente en `P_jr1`), calculado del perfil de elevación entre dos puntos (obstrucción de la primera zona de Fresnel; penalización típica 6–20 dB según grado de obstrucción). Efecto: el radio de jamming (Ec. 8) deja de ser un círculo perfecto.
2. **Clima** (OpenWeatherMap): `L_atm = 10^(−γ_R·d/10)` con `γ_R` (dB/km) dependiente de la tasa de lluvia (modelo tipo ITU-R P.838 simplificado) como factor adicional junto a `L_a·L_b`.
3. **Congestión espectral** (OpenCelliD): pasar de JSR a **SINR**: `SINR = P_sr1 / (P_jr1 + N_ambient)`, con `N_ambient` estimado a partir de densidad de celdas.
4. **Peso del enlace**: en lugar del conteo binario de vecinos del paper, `w_il = 1 / Σ_{k∈N2(l)} 1[SINR_k > τ]` (solo cuentan vecinos "útiles" sobre un umbral τ).

Las zonas de amenaza (GPSJam / ACLED / OpenAIP) se modelan como **polígonos**; un nodo dentro de uno recibe `jamming_flag = 0` (equivalente al flag del paper) y dispara recálculo de rutas.

Esto es una propuesta conceptual: no hay que re-derivar todo el modelo, basta mostrar las ecuaciones modificadas con su justificación.

---

## 6. Archivos y estado del repo

- [`pruebas_iniciales/main.py`](pruebas_iniciales/main.py) — descarga el DEM de OpenTopography (SRTMGL3, bbox Santiago: south −33.6, north −33.3, west −70.8, east −70.5) a `terreno.tif`. ✅ funciona.
- [`pruebas_iniciales/terreno.py`](pruebas_iniciales/terreno.py) — con `rasterio`/`numpy`/`matplotlib` imprime metadatos del GeoTIFF (shape, CRS, bounds, min/max/promedio de altitud), consulta la altitud en (−33.45, −70.66) y guarda `mapa_terreno.png`. ✅ funciona.
- `OpeanWeather.py` — consulta OpenWeatherMap en (−33.45, −70.66) y muestra viento (m/s), lluvia (mm/h) y visibilidad (m). ✅ funciona.
- `requirements.txt` — `rasterio>=1.3.0`, `matplotlib>=3.7.0`, `numpy>=1.24.0`, `requests>=2.28.0`.
- `informe_ruteo_resiliente_uav.tex` — informe IEEEtran (Introducción, Problemática, Hipótesis, Objetivo General, Objetivos Específicos, Infraestructura, Metadata, Amenazas, Base de datos geoespacial con polígonos, Recursos, Bibliografía). Ya refleja OpenCelliD y OpenAIP.
- `resumen_apis_pruebas.md` — resumen de las fuentes con por qué/para qué y scripts de prueba en Python (los de OpenSky, OpenCelliD, ACLED, OpenAIP aún no han sido ejecutados contra las APIs reales).

Zona de estudio usada en las pruebas: **Santiago de Chile**, bbox `(-33.6, -70.8, -33.3, -70.5)`. Para amenazas (ACLED/GPSJam) el escenario de conflicto real estaría en otra región (p. ej. Ucrania/Báltico); definir si el caso de estudio se ubica allá o si se usa Santiago solo como demostración técnica.

### Seguridad
Los scripts originales tenían **API keys escritas en el código**. Deben leerse de variables de entorno (`.env` + `.gitignore`), nunca subirse a repo/Canvas. Variables esperadas: `OPENTOPOGRAPHY_KEY`, `OPENWEATHERMAP_KEY`, `OPENCELLID_KEY`, `ACLED_KEY`, `ACLED_EMAIL`, `OPENAIP_KEY`, `OPENSKY_CLIENT_ID`, `OPENSKY_CLIENT_SECRET`. Si las keys antiguas ya estuvieron expuestas, conviene regenerarlas.

---

## 7. Pendientes y siguientes pasos sugeridos para Codex

1. Probar de verdad y dejar scripts con salida real para OpenSky, OpenCelliD, ACLED y OpenAIP (y la descarga/lectura del CSV de GPSJam). Guardar salidas/capturas para pegar en el informe (evidencia de factibilidad, criterios 4.2/5.3/6.3).
2. Unificar los scripts en un paquete: un módulo por fuente + cliente común que lea keys de entorno, cachee respuestas (cuotas: OpenTopography 200/día, OpenCelliD 1.000/día) y devuelva estructuras limpias.
3. Construir el **grafo geolocalizado** (networkx): nodos desde OpenSky, aristas por distancia (haversine) dentro de un radio de comunicación, atributos de nodo/arista con la metadata (elevación, lluvia, densidad de celdas).
4. Implementar el cálculo de línea de vista / `L_terrain` desde el DEM (perfil de elevación entre dos puntos) y el término `L_atm` desde `rain.1h`.
5. Convertir amenazas a **polígonos** (Shapely/GeoJSON; opcional PostGIS) y marcar nodos/aristas afectados (intersección geométrica).
6. Implementar el peso `w_il` extendido (SINR con umbral τ) y Dijkstra / k caminos disjuntos como base para la Tarea 2 (rutas resilientes entre un par de puntos).
7. Registrar cuenta en **ACLED** cuanto antes (aprobación lenta).
8. Decidir el área del caso de estudio (afecta cobertura de NOTAM/FAA y relevancia de GPSJam/ACLED).
9. Preparar la presentación (slides) con la misma estructura del informe.

### Convenciones a respetar
- Informe en LaTeX con el mismo formato IEEEtran del ejemplo del curso (`\documentclass[journal,10pt]{IEEEtran}`, mismos paquetes, `thebibliography`).
- Distinguir siempre metadata (estructural) de amenaza (evento puntual).
- Documentar honestamente las limitaciones de factibilidad detectadas (GPSJam sin API, ITU inaccesible, NOTAM por país, OAuth2 en OpenSky).
- No inventar salidas de API: usar solo respuestas reales o ejemplos de la documentación oficial, indicándolo.

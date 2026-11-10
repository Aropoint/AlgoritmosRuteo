# Entrega de la Tarea 3: punto → evidencia y guion del video

La Tarea 3 se entrega como **un video** subido a Canvas, en que la solución se ejecuta desde el `main` de GitLab. Esta guía indica, para cada uno de los 9 puntos del enunciado, qué archivo lo cumple y qué mostrar. Al final hay un guion con minutaje.

> **Estado (10 de noviembre de 2026).** Todo se verificó en Docker desde un **clon limpio** de la rama:
> `docker compose up --build` construyó la imagen en ~50 s y corrió los 23 pasos del pipeline en `ok`
> en ~35 s, sin ninguna descarga (instantánea versionada). El sitio respondió y reprodujo **exactamente**
> las cifras del caso de ejemplo. Pruebas: **55/55 OK** (`docker compose run --rm pruebas`), 19 de ellas
> nuevas, incluido el MILP de Gurobi contrastado con una enumeración exhaustiva.

## Cómo se ejecuta (punto 1)

La carpeta `05_T2/` es la raíz del repositorio de GitLab. Solo hace falta Docker Desktop (o Docker Engine con Compose v2):

```bash
git clone <URL del repositorio en GitLab> ruteo-uav
cd ruteo-uav
docker compose up --build        # BD + pipeline + sitio en http://localhost:8000
```

`docker compose up` levanta PostgreSQL + PostGIS + pgRouting (`db`) y el servicio `main`, que ejecuta `main.py`: primero el pipeline y después el sitio. Por defecto `USAR_INSTANTANEA=1`: los 7 JSON descargados de las APIs públicas están versionados en `Datos/instantanea/` (1,7 MB, con SHA-256 en `MANIFIESTO.json`). Así el video no depende de Overpass, que llegó a tardar 614 s y a devolver HTTP 502, y la BD es la misma que se muestra. Para demostrar la descarga real: `USAR_INSTANTANEA=0 docker compose up --build` (unos 12 minutos; en el video se acelera).

## Punto por punto

| # | Qué pide | Dónde está | Qué mostrar en el video |
|---|---|---|---|
| 1 | Ejecutar la página desde el `main` de GitLab | `main.py`, `pipeline.py`, `docker-compose.yml`, `Datos/instantanea.py` | `git clone` + `docker compose up --build` (acelerado), el resumen de los 23 pasos en `ok` y el sitio abriéndose |
| 2 | Infraestructura que no genere rectas sobre lo que no se puede sobrevolar, por altitud o por bloqueos | `Metadata/elevacion.py` (perfil cada ~90 m), `Metadata/zonas_restringidas.py`, `BD/pesos.sql`, `ruteo/pesos.py` (`excluidas_con_motivo`) | Capa «Tramos no sobrevolables» con su motivo (edificio, relieve, zona). Bajar la altura de 60 a 40 m: los tramos excluidos suben de 92 a 242 y la ruta se desvía. Dibujar una zona prohibida y ver que las rutas la rodean |
| 3 | Recibir los parámetros del usuario: restricciones de su aplicación y destino o área | `SitioWeb/static/index.html` (sección 1), `SitioWeb/app.py` (`SolicitudT3`) | Perfil de aplicación, origen y destino con clics, «Pasar por los puntos de observación», autonomía, R_min, altura y margen, zonas del usuario |
| 4 | Cargar y considerar todos o algunos metadatos y amenazas, con popups y un panel de casillas | Sección 2 del sitio (`construirPanel` en `app.js`), `ruteo/config.Considerar` | Casillas **Ver** y **Considerar** por capa. Desmarcar «considerar» en Eventos UCDP y recalcular: cambian la p y las rutas. Popups de tramos y nodos con p por amenaza; viento como flecha con detalle (no es un polígono) |
| 5 | Un archivo que genere la probabilidad de falla de cada enlace y nodo a partir de cada amenaza | **`BD/probabilidades.py` + `BD/probabilidades.sql`** → columnas `pf_*` y `BD/salida/probabilidades.json` (`BD/ESTRUCTURA_probabilidades_json.md`) | El modelo `p_i = 1 − exp(−λ_i · r_i · L)`, `p = 1 − Π(1 − p_i)`, y la capa de tramos coloreada por p |
| 6 | La mejor ruta con 4 técnicas, cada una con su casilla | `comun/tecnicas.py`, `ruteo/optimizacion.py`, `ruteo/modelo_t3.py`, `ruteo/hormigas.py` | Las 4 rutas en el mapa con sus casillas en el panel. Explicar cada técnica (abajo) |
| 6.1 | `pgr_dijkstra` con peso solo la distancia en metros | `comun/tecnicas.dijkstra_m`: `cost = reverse_cost = largo_m` | La consulta SQL en el detalle de la técnica |
| 6.2 | CPLEX o Gurobi con el modelo formal: metadatos, amenazas y condiciones del usuario como restricciones | `ruteo/optimizacion.milp` (Gurobi con la licencia de `pip`) | El modelo (abajo), las 1.015 variables binarias y 373 restricciones, la poda exacta por elipse y el estado «óptimo» |
| 6.3 | `pgr_dijkstra` con los parámetros y condiciones del punto anterior | `comun/tecnicas.dijkstra_ponderado` + `ruteo/modelo_t3.lagrange` | Costo `c + λ · l` en una tabla temporal; λ hallado por bisección (14 llamadas a `pgr_dijkstra`); llega al mismo óptimo que el MILP |
| 6.4 | Una metaheurística | `ruteo/hormigas.aco` (colonia de hormigas, MMAS) | Parámetros, iteraciones y brecha frente al óptimo del MILP |
| 7 | Sorteo 0–100: hay falla si se supera el umbral | `ruteo/sorteo.py`, `POST /api/t3/sorteo`, sección 4 del sitio | «Sortear fallas»: tramos en rojo, nodos con ✕, y en el popup `n` frente al umbral `100 · (1 − p)` |
| 8 | Métrica de resiliencia por técnica, la más resiliente, junto al algoritmo y el tiempo de cómputo en la leyenda | `ruteo/resiliencia_t3.py`, leyenda del mapa (`actualizarLeyenda`) | La leyenda: algoritmo · ms · R · F · km, con ★. La tabla con el diferencial y McNemar |
| 9 | Ejemplo con ruta alternativa frente a una amenaza que cumpla los objetivos iniciales | `BD/caso_ejemplo.py` → `BD/salida/caso_ejemplo.json`, botón «Cargar caso de ejemplo» | Etapa 1 frente a etapa 2, la zona, el sorteo 30007 y los 4 objetivos cumplidos. Complemento: la flota de la Tarea 2 cambiando de ruta en vuelo |

## Las cuatro técnicas en una lámina

Todas trabajan sobre el **mismo grafo sobrevolable**: los tramos no sobrevolables por altura, relieve o zonas no entran a ninguna. Notación por arco dirigido `a = (u → v)`: `d_a` es el largo, `f_a` el factor de viento de frente, `c_a = d_a · f_a` (proporcional al tiempo de vuelo) y `l_a = −ln(1 − p_tramo) − ln(1 − p_nodo de llegada)`.

**Modelo formal (6.2, Gurobi):**

```
min   Σ c_a x_a                                    tiempo de vuelo (metadata: viento)
s.a.  Σ_out(v) x − Σ_in(v) x = 1 | −1 | 0          conservación de flujo
      Σ_in(v) x ≤ 1                                no repite nodos
      Σ d_a x_a ≤ B                                autonomía del usuario
      Σ l_a x_a ≤ −ln(R_min)                       ⇔ Π(1 − p) ≥ R_min   (amenazas)
      x_a = 0 si el tramo no es sobrevolable       altura de vuelo, margen y relieve (metadata), zonas
      x_a ∈ {0, 1}
```

Es un **camino mínimo con restricciones de recursos** (NP-difícil en general). La linealización es exacta porque `−ln` convierte el producto de fiabilidades en una suma. La **poda por elipse** es exacta: un nodo solo puede estar en un camino factible si `dist(s, v) + dist(v, t) ≤ B`. Si R_min no es alcanzable, el modelo lo informa y resuelve «máxima fiabilidad sujeta a la autonomía».

**Dijkstra ponderado (6.3)** es la **relajación lagrangiana** de ese modelo: Dijkstra no puede imponer una restricción sobre la ruta entera, pero con costo `c_a + λ · l_a` cada tramo riesgoso «cuesta» más. λ se busca por bisección como el menor que cumple R_min. La diferencia con el MILP es la brecha de dualidad: en las consultas probadas, cero.

**ACO (6.4):** cada hormiga construye un camino eligiendo arcos con probabilidad ∝ `τ^α · (1/(c + h))^β · ((1 − p_e)(1 − p_v))^γ`, donde `h` es el costo que falta hasta el destino. Las restricciones entran como penalización. Usa evaporación y depósito MMAS con cotas, y una semilla fija.

## Cifras de la consulta por defecto (inicio → destino, «Inspección de daños», R_min = 0,85, 300 sorteos)

| Técnica | km | vuelo | F = Π(1 − p) | R (resiliencia) | cumple aut. / R_min | cómputo |
|---|---|---|---|---|---|---|
| `pgr_dijkstra` (m) | 8,46 | 19,2 min | 0,740 | 88,0 % | ✓ / ✗ | 4 ms |
| MILP con Gurobi | 9,71 | 21,6 min | 0,858 | 93,3 % | ✓ / ✓ | 81 ms (46 ms de Gurobi) |
| `pgr_dijkstra` ponderado | 9,71 | 21,6 min | 0,858 | 93,3 % | ✓ / ✓ | 15 ms (λ = 11 917 m) |
| ACO | 10,63 | 23,0 min | 0,882 | **95,3 % ★** | ✓ / ✓ | 314 ms |

Diferencial frente a `pgr_dijkstra` (m): +5,3 pp para el MILP y el ponderado (McNemar p = 0,026) y +7,3 pp para ACO (p = 0,0016).

**Métrica de resiliencia (punto 8).** `R` es la fracción de los 300 sorteos 0–100, los mismos para las cuatro técnicas, en que la misión se **completa** dentro de la autonomía. El UAV sigue su ruta y nota cada falla antes de entrar con probabilidad 0,5, el mismo supuesto de la flota de la Tarea 2. Si la nota, se desvía con Dijkstra ponderado; si no, se pierde. Así, `R` suma lo que la ruta **absorbe** (no toparse con la falla) y lo que **recupera** (rodearla). Junto a `R` se informa `F`, la fiabilidad analítica. La fracción de sorteos en que la ruta queda intacta se acerca a ella (0,71 frente a 0,74 y 0,85 frente a 0,86), lo que valida el sorteo.

## Cómo decirlo con honestidad en el video

- **ACO es la más resiliente, pero no porque optimice mejor.** Su ruta es un 9,5 % más larga que el óptimo del MILP. El MILP cumple R_min con la ruta más rápida posible; no maximiza la resiliencia. Para más resiliencia se sube R_min, y el MILP sigue entregando el óptimo con esa nueva condición.
- **El MILP y Dijkstra ponderado coinciden** en las consultas probadas: la relajación lagrangiana no dejó brecha. Es un resultado, no un error.
- **Los λ_i^max son supuestos abstractos** (0,12, 0,10 y 0,03 fallas por km a intensidad máxima). Las amenazas se tratan como independientes. GPSJam no distingue tramos dentro del AOI, porque una celda H3 lo cubre entero.
- **Con los puntos de observación**, R_min = 0,85 no es alcanzable: la fiabilidad máxima es 0,649. El MILP lo informa y resuelve la máxima fiabilidad; el sitio marca ✗ en R_min para todas las técnicas.
- **El sorteo del caso de ejemplo está elegido para ilustrar**, y así lo rotula el sitio. Las cifras de R salen de los 300 sorteos.

## Lo que se fundamenta en vez de hacerse

| Decisión | Fundamento |
|---|---|
| No se densifica la malla (0,5 km) | Cada tramo recto se valida completo: edificios a ≤ 15 m de todo el segmento y relieve cada ~90 m. Una malla de 0,25 km tendría unos 2.700 tramos y superaría la licencia restringida de Gurobi (2.000 variables). Con la actual el MILP usa 1.015 |
| Gurobi y no CPLEX | La licencia que trae `pip install gurobipy` resuelve el modelo sin archivo de licencia, así que cualquiera lo replica desde GitLab. CPLEX Community se limita a 1.000 variables |
| Zonas restringidas solo aeronáuticas civiles (`aeroway`) | No se usa `landuse=military`: en una ciudad en conflicto equivaldría a mapear instalaciones militares. Las zonas prohibidas del usuario cubren los bloqueos |
| Puntos intermedios resueltos por tramos | Con varios tramos, la autonomía y la fiabilidad se reparten en proporción al largo mínimo de cada uno (Σ B_k = B y Π R_k = R_min). El modelo conjunto multiplicaría las variables por el número de tramos |
| Fallas independientes por elemento | Es lo que pide el punto 7 (un sorteo por tramo y nodo). El modelo espacial de discos de la Tarea 2 sigue en la flota |

## Guion del video (≈ 12 minutos)

| Tiempo | Qué se ve | Qué se dice |
|---|---|---|
| 0:00–1:00 | GitLab: el repo y su `README.md` | El problema: un UAV de inspección en una ciudad con amenazas; 4 técnicas comparadas por resiliencia |
| 1:00–2:30 | Terminal: `git clone`, `docker compose up --build` (acelerado) y el resumen del pipeline | Punto 1: todo corre en Docker; la instantánea hace que la ejecución sea idéntica a la del video |
| 2:30–4:00 | Mapa: capas de tramos, edificios y relieve; «Tramos no sobrevolables»; altura de 60 → 40 m | Punto 2: ninguna ruta es una recta sobre un obstáculo; el motivo de cada exclusión |
| 4:00–5:00 | Perfil, origen y destino, R_min, autonomía; dibujar una zona prohibida | Punto 3 |
| 5:00–6:00 | Panel de control: Ver y Considerar; popups; el viento | Punto 4 |
| 6:00–7:00 | `BD/probabilidades.sql`, `probabilidades.json` y la capa coloreada por p | Punto 5 |
| 7:00–9:00 | «Calcular las 4 rutas»: casillas de cada ruta, detalle de cada técnica y el modelo formal | Punto 6 |
| 9:00–10:00 | «Sortear fallas» y «Nueva semilla»; el popup de un tramo caído | Punto 7 |
| 10:00–10:45 | Leyenda y tabla: R, F, tiempo y ★; diferencial con McNemar | Punto 8, con la lectura honesta de ACO |
| 10:45–12:00 | «Cargar caso de ejemplo»: zona sobre la ruta corta, las alternativas, el sorteo 30007 y los objetivos ✓. Cierre con la animación de la flota | Punto 9 |

## Comandos útiles

```bash
docker compose run --rm pruebas                                # 55 pruebas
docker compose run --rm app python BD/probabilidades.py        # punto 5: regenera las probabilidades
docker compose run --rm app python BD/caso_ejemplo.py          # punto 9: regenera el caso de ejemplo
docker compose run --rm app python Datos/instantanea.py crear  # rehace la instantánea tras una descarga nueva
SOLO_SITIO=1 docker compose up                                 # solo el sitio, sobre la BD existente
docker compose exec db psql -U postgres -d ruteo_uav -c "SELECT metodo, largo_km, fiabilidad, resiliencia, tiempo_ms FROM rutas ORDER BY id DESC LIMIT 4"
```

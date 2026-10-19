# Propuesta técnica: ruteo físico resiliente de UAV (Tarea 2)

**Versión:** v2 (18-oct-2026) · **Estado:** núcleo algorítmico implementado y probado en Python; resultados **preliminares** solo sobre el conjunto de **ajuste**. El conjunto de evaluación no se ha ejecutado a propósito (ver §8).

Este documento formaliza lo que [CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md](CONTEXTO_PROPUESTA_RUTEO_RESILIENTE_UAV_TAREA2.md) dejó como "por formalizar": el grafo, el modelo de fallas, los pesos, las restricciones, la regla de selección, la replanificación, las métricas y el protocolo experimental. Cada sección indica el criterio de la rúbrica al que responde y el archivo donde está implementada.

---

## 1. Problema

**Misión.** Un UAV simulado parte de `A`, visita en orden los puntos de observación `P1 … Pm` y termina en `B`, sobre un grafo de navegación geolocalizado en un recorte urbano de **Mykolaiv** (referencia provisional; AOI en `ruteo/config.py`). Mínimo viable: `m = 3`, orden fijo.

**Grafo** `G = (V, E)` (`ruteo/grafo.py`):

- `V`: puntos de navegación (no UAV). Malla de 0,5 km con perturbación aleatoria, 8-vecindad y retiro del 12 % de las aristas sin desconectar el grafo: **196 nodos y 618 aristas**.
- `E`: tramos de vuelo rectos, no dirigidos, con `largo_km` geodésico (haversine) y atributos (`riesgo`, `altura_max_edificio_m`, `en_zona_restringida`).
- La conectividad es una **hipótesis del simulador**, no un corredor aéreo real.

**Presupuesto.** `km_max = (1 + β) · L*`, donde `L*` es la suma de los caminos mínimos en km entre puntos consecutivos sin fallas (`L* = 13,16 km` con la configuración por defecto).

**Éxito de misión.** Todos los puntos visitados en orden, destino alcanzado y `km recorridos ≤ km_max`.

**Pregunta.** ¿Seleccionar rutas resilientes antes de salir y replanificar ante fallas completa más misiones que Dijkstra por distancia, sin exceder el presupuesto?

## 2. Modelo de fallas (rúbrica 5.1) · `ruteo/fallas.py`

Una falla `f = (c, r, t_on)` es un **disco** de centro `c` y radio `r ~ U[0,25; 0,60] km` que bloquea todo tramo cuya distancia al centro sea `≤ r`. Se activa cuando el UAV lleva `t_on ~ U[0; 0,8·L*]` km recorridos, de modo que la falla puede aparecer después de planificar. Por defecto es permanente; el campo `duracion_km` permite modelar fallas transitorias.

- **Descubrimiento local.** El UAV no conoce las fallas. Al llegar a un nodo observa el estado de sus tramos incidentes. No hay falsos positivos: lo que observa bloqueado lo está.
- **Origen espacial.** Con probabilidad `prob_foco` la falla se ubica cerca de un *foco de amenaza*, con una gaussiana `σ = 0,5 km`; en caso contrario, se ubica de forma uniforme en el AOI. Con datos reales (sitio web y `BD/rutas_ejemplo.py`), los focos son los **incendios de guerra del período de evaluación** (posteriores a `FECHA_CORTE`; `Amenazas/incendios_guerra.py`). Si no hay, se usan los históricos, luego los eventos UCDP y, como último recurso, focos sintéticos (`comun/resiliencia.py`).
- **Independencia.** Los **eventos históricos** que alimentan los pesos (§3) y las **fallas de evaluación** son muestras independientes del mismo proceso espacial; con datos reales corresponderían a períodos distintos. Con `prob_foco = 0` el riesgo histórico no aporta información, lo que permite comprobar si el método depende de que esa información sea buena.
- **Puntos obligatorios.** Un disco que contiene un punto de la misión se vuelve a muestrear (queda registrado en `fallas_remuestreadas`), porque haría la misión imposible para cualquier método y no ayudaría a distinguirlos.
- **Tres niveles separados**, como pide el contexto: registro externo → interpretación (foco) → falla simulada reproducible (semilla).

## 3. Pesos y restricciones (rúbrica 5.2, 6.1, 6.2) · `ruteo/pesos.py`, `ruteo/config.py`

**Peso de riesgo por arista** (a partir de las amenazas):

```
riesgo(e) = D(m_e) / max_e' D(m_e')      D(x) = Σ_i exp(−‖x − ev_i‖² / 2σ²)
```

donde `m_e` es el punto medio del tramo y `ev_i` son los eventos históricos. Resultado en `[0, 1]`.

**Con las fuentes reales** (`BD/pesos.sql`), el riesgo combina tres componentes en `[0, 1]`, tratados como independientes:

```
r_eventos   = densidad normalizada de eventos UCDP (σ = 1 km)
r_incendios = densidad normalizada de incendios de guerra del período histórico (σ = 0,5 km)
p_gnss      = fracción de días en rojo de la celda GPSJam que contiene el tramo (0 si no hay datos)
riesgo(e)   = 1 − (1 − r_eventos)(1 − r_incendios)(1 − p_gnss)
```

**Restricción de altura con relieve** (`comun/transformar.py`). El UAV vuela a `altura_vuelo_m` sobre el despegue. El obstáculo de un tramo se calcula como:

```
obstáculo(e) = (terreno_max(e) − elevación(origen)) + altura_max_edificio(e)
```

donde `terreno_max` es el máximo de los extremos y el punto medio (Copernicus GLO-90) y `altura_max_edificio` es el edificio OSM más alto a ≤ 15 m del tramo. El tramo se excluye si `obstáculo ≥ altura − margen`. Sin edificio ni relieve, no restringe.

**Costo del método propuesto**, en "km equivalentes" (la distancia recorrida se sigue midiendo en km reales):

```
c(e, u→v) = largo_km(e) · f_viento(u→v) · (1 + w_R · riesgo(e)) · π(e)
f_viento   = v / (v − h),  con h = V·cos(rumbo − dir_viento) la componente de frente (h ≤ 0,8 v)
π(e)       = 1 + γ si e está a ≤ ρ de un tramo descubierto bloqueado; 1 en otro caso
```

**Preferencias del usuario y sus valores por defecto** (`Preferencias`):

| Preferencia | Efecto | Por defecto |
|---|---|---|
| `altura_vuelo_m`, `margen_vertical_m` | **Excluye** tramos sobre edificios con altura ≥ altura − margen (si OSM trae la altura) | 60 m, 10 m |
| `respetar_zonas_restringidas` | **Excluye** tramos dentro de zonas OpenAIP | Sí |
| `viento_max_m_s` | Por encima de este valor, la misión no es admisible | 12 m/s |
| `velocidad_crucero_m_s` | Entra en `f_viento` | 12 m/s |
| `desvio_max` (α) | Una candidata es válida si `km ≤ (1+α)·km_mín` | 0,35 |
| `presupuesto_extra` (β) | `km_max = (1+β)·L*` | 0,60 |
| `peso_riesgo` (w_R) | Aversión a sectores con amenazas históricas | 1,0 |

**Regla de datos faltantes:** un dato ausente nunca bloquea. Sin altura, sin zonas o sin viento, la regla queda neutra (factor 1). Las restricciones duras definen el **grafo admisible**, que es el mismo para **todos** los métodos; la línea base sigue usando como costo solo los km.

## 4. Algoritmo propuesto (rúbrica 7.1, 7.2) · `ruteo/algoritmos.py`, `ruteo/simulador.py`

**Paper del algoritmo base:** Yen, J. Y. (1971). *Finding the K Shortest Loopless Paths in a Network*. Management Science 17(11), 712–716. [doi:10.1287/mnsc.17.11.712](https://doi.org/10.1287/mnsc.17.11.712). En pgRouting corresponde a `pgr_KSP`. Luna et al. (2024) fundamenta la necesidad de replanificar durante el vuelo en misiones de inspección; **no** se reproduce su sistema.

**Aporte propio:** (1) selección resiliente del par, (2) replanificación con penalización de la zona incierta y (3) control de presupuesto.

```text
PLANIFICAR_TRAMO(s, t):
  bloq  ← excluidas ∪ conocidas
  cand  ← Yen(s, t, K=8, costo = c)  ∪ {Dijkstra_km(s, t)}
  cand  ← { r ∈ cand : km(r) ≤ (1+α)·km_mín  y  km(r) ≤ holgura }        # holgura = km_max − km_recorridos − km_mín(tramos siguientes)
  (p,q) ← argmin_{p≠q}  J(p,q) = w_L·[(km_p+km_q)/(2·km_mín) − 1] + w_S·S(p,q) + w_R·(R_p+R_q)/2
  principal ← el de menor costo c entre p y q;  alternativa ← el otro

AL_DESCUBRIR(tramo bloqueado b):
  para todo e con ‖m_e − m_b‖ ≤ ρ:  π(e) ← 1 + γ        # la falla es espacial: los tramos vecinos probablemente también caen

REACCIONAR(pos, t):
  r ← Dijkstra(pos, t, costo = c, sin conocidas)
  si km(r) > holgura:  r ← Dijkstra_km(pos, t, sin conocidas)        # si el desvío prudente no cabe, se prioriza completar
  si no hay r: fracaso ("sin_alternativa" o "atrapado")
```

**Solape espacial** `S(p,q) ∈ [0,1]`: fracción de la longitud de cada ruta cuyos tramos tienen el punto medio a menos de `d_sep = 0,4 km` de la otra (promedio simétrico). Se mide la separación **física** y no solo las aristas compartidas, porque dos rutas paralelas a 100 m caen juntas ante el mismo disco.

Parámetros (`ParametrosAlgoritmo`): `K = 8`, `w_L = 1`, `w_S = 1`, `d_sep = 0,4 km`, `ρ = 0,6 km`, `γ = 3`.

## 5. Línea base y k ≥ 2 rutas (rúbrica 8 y 9)

**Dijkstra por km, 2 rutas** (`dijkstra_dos_rutas`): la ruta 1 es `Dijkstra(cost = largo_km)`; la ruta 2 es Dijkstra **excluyendo las aristas de la ruta 1**. Si esa exclusión desconecta los extremos, se penalizan ×10 en vez de excluirlas. Es determinista y usa solo km. La versión en pgRouting está implementada en `comun/rutas.py` (`dijkstra_dos_rutas_pgr`, `ksp_pgr`, `propuesta_pgr`) y la usan el sitio y `BD/rutas_ejemplo.py`. **Todavía no se ha ejecutado contra la BD.** Las consultas son:

```sql
-- Ruta 1
SELECT * FROM pgr_dijkstra('SELECT id, source, target, largo_km AS cost, largo_km AS reverse_cost FROM aristas', :a, :b, directed := false);
-- Ruta 2: mismas aristas salvo las de la ruta 1
SELECT * FROM pgr_dijkstra('SELECT id, source, target, largo_km AS cost, largo_km AS reverse_cost FROM aristas
                            WHERE id NOT IN (SELECT edge FROM ruta_1)', :a, :b, directed := false);
-- Candidatas del método propuesto (costo enriquecido)
SELECT * FROM pgr_KSP('SELECT id, source, target, costo_c AS cost, costo_c AS reverse_cost FROM aristas', :a, :b, 8, directed := false);
```

**Método propuesto, 2 rutas:** el par `(principal, alternativa)` de §4.

## 6. Estrategias comparadas

| Clave | Estrategia | Qué aísla |
|---|---|---|
| **A** | Par Dijkstra-km calculado antes de salir; ante un bloqueo retrocede al último nodo común y toma la ruta 2; si esta también falla, la misión fracasa | Línea base de la rúbrica |
| **B** | Igual que A, con las 2 rutas más cortas de Yen | Efecto de "solo tener más rutas" |
| **D** | Dijkstra-km recalculado desde la posición actual sin los tramos vistos bloqueados | **Ablación:** efecto de replanificar, sin selección resiliente |
| **C0** | C sin penalización del entorno (γ = 0) | Aporte de `π` |
| **C1** | C sin control de presupuesto (v1 del diseño) | Aporte del control de presupuesto |
| **C** | Propuesta completa | — |

Todas las estrategias usan el mismo grafo admisible, la misma misión, el mismo escenario y el mismo presupuesto.

## 7. Métricas (rúbrica 10, 11.2) · `ruteo/metricas.py`

- **`R_mision`** = misiones completadas dentro del presupuesto / misiones evaluadas (**principal**).
- **`R_par`** = tramos en que al menos una ruta del par precalculado no toca ninguna falla del escenario / tramos. Mide la calidad del par, no la recuperación.
- **`ΔR = R_C − R_A`** en **puntos porcentuales**, con prueba exacta de **McNemar** sobre los escenarios discordantes (la comparación es pareada).
- Costo: km medios, sobrelongitud `km/L* − 1` en las exitosas, km extra **pareado** (solo en misiones que ambos métodos completan), replanificaciones, fracción de puntos visitados en las misiones fallidas y tiempo de cálculo.
- `R_oraculo_estatico`: factibilidad con conocimiento perfecto de todas las fallas desde el inicio. Es una referencia, **no** una cota estricta, porque ignora los casos en que el UAV queda atrapado.

## 8. Protocolo experimental

- Semillas separadas: **ajuste** `0–99` (diseñar y calibrar) y **evaluación** `10 000–10 299` (una sola corrida, con los parámetros congelados).
- **Hipótesis (refutable):** con los parámetros por defecto congelados, en el conjunto de evaluación, `R_C > R_A` con p < 0,05 (McNemar) y una sobrelongitud media de C que no supere β. **Se rechaza** si no hay diferencia significativa o si C excede el presupuesto con más frecuencia que A.
- **Hipótesis secundaria (la que de verdad mide el aporte propio):** `R_C > R_D`. Ver §9: con el diseño actual, **los datos de ajuste no la respaldan**.
- Barridos de sensibilidad: `prob_foco ∈ {0; 0,5; 0,8}` × `n_fallas ∈ {1, 3, 5}` y `β ∈ {0,1; 0,2; 0,6}`.

## 9. Resultados preliminares (conjunto de ajuste, 100 escenarios por celda)

Generados con `python experimentos/run_experimentos.py --conjunto ajuste --sensibilidad` y `--n-fallas 5 --presupuesto {0.1,0.2}`. Columnas `ΔR`: pp (escenarios en que solo gana el método / solo gana la referencia, p de McNemar). Sobrelongitud de las misiones exitosas: C / D / A.

| prob_foco | n_fallas | β | R_A | R_B | R_D | R_C0 | R_C1 | **R_C** | ΔR C−A | ΔR C−D | sobrelong. C / D / A |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 1 | 0.6 | 0.95 | 0.90 | 0.98 | 0.98 | 0.98 | **0.98** | +3 (4/1, p=0.375) | +0 (1/1, p=1) | 7.5 % / 0.8 % / 2.1 % |
| 0.0 | 3 | 0.6 | 0.81 | 0.76 | 0.96 | 0.97 | 0.96 | **0.97** | +16 (17/1, p=0.00014) | +1 (3/2, p=1) | 10.2 % / 2.2 % / 5.3 % |
| 0.0 | 5 | 0.6 | 0.70 | 0.62 | 0.92 | 0.93 | 0.91 | **0.92** | +22 (25/3, p=3e-05) | +0 (5/5, p=1) | 12.6 % / 3.8 % / 7.8 % |
| 0.5 | 1 | 0.6 | 0.99 | 0.97 | 1.00 | 0.99 | 0.99 | **0.99** | +0 (1/1, p=1) | −1 (0/1, p=1) | 7.0 % / 0.5 % / 0.8 % |
| 0.5 | 3 | 0.6 | 0.91 | 0.82 | 0.96 | 0.97 | 0.96 | **0.97** | +6 (7/1, p=0.0703) | +1 (2/1, p=1) | 8.7 % / 1.4 % / 3.3 % |
| 0.5 | 5 | 0.6 | 0.87 | 0.73 | 0.96 | 0.97 | 0.96 | **0.97** | +10 (12/2, p=0.0129) | +1 (3/2, p=1) | 10.3 % / 2.0 % / 5.1 % |
| 0.8 | 1 | 0.6 | 0.99 | 0.98 | 1.00 | 1.00 | 1.00 | **1.00** | +1 (1/0, p=1) | +0 (0/0, p=1) | 6.6 % / 0.1 % / 0.2 % |
| 0.8 | 3 | 0.6 | 0.97 | 0.91 | 0.97 | 0.99 | 0.99 | **0.99** | +2 (3/1, p=0.625) | +2 (3/1, p=0.62) | 7.5 % / 0.5 % / 2.1 % |
| 0.8 | 5 | 0.6 | 0.95 | 0.87 | 0.97 | 0.99 | 0.99 | **0.99** | +4 (5/1, p=0.219) | +2 (3/1, p=0.62) | 7.9 % / 0.8 % / 3.2 % |
| 0.5 | 5 | **0.1** | 0.70 | 0.71 | 0.91 | 0.83 | 0.71 | **0.84** | +14 (18/4, p=0.00434) | −7 (4/11, p=0.12) | 6.5 % / 1.0 % / 0.1 % |
| 0.5 | 5 | **0.2** | 0.75 | 0.72 | 0.94 | 0.94 | 0.85 | **0.90** | +15 (18/3, p=0.00149) | −4 (3/7, p=0.34) | 8.0 % / 1.4 % / 1.1 % |

`R_par` (β = 0,6): C obtiene el valor más alto en las 9 celdas (por ejemplo, con `prob_foco = 0,5` y 5 fallas: C 0,94, A 0,91 y B 0,88). La selección sí produce pares físicamente más independientes. El tiempo de cálculo medio de C es de unos 34 ms por misión, frente a ~1 ms de A y D.

### Lectura honesta

1. **Frente a Dijkstra (A), la propuesta nunca empeora la tasa de misiones completadas** y la mejora hasta en +22 pp. La diferencia es significativa (p < 0,05) en 5 de las 11 celdas, todas con 3 o más fallas. Esto responde a la pregunta del enunciado.
2. **Casi toda esa mejora viene de replanificar**, no de la selección resiliente: la ablación D (Dijkstra que replanifica) alcanza la misma tasa que C con β = 0,6 y la **supera** con presupuestos ajustados (β = 0,1 y 0,2). Además, C0 (sin penalizar el entorno) rinde igual o mejor que C. Con los datos actuales no se puede afirmar que el aporte propio supere a una replanificación simple.
3. **La selección tiene un costo fijo** de ~6–7 % de km incluso sin fallas: elige rutas que evitan riesgo y que forman pares separados. Con β pequeño ese costo consume la holgura que después falta para los desvíos.
4. **B (Yen top-2) es peor que A**: las dos rutas más cortas suelen compartir corredor. Esto confirma que *Yen por sí solo no da resiliencia*.
5. **Historial del diseño (sobre el conjunto de ajuste):** la v1 (= C1) penalizaba el entorno sin mirar el presupuesto y, con β = 0,1, se quedaba en 0,71. El control de presupuesto (v2) la subió a 0,84. Este cambio se hizo **antes** de tocar el conjunto de evaluación.

### Implicaciones para el grupo

- Si se presenta C contra A (lo que pide la rúbrica), el resultado es positivo. Si el profesor pregunta "¿y contra Dijkstra replanificando?", hay que mostrar D: **no incluirlo sería ocultar una ablación desfavorable.**
- Opciones para que la selección resiliente aporte de verdad (decidir antes de congelar parámetros):
  - **Calibrar `w_R` y `γ`** en el conjunto de ajuste (por ejemplo, con un barrido pequeño) para reducir el costo fijo.
  - **Escenarios donde la ventaja de C sea plausible:** detección tardía (el UAV solo se entera al entrar en el tramo), costo de replanificar (latencia o límite de replanificaciones) o fallas comunicadas por un UAV predecesor, que era la idea del profesor y deja al planificador información parcial antes de llegar.
  - **Redefinir el aporte como "selección consciente del presupuesto"** y medir la métrica `R_par`, donde C sí gana de forma consistente.

## 10. Limitaciones

- Grafo, focos, eventos y fallas son **sintéticos**; con datos reales cambia la distribución espacial y los resultados pueden cambiar.
- Modelo 2,5D: sin altura de vuelo variable, sin energía ni tiempo, y el viento es uniforme en el AOI.
- Un solo UAV, sin comunicación, conocimiento solo local y fallas permanentes (las transitorias están modeladas pero no se evaluaron).
- Una sola misión (mismos A, P1–P3, B) y una sola malla (semilla 7): falta variar la misión y la malla para generalizar.

## 11. Próximos pasos (ordenados por dependencia)

1. **Grupo:** acordar si se itera sobre C (§9) o se congela la v2; luego correr `--conjunto evaluacion` **una sola vez**.
2. **Implementado, sin ejecutar todavía:**
   - Docker con PostGIS y pgRouting, `BD/schema.sql`, el diagrama y los cargadores.
   - ETL de 3 metadata (OSM, elevación de Open-Meteo y viento ERA5) y 3 amenazas (GPSJam, incendios de guerra y UCDP), cada uno con su documento de estructura.
   - Pesos en SQL, rutas con `pgr_dijkstra` / `pgr_KSP`, sitio Leaflet y `main.py`.

   Falta la primera ejecución completa (`python main.py`) y corregir lo que falle (ver `ENTREGA_TAREA2.md`).
3. Comparar las rutas de pgRouting con las de Python (`ruteo/algoritmos.py`) sobre el mismo grafo. Pueden diferir solo en empates.
4. Opcional, para fortalecer el aporte frente a D: el aviso compartido entre UAV (estrategias D_A y C_A, ver `research_reformulación/`).

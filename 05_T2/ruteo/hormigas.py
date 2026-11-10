"""Técnica 6.4: colonia de hormigas (ACO) para el camino s -> t con las restricciones del usuario.

Base: Ant System (Dorigo, Maniezzo y Colorni, 1996, IEEE Trans. SMC-B 26(1):29-41) con las cotas de
feromona de MAX-MIN Ant System (Stützle y Hoos, 2000, Future Gener. Comput. Syst. 16(8):889-914).

Por qué ACO: construye caminos sobre el grafo paso a paso, que es justo la forma del problema, y
admite restricciones sobre la ruta completa (fiabilidad, autonomía) sin linealizarlas.

Cada hormiga sale de s y elige el siguiente arco a = (u -> v), entre los vecinos no visitados,
con probabilidad proporcional a

    tau_a^alfa * (1 / (c_a + h(v)))^beta * ((1 - p_e)(1 - p_v))^gamma

donde tau es la feromona, c el costo del arco (km equivalentes con viento), h(v) el costo mínimo
que falta desde v hasta t (heurística de distancia) y el último factor atrae hacia lo fiable.
Calidad de un camino (menor es mejor), con M = penalización:

    F = C * (1 + M * [exceso_fiabilidad / l_max + exceso_autonomía / B])

Tras cada iteración se evapora la feromona (factor 1 - rho), la mejor hormiga de la iteración
deposita 1/F en sus arcos (y la mejor global cada 5 iteraciones) y tau se acota a [tau_min, tau_max].
Se detiene tras `iteraciones` o `sin_mejora` iteraciones seguidas sin mejorar. Con la semilla fija es
reproducible. Solo biblioteca estándar.
"""
from __future__ import annotations

import math
import random
import time

from .algoritmos import Ruta, distancias
from .config import ParametrosACO
from .modelo_t3 import Instancia


def aco(inst: Instancia, s: int, t: int, autonomia_km: float, l_max: float,
        params: ParametrosACO = ParametrosACO()) -> tuple[Ruta | None, dict]:
    t0 = time.perf_counter()
    g = inst.g
    rng = random.Random(params.semilla)
    h = distancias(g, t, inst.c, inst.excluidas, hacia_origen=True)  # costo mínimo de cada nodo hasta t
    if s not in h:
        return None, {"error": "Sin camino sobrevolable."}

    # Vecinos admisibles con su factor heurístico precalculado (no cambia entre hormigas).
    vecinos: dict[int, list[tuple[int, int, float]]] = {}
    for aid, u, v in inst.arcos():
        if v not in h or v == s or u == t:
            continue
        p_e = inst.prob.aristas.get(aid, 0.0)
        p_v = inst.prob.nodos.get(v, 0.0)
        eta = (1.0 / (inst.c(aid, u, v) + h[v] + 1e-9)) ** params.beta * ((1 - p_e) * (1 - p_v)) ** params.gamma
        vecinos.setdefault(u, []).append((v, aid, eta))

    def calidad(nodos: list[int], aristas: list[int]) -> tuple[float, bool, float, float, float]:
        c = sum(inst.c(a, nodos[i], nodos[i + 1]) for i, a in enumerate(aristas))
        l_r = sum(inst.l(a, nodos[i], nodos[i + 1]) for i, a in enumerate(aristas))
        km = sum(inst.d(a) for a in aristas)
        exceso = max(0.0, l_r - l_max) / max(l_max, 1e-9) + max(0.0, km - autonomia_km) / max(autonomia_km, 1e-9)
        return c * (1 + params.penalizacion * exceso), exceso == 0.0, c, l_r, km

    tau_max = 1.0 / (params.rho * h[s])
    tau_min = tau_max / 50
    # MMAS: la feromona parte en tau_max en todos los arcos, lo que favorece explorar al inicio.
    tau: dict[tuple[int, int], float] = {(aid, u): tau_max for u, lista in vecinos.items() for _, aid, _ in lista}

    def feromona(aid: int, u: int) -> float:
        return tau[(aid, u)]

    def construir() -> tuple[list[int], list[int]] | None:
        nodos, aristas, vistos = [s], [], {s}
        while nodos[-1] != t:
            u = nodos[-1]
            cands = [(v, aid, eta) for v, aid, eta in vecinos.get(u, ()) if v not in vistos]
            if not cands:
                return None  # callejón sin salida: la hormiga se descarta
            pesos = [feromona(aid, u) ** params.alfa * eta for _, aid, eta in cands]
            v, aid, _ = rng.choices(cands, weights=pesos)[0]
            nodos.append(v)
            aristas.append(aid)
            vistos.add(v)
        return nodos, aristas

    mejor = None  # (factible, F, nodos, aristas)
    convergencia, validas, sin_mejora, mejor_iteracion = [], 0, 0, 0
    it = 0
    for it in range(1, params.iteraciones + 1):
        mejor_it = None
        for _ in range(params.n_hormigas):
            camino = construir()
            if camino is None:
                continue
            validas += 1
            F, factible = calidad(*camino)[:2]
            if mejor_it is None or (not factible, F) < (not mejor_it[0], mejor_it[1]):
                mejor_it = (factible, F, *camino)
        if mejor_it is not None and (mejor is None or (not mejor_it[0], mejor_it[1]) < (not mejor[0], mejor[1])):
            mejor, sin_mejora, mejor_iteracion = mejor_it, 0, it
            tau_max = 1.0 / (params.rho * mejor[1])
            tau_min = tau_max / 50
        else:
            sin_mejora += 1
        # Evaporación y depósito (MMAS: la mejor de la iteración; la global cada 5 iteraciones).
        for k in tau:
            tau[k] *= 1 - params.rho
        depositante = mejor if (it % 5 == 0 and mejor) else mejor_it
        if depositante is not None:
            _, F, nodos, aristas = depositante
            for i, aid in enumerate(aristas):
                tau[(aid, nodos[i])] += 1.0 / F
        for k in tau:
            tau[k] = min(tau_max, max(tau_min, tau[k]))
        convergencia.append(round(mejor[1], 4) if mejor else None)
        if sin_mejora >= params.sin_mejora:
            break

    detalle = {"iteraciones": it, "mejor_iteracion": mejor_iteracion, "hormigas_validas": validas,
               "hormigas_totales": it * params.n_hormigas, "convergencia": convergencia,
               "parametros": {k: getattr(params, k) for k in ("n_hormigas", "iteraciones", "alfa", "beta", "gamma",
                                                              "rho", "sin_mejora", "penalizacion", "semilla")},
               "tiempo_total_ms": round(1000 * (time.perf_counter() - t0), 2)}
    if mejor is None:
        detalle["error"] = "Ninguna hormiga llegó al destino."
        return None, detalle
    factible, F, nodos, aristas = mejor
    detalle.update(factible=factible, aptitud=round(F, 6))
    if not factible:
        detalle["nota"] = "La mejor ruta encontrada viola la fiabilidad mínima o la autonomía (se muestra igual)."
    return Ruta(nodos, aristas), detalle

"""Instancia común de las cuatro técnicas de la Tarea 3 (punto 6) y evaluación de sus rutas.

Todas trabajan sobre el MISMO grafo sobrevolable (punto 2: sin los tramos excluidos por altura,
relieve o zonas) y se diferencian en qué consideran:

    6.1 dijkstra_m          solo la distancia en metros (pgr_dijkstra)
    6.2 milp_gurobi         modelo formal: min sum c_a x_a  s.a. flujo, autonomía y fiabilidad >= R_min
    6.3 dijkstra_ponderado  pgr_dijkstra con costo c_a + lambda * l_a (relajación lagrangiana del 6.2)
    6.4 aco                 colonia de hormigas con las mismas restricciones como penalización

Notación por arco dirigido a = (u -> v) de un tramo e:
    d_a  largo del tramo (km)
    f_a  factor de viento de frente v / (v - h)  (1 si el viento no se considera)
    c_a  = d_a * f_a, km equivalentes = tiempo de vuelo x velocidad de crucero (objetivo)
    l_a  = -ln(1 - p_e) - ln(1 - p_v): sumado sobre la ruta da -ln(fiabilidad)
Restricciones del usuario:  sum d_a x_a <= autonomía (km)  y  sum l_a x_a <= -ln(R_min).
Solo biblioteca estándar.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable

from .algoritmos import Costo, Ruta, dijkstra
from .config import Considerar, Preferencias
from .grafo import Grafo
from .pesos import Viento, factor_viento
from .probabilidad import Probabilidades

TECNICAS = {  # clave -> nombre que muestra el sitio
    "dijkstra_m": "pgr_dijkstra (metros)",
    "milp_gurobi": "MILP con Gurobi",
    "dijkstra_ponderado": "pgr_dijkstra ponderado",
    "aco": "Colonia de hormigas (ACO)",
}


@dataclass
class Instancia:
    g: Grafo
    prefs: Preferencias
    prob: Probabilidades
    excluidas: frozenset[int]
    viento: Viento | None = None
    considerar: Considerar = field(default_factory=Considerar)
    _f: dict = field(default_factory=dict, repr=False)

    def f(self, aid: int, u: int, v: int) -> float:
        if self.viento is None or not self.considerar.viento:
            return 1.0
        if (aid, u) not in self._f:
            self._f[(aid, u)] = factor_viento(self.g, u, v, self.viento, self.prefs)
        return self._f[(aid, u)]

    def d(self, aid: int, u: int = 0, v: int = 0) -> float:
        return self.g.aristas[aid].largo_km

    def c(self, aid: int, u: int, v: int) -> float:
        return self.g.aristas[aid].largo_km * self.f(aid, u, v)

    def l(self, aid: int, u: int, v: int) -> float:
        return self.prob.l_arco(aid, v)

    def costo_lagrange(self, lam_km: float) -> Costo:
        return lambda aid, u, v: self.c(aid, u, v) + lam_km * self.l(aid, u, v)

    def arcos(self):
        """Arcos dirigidos sobrevolables (aid, u, v): cada tramo admisible en sus dos sentidos."""
        for aid, a in self.g.aristas.items():
            if aid not in self.excluidas:
                yield aid, a.u, a.v
                yield aid, a.v, a.u

    def metricas(self, ruta: Ruta, autonomia_km: float, r_min: float) -> dict:
        nodos, aristas = ruta.nodos, ruta.aristas
        largo = ruta.largo_km(self.g)
        objetivo = sum(self.c(a, nodos[i], nodos[i + 1]) for i, a in enumerate(aristas))
        fiab = self.prob.fiabilidad(nodos, aristas)
        return {
            "largo_km": round(largo, 4),
            "largo_m": round(1000 * largo, 1),
            "objetivo_km_eq": round(objetivo, 4),
            "tiempo_vuelo_min": round(1000 * objetivo / self.prefs.velocidad_crucero_m_s / 60, 2),
            "fiabilidad": round(fiab, 6),
            "cumple_autonomia": largo <= autonomia_km + 1e-9,
            "cumple_fiabilidad": fiab >= r_min - 1e-9,
            "tramos": len(aristas),
        }


def concatenar(tramos: list[Ruta]) -> Ruta:
    nodos, aristas = list(tramos[0].nodos), list(tramos[0].aristas)
    for r in tramos[1:]:
        nodos += r.nodos[1:]
        aristas += r.aristas
    return Ruta(nodos, aristas)


def largos_minimos(inst: Instancia, secuencia: list[int]) -> list[float] | None:
    """km del camino más corto sobrevolable de cada tramo de la misión (None si alguno es imposible)."""
    salida = []
    for s, t in zip(secuencia, secuencia[1:]):
        r = dijkstra(inst.g, s, t, inst.d, inst.excluidas)
        if r is None:
            return None
        salida.append(r.largo_km(inst.g))
    return salida


ResolverTramo = Callable[[int, int, float, float], tuple["Ruta | None", dict]]


@dataclass
class ResultadoTecnica:
    clave: str
    ruta: Ruta | None
    tramos: list[Ruta]
    tiempo_ms: float
    detalle: dict
    error: str | None = None


def por_tramos(clave: str, inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float,
               resolver: ResolverTramo) -> ResultadoTecnica:
    """Resuelve la misión tramo a tramo (s_k -> t_k) y concatena.

    Con puntos intermedios, la autonomía y la fiabilidad se reparten en proporción al largo
    mínimo L*_k de cada tramo:  B_k = B * L*_k / L*,  R_k = R_min ** (L*_k / L*), de modo que
    sum B_k = B y prod R_k = R_min. Es una descomposición (documentada): el óptimo global con
    restricciones compartidas podría repartirlas distinto.
    """
    t0 = time.perf_counter()
    minimos = largos_minimos(inst, secuencia)
    if minimos is None:
        return ResultadoTecnica(clave, None, [], 0.0, {}, "No hay ruta sobrevolable para algún tramo de la misión.")
    total = sum(minimos) or 1.0
    l_total = -math.log(max(r_min, 1e-12))
    tramos, detalles = [], []
    for k, (s, t) in enumerate(zip(secuencia, secuencia[1:])):
        parte = minimos[k] / total
        ruta, det = resolver(s, t, autonomia_km * parte, l_total * parte)
        detalles.append(det)
        if ruta is None:
            return ResultadoTecnica(clave, None, tramos, round(1000 * (time.perf_counter() - t0), 2),
                                    {"tramos": detalles}, det.get("error") or "Sin ruta para un tramo de la misión.")
        tramos.append(ruta)
    detalle = detalles[0] if len(detalles) == 1 else {"tramos": detalles}
    return ResultadoTecnica(clave, concatenar(tramos), tramos, round(1000 * (time.perf_counter() - t0), 2), detalle)


# ---------------------------------------------------------------- 6.3: relajación lagrangiana

Camino = Callable[[float], "Ruta | None"]  # lambda (km) -> camino mínimo con costo c + lambda * l


def lagrange(inst: Instancia, s: int, t: int, autonomia_km: float, l_max: float,
             camino: Camino | None = None, iteraciones: int = 12,
             lam_min: float = 1e-2, lam_max: float = 1e4) -> tuple[Ruta | None, dict]:
    """Dijkstra con costo c_a + lambda * l_a, buscando por bisección el menor lambda que cumple R_min.

    Es la relajación lagrangiana de la restricción de fiabilidad del MILP: Dijkstra no puede
    imponer una restricción sobre la ruta completa, pero al subir lambda cada tramo riesgoso
    "cuesta" más km. Al crecer lambda, la fiabilidad del camino no baja y su costo c no baja, así
    que el menor lambda factible da el camino factible más barato de esta familia. La brecha con el
    MILP es la brecha de dualidad. La autonomía se verifica después (no entra al costo).
    `camino` es el oráculo: pgr_dijkstra en el sitio (comun/tecnicas.py), Dijkstra en Python en las pruebas.
    """
    if camino is None:
        def camino(lam: float) -> Ruta | None:
            return dijkstra(inst.g, s, t, inst.costo_lagrange(lam), inst.excluidas)

    def suma_l(r: Ruta) -> float:
        return sum(inst.l(a, r.nodos[i], r.nodos[i + 1]) for i, a in enumerate(r.aristas))

    llamadas = 0

    def probar(lam: float):
        nonlocal llamadas
        llamadas += 1
        r = camino(lam)
        return r, (suma_l(r) if r else math.inf)

    r0, l0 = probar(0.0)
    if r0 is None:
        return None, {"error": "Sin camino sobrevolable.", "llamadas_dijkstra": llamadas}
    if l0 <= l_max + 1e-12:
        return r0, {"lambda_km": 0.0, "lambda_m": 0.0, "llamadas_dijkstra": llamadas, "cumple_fiabilidad": True}
    r_hi, l_hi = probar(lam_max)
    if l_hi > l_max + 1e-12:
        return r_hi, {"lambda_km": lam_max, "lambda_m": 1000 * lam_max, "llamadas_dijkstra": llamadas,
                      "cumple_fiabilidad": False,
                      "nota": "Ni con el mayor lambda se alcanza R_min: se entrega el camino más fiable que encontró."}
    lo, hi, mejor, lam_mejor = math.log10(lam_min), math.log10(lam_max), r_hi, lam_max
    for _ in range(iteraciones):
        medio = (lo + hi) / 2
        r, l_r = probar(10 ** medio)
        if l_r <= l_max + 1e-12:
            hi, mejor, lam_mejor = medio, r, 10 ** medio
        else:
            lo = medio
    return mejor, {"lambda_km": round(lam_mejor, 4), "lambda_m": round(1000 * lam_mejor, 1),
                   "llamadas_dijkstra": llamadas, "cumple_fiabilidad": True}

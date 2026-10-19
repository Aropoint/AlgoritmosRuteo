"""Algoritmos de ruteo: Dijkstra, Yen (k caminos simples) y selección resiliente de pares.

- Dijkstra (1959): camino mínimo; con costo = km replica pgr_dijkstra.
- Yen (1971), "Finding the K Shortest Loopless Paths in a Network": genera
  candidatos; equivale a pgr_KSP. Yen NO garantiza resiliencia por sí solo.
- seleccionar_par: aporte del grupo. Elige, entre los candidatos dentro del
  desvío permitido, el par (principal, alternativa) que minimiza
      J(p, q) = w_L * estiramiento + w_S * solape_espacial + w_R * riesgo
  priorizando alternativas que NO compartan corredor físico, porque una falla
  espacial que bloquea un tramo suele bloquear también los tramos vecinos.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from itertools import combinations, count
from typing import Callable

from .config import ParametrosAlgoritmo, Preferencias
from .geo import dist_punto_segmento
from .grafo import Grafo

Costo = Callable[[int, int, int], float]  # (id_arista, desde, hacia) -> costo


@dataclass
class Ruta:
    nodos: list[int]
    aristas: list[int]

    def largo_km(self, g: Grafo) -> float:
        return sum(g.aristas[a].largo_km for a in self.aristas)

    def costo(self, costo: Costo) -> float:
        return sum(costo(a, self.nodos[i], self.nodos[i + 1]) for i, a in enumerate(self.aristas))

    def riesgo_medio(self, g: Grafo) -> float:
        largo = self.largo_km(g)
        if largo == 0:
            return 0.0
        return sum(g.aristas[a].largo_km * g.aristas[a].atributos.get("riesgo", 0.0) for a in self.aristas) / largo

    def clave(self) -> tuple[int, ...]:
        return tuple(self.nodos)


def dijkstra(
    g: Grafo,
    s: int,
    t: int,
    costo: Costo,
    bloqueadas: frozenset[int] | set[int] = frozenset(),
    nodos_excluidos: frozenset[int] | set[int] = frozenset(),
) -> Ruta | None:
    dist = {s: 0.0}
    previo: dict[int, tuple[int, int]] = {}
    desempate = count()
    cola = [(0.0, next(desempate), s)]
    cerrados = set()
    while cola:
        d, _, u = heapq.heappop(cola)
        if u in cerrados:
            continue
        if u == t:
            break
        cerrados.add(u)
        for v, aid in g.ady[u]:
            if aid in bloqueadas or v in nodos_excluidos or v in cerrados:
                continue
            c = costo(aid, u, v)
            if math.isinf(c):
                continue
            nd = d + c
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                previo[v] = (u, aid)
                heapq.heappush(cola, (nd, next(desempate), v))
    if t not in dist:
        return None
    nodos, aristas = [t], []
    while nodos[-1] != s:
        u, aid = previo[nodos[-1]]
        nodos.append(u)
        aristas.append(aid)
    return Ruta(nodos[::-1], aristas[::-1])


def yen(
    g: Grafo,
    s: int,
    t: int,
    k: int,
    costo: Costo,
    bloqueadas: frozenset[int] | set[int] = frozenset(),
) -> list[Ruta]:
    """k caminos simples de menor costo, en orden no decreciente."""
    primera = dijkstra(g, s, t, costo, bloqueadas)
    if primera is None:
        return []
    A = [primera]
    B: list[tuple[float, int, Ruta]] = []
    vistas = {primera.clave()}
    desempate = count()
    while len(A) < k:
        previa = A[-1]
        for j in range(len(previa.nodos) - 1):
            espuela = previa.nodos[j]
            raiz_nodos = previa.nodos[: j + 1]
            raiz_aristas = previa.aristas[:j]
            excluidas = set(bloqueadas)
            for r in A:
                if r.nodos[: j + 1] == raiz_nodos:
                    excluidas.add(r.aristas[j])
            tramo = dijkstra(g, espuela, t, costo, excluidas, set(raiz_nodos[:-1]))
            if tramo is None:
                continue
            candidata = Ruta(raiz_nodos[:-1] + tramo.nodos, raiz_aristas + tramo.aristas)
            if candidata.clave() in vistas:
                continue
            vistas.add(candidata.clave())
            heapq.heappush(B, (candidata.costo(costo), next(desempate), candidata))
        if not B:
            break
        A.append(heapq.heappop(B)[2])
    return A


def dijkstra_dos_rutas(g: Grafo, s: int, t: int, costo: Costo, bloqueadas=frozenset()) -> list[Ruta]:
    """Línea base de la rúbrica (k = 2 solo con Dijkstra por km).

    Ruta 1: Dijkstra. Ruta 2: Dijkstra excluyendo las aristas de la ruta 1
    (en SQL: pgr_dijkstra sobre aristas WHERE id NOT IN ruta_1). Si eso
    desconecta s y t, se repite penalizando x10 en vez de excluir.
    """
    r1 = dijkstra(g, s, t, costo, bloqueadas)
    if r1 is None:
        return []
    usadas = set(r1.aristas)
    r2 = dijkstra(g, s, t, costo, set(bloqueadas) | usadas)
    if r2 is None:
        penal = lambda aid, u, v: costo(aid, u, v) * (10.0 if aid in usadas else 1.0)
        r2 = dijkstra(g, s, t, penal, bloqueadas)
        if r2 is not None and r2.clave() == r1.clave():
            r2 = None
    return [r1] + ([r2] if r2 else [])


def _fraccion_cercana(g: Grafo, p: Ruta, q: Ruta, d_km: float) -> float:
    """Fracción de la longitud de q cuyo punto medio de tramo está a < d_km de algún tramo de p."""
    segmentos_p = [g.extremos_xy(a) for a in p.aristas]
    aristas_p = set(p.aristas)
    total = cerca = 0.0
    for a in q.aristas:
        largo = g.aristas[a].largo_km
        total += largo
        if a in aristas_p:
            cerca += largo
            continue
        m = g.punto_medio_xy(a)
        if any(dist_punto_segmento(m, *seg) < d_km for seg in segmentos_p):
            cerca += largo
    return cerca / total if total else 1.0


def solape_espacial(g: Grafo, p: Ruta, q: Ruta, d_km: float) -> float:
    """S(p, q) in [0, 1]: 0 = corredores separados, 1 = mismo corredor (simétrico)."""
    return (_fraccion_cercana(g, p, q, d_km) + _fraccion_cercana(g, q, p, d_km)) / 2


@dataclass
class SeleccionPar:
    principal: Ruta
    alternativa: Ruta | None
    puntaje: float | None
    detalle: dict = field(default_factory=dict)


def seleccionar_par(
    g: Grafo,
    candidatas: list[Ruta],
    largo_minimo_km: float,
    costo: Costo,
    prefs: Preferencias,
    params: ParametrosAlgoritmo,
) -> SeleccionPar:
    """Selección resiliente del par de rutas para un tramo de misión."""
    limite = (1 + prefs.desvio_max) * largo_minimo_km + 1e-9
    validas = [r for r in candidatas if r.largo_km(g) <= limite]
    if not validas:
        validas = [min(candidatas, key=lambda r: r.largo_km(g))]
    if len(validas) == 1:
        return SeleccionPar(validas[0], None, None, {"candidatas": len(candidatas), "validas": 1})

    mejor = None
    for p, q in combinations(validas, 2):
        estiramiento = (p.largo_km(g) + q.largo_km(g)) / (2 * largo_minimo_km) - 1
        solape = solape_espacial(g, p, q, params.d_separacion_km)
        riesgo = (p.riesgo_medio(g) + q.riesgo_medio(g)) / 2
        j = params.peso_longitud * estiramiento + params.peso_solape * solape + prefs.peso_riesgo * riesgo
        if mejor is None or j < mejor[0]:
            mejor = (j, p, q, {"estiramiento": estiramiento, "solape": solape, "riesgo": riesgo})
    j, p, q, terminos = mejor
    principal, alternativa = (p, q) if p.costo(costo) <= q.costo(costo) else (q, p)
    terminos.update(candidatas=len(candidatas), validas=len(validas))
    return SeleccionPar(principal, alternativa, j, terminos)

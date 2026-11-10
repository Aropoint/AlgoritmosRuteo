"""Sorteo de fallas con números aleatorios entre 0 y 100 (Tarea 3, punto 7).

Para cada tramo y cada nodo se sortea n ~ U[0, 100) y se compara con su umbral de falla:

    umbral = 100 * (1 - p)        hay falla si n supera el umbral

así la falla ocurre con probabilidad exactamente p. Con la misma semilla el sorteo se repite.
Los elementos se sortean siempre en el mismo orden (ids crecientes) para que una semilla dé el
mismo resultado sin importar qué técnicas se evalúan. Un nodo que falla deja inutilizables todos
sus tramos. Los nodos obligatorios (origen, puntos intermedios y destino) tienen p = 0: son comunes
a todas las técnicas y no las distinguen.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .grafo import Grafo
from .probabilidad import Probabilidades, umbral_falla


@dataclass(frozen=True)
class Tirada:
    n: float        # número aleatorio en [0, 100)
    umbral: float   # 100 * (1 - p)
    p: float

    @property
    def falla(self) -> bool:
        return self.n > self.umbral

    def a_dict(self) -> dict:
        return {"n": round(self.n, 3), "umbral": round(self.umbral, 3), "p": round(self.p, 6), "falla": self.falla}


@dataclass
class Sorteo:
    semilla: int
    aristas: dict[int, Tirada]
    nodos: dict[int, Tirada]

    def aristas_falladas(self) -> set[int]:
        return {a for a, t in self.aristas.items() if t.falla}

    def nodos_fallados(self) -> set[int]:
        return {n for n, t in self.nodos.items() if t.falla}

    def caidas(self, g: Grafo) -> frozenset[int]:
        """Tramos inutilizables: los que fallan y todos los que tocan un nodo que falla."""
        caidas = self.aristas_falladas()
        for n in self.nodos_fallados():
            caidas.update(aid for _, aid in g.ady[n])
        return frozenset(caidas)

    def primer_fallo(self, nodos: list[int], aristas: list[int]) -> dict | None:
        """Primer elemento de la ruta, en orden de recorrido, que falla en este sorteo."""
        for i, n in enumerate(nodos):
            if i > 0:
                a = aristas[i - 1]
                if self.aristas[a].falla:
                    return {"tipo": "tramo", "id": a, "posicion": i - 1, **self.aristas[a].a_dict()}
            if self.nodos[n].falla:
                return {"tipo": "nodo", "id": n, "posicion": i, **self.nodos[n].a_dict()}
        return None


def sortear(prob: Probabilidades, semilla: int) -> Sorteo:
    rng = random.Random(semilla)
    aristas = {}
    for aid in sorted(prob.aristas):
        p = prob.aristas[aid]
        aristas[aid] = Tirada(rng.uniform(0, 100), umbral_falla(p), p)
    nodos = {}
    for nid in sorted(prob.nodos):
        p = prob.nodos[nid]
        nodos[nid] = Tirada(rng.uniform(0, 100), umbral_falla(p), p)
    return Sorteo(semilla, aristas, nodos)

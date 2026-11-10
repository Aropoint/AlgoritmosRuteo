"""Probabilidad de falla de tramos y nodos según las amenazas consideradas (Tarea 3, punto 5).

BD/probabilidades.sql guarda, por tramo y por nodo, la probabilidad de falla de cada amenaza:

    p_i = 1 - exp(-lambda_i^max * r_i * L)      (L = largo del tramo, o exposición del nodo)

Aquí se combinan en cada consulta, con solo las amenazas que el usuario marcó como "Considerar",
más las zonas de amenaza que dibujó en el mapa (discos abstractos con su probabilidad):

    p = 1 - prod_i (1 - p_i)                    (amenazas independientes)

La fiabilidad de una ruta es prod (1 - p) sobre sus tramos y nodos. Como -ln(1 - p) se suma a lo
largo de la ruta, la restricción "fiabilidad >= R_min" es lineal:  sum l_a <= -ln(R_min).
Solo biblioteca estándar: se prueba sin BD (tests/test_t3.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

from .geo import dist_punto_segmento
from .grafo import Grafo

AMENAZAS = ("eventos", "incendios", "gnss")   # sufijo de las columnas pf_* de la BD
ZONAS_USUARIO = "zonas_usuario"               # clave de "Considerar" para las zonas dibujadas
P_TOPE = 1 - 1e-9                             # evita -ln(0) con p = 1


def p_desde_tasa(tasa_por_km: float, largo_km: float) -> float:
    """Probabilidad de falla de un elemento expuesto `largo_km` a una tasa constante."""
    return 1.0 - math.exp(-max(tasa_por_km, 0.0) * max(largo_km, 0.0))


def combinar(ps: Iterable[float]) -> float:
    """Probabilidad de que ocurra al menos una de las fallas, tratadas como independientes."""
    supervivencia = 1.0
    for p in ps:
        supervivencia *= 1.0 - min(max(p, 0.0), 1.0)
    return 1.0 - supervivencia


def log_supervivencia(p: float) -> float:
    """l = -ln(1 - p) >= 0. Sumado sobre una ruta, exp(-sum l) es su fiabilidad."""
    return -math.log(1.0 - min(max(p, 0.0), P_TOPE))


def umbral_falla(p: float) -> float:
    """Umbral del sorteo 0-100 (punto 7): hay falla si el número aleatorio supera 100 * (1 - p)."""
    return 100.0 * (1.0 - min(max(p, 0.0), 1.0))


@dataclass(frozen=True)
class ZonaAmenaza:
    """Zona de amenaza dibujada por el usuario: disco abstracto (no es un sistema real).

    Todo tramo que toca el disco, y todo nodo dentro de él, suma la probabilidad de falla `p`.
    """
    lat: float
    lon: float
    radio_km: float
    p: float


@dataclass
class Probabilidades:
    aristas: dict[int, float]                                   # p combinada por tramo
    nodos: dict[int, float]                                     # p combinada por nodo
    detalle_aristas: dict[int, dict[str, float]] = field(default_factory=dict)  # por componente
    detalle_nodos: dict[int, dict[str, float]] = field(default_factory=dict)
    activas: tuple[str, ...] = ()

    def l_arco(self, aid: int, v: int) -> float:
        """-ln(1-p) del tramo más el del nodo al que se llega: suma exacta sobre la ruta."""
        return log_supervivencia(self.aristas.get(aid, 0.0)) + log_supervivencia(self.nodos.get(v, 0.0))

    def fiabilidad(self, nodos: list[int], aristas: list[int]) -> float:
        f = 1.0
        for a in aristas:
            f *= 1.0 - self.aristas.get(a, 0.0)
        for n in nodos:
            f *= 1.0 - self.nodos.get(n, 0.0)
        return f


def zonas_que_tocan_arista(g: Grafo, aid: int, zonas: list[ZonaAmenaza]) -> list[int]:
    a, b = g.extremos_xy(aid)
    return [i for i, z in enumerate(zonas) if dist_punto_segmento(g.proy.a_xy(z.lat, z.lon), a, b) <= z.radio_km]


def zonas_que_contienen_nodo(g: Grafo, nid: int, zonas: list[ZonaAmenaza]) -> list[int]:
    x, y = g.nodos[nid].xy
    salida = []
    for i, z in enumerate(zonas):
        zx, zy = g.proy.a_xy(z.lat, z.lon)
        if math.hypot(x - zx, y - zy) <= z.radio_km:
            salida.append(i)
    return salida


def calcular(g: Grafo, activas: Iterable[str], zonas: list[ZonaAmenaza] | None = None,
             obligatorios: Iterable[int] = ()) -> Probabilidades:
    """Probabilidades del grafo con las amenazas activas.

    Los componentes por amenaza salen de atributos["pf"] (cargados desde la BD por
    comun/rutas.grafo_desde_bd). Los nodos obligatorios (origen, puntos intermedios y destino) no
    fallan: son comunes a todas las técnicas y no las distinguen (se documenta en el sitio).
    """
    activas = tuple(a for a in activas if a in (*AMENAZAS, ZONAS_USUARIO))
    zonas = list(zonas or []) if ZONAS_USUARIO in activas else []
    obligatorios = set(obligatorios)
    det_a: dict[int, dict[str, float]] = {}
    det_n: dict[int, dict[str, float]] = {}
    for aid, a in g.aristas.items():
        pf = a.atributos.get("pf", {})
        comp = {k: float(pf.get(k, 0.0)) for k in AMENAZAS if k in activas}
        for i in zonas_que_tocan_arista(g, aid, zonas):
            comp[f"zona_{i + 1}"] = zonas[i].p
        det_a[aid] = comp
    for nid, n in g.nodos.items():
        if nid in obligatorios:
            det_n[nid] = {}
            continue
        pf = n.atributos.get("pf", {})
        comp = {k: float(pf.get(k, 0.0)) for k in AMENAZAS if k in activas}
        for i in zonas_que_contienen_nodo(g, nid, zonas):
            comp[f"zona_{i + 1}"] = zonas[i].p
        det_n[nid] = comp
    return Probabilidades(
        aristas={aid: combinar(c.values()) for aid, c in det_a.items()},
        nodos={nid: combinar(c.values()) for nid, c in det_n.items()},
        detalle_aristas=det_a, detalle_nodos=det_n, activas=activas,
    )

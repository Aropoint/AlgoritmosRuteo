"""Grafo de navegación G = (V, E): vértices = puntos geográficos, aristas = tramos de vuelo.

Los vértices NO son UAV y las aristas NO son enlaces de radio ni calles.
La malla es sintética y geolocalizada: su conectividad es una hipótesis del
simulador, no un corredor aéreo real.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from .config import AOI, Mision, ParametrosMalla
from .geo import ProyeccionLocal, haversine_km


@dataclass
class Nodo:
    id: int
    lat: float
    lon: float
    tipo: str = "navegacion"  # navegacion | inicio | observacion | destino
    xy: tuple[float, float] = (0.0, 0.0)


@dataclass
class Arista:
    id: int
    u: int
    v: int
    largo_km: float
    atributos: dict = field(default_factory=dict)


class Grafo:
    """Grafo no dirigido; cada arista se puede recorrer en ambos sentidos."""

    def __init__(self, proyeccion: ProyeccionLocal):
        self.proy = proyeccion
        self.nodos: dict[int, Nodo] = {}
        self.aristas: dict[int, Arista] = {}
        self.ady: dict[int, list[tuple[int, int]]] = {}  # nodo -> [(vecino, id_arista)]

    def agregar_nodo(self, nid: int, lat: float, lon: float, tipo: str = "navegacion") -> Nodo:
        n = Nodo(nid, lat, lon, tipo, self.proy.a_xy(lat, lon))
        self.nodos[nid] = n
        self.ady.setdefault(nid, [])
        return n

    def agregar_arista(self, u: int, v: int, atributos: dict | None = None) -> Arista:
        aid = max(self.aristas, default=-1) + 1
        nu, nv = self.nodos[u], self.nodos[v]
        a = Arista(aid, u, v, haversine_km(nu.lat, nu.lon, nv.lat, nv.lon), atributos or {})
        self.aristas[aid] = a
        self.ady[u].append((v, aid))
        self.ady[v].append((u, aid))
        return a

    def quitar_arista(self, aid: int) -> None:
        a = self.aristas.pop(aid)
        self.ady[a.u] = [(w, x) for w, x in self.ady[a.u] if x != aid]
        self.ady[a.v] = [(w, x) for w, x in self.ady[a.v] if x != aid]

    def otro_extremo(self, aid: int, u: int) -> int:
        a = self.aristas[aid]
        return a.v if a.u == u else a.u

    def punto_medio_xy(self, aid: int) -> tuple[float, float]:
        a = self.aristas[aid]
        (x1, y1), (x2, y2) = self.nodos[a.u].xy, self.nodos[a.v].xy
        return (x1 + x2) / 2, (y1 + y2) / 2

    def extremos_xy(self, aid: int) -> tuple[tuple[float, float], tuple[float, float]]:
        a = self.aristas[aid]
        return self.nodos[a.u].xy, self.nodos[a.v].xy

    def conexo(self) -> bool:
        if not self.nodos:
            return True
        inicio = next(iter(self.nodos))
        vistos = {inicio}
        cola = deque([inicio])
        while cola:
            u = cola.popleft()
            for w, _ in self.ady[u]:
                if w not in vistos:
                    vistos.add(w)
                    cola.append(w)
        return len(vistos) == len(self.nodos)

    def nodo_mas_cercano(self, lat: float, lon: float) -> int:
        return min(self.nodos.values(), key=lambda n: haversine_km(lat, lon, n.lat, n.lon)).id

    def a_json(self) -> dict:
        """Estructura documentada en Infraestructura/ESTRUCTURA_infraestructura_json.md."""
        return {
            "tipo": "grafo_navegacion_uav",
            "crs": "EPSG:4326",
            "nodos": [
                {"id": n.id, "lat": round(n.lat, 6), "lon": round(n.lon, 6), "tipo": n.tipo}
                for n in self.nodos.values()
            ],
            "aristas": [
                {
                    "id": a.id,
                    "source": a.u,
                    "target": a.v,
                    "largo_km": round(a.largo_km, 5),
                    "geometria": [
                        [round(self.nodos[a.u].lon, 6), round(self.nodos[a.u].lat, 6)],
                        [round(self.nodos[a.v].lon, 6), round(self.nodos[a.v].lat, 6)],
                    ],
                    "atributos": a.atributos,
                }
                for a in self.aristas.values()
            ],
        }


def generar_malla(params: ParametrosMalla = ParametrosMalla(), aoi: dict = AOI) -> Grafo:
    """Malla regular con perturbación aleatoria, 8-vecindad y retiro parcial de aristas.

    El retiro de aristas evita una cuadrícula perfecta (con infinitos empates)
    y nunca desconecta el grafo.
    """
    rng = random.Random(params.semilla)
    lat0 = (aoi["sur"] + aoi["norte"]) / 2
    lon0 = (aoi["oeste"] + aoi["este"]) / 2
    proy = ProyeccionLocal(lat0, lon0)
    g = Grafo(proy)

    x_min, y_min = proy.a_xy(aoi["sur"], aoi["oeste"])
    x_max, y_max = proy.a_xy(aoi["norte"], aoi["este"])
    paso = params.espaciado_km
    columnas = int((x_max - x_min) / paso) + 1
    filas = int((y_max - y_min) / paso) + 1

    indice: dict[tuple[int, int], int] = {}
    for f in range(filas):
        for c in range(columnas):
            dx = rng.uniform(-params.jitter, params.jitter) * paso
            dy = rng.uniform(-params.jitter, params.jitter) * paso
            x = min(max(x_min + c * paso + dx, x_min), x_max)
            y = min(max(y_min + f * paso + dy, y_min), y_max)
            lat, lon = proy.a_latlon(x, y)
            nid = len(indice)
            indice[(f, c)] = nid
            g.agregar_nodo(nid, lat, lon)

    vecinos = [(0, 1), (1, 0)] + ([(1, 1), (1, -1)] if params.diagonales else [])
    for (f, c), u in indice.items():
        for df, dc in vecinos:
            v = indice.get((f + df, c + dc))
            if v is not None:
                g.agregar_arista(u, v)

    objetivo = int(len(g.aristas) * params.fraccion_eliminada)
    candidatas = list(g.aristas)
    rng.shuffle(candidatas)
    retiradas = 0
    for aid in candidatas:
        if retiradas >= objetivo:
            break
        a = g.aristas[aid]
        g.quitar_arista(aid)
        if g.conexo():
            retiradas += 1
        else:
            g.agregar_arista(a.u, a.v, a.atributos)
    return g


def nodos_mision(g: Grafo, mision: Mision = Mision(), aoi: dict = AOI) -> list[int]:
    """Devuelve [inicio, P1, ..., Pm, destino] como ids de nodo y marca su tipo."""

    def a_nodo(fx: float, fy: float) -> int:
        lat = aoi["sur"] + fy * (aoi["norte"] - aoi["sur"])
        lon = aoi["oeste"] + fx * (aoi["este"] - aoi["oeste"])
        return g.nodo_mas_cercano(lat, lon)

    secuencia = [a_nodo(*mision.inicio)]
    g.nodos[secuencia[0]].tipo = "inicio"
    for p in mision.observacion:
        nid = a_nodo(*p)
        g.nodos[nid].tipo = "observacion"
        secuencia.append(nid)
    fin = a_nodo(*mision.destino)
    g.nodos[fin].tipo = "destino"
    secuencia.append(fin)
    if len(set(secuencia)) != len(secuencia):
        raise ValueError("Dos puntos de misión cayeron en el mismo nodo; separa sus coordenadas.")
    return secuencia

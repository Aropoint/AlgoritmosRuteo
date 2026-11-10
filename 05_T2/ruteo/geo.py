"""Utilidades geográficas: distancia geodésica y proyección local en km."""
from __future__ import annotations

import math

R_TIERRA_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_TIERRA_KM * math.asin(math.sqrt(a))


class ProyeccionLocal:
    """Proyección equirectangular centrada en el AOI.

    En un área de ~10 km el error frente a la geodésica es despreciable
    para decidir si un tramo cae dentro del radio de una falla.
    """

    def __init__(self, lat0: float, lon0: float):
        self.lat0 = lat0
        self.lon0 = lon0
        self.kx = math.radians(1) * R_TIERRA_KM * math.cos(math.radians(lat0))
        self.ky = math.radians(1) * R_TIERRA_KM

    def a_xy(self, lat: float, lon: float) -> tuple[float, float]:
        return (lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky

    def a_latlon(self, x: float, y: float) -> tuple[float, float]:
        return self.lat0 + y / self.ky, self.lon0 + x / self.kx


def dist_punto_segmento(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia euclidiana (km) entre el punto p y el segmento ab, en coordenadas proyectadas."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / largo2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def rumbo_grados(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Rumbo inicial de 1 a 2, en grados desde el norte en sentido horario."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def punto_en_poligono(p: tuple[float, float], poligono: list[tuple[float, float]]) -> bool:
    """Regla del rayo (par/impar) en coordenadas proyectadas. El polígono no necesita cerrarse."""
    x, y = p
    dentro = False
    n = len(poligono)
    for i in range(n):
        (x1, y1), (x2, y2) = poligono[i], poligono[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            dentro = not dentro
    return dentro


def _orientacion(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segmentos_se_cruzan(a, b, c, d) -> bool:
    """¿Se tocan los segmentos ab y cd? Incluye los casos colineales y de contacto en un extremo."""
    o1, o2, o3, o4 = _orientacion(a, b, c), _orientacion(a, b, d), _orientacion(c, d, a), _orientacion(c, d, b)
    if o1 * o2 < 0 and o3 * o4 < 0:  # cruce propio
        return True

    def sobre(p, q, r, o):  # r colineal con pq y dentro de su caja
        return abs(o) < 1e-12 and min(p[0], q[0]) - 1e-12 <= r[0] <= max(p[0], q[0]) + 1e-12 \
            and min(p[1], q[1]) - 1e-12 <= r[1] <= max(p[1], q[1]) + 1e-12

    return sobre(a, b, c, o1) or sobre(a, b, d, o2) or sobre(c, d, a, o3) or sobre(c, d, b, o4)


def segmento_toca_poligono(a, b, poligono: list[tuple[float, float]]) -> bool:
    """El tramo ab entra, sale o cruza el polígono (zona prohibida dibujada por el usuario)."""
    if punto_en_poligono(a, poligono) or punto_en_poligono(b, poligono):
        return True
    n = len(poligono)
    return any(segmentos_se_cruzan(a, b, poligono[i], poligono[(i + 1) % n]) for i in range(n))

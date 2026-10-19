"""Modelo de fallas espaciales (rúbrica 5.1).

Una falla es un disco (centro, radio) que deja indisponibles los tramos que
lo intersectan desde que el UAV ha recorrido `inicio_km` y, si es transitoria,
durante `duracion_km`. El planificador NO conoce las fallas: las descubre al
llegar a un nodo incidente al tramo afectado.

Tres niveles separados (ver CONTEXTO §7):
1. Registro externo (p. ej. un evento ACLED/FIRMS) -> focos de amenaza.
2. Interpretación: los focos sesgan dónde es más probable una falla.
3. Falla simulada: disco reproducible generado con semilla.

Los eventos usados para estimar pesos de riesgo y las fallas de evaluación
son muestras INDEPENDIENTES del mismo proceso espacial; con prob_foco = 0 los
pesos de riesgo no aportan información y la comparación lo debe reflejar.
"""
from __future__ import annotations

import random
from dataclasses import asdict, dataclass

from .config import ParametrosFallas
from .geo import dist_punto_segmento
from .grafo import Grafo


@dataclass(frozen=True)
class Falla:
    id: int
    x: float          # km, proyección local
    y: float
    radio_km: float
    inicio_km: float  # se activa cuando el UAV ha recorrido esta distancia
    duracion_km: float | None = None  # None = permanente durante la misión
    origen: str = "uniforme"  # uniforme | foco

    def activa(self, recorrido_km: float) -> bool:
        if recorrido_km < self.inicio_km:
            return False
        return self.duracion_km is None or recorrido_km < self.inicio_km + self.duracion_km


@dataclass
class Escenario:
    semilla: int
    fallas: list[Falla]
    afectadas: dict[int, frozenset[int]]  # id_falla -> aristas bloqueadas por esa falla
    descartadas: int = 0  # fallas re-muestreadas por cubrir un punto obligatorio

    def bloqueada(self, aid: int, recorrido_km: float) -> bool:
        return any(aid in self.afectadas[f.id] and f.activa(recorrido_km) for f in self.fallas)

    def todas_afectadas(self) -> frozenset[int]:
        return frozenset().union(*self.afectadas.values()) if self.afectadas else frozenset()

    def a_json(self, g: Grafo) -> dict:
        salida = []
        for f in self.fallas:
            lat, lon = g.proy.a_latlon(f.x, f.y)
            d = asdict(f)
            d.update(lat=round(lat, 6), lon=round(lon, 6), aristas=sorted(self.afectadas[f.id]))
            salida.append(d)
        return {"semilla": self.semilla, "descartadas": self.descartadas, "fallas": salida}


def limites_xy(g: Grafo) -> tuple[float, float, float, float]:
    xs = [n.xy[0] for n in g.nodos.values()]
    ys = [n.xy[1] for n in g.nodos.values()]
    return min(xs), min(ys), max(xs), max(ys)


def generar_focos(g: Grafo, n: int, semilla: int) -> list[tuple[float, float]]:
    """Focos sintéticos de amenaza. Con datos reales se reemplazan por eventos geolocalizados."""
    rng = random.Random(semilla)
    x0, y0, x1, y1 = limites_xy(g)
    return [(rng.uniform(x0, x1), rng.uniform(y0, y1)) for _ in range(n)]


def muestrear_cerca_de_focos(rng: random.Random, focos, sigma: float, limites) -> tuple[float, float]:
    x0, y0, x1, y1 = limites
    fx, fy = rng.choice(focos)
    x = min(max(rng.gauss(fx, sigma), x0), x1)
    y = min(max(rng.gauss(fy, sigma), y0), y1)
    return x, y


def eventos_historicos(g: Grafo, focos, params: ParametrosFallas, semilla: int) -> list[tuple[float, float]]:
    """Eventos del período de ajuste: solo alimentan los pesos de riesgo (pesos.py)."""
    rng = random.Random(semilla)
    lim = limites_xy(g)
    return [muestrear_cerca_de_focos(rng, focos, params.sigma_foco_km, lim) for _ in range(params.n_eventos_historicos)]


def aristas_en_disco(g: Grafo, x: float, y: float, radio: float) -> frozenset[int]:
    return frozenset(
        aid for aid in g.aristas
        if dist_punto_segmento((x, y), *g.extremos_xy(aid)) <= radio
    )


def generar_escenario(
    g: Grafo,
    focos,
    params: ParametrosFallas,
    largo_mision_km: float,
    puntos_obligatorios: list[int],
    semilla: int,
) -> Escenario:
    """Fallas de evaluación. Un disco que contiene un punto obligatorio se re-muestrea:
    haría la misión imposible para cualquier método y no discrimina entre ellos."""
    rng = random.Random(semilla)
    lim = limites_xy(g)
    x0, y0, x1, y1 = lim
    obligatorios_xy = [g.nodos[n].xy for n in puntos_obligatorios]
    fallas: list[Falla] = []
    afectadas: dict[int, frozenset[int]] = {}
    descartadas = 0
    while len(fallas) < params.n_fallas:
        if descartadas > 1000:
            raise RuntimeError("No se pudieron ubicar fallas sin cubrir puntos obligatorios.")
        if focos and rng.random() < params.prob_foco:
            x, y = muestrear_cerca_de_focos(rng, focos, params.sigma_foco_km, lim)
            origen = "foco"
        else:
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
            origen = "uniforme"
        radio = rng.uniform(params.radio_min_km, params.radio_max_km)
        inicio = rng.uniform(0, params.inicio_max_frac * largo_mision_km)
        if any((x - px) ** 2 + (y - py) ** 2 <= radio ** 2 for px, py in obligatorios_xy):
            descartadas += 1
            continue
        f = Falla(len(fallas), x, y, radio, inicio, None, origen)
        fallas.append(f)
        afectadas[f.id] = aristas_en_disco(g, x, y, radio)
    return Escenario(semilla, fallas, afectadas, descartadas)

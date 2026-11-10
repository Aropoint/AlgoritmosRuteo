"""Conversión de metadata y amenazas en restricciones y costos (rúbrica 5.2, 6.1, 6.2).

Restricciones duras (definen el grafo admisible, igual para TODOS los métodos):
- Tramo sobre edificación con altura >= altura_vuelo - margen (si OSM trae altura).
- Tramo dentro de zona restringida publicada (si respetar_zonas_restringidas).
- Viento medio > viento_max: la misión completa no es admisible.

Costos blandos (solo el método propuesto):
- Viento de frente: factor v / (v - h), con h = componente de frente (m/s).
- Riesgo histórico: factor (1 + w_R * riesgo), riesgo in [0, 1] estimado con
  una densidad de núcleo gaussiano sobre eventos del período de ajuste.
- Incertidumbre tras descubrir un bloqueo: factor (1 + gamma) en un radio rho.

Un dato ausente nunca bloquea: sin altura de edificio, sin zonas o sin viento,
la regla correspondiente queda neutra (factor 1) y se informa como tal.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .config import Considerar, Preferencias
from .geo import rumbo_grados, segmento_toca_poligono
from .grafo import Grafo


@dataclass(frozen=True)
class Viento:
    velocidad_m_s: float
    direccion_desde_grados: float  # convención meteorológica: de dónde sopla
    fuente: str = "sin_dato"


def asignar_riesgo(g: Grafo, eventos_xy: list[tuple[float, float]], sigma_km: float = 0.5) -> None:
    """Escribe atributos['riesgo'] in [0, 1] en cada arista (punto medio del tramo)."""
    if not eventos_xy:
        for a in g.aristas.values():
            a.atributos["riesgo"] = 0.0
        return
    dens = {}
    for aid in g.aristas:
        mx, my = g.punto_medio_xy(aid)
        dens[aid] = sum(math.exp(-((mx - ex) ** 2 + (my - ey) ** 2) / (2 * sigma_km ** 2)) for ex, ey in eventos_xy)
    maximo = max(dens.values()) or 1.0
    for aid, d in dens.items():
        g.aristas[aid].atributos["riesgo"] = round(d / maximo, 4)


def arista_admisible(atributos: dict, prefs: Preferencias) -> bool:
    altura = atributos.get("altura_max_edificio_m")
    if altura is not None and altura >= prefs.altura_vuelo_m - prefs.margen_vertical_m:
        return False
    if prefs.respetar_zonas_restringidas and atributos.get("en_zona_restringida", False):
        return False
    return True


def aristas_excluidas(g: Grafo, prefs: Preferencias) -> frozenset[int]:
    return frozenset(aid for aid, a in g.aristas.items() if not arista_admisible(a.atributos, prefs))


# ---------------------------------------------------------------- Tarea 3 (punto 2: tramos no sobrevolables)
#
# comun/rutas.grafo_desde_bd guarda por separado la altura del edificio (`edificio_m`) y el relieve
# relativo al despegue (`relieve_m`), para que las casillas "Considerar" de edificios y relieve
# decidan qué entra al obstáculo. Un grafo sin esas claves (Tarea 2, pruebas) usa el obstáculo ya
# combinado `altura_max_edificio_m`, con el mismo resultado que arista_admisible.

def obstaculo_m(atributos: dict, considerar: Considerar = Considerar()) -> float | None:
    """Altura del obstáculo del tramo sobre el despegue, con solo la metadata considerada."""
    if "edificio_m" not in atributos and "relieve_m" not in atributos:
        return atributos.get("altura_max_edificio_m")
    edificio = atributos.get("edificio_m") if considerar.edificios else None
    relieve = atributos.get("relieve_m") if considerar.relieve else None
    if edificio is None and relieve is None:
        return None
    return (relieve or 0.0) + (edificio or 0.0)


def motivo_exclusion(atributos: dict, prefs: Preferencias, considerar: Considerar = Considerar()) -> str | None:
    """Por qué el tramo no es sobrevolable: relieve, edificio o zona_publicada (None = sobrevolable)."""
    umbral = prefs.altura_vuelo_m - prefs.margen_vertical_m
    obstaculo = obstaculo_m(atributos, considerar)
    if obstaculo is not None and obstaculo >= umbral:
        relieve = atributos.get("relieve_m") if considerar.relieve else None
        return "relieve" if relieve is not None and relieve >= umbral else "edificio"
    if prefs.respetar_zonas_restringidas and considerar.zonas_publicadas and atributos.get("en_zona_restringida", False):
        return "zona_publicada"
    return None


def excluidas_con_motivo(g: Grafo, prefs: Preferencias, considerar: Considerar = Considerar(),
                         zonas_prohibidas_xy: list[list[tuple[float, float]]] | None = None) -> dict[int, str]:
    """Tramos que ninguna técnica puede usar, con su motivo. Las zonas prohibidas son polígonos en km locales."""
    zonas = zonas_prohibidas_xy if considerar.zonas_usuario else None
    salida = {}
    for aid, a in g.aristas.items():
        motivo = motivo_exclusion(a.atributos, prefs, considerar)
        if motivo is None and zonas:
            extremos = g.extremos_xy(aid)
            if any(segmento_toca_poligono(*extremos, z) for z in zonas):
                motivo = "zona_usuario"
        if motivo:
            salida[aid] = motivo
    return salida


def mision_admisible(viento: Viento | None, prefs: Preferencias) -> bool:
    return viento is None or viento.velocidad_m_s <= prefs.viento_max_m_s


def factor_viento(g: Grafo, u: int, v: int, viento: Viento | None, prefs: Preferencias) -> float:
    if viento is None or viento.velocidad_m_s == 0:
        return 1.0
    nu, nv = g.nodos[u], g.nodos[v]
    rumbo = rumbo_grados(nu.lat, nu.lon, nv.lat, nv.lon)
    frente = viento.velocidad_m_s * math.cos(math.radians(rumbo - viento.direccion_desde_grados))
    vel = prefs.velocidad_crucero_m_s
    frente = min(frente, 0.8 * vel)  # evita velocidad sobre tierra nula o negativa
    return vel / (vel - frente)


def costo_km(g: Grafo):
    """Costo de la línea base: solo longitud en km (igual que pgr_dijkstra con cost = largo_km)."""
    return lambda aid, u, v: g.aristas[aid].largo_km


def costo_propuesta(g: Grafo, prefs: Preferencias, viento: Viento | None, penalizadas: dict[int, float] | None = None):
    """Costo del método propuesto en "km equivalentes"; la distancia real se sigue midiendo en km."""
    penal = penalizadas or {}
    w_r = prefs.peso_riesgo

    def costo(aid: int, u: int, v: int) -> float:
        a = g.aristas[aid]
        c = a.largo_km * factor_viento(g, u, v, viento, prefs)
        c *= 1 + w_r * a.atributos.get("riesgo", 0.0)
        return c * penal.get(aid, 1.0)

    return costo

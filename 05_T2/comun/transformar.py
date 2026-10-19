"""Transformaciones puras del ETL y de las restricciones.

Solo usa la biblioteca estándar para poder probarlas sin red ni BD
(tests/test_etl.py).
"""
from __future__ import annotations

import math
import re

METROS_POR_NIVEL = 3.0  # altura asumida por piso cuando OSM solo trae building:levels

_NUMERO = re.compile(r"-?\d+(?:[.,]\d+)?")


def _numeros(texto: str) -> list[float]:
    return [float(x.replace(",", ".")) for x in _NUMERO.findall(texto)]


def parsear_altura_m(valor: str | None) -> float | None:
    """Tag OSM `height`: '12', '12 m', '12.5m', '40 ft', "40'". None si no se entiende."""
    if not valor:
        return None
    nums = _numeros(valor)
    if not nums or nums[0] <= 0:
        return None
    pies = "ft" in valor.lower() or "'" in valor
    return round(nums[0] * (0.3048 if pies else 1.0), 2)


def parsear_niveles(valor: str | None) -> int | None:
    """Tag OSM `building:levels`: '5', '5;6' (toma el mayor). None si no se entiende."""
    if not valor:
        return None
    nums = [n for n in _numeros(valor) if n > 0]
    return int(max(nums)) if nums else None


def altura_estimada_m(altura_m: float | None, niveles: int | None) -> tuple[float | None, str | None]:
    """(altura, origen). Prioriza `height`; si no hay, niveles x 3 m; si no, sin dato."""
    if altura_m is not None:
        return altura_m, "height"
    if niveles is not None:
        return round(niveles * METROS_POR_NIVEL, 2), "building:levels"
    return None, None


def anillo_cerrado(coords: list[list[float]]) -> list[list[float]] | None:
    """Anillo GeoJSON [[lon, lat], ...] cerrado; None si tiene menos de 3 vértices distintos."""
    if len(coords) < 3:
        return None
    anillo = [list(c) for c in coords]
    if anillo[0] != anillo[-1]:
        anillo.append(anillo[0])
    return anillo if len(anillo) >= 4 else None


def pct_malo_gpsjam(buenos: int, malos: int) -> float | None:
    """Porcentaje de aviones con navegación degradada según la fórmula publicada por GPSJam.

    GPSJam resta 1 avión "malo" para que un único avión con problemas no tiña
    la celda: (malos - 1) / (buenos + malos). None si no hubo aviones.
    """
    total = buenos + malos
    if total <= 0:
        return None
    return 100.0 * max(malos - 1, 0) / total


def celda_roja_gpsjam(buenos: int, malos: int, umbral_pct: float = 10.0) -> bool:
    """Regla del mapa de GPSJam: celda roja si más del 10 % de los aviones reporta degradación."""
    pct = pct_malo_gpsjam(buenos, malos)
    return pct is not None and pct > umbral_pct


def direccion_media_grados(direcciones: list[float], pesos: list[float] | None = None) -> float | None:
    """Media circular (la media aritmética de 350° y 10° sería 180°, no 0°)."""
    if not direcciones:
        return None
    pesos = pesos or [1.0] * len(direcciones)
    s = sum(w * math.sin(math.radians(d)) for d, w in zip(direcciones, pesos))
    c = sum(w * math.cos(math.radians(d)) for d, w in zip(direcciones, pesos))
    if math.hypot(s, c) < 1e-9 * max(sum(pesos), 1e-9):  # direcciones opuestas se anulan: no hay dirección media
        return None
    return round(math.degrees(math.atan2(s, c)) % 360, 1) % 360  # el último % evita devolver 360.0


def percentil(valores: list[float], p: float) -> float | None:
    """Percentil con interpolación lineal (igual que percentile_cont de PostgreSQL)."""
    xs = sorted(v for v in valores if v is not None)
    if not xs:
        return None
    pos = (len(xs) - 1) * p
    i = int(math.floor(pos))
    j = min(i + 1, len(xs) - 1)
    return xs[i] + (xs[j] - xs[i]) * (pos - i)


def viento_a_altura(v_ref_m_s: float, h_ref_m: float, h_m: float, alfa: float = 1 / 7) -> float:
    """Ley potencial del perfil de viento: v(h) = v_ref * (h / h_ref)^alfa (alfa = 1/7, terreno abierto)."""
    if h_m <= 0 or h_ref_m <= 0:
        return v_ref_m_s
    return v_ref_m_s * (h_m / h_ref_m) ** alfa


def obstaculo_relativo_m(altura_edificio_m: float | None, terreno_max_m: float | None,
                         elevacion_origen_m: float | None) -> float | None:
    """Altura del obstáculo de un tramo medida sobre el punto de despegue.

    El UAV vuela a altura constante sobre el despegue (altura_vuelo_m). Un tramo
    queda bloqueado si relieve relativo + edificio >= altura_vuelo - margen.
    Sin dato de edificio ni de relieve, devuelve None: un dato ausente no bloquea.
    """
    relieve = None
    if terreno_max_m is not None and elevacion_origen_m is not None:
        relieve = terreno_max_m - elevacion_origen_m
    if altura_edificio_m is None and relieve is None:
        return None
    return round((relieve or 0.0) + (altura_edificio_m or 0.0), 2)

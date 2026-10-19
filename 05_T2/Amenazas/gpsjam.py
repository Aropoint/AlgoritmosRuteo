"""Amenaza 1: degradación GNSS por celda H3 sobre el AOI (GPSJam) -> JSON.

GPSJam publica un CSV diario por celda H3 de resolución 4 (~1.770 km²) con el
número de aviones con navegación buena y degradada (ADS-B). Aquí solo se
agregan esos conteos en las celdas que cubren el AOI y su primer anillo, durante
los VENTANA_DIAS días que terminan en FECHA_CORTE: días con datos, días en rojo
(regla publicada por GPSJam) e intensidad media. No se intenta localizar emisores.

Uso en el ruteo (peso, rúbrica 5.2): p_gnss = fracción de días en rojo de la
celda que contiene el tramo. Celda sin aviones = sin dato (p_gnss = 0).

Uso (dentro del contenedor app):  python Amenazas/gpsjam.py
Salida: Amenazas/salida/gpsjam.json (estructura en ESTRUCTURA_gpsjam_json.md)
"""
from __future__ import annotations

import csv
import io
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import h3  # noqa: E402

from comun.ajustes import (CACHE, FECHA_CORTE, VENTANA_DIAS, ahora_utc, bbox, centro_aoi,  # noqa: E402
                           guardar_json, inicio_ventana)
from comun.red import NoEncontrado, descargar  # noqa: E402
from comun.transformar import celda_roja_gpsjam, pct_malo_gpsjam  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "gpsjam.json"
URL = "https://gpsjam.org/data/{fecha}-h3_4.csv"
RESOLUCION = 4


def celdas_aoi() -> tuple[set[str], set[str]]:
    """(celdas que tocan el AOI, celdas del AOI más su primer anillo)."""
    sur, oeste, norte, este = bbox(0.0)
    lat0, lon0 = centro_aoi()
    puntos = [(sur, oeste), (sur, este), (norte, oeste), (norte, este), (lat0, lon0)]
    nucleo = {h3.latlng_to_cell(lat, lon, RESOLUCION) for lat, lon in puntos}
    contexto = set()
    for c in nucleo:
        contexto.update(h3.grid_disk(c, 1))
    return nucleo, contexto


def csv_del_dia(fecha) -> str | None:
    """CSV de un día (desde la caché si ya se bajó). None si GPSJam no tiene archivo para esa fecha."""
    cache = CACHE / "gpsjam" / f"{fecha.isoformat()}-h3_4.csv"
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_text(encoding="utf-8")
    try:
        texto = descargar(URL.format(fecha=fecha.isoformat()), timeout=90).decode("utf-8")
    except NoEncontrado:
        return None
    if not texto.startswith("hex,"):
        print(f"  aviso: contenido inesperado para {fecha}; se omite el día")
        return None
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(texto, encoding="utf-8")
    return texto


def contorno(celda: str) -> list[list[float]]:
    anillo = [[round(lng, 6), round(lat, 6)] for lat, lng in h3.cell_to_boundary(celda)]
    return anillo + [anillo[0]]


def main() -> None:
    nucleo, contexto = celdas_aoi()
    acumulado = {c: {"dias_con_datos": 0, "dias_rojos": 0, "suma_pct": 0.0, "buenos": 0, "malos": 0}
                 for c in contexto}
    dias_ok, dias_faltantes = 0, []
    fecha = inicio_ventana()
    while fecha <= FECHA_CORTE:
        texto = csv_del_dia(fecha)
        if texto is None:
            dias_faltantes.append(fecha.isoformat())
        else:
            dias_ok += 1
            for fila in csv.DictReader(io.StringIO(texto)):
                celda = fila["hex"]
                if celda not in acumulado:
                    continue
                buenos, malos = int(fila["count_good_aircraft"]), int(fila["count_bad_aircraft"])
                pct = pct_malo_gpsjam(buenos, malos)
                if pct is None:
                    continue
                a = acumulado[celda]
                a["dias_con_datos"] += 1
                a["dias_rojos"] += int(celda_roja_gpsjam(buenos, malos))
                a["suma_pct"] += pct
                a["buenos"] += buenos
                a["malos"] += malos
        fecha += timedelta(days=1)

    celdas = []
    for c in sorted(contexto):
        a = acumulado[c]
        n = a["dias_con_datos"]
        celdas.append({
            "h3": c,
            "contiene_aoi": c in nucleo,
            "dias_ventana": dias_ok,
            "dias_con_datos": n,
            "dias_rojos": a["dias_rojos"],
            "frac_dias_rojos": round(a["dias_rojos"] / n, 4) if n else None,
            "pct_malo_medio": round(a["suma_pct"] / n, 2) if n else None,
            "aviones_buenos": a["buenos"],
            "aviones_malos": a["malos"],
            "geometria": {"type": "Polygon", "coordinates": [contorno(c)]},
        })

    salida = {
        "tipo": "amenaza_gpsjam",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "GPSJam (datos ADS-B agregados por celda H3)",
            "url": "https://gpsjam.org/data/",
            "licencia": "Sin licencia declarada por el sitio; citar gpsjam.org",
            "generado_utc": ahora_utc(),
            "parametros": {"desde": inicio_ventana().isoformat(), "hasta": FECHA_CORTE.isoformat(),
                           "ventana_dias": VENTANA_DIAS, "resolucion_h3": RESOLUCION,
                           "celdas_aoi": sorted(nucleo), "anillo": 1},
            "regla_roja": "(malos - 1) / (buenos + malos) > 10 %",
            "dias_sin_archivo": dias_faltantes,
            "advertencias": [
                "Mide aviones en altura con ADS-B, no drones a 50-150 m: es un indicador regional.",
                "Cada celda cubre ~1.770 km²: todos los tramos del AOI suelen caer en la misma celda.",
                "Sin aviones no hay dato: en zonas de guerra sin tráfico civil la celda queda vacía, "
                "lo que no significa ausencia de interferencia.",
                "Desde el 2026-08-27 GPSJam combina dos redes de receptores; ventanas que crucen esa fecha no son comparables.",
            ],
        },
        "celdas": celdas,
    }
    guardar_json(SALIDA, salida)
    con_datos = sum(1 for c in celdas if c["dias_con_datos"])
    print(f"{len(celdas)} celdas ({con_datos} con datos), {dias_ok} días leídos, "
          f"{len(dias_faltantes)} sin archivo -> {SALIDA}")


if __name__ == "__main__":
    main()

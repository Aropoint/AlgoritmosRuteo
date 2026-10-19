"""Amenaza 2: incendios clasificados como de guerra cerca del AOI (modelo de The Economist sobre NASA FIRMS) -> JSON.

The Economist clasifica los focos de calor satelitales (NASA FIRMS) como
"relacionados con la guerra" cuando la actividad de fuego en una celda de 0,1°
es anormalmente alta para la fecha. Se filtran al AOI + BUFFER_KM y a dos períodos:
- historico:  [INICIO_HISTORICO, FECHA_CORTE]  -> pesos de riesgo (r_incendios),
- evaluacion: (FECHA_CORTE, FECHA_CORTE + DIAS_EVALUACION] -> focos de las fallas simuladas.
Separar los períodos evita evaluar el método con los mismos datos que fijaron sus pesos.

Uso (dentro del contenedor app):  python Amenazas/incendios_guerra.py [--refrescar]
Salida: Amenazas/salida/incendios_guerra.json (estructura en ESTRUCTURA_incendios_guerra_json.md)
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import (BUFFER_KM, CACHE, FECHA_CORTE, INICIO_HISTORICO, ahora_utc, bbox,  # noqa: E402
                           en_bbox, fin_evaluacion, guardar_json)
from comun.red import descargar_a_archivo  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "incendios_guerra.json"
URL = ("https://raw.githubusercontent.com/TheEconomist/the-economist-war-fire-model/"
       "master/output-data/ukraine_war_fires.csv")  # ~70 MB, actualizado a diario


def main() -> None:
    archivo = descargar_a_archivo(URL, CACHE / "economist" / "ukraine_war_fires.csv",
                                  refrescar="--refrescar" in sys.argv)
    caja = bbox(BUFFER_KM)
    fin = fin_evaluacion()
    incendios, leidas = [], 0
    with archivo.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            leidas += 1
            try:
                lat, lon = float(fila["LATITUDE"]), float(fila["LONGITUDE"])
                fecha = date.fromisoformat(fila["date"][:10])
            except (KeyError, ValueError):
                continue
            if not en_bbox(lat, lon, caja) or not (INICIO_HISTORICO <= fecha <= fin):
                continue
            hora = fila.get("ACQ_TIME", "")
            incendios.append({
                "fecha": fecha.isoformat(),
                "hora_utc": int(hora) if hora.isdigit() else None,
                "guerra": fila.get("war_fire") in ("1", "TRUE", "True", "true"),
                "periodo": "historico" if fecha <= FECHA_CORTE else "evaluacion",
                "lat": round(lat, 5),
                "lon": round(lon, 5),
            })

    resumen = {p: sum(1 for x in incendios if x["periodo"] == p and x["guerra"]) for p in ("historico", "evaluacion")}
    salida = {
        "tipo": "amenaza_incendios_guerra",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "The Economist war-fire model (sobre NASA FIRMS VIIRS)",
            "url": URL,
            "licencia": "Datos CC BY 4.0 (The Economist); focos FIRMS de NASA, uso abierto con atribución",
            "generado_utc": ahora_utc(),
            "parametros": {"bbox": dict(zip(("sur", "oeste", "norte", "este"), caja)), "buffer_km": BUFFER_KM,
                           "historico": [INICIO_HISTORICO.isoformat(), FECHA_CORTE.isoformat()],
                           "evaluacion": [FECHA_CORTE.isoformat(), fin.isoformat()]},
            "conteos": {"filas_leidas": leidas, "incendios": len(incendios), "de_guerra_por_periodo": resumen},
            "advertencias": [
                "La clasificación es probabilística: hay falsos positivos y, sobre todo, falsos negativos.",
                "Los satélites no ven bajo nubes; ataques sin fuego visible no aparecen.",
                "Del 4 al 11 de abril de 2023 (ola de calor) el modelo no clasifica eventos.",
            ],
        },
        "incendios": incendios,
    }
    guardar_json(SALIDA, salida, compacto=True)
    print(f"{len(incendios)} incendios cerca del AOI (de guerra: {resumen}) de {leidas} filas -> {SALIDA}")


if __name__ == "__main__":
    main()

"""Metadata 3: viento horario a 100 m en el AOI (Open-Meteo Historical Weather API, ERA5) -> JSON.

Ventana: los VENTANA_DIAS días que terminan en FECHA_CORTE (comun/ajustes.py),
la misma de GPSJam, para que clima y amenazas sean del mismo período.
Uso en el ruteo:
- Restricción (rúbrica 6.1): si el viento representativo a la altura de vuelo
  supera viento_max_m_s, la misión no es admisible.
- Peso blando: factor v / (v - h) con h = componente de frente en cada tramo.

Uso (dentro del contenedor app):  python Metadata/viento.py
Salida: Metadata/salida/viento.json (estructura en ESTRUCTURA_viento_json.md)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import FECHA_CORTE, VENTANA_DIAS, ahora_utc, centro_aoi, guardar_json, inicio_ventana  # noqa: E402
from comun.red import descargar  # noqa: E402
from comun.transformar import direccion_media_grados, percentil  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "viento.json"
URL = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES = "wind_speed_100m,wind_direction_100m,wind_gusts_10m"


def main() -> None:
    lat, lon = centro_aoi()
    params = {
        "latitude": round(lat, 4), "longitude": round(lon, 4),
        "start_date": inicio_ventana().isoformat(), "end_date": FECHA_CORTE.isoformat(),
        "hourly": VARIABLES, "wind_speed_unit": "ms", "timezone": "UTC",
    }
    r = json.loads(descargar(URL, params=params))
    h = r.get("hourly", {})
    horas = [
        {"ts_utc": ts + "Z", "velocidad_m_s": v, "direccion_grados": d, "rafaga_10m_m_s": g}
        for ts, v, d, g in zip(h.get("time", []), h.get("wind_speed_100m", []),
                               h.get("wind_direction_100m", []), h.get("wind_gusts_10m", []))
    ]
    if not horas:
        raise SystemExit(f"Open-Meteo no devolvió datos horarios: {r}")
    validas = [x for x in horas if x["velocidad_m_s"] is not None and x["direccion_grados"] is not None]
    velocidades = [x["velocidad_m_s"] for x in validas]
    rafagas = [x["rafaga_10m_m_s"] for x in horas if x["rafaga_10m_m_s"] is not None]
    resumen = {
        "horas_validas": len(validas),
        "velocidad_mediana_m_s": round(percentil(velocidades, 0.5), 2) if velocidades else None,
        "velocidad_p95_m_s": round(percentil(velocidades, 0.95), 2) if velocidades else None,
        "rafaga_max_10m_m_s": max(rafagas) if rafagas else None,
        "direccion_media_grados": direccion_media_grados([x["direccion_grados"] for x in validas], velocidades),
    }
    salida = {
        "tipo": "metadata_viento",
        "metadatos": {
            "fuente": "Open-Meteo Historical Weather API (reanálisis ERA5)",
            "url": URL,
            "licencia": "CC BY 4.0, uso no comercial (Open-Meteo); ERA5 © Copernicus Climate Change Service",
            "generado_utc": ahora_utc(),
            "parametros": {**params, "ventana_dias": VENTANA_DIAS},
            "advertencias": [
                "ERA5 tiene ~25 km de resolución: un solo valor representa todo el AOI.",
                "El viento a la altura de vuelo se obtiene con la ley potencial desde 100 m (alfa = 1/7).",
            ],
        },
        "punto": {"lat": r.get("latitude"), "lon": r.get("longitude"), "elevacion_m": r.get("elevation")},
        "unidades": r.get("hourly_units", {}),
        "resumen": resumen,
        "horas": horas,
    }
    guardar_json(SALIDA, salida)
    print(f"{len(horas)} horas; mediana {resumen['velocidad_mediana_m_s']} m/s desde "
          f"{resumen['direccion_media_grados']}° -> {SALIDA}")


if __name__ == "__main__":
    main()

"""Metadata 2: elevación del terreno en nodos y puntos medios de tramo (Open-Meteo Elevation API) -> JSON.

Fuente del modelo: Copernicus DEM GLO-90 (90 m), servido por Open-Meteo sin clave.
Uso en el ruteo (restricción dura, rúbrica 6.1): el UAV vuela a altura constante
sobre el despegue; el relieve relativo de cada tramo se suma a la altura de los
edificios para decidir si el tramo es admisible (ver comun/transformar.py).

Requiere Infraestructura/salida/infraestructura.json (los puntos a consultar).

Uso (dentro del contenedor app):  python Metadata/elevacion.py
Salida: Metadata/salida/elevacion.json (estructura en ESTRUCTURA_elevacion_json.md)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import INFRAESTRUCTURA_JSON, ahora_utc, guardar_json, leer_json  # noqa: E402
from comun.red import descargar  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "elevacion.json"
URL = "https://api.open-meteo.com/v1/elevation"
POR_CONSULTA = 100  # máximo de coordenadas por llamada que admite la API


def puntos_a_consultar(infra: dict) -> list[dict]:
    nodos = {n["id"]: n for n in infra["nodos"]}
    puntos = [{"tipo": "nodo", "ref_id": n["id"], "lat": n["lat"], "lon": n["lon"]} for n in infra["nodos"]]
    for a in infra["aristas"]:
        u, v = nodos[a["source"]], nodos[a["target"]]
        puntos.append({"tipo": "punto_medio", "ref_id": a["id"],
                       "lat": round((u["lat"] + v["lat"]) / 2, 6), "lon": round((u["lon"] + v["lon"]) / 2, 6)})
    return puntos


def main() -> None:
    puntos = puntos_a_consultar(leer_json(INFRAESTRUCTURA_JSON))
    for i in range(0, len(puntos), POR_CONSULTA):
        lote = puntos[i:i + POR_CONSULTA]
        respuesta = json.loads(descargar(URL, params={
            "latitude": ",".join(str(p["lat"]) for p in lote),
            "longitude": ",".join(str(p["lon"]) for p in lote),
        }))
        elevaciones = respuesta.get("elevation", [])
        if len(elevaciones) != len(lote):
            raise SystemExit(f"La API devolvió {len(elevaciones)} elevaciones para {len(lote)} puntos.")
        for p, e in zip(lote, elevaciones):
            p["elevacion_m"] = None if e is None else round(float(e), 1)
        time.sleep(0.5)  # cortesía con la API gratuita

    valores = [p["elevacion_m"] for p in puntos if p["elevacion_m"] is not None]
    salida = {
        "tipo": "metadata_elevacion",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "Open-Meteo Elevation API (Copernicus DEM GLO-90)",
            "url": URL,
            "licencia": "CC BY 4.0 (Open-Meteo); Copernicus DEM © DLR e.V. 2010-2014 y © Airbus Defence and Space "
                        "GmbH 2014-2018, provisto bajo COPERNICUS por la Unión Europea y la ESA",
            "generado_utc": ahora_utc(),
            "parametros": {"resolucion_m": 90, "puntos": len(puntos), "por_consulta": POR_CONSULTA},
            "resumen": {"min_m": min(valores) if valores else None, "max_m": max(valores) if valores else None},
            "advertencias": [
                "GLO-90 es un modelo de superficie: incluye en parte vegetación y edificios.",
                "Con 90 m de resolución, un tramo de ~0,5 km se muestrea solo en sus extremos y su punto medio.",
            ],
        },
        "puntos": puntos,
    }
    guardar_json(SALIDA, salida)
    print(f"{len(puntos)} puntos, elevación de {salida['metadatos']['resumen']['min_m']} "
          f"a {salida['metadatos']['resumen']['max_m']} m -> {SALIDA}")


if __name__ == "__main__":
    main()

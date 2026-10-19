"""Metadata 1: edificios de OpenStreetMap con su altura (Overpass API) -> JSON.

Uso en el ruteo (restricción dura, rúbrica 6.1): un tramo que pasa a menos de
15 m de un edificio cuya altura, sumada al relieve, alcanza altura_vuelo - margen
queda fuera del grafo admisible. Altura: tag `height`; si no existe,
`building:levels` x 3 m; si tampoco, sin dato (no restringe).

Uso (dentro del contenedor app):  python Metadata/osm_edificios.py
Salida: Metadata/salida/osm_edificios.json (estructura en ESTRUCTURA_osm_edificios_json.md)
Datos © colaboradores de OpenStreetMap, licencia ODbL 1.0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import ahora_utc, bbox, guardar_json  # noqa: E402
from comun.red import descargar  # noqa: E402
from comun.transformar import altura_estimada_m, anillo_cerrado, parsear_altura_m, parsear_niveles  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "osm_edificios.json"
SERVIDORES = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def consulta(sur: float, oeste: float, norte: float, este: float) -> str:
    caja = f"{sur:.6f},{oeste:.6f},{norte:.6f},{este:.6f}"
    return f"""[out:json][timeout:240];
(
  way["building"]({caja});
  relation["building"]["type"="multipolygon"]({caja});
);
out tags geom;"""


def poligonos(elemento: dict) -> list[list[list[list[float]]]]:
    """Polígonos GeoJSON [[anillo]] del elemento. Relaciones: solo anillos exteriores cerrados (sin huecos)."""
    if elemento["type"] == "way":
        anillo = anillo_cerrado([[p["lon"], p["lat"]] for p in elemento.get("geometry", [])])
        return [[anillo]] if anillo else []
    salida = []
    for miembro in elemento.get("members", []):
        if miembro.get("role") == "outer" and miembro.get("geometry"):
            pts = [[p["lon"], p["lat"]] for p in miembro["geometry"]]
            if pts[0] == pts[-1]:
                anillo = anillo_cerrado(pts)
                if anillo:
                    salida.append([anillo])
    return salida


def main() -> None:
    sur, oeste, norte, este = bbox(0.0)
    q = consulta(sur, oeste, norte, este)
    datos, servidor, ultimo_error = None, None, None
    for url in SERVIDORES:
        try:
            datos = json.loads(descargar(url, data={"data": q}, timeout=300, intentos=2))
            servidor = url
            break
        except Exception as e:  # el siguiente servidor espejo puede responder
            ultimo_error = e
            print(f"  aviso: {url} no respondió ({e})")
    if datos is None:
        raise SystemExit(f"Overpass no respondió: {ultimo_error}")

    edificios, sin_geometria = [], 0
    for el in datos.get("elements", []):
        tags = el.get("tags", {})
        polis = poligonos(el)
        if not polis:
            sin_geometria += 1
            continue
        altura = parsear_altura_m(tags.get("height"))
        niveles = parsear_niveles(tags.get("building:levels"))
        estimada, origen = altura_estimada_m(altura, niveles)
        edificios.append({
            "osm_tipo": el["type"],
            "osm_id": el["id"],
            "tipo_edificio": tags.get("building"),
            "altura_m": altura,
            "niveles": niveles,
            "altura_estimada_m": estimada,
            "origen_altura": origen,
            "geometria": {"type": "MultiPolygon",
                          "coordinates": [[[[round(x, 7), round(y, 7)] for x, y in anillo] for anillo in p] for p in polis]},
        })

    con_altura = sum(1 for e in edificios if e["altura_estimada_m"] is not None)
    salida = {
        "tipo": "metadata_edificios_osm",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "OpenStreetMap vía Overpass API",
            "url": servidor,
            "licencia": "ODbL 1.0 (© colaboradores de OpenStreetMap)",
            "generado_utc": ahora_utc(),
            "parametros": {"bbox": {"sur": sur, "oeste": oeste, "norte": norte, "este": este},
                           "consulta_overpass": q, "metros_por_nivel": 3.0},
            "conteos": {"elementos_osm": len(datos.get("elements", [])), "edificios": len(edificios),
                        "con_altura": con_altura, "descartados_sin_geometria": sin_geometria},
            "advertencias": [
                "La cobertura de alturas en OSM es incompleta; sin altura el edificio no restringe.",
                "Las relaciones multipolígono se guardan solo con sus anillos exteriores cerrados (sin huecos).",
                "Los datos de OSM son colaborativos y pueden no reflejar daños recientes por la guerra.",
            ],
        },
        "edificios": edificios,
    }
    guardar_json(SALIDA, salida, compacto=True)
    print(f"{len(edificios)} edificios ({con_altura} con altura) -> {SALIDA}")


if __name__ == "__main__":
    main()

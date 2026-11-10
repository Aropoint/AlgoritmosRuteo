"""Metadata 4: zonas restringidas publicadas en OpenStreetMap (aeródromos y helipuertos) -> JSON.

Uso en el ruteo (Tarea 3, punto 2: bloqueos): un tramo que toca una de estas zonas no es
sobrevolable para ninguna técnica (BD/pesos.sql marca aristas.en_zona_restringida). Un helipuerto
que OSM trae como punto se convierte en un círculo de `buffer_helipuerto_m` (parametros_pesos).

Solo se usan zonas aeronáuticas civiles (`aeroway`). No se usa `landuse=military`: en una ciudad
en conflicto equivaldría a mapear instalaciones militares, y el proyecto no liga sus datos a
instalaciones concretas. Si el AOI no tiene ninguna zona, el JSON queda vacío y la restricción es
neutra; las zonas prohibidas que el usuario dibuja en el sitio cumplen el mismo papel.

Uso (dentro del contenedor app):  python Metadata/zonas_restringidas.py
Salida: Metadata/salida/zonas_restringidas.json (estructura en ESTRUCTURA_zonas_restringidas_json.md)
Datos © colaboradores de OpenStreetMap, licencia ODbL 1.0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import ahora_utc, bbox, guardar_json  # noqa: E402
from comun.red import descargar  # noqa: E402
from comun.transformar import anillo_cerrado  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "zonas_restringidas.json"
SERVIDORES = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
CLASES = ("aerodrome", "heliport", "helipad")


def consulta(sur: float, oeste: float, norte: float, este: float) -> str:
    caja = f"{sur:.6f},{oeste:.6f},{norte:.6f},{este:.6f}"
    filtro = "|".join(CLASES)
    return f"""[out:json][timeout:120];
nwr["aeroway"~"^({filtro})$"]({caja});
out tags geom;"""


def geometria(el: dict) -> dict | None:
    """GeoJSON del elemento: Point para nodos, MultiPolygon para vías y relaciones cerradas."""
    if el["type"] == "node":
        return {"type": "Point", "coordinates": [round(el["lon"], 7), round(el["lat"], 7)]}
    anillos = []
    if el["type"] == "way":
        pts = [[p["lon"], p["lat"]] for p in el.get("geometry", [])]
        if pts and pts[0] == pts[-1] and (anillo := anillo_cerrado(pts)):  # solo vías cerradas (áreas)
            anillos.append(anillo)
    else:
        for m in el.get("members", []):
            if m.get("role") == "outer" and m.get("geometry"):
                pts = [[p["lon"], p["lat"]] for p in m["geometry"]]
                if pts[0] == pts[-1] and (anillo := anillo_cerrado(pts)):
                    anillos.append(anillo)
    if not anillos:
        return None
    return {"type": "MultiPolygon", "coordinates": [[[[round(x, 7), round(y, 7)] for x, y in a]] for a in anillos]}


def main() -> None:
    sur, oeste, norte, este = bbox(0.0)
    q = consulta(sur, oeste, norte, este)
    datos, servidor, ultimo_error = None, None, None
    for url in SERVIDORES:
        try:
            datos = json.loads(descargar(url, data={"data": q}, timeout=180, intentos=2))
            servidor = url
            break
        except Exception as e:  # el siguiente servidor espejo puede responder
            ultimo_error = e
            print(f"  aviso: {url} no respondió ({e})")
    if datos is None:
        raise SystemExit(f"Overpass no respondió: {ultimo_error}")

    zonas, descartadas = [], 0
    for el in datos.get("elements", []):
        tags = el.get("tags", {})
        geo = geometria(el)
        if geo is None:
            descartadas += 1
            continue
        zonas.append({"osm_tipo": el["type"], "osm_id": el["id"], "clase": tags.get("aeroway"),
                      "nombre": tags.get("name"), "geometria": geo})

    salida = {
        "tipo": "metadata_zonas_restringidas_osm",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "OpenStreetMap vía Overpass API (aeroway)",
            "url": servidor,
            "licencia": "ODbL 1.0 (© colaboradores de OpenStreetMap)",
            "generado_utc": ahora_utc(),
            "parametros": {"bbox": {"sur": sur, "oeste": oeste, "norte": norte, "este": este},
                           "clases": list(CLASES), "consulta_overpass": q},
            "conteos": {"elementos_osm": len(datos.get("elements", [])), "zonas": len(zonas),
                        "descartadas_sin_geometria": descartadas},
            "advertencias": [
                "Solo zonas aeronáuticas civiles de OSM; no reemplaza la cartografía aeronáutica oficial.",
                "Sin zonas en el AOI la restricción queda neutra; el usuario puede dibujar zonas prohibidas en el sitio.",
            ],
        },
        "zonas": zonas,
    }
    guardar_json(SALIDA, salida)
    print(f"{len(zonas)} zonas restringidas ({descartadas} descartadas sin geometría) -> {SALIDA}")


if __name__ == "__main__":
    main()

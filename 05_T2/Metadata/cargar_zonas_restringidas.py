"""Carga Metadata/salida/zonas_restringidas.json en la tabla meta_zonas_restringidas (Tarea 3, punto 2).

A los helipuertos (helipad, heliport) se les aplica un radio de protección de buffer_helipuerto_m
(tabla parametros_pesos), vengan como punto o como el pequeño polígono de la losa: la zona que
importa para un UAV es el espacio de aproximación, no la losa. Los aeródromos se cargan con su
contorno. Después, BD/pesos.sql marca los tramos que tocan alguna zona.

Uso (dentro del contenedor app):  python Metadata/cargar_zonas_restringidas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "zonas_restringidas.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "zonas_restringidas", "metadata", datos["metadatos"], relativa(ENTRADA))
        buffer_m = cur.execute(
            "SELECT valor FROM parametros_pesos WHERE clave = 'buffer_helipuerto_m'").fetchone()[0]
        cur.execute("DELETE FROM meta_zonas_restringidas")
        for z in datos["zonas"]:
            con_radio = z["clase"] in ("helipad", "heliport") or z["geometria"]["type"] == "Point"
            # Helipuerto: radio buffer_m medido en metros (geography). Aeródromo: contorno, corregido si es inválido.
            cur.execute(
                """INSERT INTO meta_zonas_restringidas (osm_tipo, osm_id, clase, nombre, buffer_m, geom, fuente_id)
                   SELECT %s, %s, %s, %s, %s,
                          CASE WHEN %s THEN ST_Multi(ST_Buffer(ST_MakeValid(g)::geography, %s)::geometry)
                               ELSE ST_Multi(ST_CollectionExtract(ST_MakeValid(g), 3)) END,
                          %s
                   FROM (SELECT ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326) AS g) s
                   ON CONFLICT (osm_tipo, osm_id) DO NOTHING""",
                (z["osm_tipo"], z["osm_id"], z["clase"], z.get("nombre"), buffer_m if con_radio else 0.0,
                 con_radio, buffer_m, fid, json.dumps(z["geometria"])),
            )
        cur.execute("DELETE FROM meta_zonas_restringidas WHERE ST_IsEmpty(geom)")
        cur.execute("SELECT clase, count(*) FROM meta_zonas_restringidas GROUP BY clase ORDER BY clase")
        resumen = ", ".join(f"{c}: {n}" for c, n in cur.fetchall()) or "ninguna en el AOI"
    print(f"meta_zonas_restringidas: {resumen}")


if __name__ == "__main__":
    main()

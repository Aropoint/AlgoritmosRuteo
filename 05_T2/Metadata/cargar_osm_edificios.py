"""Carga Metadata/salida/osm_edificios.json en la tabla meta_edificios (rúbrica 3.2).

Uso (dentro del contenedor app):  python Metadata/cargar_osm_edificios.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "osm_edificios.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "osm_edificios", "metadata", datos["metadatos"], relativa(ENTRADA))
        cur.execute("DELETE FROM meta_edificios")
        # ST_MakeValid corrige anillos que se autointersectan; ST_CollectionExtract(…, 3) deja solo polígonos.
        cur.executemany(
            """INSERT INTO meta_edificios (osm_tipo, osm_id, tipo_edificio, altura_m, niveles, altura_estimada_m,
                                          origen_altura, geom, fuente_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s,
                       ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)), 3)), %s)
               ON CONFLICT (osm_tipo, osm_id) DO NOTHING""",
            [(e["osm_tipo"], e["osm_id"], e["tipo_edificio"], e["altura_m"], e["niveles"], e["altura_estimada_m"],
              e["origen_altura"], json.dumps(e["geometria"]), fid) for e in datos["edificios"]],
        )
        cur.execute("DELETE FROM meta_edificios WHERE ST_IsEmpty(geom)")
        cur.execute("SELECT count(*), count(altura_estimada_m) FROM meta_edificios")
        total, con_altura = cur.fetchone()
    print(f"meta_edificios: {total} filas ({con_altura} con altura)")


if __name__ == "__main__":
    main()

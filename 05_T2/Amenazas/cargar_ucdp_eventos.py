"""Carga Amenazas/salida/ucdp_eventos.json en la tabla amz_eventos (rúbrica 4.2).

Uso (dentro del contenedor app):  python Amenazas/cargar_ucdp_eventos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "ucdp_eventos.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "ucdp_eventos", "amenaza", datos["metadatos"], relativa(ENTRADA))
        cur.execute("DELETE FROM amz_eventos")
        cur.executemany(
            """INSERT INTO amz_eventos (id, fecha_inicio, fecha_fin, tipo_violencia, precision_lugar, precision_fecha,
                   muertes_estimadas, adm1, adm2, lugar, geom, fuente_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
               ON CONFLICT (id) DO NOTHING""",
            [(e["id"], e["fecha_inicio"], e["fecha_fin"], e["tipo_violencia"], e["precision_lugar"],
              e["precision_fecha"], e["muertes_estimadas"], e["adm1"], e["adm2"], e["lugar"], e["lon"], e["lat"], fid)
             for e in datos["eventos"] if e["id"] is not None],
        )
        cur.execute("SELECT count(*), min(fecha_inicio), max(fecha_inicio) FROM amz_eventos")
        total, desde, hasta = cur.fetchone()
    print(f"amz_eventos: {total} eventos ({desde} a {hasta})")


if __name__ == "__main__":
    main()

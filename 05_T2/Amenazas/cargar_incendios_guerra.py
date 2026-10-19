"""Carga Amenazas/salida/incendios_guerra.json en la tabla amz_incendios (rúbrica 4.2).

Uso (dentro del contenedor app):  python Amenazas/cargar_incendios_guerra.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "incendios_guerra.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "incendios_guerra", "amenaza", datos["metadatos"], relativa(ENTRADA))
        cur.execute("TRUNCATE amz_incendios RESTART IDENTITY")
        cur.executemany(
            """INSERT INTO amz_incendios (fecha, hora_utc, guerra, periodo, geom, fuente_id)
               VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)""",
            [(x["fecha"], x["hora_utc"], x["guerra"], x["periodo"], x["lon"], x["lat"], fid)
             for x in datos["incendios"]],
        )
        cur.execute("SELECT periodo, count(*) FILTER (WHERE guerra), count(*) FROM amz_incendios GROUP BY periodo ORDER BY periodo")
        filas = cur.fetchall()
    for periodo, de_guerra, total in filas:
        print(f"amz_incendios [{periodo}]: {total} focos, {de_guerra} de guerra")
    if not filas:
        print("amz_incendios: 0 focos en el AOI (r_incendios quedará en 0)")


if __name__ == "__main__":
    main()

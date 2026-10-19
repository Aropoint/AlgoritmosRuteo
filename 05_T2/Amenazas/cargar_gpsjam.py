"""Carga Amenazas/salida/gpsjam.json en la tabla amz_gpsjam_celdas (rúbrica 4.2).

Uso (dentro del contenedor app):  python Amenazas/cargar_gpsjam.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "gpsjam.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "gpsjam", "amenaza", datos["metadatos"], relativa(ENTRADA))
        cur.execute("DELETE FROM amz_gpsjam_celdas")
        cur.executemany(
            """INSERT INTO amz_gpsjam_celdas (h3, dias_ventana, dias_con_datos, dias_rojos, frac_dias_rojos,
                   pct_malo_medio, aviones_buenos, aviones_malos, contiene_aoi, geom, fuente_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s)""",
            [(c["h3"], c["dias_ventana"], c["dias_con_datos"], c["dias_rojos"], c["frac_dias_rojos"],
              c["pct_malo_medio"], c["aviones_buenos"], c["aviones_malos"], c["contiene_aoi"],
              json.dumps(c["geometria"]), fid) for c in datos["celdas"]],
        )
        cur.execute("SELECT count(*), count(frac_dias_rojos), max(frac_dias_rojos) FROM amz_gpsjam_celdas")
        total, con_datos, maximo = cur.fetchone()
    print(f"amz_gpsjam_celdas: {total} celdas ({con_datos} con datos; máx. fracción de días en rojo {maximo})")


if __name__ == "__main__":
    main()

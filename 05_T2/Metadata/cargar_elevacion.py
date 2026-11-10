"""Carga Metadata/salida/elevacion.json en la tabla meta_elevacion (rúbrica 3.2).

La elevación pasa a nodos y aristas en BD/asignar_pesos.py.

Uso (dentro del contenedor app):  python Metadata/cargar_elevacion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "elevacion.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "elevacion", "metadata", datos["metadatos"], relativa(ENTRADA))
        cur.execute("DELETE FROM meta_elevacion")
        # Un elevacion.json anterior a la Tarea 3 trae "punto_medio" (una muestra por tramo): se carga como muestra 1.
        cur.executemany(
            """INSERT INTO meta_elevacion (tipo, ref_id, orden, elevacion_m, geom, fuente_id)
               VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)""",
            [("muestra" if p["tipo"] == "punto_medio" else p["tipo"], p["ref_id"],
              p.get("orden", 1 if p["tipo"] == "punto_medio" else 0), p["elevacion_m"], p["lon"], p["lat"], fid)
             for p in datos["puntos"]],
        )
        cur.execute("SELECT count(*), min(elevacion_m), max(elevacion_m) FROM meta_elevacion")
        total, minimo, maximo = cur.fetchone()
    print(f"meta_elevacion: {total} puntos (de {minimo} a {maximo} m)")


if __name__ == "__main__":
    main()

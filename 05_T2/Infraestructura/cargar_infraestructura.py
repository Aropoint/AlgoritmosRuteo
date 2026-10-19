"""Carga Infraestructura/salida/infraestructura.json en la BD (rúbrica punto 6).

nodos -> tabla nodos; aristas -> tabla aristas (geometría LineString y rumbo);
metadatos.secuencia_mision -> tabla mision. Vacía antes nodos y todo lo que
depende de ellos (aristas, misión, rutas y evaluaciones).

Uso (dentro del contenedor app):  python Infraestructura/cargar_infraestructura.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import INFRAESTRUCTURA_JSON, leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402


def main() -> None:
    datos = leer_json(INFRAESTRUCTURA_JSON)
    meta = datos.get("metadatos", {})
    fuente = {
        "fuente": "Malla sintética geolocalizada (Infraestructura/generar_infraestructura.py)",
        "url": None,
        "licencia": "Generada por el proyecto",
        "generado_utc": meta.get("generado_utc"),
        "parametros": {"aoi": meta.get("aoi"), "malla": meta.get("parametros_malla")},
    }
    secuencia = meta.get("secuencia_mision", [])
    with conectar() as conn, conn.cursor() as cur:
        registrar_fuente(cur, "infraestructura", "infraestructura", fuente, relativa(INFRAESTRUCTURA_JSON))
        cur.execute("TRUNCATE nodos, aristas, mision, rutas, evaluaciones RESTART IDENTITY CASCADE")
        cur.executemany(
            "INSERT INTO nodos (id, tipo, geom) VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
            [(n["id"], n["tipo"], n["lon"], n["lat"]) for n in datos["nodos"]],
        )
        cur.executemany(
            """INSERT INTO aristas (id, source, target, largo_km, geom)
               VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakeLine(ST_MakePoint(%s, %s), ST_MakePoint(%s, %s)), 4326))""",
            [(a["id"], a["source"], a["target"], a["largo_km"], *a["geometria"][0], *a["geometria"][1])
             for a in datos["aristas"]],
        )
        # Rumbo de source a target (grados desde el norte): lo usa el factor de viento.
        cur.execute(
            "UPDATE aristas SET rumbo_grados = degrees(ST_Azimuth(ST_StartPoint(geom)::geography, ST_EndPoint(geom)::geography))"
        )
        roles = ["inicio"] + ["observacion"] * (len(secuencia) - 2) + ["destino"] if len(secuencia) >= 2 else []
        cur.executemany("INSERT INTO mision (orden, nodo_id, rol) VALUES (%s, %s, %s)",
                        [(i, nodo, rol) for i, (nodo, rol) in enumerate(zip(secuencia, roles))])
        cur.execute("SELECT count(*) FROM nodos")
        n_nodos = cur.fetchone()[0]
        cur.execute("SELECT count(*), round(sum(largo_km)::numeric, 2) FROM aristas")
        n_aristas, km = cur.fetchone()
    print(f"Cargados {n_nodos} nodos, {n_aristas} aristas ({km} km) y misión de {len(secuencia)} puntos")


if __name__ == "__main__":
    main()

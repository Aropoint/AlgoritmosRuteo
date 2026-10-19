"""Carga Metadata/salida/viento.json en la tabla meta_viento (rúbrica 3.2).

El resumen (mediana, p95, dirección media) lo calcula la vista v_viento_resumen.

Uso (dentro del contenedor app):  python Metadata/cargar_viento.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import leer_json, relativa  # noqa: E402
from comun.bd import conectar, registrar_fuente  # noqa: E402

ENTRADA = Path(__file__).resolve().parent / "salida" / "viento.json"


def main() -> None:
    datos = leer_json(ENTRADA)
    with conectar() as conn, conn.cursor() as cur:
        fid = registrar_fuente(cur, "viento", "metadata", datos["metadatos"], relativa(ENTRADA))
        cur.execute("DELETE FROM meta_viento")
        cur.executemany(
            """INSERT INTO meta_viento (ts_utc, velocidad_m_s, direccion_grados, rafaga_10m_m_s, fuente_id)
               VALUES (%s, %s, %s, %s, %s)""",
            [(h["ts_utc"], h["velocidad_m_s"], h["direccion_grados"], h["rafaga_10m_m_s"], fid) for h in datos["horas"]],
        )
        cur.execute("SELECT horas, round(velocidad_mediana_m_s::numeric, 2), direccion_media_grados FROM v_viento_resumen")
        horas, mediana, direccion = cur.fetchone()
    print(f"meta_viento: {horas} horas; mediana {mediana} m/s, dirección media {direccion}°")


if __name__ == "__main__":
    main()

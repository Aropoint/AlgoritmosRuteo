"""Crea la base de datos desde cero ejecutando BD/schema.sql (rúbrica punto 0).

Borra y recrea todas las tablas del proyecto. Lo ejecuta pipeline.py como primer paso.

Uso (dentro del contenedor app):  python BD/crear_bd.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.bd import conectar  # noqa: E402

ESQUEMA = Path(__file__).resolve().parent / "schema.sql"


def main() -> None:
    with conectar() as conn:
        conn.execute(ESQUEMA.read_text(encoding="utf-8"))
        postgis, pgrouting = conn.execute("SELECT postgis_lib_version(), pgr_version()").fetchone()
        tablas = [t for (t,) in conn.execute(
            """SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name <> 'spatial_ref_sys'
               ORDER BY table_name""")]
    print(f"PostGIS {postgis}, pgRouting {pgrouting}")
    print(f"{len(tablas)} tablas creadas: {', '.join(tablas)}")


if __name__ == "__main__":
    main()

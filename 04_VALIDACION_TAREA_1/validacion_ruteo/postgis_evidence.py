from __future__ import annotations

import csv
import json
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from common import env

BASE = Path(__file__).resolve().parent
OUT = BASE / "evidencia" / "postgis"
OUT.mkdir(parents=True, exist_ok=True)


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")


def write_csv(name: str, rows: list[dict]) -> None:
    path = OUT / name
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch_dicts(cur: psycopg.Cursor, sql: str, params: tuple = ()) -> list[dict]:
    cur.execute(sql, params)
    columns = [desc.name for desc in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def build_test_route(cur: psycopg.Cursor) -> tuple[str, dict]:
    cur.execute(
        """
        WITH selected AS (
          SELECT id, name, airspace_type, country, ST_PointOnSurface(geom) AS center
          FROM airspaces
          ORDER BY id
          LIMIT 1
        ),
        route AS (
          SELECT
            id AS reference_airspace_id,
            name AS reference_airspace_name,
            airspace_type AS reference_airspace_type,
            country AS reference_airspace_country,
            ST_SetSRID(
              ST_MakeLine(
                ST_Translate(center, -0.02, -0.02),
                ST_Translate(center, 0.02, 0.02)
              ),
              4326
            ) AS geom
          FROM selected
        )
        SELECT
          ST_AsText(geom) AS route_wkt,
          reference_airspace_id,
          reference_airspace_name,
          reference_airspace_type,
          reference_airspace_country
        FROM route
        """
    )
    row = cur.fetchone()
    if row is None:
        raise SystemExit("No hay registros en airspaces; importa OpenAIP antes de generar evidencia.")
    columns = [desc.name for desc in cur.description]
    data = dict(zip(columns, row))
    return data["route_wkt"], data


def main() -> None:
    load_dotenv()
    database_url = env("DATABASE_URL", required=True)

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            # Dato de prueba creado por nosotros: no representa una ruta UAV observada.
            test_route_wkt, route_metadata = build_test_route(cur)

            cur.execute("SELECT PostGIS_Version()")
            postgis_version = cur.fetchone()[0]
            write_text("01_postgis_version.txt", f"PostGIS_Version: {postgis_version}\n")

            counts = fetch_dicts(
                cur,
                """
                SELECT 'airspaces' AS table_name, COUNT(*) AS records FROM airspaces
                UNION ALL SELECT 'gpsjam_zones', COUNT(*) FROM gpsjam_zones
                UNION ALL SELECT 'osm_buildings', COUNT(*) FROM osm_buildings
                UNION ALL SELECT 'acled_events', COUNT(*) FROM acled_events
                ORDER BY table_name
                """,
            )
            write_csv("02_table_counts.csv", counts)

            geom_types = fetch_dicts(
                cur,
                """
                SELECT 'airspaces' AS table_name, ST_GeometryType(geom) AS geometry_type, COUNT(*) AS records
                FROM airspaces GROUP BY 1, 2
                UNION ALL
                SELECT 'gpsjam_zones', ST_GeometryType(geom), COUNT(*)
                FROM gpsjam_zones GROUP BY 1, 2
                UNION ALL
                SELECT 'osm_buildings', ST_GeometryType(geom), COUNT(*)
                FROM osm_buildings GROUP BY 1, 2
                UNION ALL
                SELECT 'acled_events', ST_GeometryType(geom), COUNT(*)
                FROM acled_events GROUP BY 1, 2
                ORDER BY table_name, geometry_type
                """,
            )
            write_csv("03_geometry_types.csv", geom_types)

            intersections = fetch_dicts(
                cur,
                """
                WITH route AS (
                  SELECT ST_SetSRID(ST_GeomFromText(%s), 4326) AS geom
                )
                SELECT
                  a.id,
                  a.name,
                  a.airspace_type,
                  a.country,
                  ST_AsText(ST_Intersection(a.geom, route.geom)) AS intersection_wkt
                FROM airspaces a
                CROSS JOIN route
                WHERE ST_Intersects(a.geom, route.geom)
                ORDER BY a.id
                """,
                (test_route_wkt,),
            )
            write_csv("04_route_airspace_intersections.csv", intersections)
            write_text(
                "04_route_airspace_intersections_note.txt",
                "Ruta de prueba creada por nosotros, no observada: "
                f"{test_route_wkt}\n"
                f"Poligono OpenAIP usado solo como referencia para construir la prueba: "
                f"{route_metadata}\n"
                f"Intersecciones con OpenAIP: {len(intersections)}\n",
            )

            summary = {
                "postgis_version": postgis_version,
                "table_counts": counts,
                "geometry_types": geom_types,
                "test_route": {
                    "description": "Dato de prueba creado por nosotros; no es una ruta UAV observada real.",
                    "wkt": test_route_wkt,
                    "construction_reference": route_metadata,
                    "airspace_intersections": len(intersections),
                },
            }
            write_text("00_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))

    print(f"Evidencia PostGIS guardada en {OUT}")
    print(f"Ruta de prueba creada por nosotros: {test_route_wkt}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

from common import env

BASE = Path(__file__).resolve().parent
EVIDENCIA = BASE / "evidencia"


@dataclass(frozen=True)
class Dataset:
    table: str
    path: Path
    geom_kind: str


DATASETS = [
    Dataset("airspaces", EVIDENCIA / "openaip_restricted.geojson", "polygon"),
    Dataset("osm_buildings", EVIDENCIA / "osm_buildings.geojson", "polygon"),
    Dataset("acled_events", EVIDENCIA / "acled_events.geojson", "point"),
]


def gpsjam_datasets() -> list[Dataset]:
    return [Dataset("gpsjam_zones", p, "polygon") for p in sorted(EVIDENCIA.glob("gpsjam_*.geojson"))]


def source_uid(table: str, source_file: str, properties: dict[str, Any], index: int) -> str:
    if table == "airspaces":
        return str(properties.get("id") or f"{source_file}:{index}")
    if table == "gpsjam_zones":
        return f"{source_file}:{properties.get('h3') or index}"
    if table == "osm_buildings":
        return str(properties.get("osm_id") or f"{source_file}:{index}")
    if table == "acled_events":
        return str(properties.get("event_id_cnty") or f"{source_file}:{index}")
    return f"{source_file}:{index}"


def load_features(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} no es FeatureCollection")
    return data.get("features") or []


def create_temp_table(cur: psycopg.Cursor) -> None:
    cur.execute("DROP TABLE IF EXISTS tmp_geojson_import")
    cur.execute(
        """
        CREATE TEMP TABLE tmp_geojson_import (
          source_file TEXT NOT NULL,
          source_uid TEXT NOT NULL,
          properties JSONB NOT NULL,
          geom_json JSONB NOT NULL
        ) ON COMMIT DROP
        """
    )


def copy_features(cur: psycopg.Cursor, dataset: Dataset, features: list[dict[str, Any]]) -> tuple[int, int]:
    copied = 0
    skipped = 0
    with cur.copy(
        "COPY tmp_geojson_import (source_file, source_uid, properties, geom_json) FROM STDIN"
    ) as copy:
        for index, feature in enumerate(features):
            geom = feature.get("geometry")
            if not geom or not geom.get("coordinates"):
                skipped += 1
                continue
            properties = feature.get("properties") or {}
            copy.write_row(
                (
                    dataset.path.name,
                    source_uid(dataset.table, dataset.path.name, properties, index),
                    json.dumps(properties, ensure_ascii=False),
                    json.dumps(geom, ensure_ascii=False),
                )
            )
            copied += 1
    return copied, skipped


def import_airspaces(cur: psycopg.Cursor) -> list[bool]:
    cur.execute(
        """
        WITH parsed AS (
          SELECT source_file, source_uid, properties,
                 ST_SetSRID(ST_GeomFromGeoJSON(geom_json::text), 4326) AS raw_geom
          FROM tmp_geojson_import
        ),
        fixed AS (
          SELECT *, NOT ST_IsValid(raw_geom) AS repaired,
                 CASE WHEN ST_IsValid(raw_geom) THEN raw_geom ELSE ST_MakeValid(raw_geom) END AS geom
          FROM parsed
        ),
        polygonal AS (
          SELECT source_file, source_uid, properties, ST_CollectionExtract(geom, 3) AS geom
          FROM fixed
        )
        INSERT INTO airspaces (
          source_file, source_uid, name, airspace_type, icao_class, country, properties, geom, imported_at
        )
        SELECT source_file, source_uid,
               properties->>'name',
               NULLIF(properties->>'type', '')::integer,
               properties->>'icaoClass',
               properties->>'country',
               properties,
               geom,
               now()
        FROM polygonal
        WHERE NOT ST_IsEmpty(geom)
          AND ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon')
        ON CONFLICT (source_uid) DO UPDATE SET
          source_file = EXCLUDED.source_file,
          name = EXCLUDED.name,
          airspace_type = EXCLUDED.airspace_type,
          icao_class = EXCLUDED.icao_class,
          country = EXCLUDED.country,
          properties = EXCLUDED.properties,
          geom = EXCLUDED.geom,
          imported_at = now()
        RETURNING xmax = 0 AS inserted
        """
    )
    return [row[0] for row in cur.fetchall()]


def import_gpsjam(cur: psycopg.Cursor) -> list[bool]:
    cur.execute(
        """
        WITH parsed AS (
          SELECT source_file, source_uid, properties,
                 ST_SetSRID(ST_GeomFromGeoJSON(geom_json::text), 4326) AS raw_geom
          FROM tmp_geojson_import
        ),
        fixed AS (
          SELECT *, NOT ST_IsValid(raw_geom) AS repaired,
                 CASE WHEN ST_IsValid(raw_geom) THEN raw_geom ELSE ST_MakeValid(raw_geom) END AS geom
          FROM parsed
        ),
        polygonal AS (
          SELECT source_file, source_uid, properties, ST_CollectionExtract(geom, 3) AS geom
          FROM fixed
        )
        INSERT INTO gpsjam_zones (
          source_file, source_uid, h3, good, bad, percent_bad, properties, geom, imported_at
        )
        SELECT source_file, source_uid,
               properties->>'h3',
               NULLIF(properties->>'good', '')::integer,
               NULLIF(properties->>'bad', '')::integer,
               NULLIF(properties->>'percent_bad', '')::double precision,
               properties,
               geom,
               now()
        FROM polygonal
        WHERE NOT ST_IsEmpty(geom)
          AND ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon')
        ON CONFLICT (source_uid) DO UPDATE SET
          source_file = EXCLUDED.source_file,
          h3 = EXCLUDED.h3,
          good = EXCLUDED.good,
          bad = EXCLUDED.bad,
          percent_bad = EXCLUDED.percent_bad,
          properties = EXCLUDED.properties,
          geom = EXCLUDED.geom,
          imported_at = now()
        RETURNING xmax = 0 AS inserted
        """
    )
    return [row[0] for row in cur.fetchall()]


def import_osm_buildings(cur: psycopg.Cursor) -> list[bool]:
    cur.execute(
        """
        WITH parsed AS (
          SELECT source_file, source_uid, properties,
                 ST_SetSRID(ST_GeomFromGeoJSON(geom_json::text), 4326) AS raw_geom
          FROM tmp_geojson_import
        ),
        fixed AS (
          SELECT *, NOT ST_IsValid(raw_geom) AS repaired,
                 CASE WHEN ST_IsValid(raw_geom) THEN raw_geom ELSE ST_MakeValid(raw_geom) END AS geom
          FROM parsed
        ),
        polygonal AS (
          SELECT source_file, source_uid, properties, ST_CollectionExtract(geom, 3) AS geom
          FROM fixed
        )
        INSERT INTO osm_buildings (
          source_file, source_uid, osm_id, name, building, properties, geom, imported_at
        )
        SELECT source_file, source_uid,
               NULLIF(properties->>'osm_id', '')::bigint,
               properties->>'name',
               properties->>'building',
               properties,
               geom,
               now()
        FROM polygonal
        WHERE NOT ST_IsEmpty(geom)
          AND ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon')
        ON CONFLICT (source_uid) DO UPDATE SET
          source_file = EXCLUDED.source_file,
          osm_id = EXCLUDED.osm_id,
          name = EXCLUDED.name,
          building = EXCLUDED.building,
          properties = EXCLUDED.properties,
          geom = EXCLUDED.geom,
          imported_at = now()
        RETURNING xmax = 0 AS inserted
        """
    )
    return [row[0] for row in cur.fetchall()]


def import_acled_events(cur: psycopg.Cursor) -> list[bool]:
    cur.execute(
        """
        WITH parsed AS (
          SELECT source_file, source_uid, properties,
                 ST_SetSRID(ST_GeomFromGeoJSON(geom_json::text), 4326) AS geom
          FROM tmp_geojson_import
        )
        INSERT INTO acled_events (
          source_file, source_uid, event_id_cnty, event_date, event_type, sub_event_type,
          country, admin1, location, fatalities, properties, geom, imported_at
        )
        SELECT source_file, source_uid,
               properties->>'event_id_cnty',
               NULLIF(properties->>'event_date', '')::date,
               properties->>'event_type',
               properties->>'sub_event_type',
               properties->>'country',
               properties->>'admin1',
               properties->>'location',
               NULLIF(properties->>'fatalities', '')::integer,
               properties,
               geom,
               now()
        FROM parsed
        WHERE NOT ST_IsEmpty(geom)
          AND ST_GeometryType(geom) = 'ST_Point'
          AND ST_IsValid(geom)
        ON CONFLICT (source_uid) DO UPDATE SET
          source_file = EXCLUDED.source_file,
          event_id_cnty = EXCLUDED.event_id_cnty,
          event_date = EXCLUDED.event_date,
          event_type = EXCLUDED.event_type,
          sub_event_type = EXCLUDED.sub_event_type,
          country = EXCLUDED.country,
          admin1 = EXCLUDED.admin1,
          location = EXCLUDED.location,
          fatalities = EXCLUDED.fatalities,
          properties = EXCLUDED.properties,
          geom = EXCLUDED.geom,
          imported_at = now()
        RETURNING xmax = 0 AS inserted
        """
    )
    return [row[0] for row in cur.fetchall()]


IMPORTERS = {
    "airspaces": import_airspaces,
    "gpsjam_zones": import_gpsjam,
    "osm_buildings": import_osm_buildings,
    "acled_events": import_acled_events,
}


def count_invalid(cur: psycopg.Cursor) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM tmp_geojson_import
        WHERE NOT ST_IsValid(ST_SetSRID(ST_GeomFromGeoJSON(geom_json::text), 4326))
        """
    )
    return cur.fetchone()[0]


def main() -> None:
    load_dotenv()
    database_url = env("DATABASE_URL", required=True)
    datasets = [*DATASETS, *gpsjam_datasets()]
    existing = [dataset for dataset in datasets if dataset.path.exists()]

    print("Importando GeoJSON existentes a PostGIS.")
    print("Archivos encontrados:", ", ".join(dataset.path.name for dataset in existing))

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for dataset in existing:
                features = load_features(dataset.path)
                create_temp_table(cur)
                copied, skipped = copy_features(cur, dataset, features)
                invalid = count_invalid(cur)
                results = IMPORTERS[dataset.table](cur)
                rejected = copied - len(results)
                print(
                    f"{dataset.table}: archivo={dataset.path.name} "
                    f"features={len(features)} copiados={copied} omitidos_sin_geom={skipped} "
                    f"geometrias_invalidas={invalid} importados={len(results)} rechazados={rejected} "
                    f"inserted={sum(results)} updated={len(results)-sum(results)}"
                )


if __name__ == "__main__":
    main()

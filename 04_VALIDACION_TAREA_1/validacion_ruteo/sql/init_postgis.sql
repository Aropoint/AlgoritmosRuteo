CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS airspaces (
  id BIGSERIAL PRIMARY KEY,
  source_file TEXT NOT NULL,
  source_uid TEXT NOT NULL UNIQUE,
  name TEXT,
  airspace_type INTEGER,
  icao_class TEXT,
  country TEXT,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  geom geometry(Geometry, 4326) NOT NULL,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT airspaces_geom_type_chk
    CHECK (ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon'))
);

CREATE TABLE IF NOT EXISTS gpsjam_zones (
  id BIGSERIAL PRIMARY KEY,
  source_file TEXT NOT NULL,
  source_uid TEXT NOT NULL UNIQUE,
  h3 TEXT,
  good INTEGER,
  bad INTEGER,
  percent_bad DOUBLE PRECISION,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  geom geometry(Geometry, 4326) NOT NULL,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT gpsjam_zones_geom_type_chk
    CHECK (ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon'))
);

CREATE TABLE IF NOT EXISTS osm_buildings (
  id BIGSERIAL PRIMARY KEY,
  source_file TEXT NOT NULL,
  source_uid TEXT NOT NULL UNIQUE,
  osm_id BIGINT,
  name TEXT,
  building TEXT,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  geom geometry(Geometry, 4326) NOT NULL,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT osm_buildings_geom_type_chk
    CHECK (ST_GeometryType(geom) IN ('ST_Polygon', 'ST_MultiPolygon'))
);

CREATE TABLE IF NOT EXISTS acled_events (
  id BIGSERIAL PRIMARY KEY,
  source_file TEXT NOT NULL,
  source_uid TEXT NOT NULL UNIQUE,
  event_id_cnty TEXT,
  event_date DATE,
  event_type TEXT,
  sub_event_type TEXT,
  country TEXT,
  admin1 TEXT,
  location TEXT,
  fatalities INTEGER,
  properties JSONB NOT NULL DEFAULT '{}'::jsonb,
  geom geometry(Point, 4326) NOT NULL,
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS airspaces_geom_gix ON airspaces USING GIST (geom);
CREATE INDEX IF NOT EXISTS gpsjam_zones_geom_gix ON gpsjam_zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS osm_buildings_geom_gix ON osm_buildings USING GIST (geom);
CREATE INDEX IF NOT EXISTS acled_events_geom_gix ON acled_events USING GIST (geom);

COMMENT ON TABLE airspaces IS
  'Repositorio PostGIS de zonas OpenAIP Restricted/Danger/Prohibited importadas desde GeoJSON externo.';
COMMENT ON TABLE gpsjam_zones IS
  'Repositorio PostGIS de celdas H3 GPSJam convertidas previamente a GeoJSON.';
COMMENT ON TABLE osm_buildings IS
  'Repositorio PostGIS de poligonos de edificaciones obtenidos desde OpenStreetMap/Overpass.';
COMMENT ON TABLE acled_events IS
  'Repositorio PostGIS de eventos ACLED como puntos. Cualquier buffer de amenaza debe crearse despues con un radio parametrizado y documentado como decision del modelo.';
COMMENT ON COLUMN acled_events.geom IS
  'Punto original del evento ACLED en SRID 4326. No contiene radio de amenaza.';

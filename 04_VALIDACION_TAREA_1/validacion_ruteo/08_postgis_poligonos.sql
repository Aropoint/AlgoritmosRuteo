CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS zonas_riesgo (
  id BIGSERIAL PRIMARY KEY,
  fuente TEXT NOT NULL,
  nombre TEXT,
  inicio TIMESTAMPTZ,
  fin TIMESTAMPTZ,
  severidad DOUBLE PRECISION,
  geom geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS zonas_riesgo_gix ON zonas_riesgo USING GIST (geom);

-- Evidencia de que la base trabaja con polígonos:
SELECT PostGIS_Version();
SELECT f_table_schema, f_table_name, type, srid
FROM geometry_columns
WHERE f_table_name = 'zonas_riesgo';

-- Ejemplo de consulta: ¿qué zonas intersectan una ruta (LINESTRING)?
-- SELECT id, fuente, nombre
-- FROM zonas_riesgo
-- WHERE ST_Intersects(
--   geom,
--   ST_GeomFromText('LINESTRING(-70.66 -33.45,-70.60 -33.40)',4326)
-- );

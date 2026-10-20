-- Modelo de datos de la Tarea 2: ruteo físico resiliente de UAV.
-- Crea la BD desde cero: BORRA las tablas anteriores. Requiere PostGIS y pgRouting.
-- Uso: python BD/crear_bd.py   (o: psql -d ruteo_uav -f BD/schema.sql)
-- Explicación del modelo y diagrama: BD/MODELO_BD.md y BD/diagrama_bd.png

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

DROP VIEW IF EXISTS v_viento_resumen;
DROP TABLE IF EXISTS evaluaciones, rutas, amz_eventos, amz_incendios, amz_gpsjam_celdas,
    meta_viento, meta_elevacion, meta_edificios, mision, aristas, nodos,
    parametros_pesos, fuentes CASCADE;

-- ---------------------------------------------------------------------------
-- 1. Procedencia: una fila por archivo JSON cargado
-- ---------------------------------------------------------------------------
CREATE TABLE fuentes (
    id             serial PRIMARY KEY,
    clave          text NOT NULL UNIQUE,          -- p. ej. 'osm_edificios'
    tipo           text NOT NULL CHECK (tipo IN ('infraestructura', 'metadata', 'amenaza')),
    nombre         text,
    url            text,
    licencia       text,
    descargado_utc timestamptz,
    parametros     jsonb NOT NULL DEFAULT '{}',   -- bbox, fechas y opciones de la extracción
    archivo_json   text,                          -- ruta relativa a 05_T2
    cargado_utc    timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- 2. Infraestructura: grafo de navegación (vértices = puntos, aristas = tramos de vuelo)
-- ---------------------------------------------------------------------------
CREATE TABLE nodos (
    id          integer PRIMARY KEY,              -- source/target de pgRouting
    tipo        text NOT NULL CHECK (tipo IN ('navegacion', 'inicio', 'observacion', 'destino')),
    elevacion_m double precision,                 -- terreno (meta_elevacion); NULL = sin dato
    geom        geometry(Point, 4326) NOT NULL
);

CREATE TABLE aristas (
    id                    integer PRIMARY KEY,
    source                integer NOT NULL REFERENCES nodos (id),
    target                integer NOT NULL REFERENCES nodos (id),
    largo_km              double precision NOT NULL CHECK (largo_km > 0),  -- costo de la línea base
    rumbo_grados          double precision,       -- de source a target, desde el norte (factor de viento)
    -- Restricciones derivadas de la metadata (NULL = sin dato = no restringe)
    altura_max_edificio_m double precision,       -- edificio más alto a <= buffer_edificio_m del tramo
    terreno_max_m         double precision,       -- máximo del terreno en extremos y punto medio
    en_zona_restringida   boolean NOT NULL DEFAULT false,
    -- Riesgo derivado de las amenazas, todo en [0, 1]
    r_eventos             double precision NOT NULL DEFAULT 0 CHECK (r_eventos BETWEEN 0 AND 1),
    r_incendios           double precision NOT NULL DEFAULT 0 CHECK (r_incendios BETWEEN 0 AND 1),
    p_gnss                double precision NOT NULL DEFAULT 0 CHECK (p_gnss BETWEEN 0 AND 1),
    riesgo                double precision NOT NULL DEFAULT 0 CHECK (riesgo BETWEEN 0 AND 1),
    geom                  geometry(LineString, 4326) NOT NULL,
    CHECK (source <> target)
);
CREATE INDEX aristas_source_idx ON aristas (source);
CREATE INDEX aristas_target_idx ON aristas (target);
CREATE INDEX aristas_geom_idx ON aristas USING gist (geom);
CREATE INDEX nodos_geom_idx ON nodos USING gist (geom);

CREATE TABLE mision (
    orden   smallint PRIMARY KEY,                 -- 0 = inicio, ..., último = destino
    nodo_id integer NOT NULL REFERENCES nodos (id),
    rol     text NOT NULL CHECK (rol IN ('inicio', 'observacion', 'destino'))
);

-- ---------------------------------------------------------------------------
-- 3. Metadata
-- ---------------------------------------------------------------------------
CREATE TABLE meta_edificios (                     -- OpenStreetMap (Overpass)
    osm_tipo          text NOT NULL CHECK (osm_tipo IN ('way', 'relation')),
    osm_id            bigint NOT NULL,
    tipo_edificio     text,                       -- valor del tag building
    altura_m          double precision,           -- tag height
    niveles           smallint,                   -- tag building:levels
    altura_estimada_m double precision,           -- height o niveles x 3 m; NULL = sin dato
    origen_altura     text,                       -- 'height', 'building:levels' o NULL
    geom              geometry(MultiPolygon, 4326) NOT NULL,
    fuente_id         integer NOT NULL REFERENCES fuentes (id),
    PRIMARY KEY (osm_tipo, osm_id)
);
CREATE INDEX meta_edificios_geom_idx ON meta_edificios USING gist (geom);

CREATE TABLE meta_elevacion (                     -- Open-Meteo Elevation API (Copernicus DEM GLO-90)
    id          serial PRIMARY KEY,
    tipo        text NOT NULL CHECK (tipo IN ('nodo', 'punto_medio')),
    ref_id      integer NOT NULL,                 -- id de nodo o de arista según tipo
    elevacion_m double precision,
    geom        geometry(Point, 4326) NOT NULL,
    fuente_id   integer NOT NULL REFERENCES fuentes (id),
    UNIQUE (tipo, ref_id)
);

CREATE TABLE meta_viento (                        -- Open-Meteo Historical Weather API (ERA5)
    ts_utc           timestamptz PRIMARY KEY,
    velocidad_m_s    double precision,            -- a 100 m sobre el suelo
    direccion_grados double precision,            -- de dónde sopla (convención meteorológica)
    rafaga_10m_m_s   double precision,
    fuente_id        integer NOT NULL REFERENCES fuentes (id)
);

-- ---------------------------------------------------------------------------
-- 4. Amenazas
-- ---------------------------------------------------------------------------
CREATE TABLE amz_gpsjam_celdas (                  -- GPSJam: degradación GNSS por celda H3 (res. 4)
    h3              text PRIMARY KEY,
    dias_ventana    smallint NOT NULL,
    dias_con_datos  smallint NOT NULL,
    dias_rojos      smallint NOT NULL,
    frac_dias_rojos double precision,             -- dias_rojos / dias_con_datos; NULL = sin datos
    pct_malo_medio  double precision,
    aviones_buenos  integer NOT NULL,
    aviones_malos   integer NOT NULL,
    contiene_aoi    boolean NOT NULL,
    geom            geometry(Polygon, 4326) NOT NULL,
    fuente_id       integer NOT NULL REFERENCES fuentes (id)
);
CREATE INDEX amz_gpsjam_geom_idx ON amz_gpsjam_celdas USING gist (geom);

CREATE TABLE amz_incendios (                      -- The Economist war-fire model (sobre NASA FIRMS)
    id        bigserial PRIMARY KEY,
    fecha     date NOT NULL,
    hora_utc  smallint,                           -- HHMM de adquisición
    guerra    boolean NOT NULL,                   -- clasificado como relacionado con la guerra
    periodo   text NOT NULL CHECK (periodo IN ('historico', 'evaluacion')),
    geom      geometry(Point, 4326) NOT NULL,
    fuente_id integer NOT NULL REFERENCES fuentes (id)
);
CREATE INDEX amz_incendios_geom_idx ON amz_incendios USING gist (geom);

CREATE TABLE amz_eventos (                        -- UCDP GED: eventos de violencia organizada
    id                bigint PRIMARY KEY,         -- id del evento en UCDP
    fecha_inicio      date NOT NULL,
    fecha_fin         date,
    tipo_violencia    smallint,                   -- 1 estatal, 2 no estatal, 3 unilateral
    precision_lugar   smallint,                   -- where_prec: 1 = lugar exacto ... 7
    precision_fecha   smallint,
    muertes_estimadas integer,                    -- best
    adm1              text,
    adm2              text,
    lugar             text,
    geom              geometry(Point, 4326) NOT NULL,
    fuente_id         integer NOT NULL REFERENCES fuentes (id)
);
CREATE INDEX amz_eventos_geom_idx ON amz_eventos USING gist (geom);

-- ---------------------------------------------------------------------------
-- 5. Parámetros de la asignación de pesos (BD/pesos.sql); se pueden ajustar aquí
-- ---------------------------------------------------------------------------
CREATE TABLE parametros_pesos (
    clave       text PRIMARY KEY,
    valor       double precision NOT NULL,
    descripcion text NOT NULL
);
INSERT INTO parametros_pesos (clave, valor, descripcion) VALUES
    ('sigma_eventos_km',   1.0, 'Ancho del núcleo gaussiano de densidad para eventos UCDP (km)'),
    ('sigma_incendios_km', 0.5, 'Ancho del núcleo gaussiano de densidad para incendios de guerra (km)'),
    ('corte_sigmas',       3.0, 'Eventos más lejanos que corte_sigmas * sigma no aportan densidad'),
    ('buffer_edificio_m', 15.0, 'Distancia máxima entre un tramo y un edificio para considerarlo obstáculo (m)');

-- ---------------------------------------------------------------------------
-- 6. Resultados: rutas calculadas y su evaluación de resiliencia
-- ---------------------------------------------------------------------------
CREATE TABLE rutas (
    id           serial PRIMARY KEY,
    creada_utc   timestamptz NOT NULL DEFAULT now(),
    metodo       text NOT NULL CHECK (metodo IN ('dijkstra', 'propuesta')),
    rango        smallint NOT NULL CHECK (rango IN (1, 2)),   -- 1 = principal, 2 = alternativa
    origen       integer NOT NULL REFERENCES nodos (id),
    destino      integer NOT NULL REFERENCES nodos (id),
    largo_km     double precision NOT NULL,
    costo        double precision,                             -- costo del método (km o km equivalentes)
    riesgo_medio double precision,
    aristas      integer[] NOT NULL,                           -- ids en orden de recorrido
    preferencias jsonb NOT NULL DEFAULT '{}',
    geom         geometry(LineString, 4326)
);

CREATE TABLE evaluaciones (
    id                 serial PRIMARY KEY,
    creada_utc         timestamptz NOT NULL DEFAULT now(),
    origen             integer NOT NULL REFERENCES nodos (id),
    destino            integer NOT NULL REFERENCES nodos (id),
    n_escenarios       integer NOT NULL,
    n_fallas           integer NOT NULL,
    r_par_dijkstra     double precision,           -- consulta libre: par de rutas; misión: todos los tramos conservan ruta
    r_par_propuesta    double precision,
    r_mision_dijkstra  double precision,           -- estrategia A: par fijo + retroceso
    r_mision_replan    double precision,           -- estrategia D: Dijkstra que replanifica (ablación)
    r_mision_propuesta double precision,           -- estrategia C: propuesta completa
    delta_r_pp         double precision,           -- R_mision(C) - R_mision(A), en puntos porcentuales
    p_mcnemar          double precision,
    parametros         jsonb NOT NULL DEFAULT '{}'
);

-- ---------------------------------------------------------------------------
-- 7. Vistas de apoyo
-- ---------------------------------------------------------------------------
-- Viento representativo de la ventana: mediana, p95 y dirección media circular ponderada.
CREATE VIEW v_viento_resumen AS
SELECT count(*)                                                          AS horas,
       min(ts_utc)                                                       AS desde,
       max(ts_utc)                                                       AS hasta,
       percentile_cont(0.5)  WITHIN GROUP (ORDER BY velocidad_m_s)       AS velocidad_mediana_m_s,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY velocidad_m_s)       AS velocidad_p95_m_s,
       max(rafaga_10m_m_s)                                               AS rafaga_max_m_s,
       mod((degrees(atan2(sum(velocidad_m_s * sin(radians(direccion_grados))),
                          sum(velocidad_m_s * cos(radians(direccion_grados))))) + 360)::numeric, 360)
                                                                         AS direccion_media_grados
FROM meta_viento
WHERE velocidad_m_s IS NOT NULL AND direccion_grados IS NOT NULL;

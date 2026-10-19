-- Asignación de restricciones y pesos a las aristas a partir de la metadata y las amenazas
-- (rúbrica 5.2 y 6.1). Se ejecuta después de todas las cargas: python BD/asignar_pesos.py
-- Parámetros en la tabla parametros_pesos. Un dato ausente nunca bloquea: deja NULL o 0.

-- ---------------------------------------------------------------------------
-- Metadata 2 (elevación): terreno en los nodos y máximo del terreno por tramo
-- ---------------------------------------------------------------------------
UPDATE nodos n
SET elevacion_m = e.elevacion_m
FROM meta_elevacion e
WHERE e.tipo = 'nodo' AND e.ref_id = n.id;

-- GREATEST ignora los NULL: solo queda NULL si no hay ningún dato.
UPDATE aristas a
SET terreno_max_m = GREATEST(
    (SELECT elevacion_m FROM nodos WHERE id = a.source),
    (SELECT elevacion_m FROM nodos WHERE id = a.target),
    (SELECT elevacion_m FROM meta_elevacion WHERE tipo = 'punto_medio' AND ref_id = a.id));

-- ---------------------------------------------------------------------------
-- Metadata 1 (edificios OSM): edificio más alto a menos de buffer_edificio_m del tramo.
-- El filtro && con ST_Expand usa el índice espacial; ST_DWithin en geography mide en metros.
-- ---------------------------------------------------------------------------
UPDATE aristas SET altura_max_edificio_m = NULL;

WITH p AS (SELECT valor AS buffer_m FROM parametros_pesos WHERE clave = 'buffer_edificio_m'),
alto AS (
    SELECT a.id, max(e.altura_estimada_m) AS altura
    FROM aristas a
    CROSS JOIN p
    JOIN meta_edificios e
      ON e.geom && ST_Expand(a.geom, 0.001)
     AND ST_DWithin(a.geom::geography, e.geom::geography, p.buffer_m)
    WHERE e.altura_estimada_m IS NOT NULL
    GROUP BY a.id
)
UPDATE aristas a
SET altura_max_edificio_m = alto.altura
FROM alto
WHERE a.id = alto.id;

-- ---------------------------------------------------------------------------
-- Amenaza 3 (eventos UCDP): densidad de núcleo gaussiano en el punto medio del tramo,
-- normalizada por el máximo del AOI:  D(m) = sum_i exp(-d(m, ev_i)^2 / (2 sigma^2)).
-- ---------------------------------------------------------------------------
WITH p AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'sigma_eventos_km') AS sigma,
           (SELECT valor FROM parametros_pesos WHERE clave = 'corte_sigmas')     AS corte
),
pm AS (SELECT id, ST_LineInterpolatePoint(geom, 0.5)::geography AS g FROM aristas),
dens AS (
    SELECT pm.id,
           sum(exp(-power(ST_Distance(pm.g, e.geom::geography) / 1000.0, 2) / (2 * power(p.sigma, 2)))) AS d
    FROM pm
    CROSS JOIN p
    JOIN amz_eventos e ON ST_DWithin(pm.g, e.geom::geography, p.corte * p.sigma * 1000.0)
    GROUP BY pm.id
),
mx AS (SELECT max(d) AS m FROM dens)
UPDATE aristas a
SET r_eventos = COALESCE(round((dens.d / NULLIF(mx.m, 0))::numeric, 4), 0)
FROM pm
LEFT JOIN dens ON dens.id = pm.id
CROSS JOIN mx
WHERE a.id = pm.id;

-- ---------------------------------------------------------------------------
-- Amenaza 2 (incendios de guerra): misma densidad, solo incendios clasificados como
-- de guerra y del período histórico (los del período de evaluación se reservan para las fallas).
-- ---------------------------------------------------------------------------
WITH p AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'sigma_incendios_km') AS sigma,
           (SELECT valor FROM parametros_pesos WHERE clave = 'corte_sigmas')       AS corte
),
pm AS (SELECT id, ST_LineInterpolatePoint(geom, 0.5)::geography AS g FROM aristas),
dens AS (
    SELECT pm.id,
           sum(exp(-power(ST_Distance(pm.g, f.geom::geography) / 1000.0, 2) / (2 * power(p.sigma, 2)))) AS d
    FROM pm
    CROSS JOIN p
    JOIN amz_incendios f
      ON f.guerra AND f.periodo = 'historico'
     AND ST_DWithin(pm.g, f.geom::geography, p.corte * p.sigma * 1000.0)
    GROUP BY pm.id
),
mx AS (SELECT max(d) AS m FROM dens)
UPDATE aristas a
SET r_incendios = COALESCE(round((dens.d / NULLIF(mx.m, 0))::numeric, 4), 0)
FROM pm
LEFT JOIN dens ON dens.id = pm.id
CROSS JOIN mx
WHERE a.id = pm.id;

-- ---------------------------------------------------------------------------
-- Amenaza 1 (GPSJam): fracción de días con la celda en rojo, en la celda que contiene
-- el punto medio del tramo. Celda sin datos (sin aviones) = 0: ausencia de dato, no de amenaza.
-- ---------------------------------------------------------------------------
UPDATE aristas a
SET p_gnss = COALESCE((
    SELECT c.frac_dias_rojos
    FROM amz_gpsjam_celdas c
    WHERE ST_Contains(c.geom, ST_LineInterpolatePoint(a.geom, 0.5))
    LIMIT 1), 0);

-- ---------------------------------------------------------------------------
-- Riesgo combinado: probabilidad de que ocurra al menos una de las tres amenazas,
-- tratándolas como independientes. Entra al costo del método propuesto como (1 + w_R * riesgo).
-- ---------------------------------------------------------------------------
UPDATE aristas
SET riesgo = round((1 - (1 - r_eventos) * (1 - r_incendios) * (1 - p_gnss))::numeric, 4);

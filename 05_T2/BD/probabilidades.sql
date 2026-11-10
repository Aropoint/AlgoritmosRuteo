-- Probabilidad de falla de cada tramo y de cada nodo a partir de cada amenaza (Tarea 3, punto 5).
-- Lo ejecuta BD/probabilidades.py después de BD/asignar_pesos.py, que deja en las aristas la
-- intensidad r_i en [0, 1] de cada amenaza (r_eventos, r_incendios, p_gnss).
--
-- Modelo de tasa de falla por km (parámetros en parametros_pesos; son supuestos abstractos):
--   lambda_i(x) = lambda_i^max * r_i(x)                       [1/km]
--   tramo e:  p_i(e) = 1 - exp(-lambda_i(punto medio de e) * largo_km(e))
--   nodo v:   p_i(v) = 1 - exp(-lambda_i(v) * exposicion_nodo_km)
--   combinada: p(x) = 1 - prod_i (1 - p_i(x))                 (amenazas tratadas como independientes)
--
-- Por qué así: un tramo más largo está más expuesto, y -ln(1 - p) se SUMA a lo largo de una ruta,
-- de modo que la fiabilidad prod(1 - p) entra lineal y exacta en Dijkstra y en el MILP.
-- La combinación que usa el sitio se rehace en cada consulta (ruteo/probabilidad.py) con solo las
-- amenazas marcadas como "Considerar"; aquí se guarda cada componente y el total con las tres.

-- ---------------------------------------------------------------------------
-- 1. Intensidad de cada amenaza en los nodos. Mismo núcleo gaussiano que pesos.sql, normalizado
--    por el máximo de los TRAMOS para que nodos y tramos queden en la misma escala (tope 1).
-- ---------------------------------------------------------------------------
UPDATE nodos SET r_eventos = 0, r_incendios = 0, p_gnss = 0;

-- Amenaza 3 (eventos UCDP)
WITH p AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'sigma_eventos_km') AS sigma,
           (SELECT valor FROM parametros_pesos WHERE clave = 'corte_sigmas')     AS corte
),
puntos AS (
    SELECT 'arista' AS tipo, id, ST_LineInterpolatePoint(geom, 0.5)::geography AS g FROM aristas
    UNION ALL
    SELECT 'nodo', id, geom::geography FROM nodos
),
dens AS (
    SELECT pt.tipo, pt.id,
           sum(exp(-power(ST_Distance(pt.g, e.geom::geography) / 1000.0, 2) / (2 * power(p.sigma, 2)))) AS d
    FROM puntos pt
    CROSS JOIN p
    JOIN amz_eventos e ON ST_DWithin(pt.g, e.geom::geography, p.corte * p.sigma * 1000.0)
    GROUP BY pt.tipo, pt.id
),
mx AS (SELECT max(d) AS m FROM dens WHERE tipo = 'arista')
UPDATE nodos n
SET r_eventos = LEAST(1, COALESCE(round((dens.d / NULLIF(mx.m, 0))::numeric, 4), 0))
FROM dens CROSS JOIN mx
WHERE dens.tipo = 'nodo' AND dens.id = n.id;

-- Amenaza 2 (incendios de guerra del período histórico; los de evaluación se reservan)
WITH p AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'sigma_incendios_km') AS sigma,
           (SELECT valor FROM parametros_pesos WHERE clave = 'corte_sigmas')       AS corte
),
puntos AS (
    SELECT 'arista' AS tipo, id, ST_LineInterpolatePoint(geom, 0.5)::geography AS g FROM aristas
    UNION ALL
    SELECT 'nodo', id, geom::geography FROM nodos
),
dens AS (
    SELECT pt.tipo, pt.id,
           sum(exp(-power(ST_Distance(pt.g, f.geom::geography) / 1000.0, 2) / (2 * power(p.sigma, 2)))) AS d
    FROM puntos pt
    CROSS JOIN p
    JOIN amz_incendios f
      ON f.guerra AND f.periodo = 'historico'
     AND ST_DWithin(pt.g, f.geom::geography, p.corte * p.sigma * 1000.0)
    GROUP BY pt.tipo, pt.id
),
mx AS (SELECT max(d) AS m FROM dens WHERE tipo = 'arista')
UPDATE nodos n
SET r_incendios = LEAST(1, COALESCE(round((dens.d / NULLIF(mx.m, 0))::numeric, 4), 0))
FROM dens CROSS JOIN mx
WHERE dens.tipo = 'nodo' AND dens.id = n.id;

-- Amenaza 1 (GPSJam): fracción de días en rojo de la celda que contiene el nodo; sin datos = 0.
UPDATE nodos n
SET p_gnss = COALESCE((
    SELECT c.frac_dias_rojos
    FROM amz_gpsjam_celdas c
    WHERE ST_Contains(c.geom, n.geom)
    LIMIT 1), 0);

-- ---------------------------------------------------------------------------
-- 2. Probabilidad de falla por amenaza y combinada
-- ---------------------------------------------------------------------------
WITH l AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_eventos_por_km')   AS ev,
           (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_incendios_por_km') AS inc,
           (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_gnss_por_km')      AS gnss
)
UPDATE aristas a
SET pf_eventos   = round((1 - exp(-l.ev   * a.r_eventos   * a.largo_km))::numeric, 6),
    pf_incendios = round((1 - exp(-l.inc  * a.r_incendios * a.largo_km))::numeric, 6),
    pf_gnss      = round((1 - exp(-l.gnss * a.p_gnss      * a.largo_km))::numeric, 6)
FROM l;

WITH l AS (
    SELECT (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_eventos_por_km')   AS ev,
           (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_incendios_por_km') AS inc,
           (SELECT valor FROM parametros_pesos WHERE clave = 'lambda_gnss_por_km')      AS gnss,
           (SELECT valor FROM parametros_pesos WHERE clave = 'exposicion_nodo_km')      AS expo
)
UPDATE nodos n
SET pf_eventos   = round((1 - exp(-l.ev   * n.r_eventos   * l.expo))::numeric, 6),
    pf_incendios = round((1 - exp(-l.inc  * n.r_incendios * l.expo))::numeric, 6),
    pf_gnss      = round((1 - exp(-l.gnss * n.p_gnss      * l.expo))::numeric, 6)
FROM l;

UPDATE aristas SET pf_total = round((1 - (1 - pf_eventos) * (1 - pf_incendios) * (1 - pf_gnss))::numeric, 6);
UPDATE nodos   SET pf_total = round((1 - (1 - pf_eventos) * (1 - pf_incendios) * (1 - pf_gnss))::numeric, 6);

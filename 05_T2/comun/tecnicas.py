"""Las cuatro técnicas de ruteo de la Tarea 3 sobre la BD (punto 6).

- 6.1 pgr_dijkstra con cost = reverse_cost = largo_m (solo la distancia en metros).
- 6.2 MILP con Gurobi (ruteo/optimizacion.py) sobre el grafo que se reconstruye desde la BD.
- 6.3 pgr_dijkstra con cost = 1000 * (c_a + lambda * l_a): los costos dirigidos de cada arco se cargan
      en una tabla temporal (t3_arcos) y lambda se busca por bisección (ruteo/modelo_t3.lagrange).
- 6.4 colonia de hormigas (ruteo/hormigas.py).

Las cuatro usan el mismo grafo sobrevolable: los tramos excluidos (altura, relieve, zonas) no entran
a ninguna. Cada una se cronometra por separado; el tiempo incluye las consultas a la BD.
"""
from __future__ import annotations

from psycopg import sql

from comun.rutas import _camino_pgr_dijkstra, _sql_aristas
from ruteo.config import ParametrosACO
from ruteo.hormigas import aco
from ruteo.modelo_t3 import Instancia, ResultadoTecnica, lagrange, por_tramos
from ruteo.optimizacion import milp

LARGO_M = sql.SQL("largo_m")

CONSULTA_DIJKSTRA_M = ("SELECT * FROM pgr_dijkstra('SELECT id, source, target, largo_m AS cost, largo_m AS reverse_cost "
                       "FROM aristas WHERE id NOT IN (<tramos no sobrevolables>)', s, t, directed => true)")
CONSULTA_PONDERADA = ("SELECT * FROM pgr_dijkstra('SELECT id, source, target, c_ida + λ * l_ida AS cost, "
                      "c_vuelta + λ * l_vuelta AS reverse_cost FROM t3_arcos', s, t, directed => true)")


def dijkstra_m(conn, inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float) -> ResultadoTecnica:
    consulta = _sql_aristas(conn, LARGO_M, LARGO_M, inst.excluidas)

    def tramo(s, t, _b, _l):
        r = _camino_pgr_dijkstra(conn, consulta, s, t)
        return r, ({"consulta": CONSULTA_DIJKSTRA_M} if r else {"error": "pgr_dijkstra no encontró camino."})

    return por_tramos("dijkstra_m", inst, secuencia, autonomia_km, r_min, tramo)


def cargar_arcos(conn, inst: Instancia) -> int:
    """Tabla temporal de la sesión con los costos dirigidos de cada tramo sobrevolable (en metros).

    c_ida / c_vuelta: 1000 * d * f_viento en cada sentido; l_ida / l_vuelta: -ln(1-p) del tramo más el
    del nodo de llegada. Así pgr_dijkstra puede usar las probabilidades combinadas de la consulta.
    """
    conn.execute("""CREATE TEMP TABLE IF NOT EXISTS t3_arcos (
                        id integer PRIMARY KEY, source integer NOT NULL, target integer NOT NULL,
                        c_ida double precision, c_vuelta double precision,
                        l_ida double precision, l_vuelta double precision)""")
    conn.execute("TRUNCATE t3_arcos")
    filas = 0
    with conn.cursor() as cur, cur.copy("COPY t3_arcos FROM STDIN") as copia:
        for aid, a in inst.g.aristas.items():
            if aid in inst.excluidas:
                continue
            copia.write_row((aid, a.u, a.v, 1000 * inst.c(aid, a.u, a.v), 1000 * inst.c(aid, a.v, a.u),
                             inst.l(aid, a.u, a.v), inst.l(aid, a.v, a.u)))
            filas += 1
    return filas


def _camino_ponderado(conn, s: int, t: int, lam_km: float):
    lam_m = sql.Literal(float(1000 * lam_km))
    consulta = sql.SQL("SELECT id, source, target, c_ida + {l} * l_ida AS cost, c_vuelta + {l} * l_vuelta AS reverse_cost "
                       "FROM t3_arcos").format(l=lam_m).as_string(conn)
    return _camino_pgr_dijkstra(conn, consulta, s, t)


def dijkstra_ponderado(conn, inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float) -> ResultadoTecnica:
    cargar_arcos(conn, inst)

    def tramo(s, t, b, l_max):
        r, det = lagrange(inst, s, t, b, l_max, camino=lambda lam: _camino_ponderado(conn, s, t, lam))
        det["consulta"] = CONSULTA_PONDERADA
        return r, det

    return por_tramos("dijkstra_ponderado", inst, secuencia, autonomia_km, r_min, tramo)


def milp_gurobi(inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float) -> ResultadoTecnica:
    return por_tramos("milp_gurobi", inst, secuencia, autonomia_km, r_min, lambda s, t, b, l: milp(inst, s, t, b, l))


def colonia(inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float,
            params: ParametrosACO = ParametrosACO()) -> ResultadoTecnica:
    return por_tramos("aco", inst, secuencia, autonomia_km, r_min, lambda s, t, b, l: aco(inst, s, t, b, l, params))


def ejecutar(conn, inst: Instancia, secuencia: list[int], autonomia_km: float, r_min: float,
             params_aco: ParametrosACO = ParametrosACO()) -> dict[str, ResultadoTecnica]:
    """Las cuatro técnicas, en el orden del enunciado."""
    return {
        "dijkstra_m": dijkstra_m(conn, inst, secuencia, autonomia_km, r_min),
        "milp_gurobi": milp_gurobi(inst, secuencia, autonomia_km, r_min),
        "dijkstra_ponderado": dijkstra_ponderado(conn, inst, secuencia, autonomia_km, r_min),
        "aco": colonia(inst, secuencia, autonomia_km, r_min, params_aco),
    }


def lambda_recuperacion(res: ResultadoTecnica, defecto_km: float = 1.0) -> float:
    """lambda que usa la recuperación del punto 8: el mayor que encontró el Dijkstra ponderado en sus tramos.

    Nunca baja de `defecto_km`, para que la recuperación evite el riesgo aunque R_min no apriete.
    """
    detalles = res.detalle.get("tramos", [res.detalle]) if res.detalle else []
    valores = [d.get("lambda_km") for d in detalles if d.get("lambda_km") is not None]
    return max(valores + [defecto_km])

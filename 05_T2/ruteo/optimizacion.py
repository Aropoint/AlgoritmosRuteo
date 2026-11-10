"""Técnica 6.2: modelo formal de optimización resuelto con Gurobi (Tarea 3).

Problema de camino mínimo con restricciones de recursos (RCSP), en arcos dirigidos a = (u -> v)
de los tramos sobrevolables (ver ruteo/modelo_t3.py para la notación):

    x_a in {0, 1}
    min   sum_a c_a x_a                                   tiempo de vuelo (km equivalentes, con viento)
    s.a.  sum_{a in out(v)} x_a - sum_{a in in(v)} x_a = 1 (v = s), -1 (v = t), 0 (resto)   flujo
          sum_{a in in(v)} x_a <= 1          para todo v      no repite nodos
          sum_a d_a x_a <= B                                  autonomía del usuario (km)
          sum_a l_a x_a <= -ln(R_min)                         fiabilidad prod(1 - p) >= R_min
          (sin arcos hacia s ni desde t; los tramos no sobrevolables no tienen variable: x = 0)

- Metadata: la altura de edificios y el relieve deciden qué tramos existen; el viento entra en c_a.
- Amenazas: entran en l_a, la probabilidad de falla de tramos y nodos (BD/probabilidades.sql).
- Usuario: B, R_min, altura de vuelo y margen, zonas prohibidas y de amenaza.

Poda exacta: un nodo v solo puede estar en un camino factible si dist(s, v) + dist(v, t) <= B
(km). Lo mismo para cada arco. Achica el modelo sin cambiar su óptimo, para que quepa en la
licencia restringida de gurobipy (2.000 variables y 2.000 restricciones).

Ciclos: con c_a > 0 y restricciones de recurso "<=", un ciclo aislado nunca mejora el objetivo
ni ayuda a cumplir las restricciones, así que el óptimo es un camino simple. Igual se verifica, y
si apareciera uno se corta (sum x_ciclo <= |ciclo| - 1) y se vuelve a resolver.

Infactible (R_min o B demasiado exigentes): se informa y se resuelve el modelo secundario
"máxima fiabilidad sujeta a la autonomía" para mostrar lo mejor posible.
"""
from __future__ import annotations

import math
import time

from .algoritmos import Ruta, distancias
from .modelo_t3 import Instancia

LIMITE_LICENCIA = 2000  # variables y restricciones de la licencia restringida de gurobipy


def disponible() -> bool:
    try:
        import gurobipy  # noqa: F401
        return True
    except ImportError:
        return False


def _camino(arcos_elegidos: list[tuple[int, int, int]], s: int, t: int) -> tuple[Ruta | None, list]:
    """Recorre los arcos elegidos desde s. Devuelve el camino y los arcos sobrantes (ciclos)."""
    salida = {u: (aid, v) for aid, u, v in arcos_elegidos}
    nodos, aristas, usados = [s], [], set()
    while nodos[-1] != t:
        u = nodos[-1]
        if u not in salida or u in usados:
            return None, arcos_elegidos
        usados.add(u)
        aid, v = salida[u]
        aristas.append(aid)
        nodos.append(v)
    en_camino = set(zip(aristas, nodos[:-1]))
    sobrantes = [(aid, u, v) for aid, u, v in arcos_elegidos if (aid, u) not in en_camino]
    return Ruta(nodos, aristas), sobrantes


def milp(inst: Instancia, s: int, t: int, autonomia_km: float, l_max: float,
         tiempo_limite_s: float = 10.0, semilla: int = 0, podar: bool = True) -> tuple[Ruta | None, dict]:
    t0 = time.perf_counter()
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        return None, {"error": "gurobipy no está instalado en el contenedor."}

    g = inst.g
    total_arcos = sum(1 for _ in inst.arcos())
    if podar:
        ds = distancias(g, s, inst.d, inst.excluidas)
        dt = distancias(g, t, inst.d, inst.excluidas, hacia_origen=True)
        arcos = [(aid, u, v) for aid, u, v in inst.arcos()
                 if v != s and u != t and ds.get(u, math.inf) + inst.d(aid) + dt.get(v, math.inf) <= autonomia_km + 1e-9]
    else:
        arcos = [(aid, u, v) for aid, u, v in inst.arcos() if v != s and u != t]
    nodos = {s, t} | {u for _, u, _ in arcos} | {v for _, _, v in arcos}
    detalle = {"arcos_sobrevolables": total_arcos, "arcos_tras_poda": len(arcos), "nodos_modelo": len(nodos)}
    if not arcos:
        detalle["error"] = "Ningún arco cabe en la autonomía: el modelo no tiene solución."
        return None, detalle

    c = [inst.c(*a) for a in arcos]
    d = [inst.d(a[0]) for a in arcos]
    l = [inst.l(*a) for a in arcos]
    sale: dict[int, list[int]] = {v: [] for v in nodos}
    entra: dict[int, list[int]] = {v: [] for v in nodos}
    for i, (_, u, v) in enumerate(arcos):
        sale[u].append(i)
        entra[v].append(i)

    try:
        with gp.Env(empty=True) as env:
            env.setParam("OutputFlag", 0)
            env.start()
            with gp.Model("ruteo_uav_t3", env=env) as m:
                x = m.addVars(len(arcos), vtype=GRB.BINARY, name="x")
                for v in nodos:
                    balance = 1 if v == s else (-1 if v == t else 0)
                    m.addConstr(gp.quicksum(x[i] for i in sale[v]) - gp.quicksum(x[i] for i in entra[v]) == balance,
                                name=f"flujo_{v}")
                    if v != s and entra[v]:
                        m.addConstr(gp.quicksum(x[i] for i in entra[v]) <= 1, name=f"visita_{v}")
                m.addConstr(gp.quicksum(d[i] * x[i] for i in range(len(arcos))) <= autonomia_km, name="autonomia")
                r_fiab = m.addConstr(gp.quicksum(l[i] * x[i] for i in range(len(arcos))) <= l_max, name="fiabilidad")
                m.setObjective(gp.quicksum(c[i] * x[i] for i in range(len(arcos))), GRB.MINIMIZE)
                m.Params.TimeLimit = tiempo_limite_s
                m.Params.MIPGap = 0.0
                m.Params.Seed = semilla
                m.update()
                detalle.update(n_variables=m.NumVars, n_restricciones=m.NumConstrs, limite_licencia=LIMITE_LICENCIA)

                secundario, cortes, runtime = False, 0, 0.0
                while True:
                    m.optimize()
                    runtime += m.Runtime
                    if m.Status in (GRB.INFEASIBLE, GRB.INF_OR_UNBD) and not secundario:
                        # R_min no alcanzable dentro de la autonomía: máxima fiabilidad posible.
                        secundario = True
                        m.remove(r_fiab)
                        m.setObjective(gp.quicksum(l[i] * x[i] for i in range(len(arcos))), GRB.MINIMIZE)
                        continue
                    if m.SolCount == 0:
                        detalle.update(estado=_estado(m.Status), runtime_gurobi_ms=round(1000 * runtime, 2),
                                       error="Sin solución: la autonomía no alcanza para unir origen y destino.")
                        return None, detalle
                    elegidos = [arcos[i] for i in range(len(arcos)) if x[i].X > 0.5]
                    ruta, sobrantes = _camino(elegidos, s, t)
                    if ruta is not None and not sobrantes:
                        break
                    cortes += 1  # ciclo aislado: se corta y se vuelve a resolver (no debería ocurrir)
                    idx = [i for i in range(len(arcos)) if arcos[i] in set(sobrantes)]
                    m.addConstr(gp.quicksum(x[i] for i in idx) <= len(idx) - 1, name=f"ciclo_{cortes}")
                    if cortes > 20:
                        detalle["error"] = "No se pudo eliminar los ciclos de la solución."
                        return None, detalle
                detalle.update(
                    estado=_estado(m.Status), objetivo=round(m.ObjVal, 6), cota=round(m.ObjBound, 6),
                    gap=round(m.MIPGap, 6) if m.IsMIP else 0.0, runtime_gurobi_ms=round(1000 * runtime, 2),
                    cortes_ciclo=cortes, modelo_secundario=secundario,
                    tiempo_total_ms=round(1000 * (time.perf_counter() - t0), 2),
                )
                if secundario:
                    detalle["nota"] = (f"R_min no es alcanzable con esta autonomía: se resolvió máx. fiabilidad "
                                       f"(fiabilidad máxima = {math.exp(-m.ObjVal):.4f}).")
                return ruta, detalle
    except gp.GurobiError as e:
        detalle["error"] = f"Gurobi: {e}"
        if "size-limited" in str(e).lower() or getattr(e, "errno", None) == 10010:
            detalle["error"] += f" (el modelo supera la licencia restringida de {LIMITE_LICENCIA} variables o restricciones)"
        return None, detalle


def _estado(codigo: int) -> str:
    from gurobipy import GRB
    nombres = {GRB.OPTIMAL: "óptimo", GRB.INFEASIBLE: "infactible", GRB.TIME_LIMIT: "límite de tiempo",
               GRB.INF_OR_UNBD: "infactible o no acotado", GRB.SUBOPTIMAL: "subóptimo"}
    return nombres.get(codigo, f"código {codigo}")

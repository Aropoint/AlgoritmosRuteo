"""Rutas sobre la BD (rúbrica 8 y 9).

- Línea base: dos rutas con pgr_dijkstra y costo = largo_km. La ruta 2 repite
  pgr_dijkstra sin las aristas de la ruta 1; si eso desconecta origen y
  destino, las penaliza x10 (igual que ruteo.algoritmos.dijkstra_dos_rutas).
- Propuesta: candidatas con pgr_KSP (Yen, 1971) sobre el costo enriquecido
      c(e, u->v) = largo_km * f_viento(u->v) * (1 + w_R * riesgo)
  más la ruta más corta en km. Después, ruteo.algoritmos.seleccionar_par elige
  el par (principal, alternativa) con menor J = estiramiento + solape + riesgo.
- Restricciones duras: ruteo.pesos.arista_admisible se evalúa en Python sobre
  los atributos cargados y la lista de aristas excluidas se pasa a SQL, de modo
  que ambos métodos usan exactamente el mismo grafo admisible.
"""
from __future__ import annotations

from psycopg import sql
from psycopg.types.json import Jsonb

from comun.ajustes import centro_aoi
from comun.transformar import obstaculo_relativo_m, viento_a_altura
from ruteo.algoritmos import Ruta, SeleccionPar, seleccionar_par
from ruteo.config import ParametrosAlgoritmo, Preferencias
from ruteo.geo import ProyeccionLocal
from ruteo.grafo import Arista, Grafo
from ruteo.pesos import Viento, costo_propuesta

ALTURA_REF_VIENTO_M = 100.0  # ERA5 (Open-Meteo) entrega el viento a 100 m sobre el suelo
KM = sql.SQL("largo_km")


def elevacion_nodo(conn, nodo: int) -> float | None:
    fila = conn.execute("SELECT elevacion_m FROM nodos WHERE id = %s", (nodo,)).fetchone()
    return fila[0] if fila else None


def grafo_desde_bd(conn, elevacion_origen_m: float | None) -> Grafo:
    """Reconstruye el grafo de ruteo/ con los ids de la BD, que son los mismos de pgRouting.

    En `altura_max_edificio_m` se guarda el obstáculo relativo al despegue
    (relieve + edificio), que es lo que ruteo.pesos compara con altura_vuelo - margen.
    """
    lat0, lon0 = centro_aoi()
    g = Grafo(ProyeccionLocal(lat0, lon0))
    for nid, tipo, lat, lon in conn.execute("SELECT id, tipo, ST_Y(geom), ST_X(geom) FROM nodos ORDER BY id"):
        g.agregar_nodo(nid, lat, lon, tipo)
    filas = conn.execute(
        """SELECT id, source, target, largo_km, riesgo, altura_max_edificio_m, terreno_max_m, en_zona_restringida
           FROM aristas ORDER BY id"""
    )
    for aid, u, v, largo, riesgo, altura_edificio, terreno, zona in filas:
        atributos = {"riesgo": riesgo, "en_zona_restringida": zona}
        obstaculo = obstaculo_relativo_m(altura_edificio, terreno, elevacion_origen_m)
        if obstaculo is not None:
            atributos["altura_max_edificio_m"] = obstaculo
        g.aristas[aid] = Arista(aid, u, v, largo, atributos)
        g.ady[u].append((v, aid))
        g.ady[v].append((u, aid))
    return g


def viento_bd(conn, altura_vuelo_m: float) -> tuple[Viento | None, dict]:
    """Viento representativo (mediana de la ventana) llevado a la altura de vuelo por la ley potencial."""
    fila = conn.execute(
        """SELECT horas, velocidad_mediana_m_s, velocidad_p95_m_s, direccion_media_grados, rafaga_max_m_s, desde, hasta
           FROM v_viento_resumen"""
    ).fetchone()
    if not fila or not fila[0] or fila[1] is None or fila[3] is None:
        return None, {"fuente": "sin_dato", "nota": "Sin datos de viento: el factor de viento queda neutro (1)."}
    horas, mediana, p95, direccion, rafaga, desde, hasta = fila
    v = viento_a_altura(mediana, ALTURA_REF_VIENTO_M, altura_vuelo_m)
    info = {
        "fuente": "Open-Meteo (ERA5)",
        "horas": horas,
        "desde": desde.isoformat() if desde else None,
        "hasta": hasta.isoformat() if hasta else None,
        "mediana_100m_m_s": round(mediana, 2),
        "p95_100m_m_s": round(p95, 2) if p95 is not None else None,
        "rafaga_max_10m_m_s": round(rafaga, 2) if rafaga is not None else None,
        "velocidad_a_altura_vuelo_m_s": round(v, 2),
        "direccion_desde_grados": round(float(direccion), 1),
    }
    return Viento(round(v, 2), float(direccion), "open-meteo"), info


# ---------------------------------------------------------------------------
# SQL de aristas para pgRouting
# ---------------------------------------------------------------------------

def _sql_aristas(conn, costo: sql.Composable, reverso: sql.Composable, excluidas) -> str:
    """Consulta de aristas (id, source, target, cost, reverse_cost) sin las excluidas."""
    q = sql.SQL("SELECT id, source, target, {c} AS cost, {r} AS reverse_cost FROM aristas").format(c=costo, r=reverso)
    if excluidas:
        ids = sql.SQL(", ").join(sql.Literal(int(i)) for i in sorted(excluidas))
        q = q + sql.SQL(" WHERE id NOT IN ({ids})").format(ids=ids)
    return q.as_string(conn)


def _costo_penalizado(aristas: list[int]) -> sql.Composable:
    ids = sql.SQL(", ").join(sql.Literal(int(i)) for i in sorted(set(aristas)))
    return sql.SQL("CASE WHEN id IN ({ids}) THEN 10 * largo_km ELSE largo_km END").format(ids=ids)


def _costo_propuesta_sql(prefs: Preferencias, viento: Viento | None, inverso: bool) -> sql.Composable:
    """Mismo costo que ruteo.pesos.costo_propuesta, en SQL (inverso = de target a source)."""
    riesgo = sql.SQL("(1 + {w} * riesgo)").format(w=sql.Literal(float(prefs.peso_riesgo)))
    if viento is None or viento.velocidad_m_s == 0:
        return sql.SQL("largo_km * {r}").format(r=riesgo)
    v = float(prefs.velocidad_crucero_m_s)
    rumbo = sql.SQL("(COALESCE(rumbo_grados, 0) + 180)") if inverso else sql.SQL("COALESCE(rumbo_grados, 0)")
    frente = sql.SQL("LEAST({w} * cos(radians({rumbo} - {d})), {tope})").format(
        w=sql.Literal(float(viento.velocidad_m_s)), rumbo=rumbo,
        d=sql.Literal(float(viento.direccion_desde_grados)), tope=sql.Literal(0.8 * v),
    )
    return sql.SQL("largo_km * {v} / ({v} - {frente}) * {r}").format(v=sql.Literal(v), frente=frente, r=riesgo)


def _camino_pgr_dijkstra(conn, aristas_sql: str, s: int, t: int) -> Ruta | None:
    filas = conn.execute(
        "SELECT node, edge FROM pgr_dijkstra(%s, %s::bigint, %s::bigint, directed => true) ORDER BY path_seq",
        (aristas_sql, s, t),
    ).fetchall()
    if not filas:
        return None
    return Ruta([int(n) for n, _ in filas], [int(e) for _, e in filas if e != -1])


# ---------------------------------------------------------------------------
# Métodos
# ---------------------------------------------------------------------------

def dijkstra_dos_rutas_pgr(conn, s: int, t: int, excluidas) -> list[Ruta]:
    """Rúbrica 8: k = 2 rutas distintas usando solo pgr_dijkstra y la distancia en km."""
    r1 = _camino_pgr_dijkstra(conn, _sql_aristas(conn, KM, KM, excluidas), s, t)
    if r1 is None:
        return []
    r2 = _camino_pgr_dijkstra(conn, _sql_aristas(conn, KM, KM, set(excluidas) | set(r1.aristas)), s, t)
    if r2 is None:
        penal = _costo_penalizado(r1.aristas)
        r2 = _camino_pgr_dijkstra(conn, _sql_aristas(conn, penal, penal, excluidas), s, t)
        if r2 is not None and r2.clave() == r1.clave():
            r2 = None
    return [r1] + ([r2] if r2 else [])


def ksp_pgr(conn, s: int, t: int, k: int, prefs: Preferencias, viento: Viento | None, excluidas) -> list[Ruta]:
    """Candidatas de Yen con pgr_KSP sobre el costo enriquecido (dirigido por el viento)."""
    aristas_sql = _sql_aristas(conn, _costo_propuesta_sql(prefs, viento, False),
                               _costo_propuesta_sql(prefs, viento, True), excluidas)
    filas = conn.execute(
        """SELECT path_id, node, edge
           FROM pgr_KSP(%s, %s::bigint, %s::bigint, %s::integer, directed => true)
           ORDER BY path_id, path_seq""",
        (aristas_sql, s, t, k),
    ).fetchall()
    caminos: dict[int, tuple[list[int], list[int]]] = {}
    for pid, nodo, arista in filas:
        nodos, aristas = caminos.setdefault(pid, ([], []))
        nodos.append(int(nodo))
        if arista != -1:
            aristas.append(int(arista))
    return [Ruta(n, a) for n, a in caminos.values()]


def propuesta_pgr(conn, g: Grafo, s: int, t: int, prefs: Preferencias, params: ParametrosAlgoritmo,
                  viento: Viento | None, excluidas, mas_corta: Ruta) -> SeleccionPar | None:
    """Rúbrica 9: par del método propuesto (pgr_KSP + selección resiliente con control de presupuesto)."""
    candidatas = ksp_pgr(conn, s, t, params.k_candidatas, prefs, viento, excluidas)
    if not candidatas:
        return None
    if mas_corta.clave() not in {r.clave() for r in candidatas}:
        candidatas.append(mas_corta)
    largo_min = mas_corta.largo_km(g)
    presupuesto = (1 + prefs.presupuesto_extra) * largo_min
    caben = [r for r in candidatas if r.largo_km(g) <= presupuesto + 1e-9] or [mas_corta]
    return seleccionar_par(g, caben, largo_min, costo_propuesta(g, prefs, viento), prefs, params)


# ---------------------------------------------------------------------------
# Serialización y persistencia
# ---------------------------------------------------------------------------

def ruta_a_dict(g: Grafo, r: Ruta, costo=None) -> dict:
    return {
        "nodos": r.nodos,
        "aristas": r.aristas,
        "largo_km": round(r.largo_km(g), 3),
        "costo": round(r.costo(costo), 3) if costo else None,
        "riesgo_medio": round(r.riesgo_medio(g), 4),
        "coordenadas": [[round(g.nodos[n].lat, 6), round(g.nodos[n].lon, 6)] for n in r.nodos],
    }


def guardar_ruta(conn, metodo: str, rango: int, s: int, t: int, ruta: dict, preferencias: dict) -> int:
    wkt = "LINESTRING(" + ", ".join(f"{lon} {lat}" for lat, lon in ruta["coordenadas"]) + ")"
    return conn.execute(
        """INSERT INTO rutas (metodo, rango, origen, destino, largo_km, costo, riesgo_medio, aristas, preferencias, geom)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
           RETURNING id""",
        (metodo, rango, s, t, ruta["largo_km"], ruta["costo"], ruta["riesgo_medio"], ruta["aristas"],
         Jsonb(preferencias), wkt),
    ).fetchone()[0]

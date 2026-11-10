"""Servicio de ruteo: lo usan el sitio web (POST /api/rutas, POST /api/flota) y BD/rutas_ejemplo.py.

Dado (origen, destino) y las preferencias del usuario (o las por defecto):
1. Reconstruye el grafo desde la BD y aplica las restricciones duras.
2. Línea base: 2 rutas con pgr_dijkstra, solo por km (rúbrica 8).
3. Propuesta: pgr_KSP + selección resiliente del par (rúbrica 9).
4. Resiliencia de ambos pares sobre N escenarios de fallas y su diferencial (rúbrica 10 y 11.2).
5. Si guardar=True, deja las rutas y la evaluación en las tablas rutas y evaluaciones.

simular_flota: la misma misión con 3 a 5 UAV, sin aviso y con aviso compartido (ruteo/flota.py),
más la línea de tiempo de un escenario para animarlo en el mapa.

Tarea 3 (POST /api/t3/rutas y POST /api/t3/sorteo):
- resolver_t3: las cuatro técnicas (comun/tecnicas.py) con su tiempo de cómputo, fiabilidad y
  resiliencia sobre los mismos sorteos 0-100 (ruteo/resiliencia_t3.py).
- sortear_t3: un sorteo 0-100 con semilla, qué ruta sobrevive y cómo se recupera cada una.
"""
from __future__ import annotations

from dataclasses import asdict, replace

from psycopg.types.json import Jsonb

from comun import tecnicas
from comun.resiliencia import evaluar, focos_bd
from comun.rutas import (dijkstra_dos_rutas_pgr, elevacion_nodo, grafo_desde_bd, guardar_ruta,
                         propuesta_pgr, ruta_a_dict, viento_bd)
from ruteo import resiliencia_t3
from ruteo.algoritmos import Ruta
from ruteo.config import (SEMILLAS, Configuracion, Considerar, ParametrosACO, ParametrosAlgoritmo, ParametrosFallas,
                          ParametrosFlota, ParametrosResiliencia, Preferencias)
from ruteo.fallas import generar_escenario
from ruteo.flota import ESTRATEGIAS_FLOTA, ejecutar_flota, linea_de_tiempo
from ruteo.metricas import diferencial, resumir_flota, seguidores
from ruteo.modelo_t3 import TECNICAS, Instancia, ResultadoTecnica, largos_minimos
from ruteo.pesos import aristas_excluidas, costo_km, costo_propuesta, excluidas_con_motivo, mision_admisible, obstaculo_m
from ruteo.probabilidad import ZonaAmenaza, calcular
from ruteo.simulador import largo_minimo_mision
from ruteo.sorteo import sortear


def nodo_mas_cercano(conn, lat: float, lon: float) -> int:
    """Nodo más cercano a un clic en el mapa (índice espacial KNN de PostGIS)."""
    return conn.execute(
        "SELECT id FROM nodos ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) LIMIT 1", (lon, lat)
    ).fetchone()[0]


def _redondear(d: dict) -> dict:
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}


def resolver(conn, s: int, t: int, prefs: Preferencias = Preferencias(),
             params: ParametrosAlgoritmo = ParametrosAlgoritmo(),
             n_escenarios: int = 100, n_fallas: int = 3, guardar: bool = True) -> dict:
    if s == t:
        return {"error": "El origen y el destino son el mismo nodo."}
    elevacion = elevacion_nodo(conn, s)
    g = grafo_desde_bd(conn, elevacion)
    if s not in g.nodos or t not in g.nodos:
        return {"error": "Origen o destino fuera del grafo."}
    viento, viento_info = viento_bd(conn, prefs.altura_vuelo_m)
    excluidas = aristas_excluidas(g, prefs)
    salida: dict = {
        "origen": s,
        "destino": t,
        "preferencias": asdict(prefs),
        "parametros_algoritmo": asdict(params),
        "elevacion_origen_m": elevacion,
        "viento": viento_info,
        "aristas_excluidas": sorted(excluidas),
        "advertencias": [],
    }
    if not mision_admisible(viento, prefs):
        salida["advertencias"].append(
            f"Misión no admisible: viento de {viento.velocidad_m_s} m/s a la altura de vuelo supera el máximo "
            f"de {prefs.viento_max_m_s} m/s. Las rutas se muestran solo como referencia.")

    dijkstra = dijkstra_dos_rutas_pgr(conn, s, t, excluidas)
    if not dijkstra:
        salida["error"] = "No hay ruta admisible entre origen y destino con estas restricciones."
        return salida
    seleccion = propuesta_pgr(conn, g, s, t, prefs, params, viento, excluidas, dijkstra[0])
    par_propuesta = [seleccion.principal, seleccion.alternativa] if seleccion else []
    if len(dijkstra) < 2:
        salida["advertencias"].append("pgr_dijkstra solo encontró una ruta distinta.")
    if seleccion and seleccion.alternativa is None:
        salida["advertencias"].append("La propuesta solo encontró una ruta válida dentro del desvío y el presupuesto.")

    costo_p = costo_propuesta(g, prefs, viento)
    salida["dijkstra"] = [ruta_a_dict(g, r, costo_km(g)) for r in dijkstra]
    salida["propuesta"] = [ruta_a_dict(g, r, costo_p) for r in par_propuesta if r is not None]
    salida["seleccion"] = _redondear({"J": seleccion.puntaje, **seleccion.detalle}) if seleccion else None

    focos, origen_focos = focos_bd(conn, g)
    evaluacion = evaluar(g, s, t, prefs, viento, dijkstra, par_propuesta, focos, n_escenarios, n_fallas)
    evaluacion.update(origen_focos=origen_focos, n_focos=len(focos))
    salida["resiliencia"] = evaluacion

    if guardar and "error" not in evaluacion:
        for metodo, rutas in (("dijkstra", salida["dijkstra"]), ("propuesta", salida["propuesta"])):
            for rango, ruta in enumerate(rutas, start=1):
                ruta["id_bd"] = guardar_ruta(conn, metodo, rango, s, t, ruta, salida["preferencias"])
        dif = evaluacion["diferencial_C_vs_A"]
        salida["id_evaluacion"] = conn.execute(
            """INSERT INTO evaluaciones (origen, destino, n_escenarios, n_fallas, r_par_dijkstra, r_par_propuesta,
                   r_mision_dijkstra, r_mision_replan, r_mision_propuesta, delta_r_pp, p_mcnemar, parametros)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (s, t, evaluacion["n_escenarios"], n_fallas, evaluacion["r_par"]["dijkstra"],
             evaluacion["r_par"]["propuesta"], evaluacion["r_mision"]["A_dijkstra_fijo"],
             evaluacion["r_mision"]["D_dijkstra_replan"], evaluacion["r_mision"]["C_propuesta"],
             dif["delta_R_pp"], dif["p_mcnemar"],
             Jsonb({"preferencias": salida["preferencias"], "origen_focos": origen_focos})),
        ).fetchone()[0]
        conn.commit()
    return salida


def mision_bd(conn) -> list[int]:
    return [fila[0] for fila in conn.execute("SELECT nodo_id FROM mision ORDER BY orden")]


def simular_flota(conn, secuencia: list[int], prefs: Preferencias = Preferencias(),
                  flota: ParametrosFlota = ParametrosFlota(), n_fallas: int = 3, n_escenarios: int = 30,
                  semilla: int | None = None, sin_aviso: str = "D", con_aviso: str = "C_A") -> dict:
    """Compara la flota sin aviso y con aviso en N escenarios y devuelve uno animable.

    Si no se pide una semilla, se anima el primer escenario en que el aviso cambió alguna ruta en
    vuelo y la flota con aviso completó más misiones; el sitio lo rotula como elegido para ilustrar.
    """
    if len(set(secuencia)) != len(secuencia):
        return {"error": "La misión repite nodos (origen y destino iguales)."}
    g = grafo_desde_bd(conn, elevacion_nodo(conn, secuencia[0]))
    if any(n not in g.nodos for n in secuencia):
        return {"error": "Algún punto de la misión está fuera del grafo."}
    viento, viento_info = viento_bd(conn, prefs.altura_vuelo_m)
    excluidas = aristas_excluidas(g, prefs)
    largo_min = largo_minimo_mision(g, secuencia, excluidas)
    if largo_min is None:
        return {"error": "No hay ruta admisible para la misión con estas restricciones."}
    presupuesto = (1 + prefs.presupuesto_extra) * largo_min
    cfg = Configuracion(preferencias=prefs, fallas=replace(ParametrosFallas(), n_fallas=n_fallas), flota=flota)
    focos, origen_focos = focos_bd(conn, g)

    claves = [sin_aviso, "D_A", con_aviso] if con_aviso != "D_A" else [sin_aviso, con_aviso]
    nombres = {k: ESTRATEGIAS_FLOTA[k][2] for k in claves}
    resultados = {nombres[k]: [] for k in claves}
    escenarios = []
    for s in list(SEMILLAS["sitio"])[:n_escenarios]:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, secuencia, s)
        escenarios.append(esc)
        for k in claves:
            resultados[nombres[k]].append(ejecutar_flota(g, cfg, secuencia, esc, k, presupuesto, viento))

    sin, con = resultados[nombres[sin_aviso]], resultados[nombres[con_aviso]]
    if semilla is None:
        idx = next((i for i, (a, b) in enumerate(zip(sin, con))
                    if b.completadas > a.completadas and any(u.replan_por_aviso for u in b.uavs)),
                   next((i for i, b in enumerate(con) if any(u.replan_por_aviso for u in b.uavs)), 0))
        esc, r_sin, r_con = escenarios[idx], sin[idx], con[idx]
        motivo = "elegido para ilustrar el aviso" if any(u.replan_por_aviso for u in r_con.uavs) else "primero del conjunto"
    else:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, secuencia, semilla)
        r_sin = ejecutar_flota(g, cfg, secuencia, esc, sin_aviso, presupuesto, viento)
        r_con = ejecutar_flota(g, cfg, secuencia, esc, con_aviso, presupuesto, viento)
        motivo = "pedido"

    por_seguidor = seguidores(resultados)
    comparaciones = [(con_aviso, sin_aviso), ("D_A", sin_aviso), (con_aviso, "D_A")]
    v = prefs.velocidad_crucero_m_s
    salida = {
        "secuencia": secuencia,
        "preferencias": asdict(prefs),
        "flota": asdict(flota),
        "n_fallas": n_fallas,
        "viento": viento_info,
        "aristas_excluidas": len(excluidas),
        "largo_minimo_km": round(largo_min, 3),
        "presupuesto_km": round(presupuesto, 3),
        "origen_focos": origen_focos,
        "n_focos": len(focos),
        "n_escenarios": len(escenarios),
        "resumen": resumir_flota(resultados, largo_min, v),
        "diferenciales_seguidores": [diferencial(por_seguidor, nombres[m], nombres[r], largo_min)
                                     for m, r in comparaciones if m in nombres and r in nombres and m != r],
        "escenario_animado": {"semilla": esc.semilla, "motivo": motivo},
        "radio_silencio_km": cfg.algoritmo.radio_incertidumbre_km,
        "animacion": {"sin_aviso": linea_de_tiempo(g, r_sin, esc, v), "con_aviso": linea_de_tiempo(g, r_con, esc, v)},
        "advertencias": [],
    }
    if not mision_admisible(viento, prefs):
        salida["advertencias"].append(
            f"Misión no admisible: viento de {viento.velocidad_m_s} m/s supera el máximo de {prefs.viento_max_m_s} m/s. "
            "La simulación se muestra solo como referencia.")
    return salida


# ---------------------------------------------------------------------------
# Tarea 3: cuatro técnicas, probabilidad de falla, sorteo 0-100 y resiliencia
# ---------------------------------------------------------------------------

def preparar_t3(conn, secuencia: list[int], prefs: Preferencias, considerar: Considerar,
                zonas_prohibidas: list[list[tuple[float, float]]], zonas_amenaza: list[ZonaAmenaza]) -> dict:
    """Grafo sobrevolable, probabilidades combinadas y autonomía de una consulta (común a rutas y sorteo)."""
    if len(secuencia) < 2 or len(set(secuencia)) != len(secuencia):
        return {"error": "La misión necesita origen y destino distintos, sin repetir nodos."}
    g = grafo_desde_bd(conn, elevacion_nodo(conn, secuencia[0]))
    if any(n not in g.nodos for n in secuencia):
        return {"error": "Algún punto de la misión está fuera del grafo."}
    viento, viento_info = viento_bd(conn, prefs.altura_vuelo_m)
    prohibidas_xy = [[g.proy.a_xy(lat, lon) for lat, lon in z] for z in zonas_prohibidas if len(z) >= 3]
    motivos = excluidas_con_motivo(g, prefs, considerar, prohibidas_xy)
    prob = calcular(g, considerar.amenazas(), zonas_amenaza, obligatorios=secuencia)
    inst = Instancia(g, prefs, prob, frozenset(motivos), viento, considerar)
    umbral = prefs.altura_vuelo_m - prefs.margen_vertical_m
    excluidas = [{"id": aid, "motivo": m, "obstaculo_m": obstaculo_m(g.aristas[aid].atributos, considerar),
                  "umbral_m": umbral} for aid, m in sorted(motivos.items())]
    minimos = largos_minimos(inst, secuencia)
    if minimos is None:
        return {"error": "No hay ruta sobrevolable para la misión con estas restricciones (altura, relieve o zonas).",
                "excluidas": excluidas}
    largo_min = sum(minimos)
    autonomia = prefs.autonomia_km or (1 + prefs.presupuesto_extra) * largo_min
    advertencias = []
    if considerar.viento and not mision_admisible(viento, prefs):
        advertencias.append(f"Viento de {viento.velocidad_m_s} m/s a la altura de vuelo: supera el máximo de "
                            f"{prefs.viento_max_m_s} m/s. Las rutas se muestran solo como referencia.")
    if autonomia < largo_min - 1e-9:
        advertencias.append(f"La autonomía ({autonomia:.2f} km) no alcanza ni para la ruta más corta "
                            f"({largo_min:.2f} km): ninguna técnica puede cumplirla.")
    return {"g": g, "inst": inst, "motivos": motivos, "excluidas": excluidas, "viento_info": viento_info,
            "largo_min": largo_min, "autonomia": autonomia, "advertencias": advertencias}


def _tecnica_a_dict(inst: Instancia, res: ResultadoTecnica, autonomia: float, r_min: float) -> dict:
    g = inst.g
    d = {"clave": res.clave, "nombre": TECNICAS[res.clave], "tiempo_ms": res.tiempo_ms, "error": res.error,
         "detalle": res.detalle}
    if res.ruta is not None:
        d.update(inst.metricas(res.ruta, autonomia, r_min))
        d.update(nodos=res.ruta.nodos, aristas=res.ruta.aristas,
                 coordenadas=[[round(g.nodos[n].lat, 6), round(g.nodos[n].lon, 6)] for n in res.ruta.nodos])
    return d


def resolver_t3(conn, secuencia: list[int], prefs: Preferencias = Preferencias(), considerar: Considerar = Considerar(),
                zonas_prohibidas: list | None = None, zonas_amenaza: list[ZonaAmenaza] | None = None,
                params_aco: ParametrosACO = ParametrosACO(), res: ParametrosResiliencia = ParametrosResiliencia(),
                guardar: bool = True) -> dict:
    zonas_prohibidas, zonas_amenaza = zonas_prohibidas or [], zonas_amenaza or []
    n_sorteos = res.n_sorteos
    prep = preparar_t3(conn, secuencia, prefs, considerar, zonas_prohibidas, zonas_amenaza)
    if "error" in prep:
        return {"error": prep["error"], "excluidas": prep.get("excluidas", [])}
    g, inst, autonomia = prep["g"], prep["inst"], prep["autonomia"]
    r_min = prefs.prob_exito_min
    resultados = tecnicas.ejecutar(conn, inst, secuencia, autonomia, r_min, params_aco)
    lam = tecnicas.lambda_recuperacion(resultados["dijkstra_ponderado"])
    salida = {
        "secuencia": secuencia,
        "preferencias": asdict(prefs),
        "considerar": asdict(considerar),
        "autonomia_km": round(autonomia, 4),
        "largo_minimo_km": round(prep["largo_min"], 4),
        "r_min": r_min,
        "viento": prep["viento_info"],
        "excluidas": prep["excluidas"],
        "zonas_amenaza": [asdict(z) for z in zonas_amenaza],
        "n_zonas_prohibidas": len(zonas_prohibidas),
        "probabilidades": {"aristas": {a: round(p, 6) for a, p in inst.prob.aristas.items()},
                           "nodos": {n: round(p, 6) for n, p in inst.prob.nodos.items()},
                           "activas": list(inst.prob.activas)},
        "lambda_recuperacion_km": lam,
        "tecnicas": [_tecnica_a_dict(inst, r, autonomia, r_min) for r in resultados.values()],
        "advertencias": list(prep["advertencias"]),
    }
    for t in salida["tecnicas"]:
        if t["error"]:
            salida["advertencias"].append(f"{t['nombre']}: {t['error']}")
    if n_sorteos > 0:
        semillas = list(SEMILLAS["sorteos"])[:n_sorteos]
        ev = resiliencia_t3.evaluar(inst, secuencia, resultados, autonomia, semillas, inst.costo_lagrange(lam),
                                    res.prob_deteccion)
        salida["resiliencia"] = ev
        salida["mas_resiliente"] = ev["mas_resiliente"]
        for t in salida["tecnicas"]:
            t.update({k: v for k, v in ev["por_tecnica"].get(t["clave"], {}).items() if k != "fiabilidad"})
    if guardar:
        s, t = secuencia[0], secuencia[-1]
        for tec in salida["tecnicas"]:
            if "coordenadas" not in tec:
                continue
            ruta = {"coordenadas": tec["coordenadas"], "largo_km": tec["largo_km"], "costo": tec["objetivo_km_eq"],
                    "riesgo_medio": round(Ruta(tec["nodos"], tec["aristas"]).riesgo_medio(g), 4), "aristas": tec["aristas"]}
            tec["id_bd"] = guardar_ruta(conn, tec["clave"], 1, s, t, ruta, salida["preferencias"])
            conn.execute("UPDATE rutas SET tiempo_ms = %s, fiabilidad = %s, resiliencia = %s WHERE id = %s",
                         (tec["tiempo_ms"], tec["fiabilidad"], tec.get("resiliencia"), tec["id_bd"]))
        resumen = {tec["clave"]: {k: tec.get(k) for k in ("largo_km", "fiabilidad", "resiliencia", "tiempo_ms")}
                   for tec in salida["tecnicas"]}
        salida["id_evaluacion"] = conn.execute(
            """INSERT INTO evaluaciones_t3 (origen, destino, secuencia, n_sorteos, mas_resiliente, resultados, parametros)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (s, t, secuencia, n_sorteos, salida.get("mas_resiliente"), Jsonb(resumen),
             Jsonb({"preferencias": salida["preferencias"], "considerar": salida["considerar"],
                    "zonas_amenaza": salida["zonas_amenaza"], "zonas_prohibidas": zonas_prohibidas})),
        ).fetchone()[0]
        conn.commit()
    return salida


def ruta_desde_nodos(g, nodos: list[int], excluidas=frozenset()) -> Ruta | None:
    """Reconstruye una ruta enviada por el sitio (lista de nodos); None si no es un camino válido."""
    aristas = []
    for u, v in zip(nodos, nodos[1:]):
        aid = next((a for w, a in g.ady.get(u, []) if w == v and a not in excluidas), None)
        if aid is None:
            return None
        aristas.append(aid)
    return Ruta(list(nodos), aristas)


def partir(ruta: Ruta, secuencia: list[int]) -> list[Ruta]:
    """Divide una ruta en los tramos de la misión (de un punto obligatorio al siguiente)."""
    tramos, inicio, k = [], 0, 1
    for i, n in enumerate(ruta.nodos):
        if k < len(secuencia) and i > inicio and n == secuencia[k]:
            tramos.append(Ruta(ruta.nodos[inicio:i + 1], ruta.aristas[inicio:i]))
            inicio, k = i, k + 1
    return tramos if k == len(secuencia) else [ruta]


def sortear_t3(conn, secuencia: list[int], semilla: int, prefs: Preferencias = Preferencias(),
               considerar: Considerar = Considerar(), zonas_prohibidas: list | None = None,
               zonas_amenaza: list[ZonaAmenaza] | None = None, rutas_nodos: dict[str, list[int]] | None = None,
               lambda_km: float | None = None, params_aco: ParametrosACO = ParametrosACO(),
               prob_deteccion: float = ParametrosResiliencia().prob_deteccion) -> dict:
    """Punto 7: un sorteo 0-100 sobre todos los tramos y nodos, y qué le pasa a la ruta de cada técnica.

    El vuelo de cada ruta se simula igual que en la métrica de resiliencia (ruteo/resiliencia_t3.volar):
    nota la falla antes de entrar con probabilidad prob_deteccion y se desvía, o entra y se pierde.
    """
    prep = preparar_t3(conn, secuencia, prefs, considerar, zonas_prohibidas or [], zonas_amenaza or [])
    if "error" in prep:
        return {"error": prep["error"]}
    g, inst, autonomia = prep["g"], prep["inst"], prep["autonomia"]
    if rutas_nodos:
        resultados = {}
        for k, nodos in rutas_nodos.items():
            ruta = ruta_desde_nodos(g, nodos, inst.excluidas) if k in TECNICAS else None
            if ruta is not None:
                resultados[k] = ResultadoTecnica(k, ruta, partir(ruta, secuencia), 0.0, {})
    else:
        resultados = tecnicas.ejecutar(conn, inst, secuencia, autonomia, prefs.prob_exito_min, params_aco)
        lambda_km = tecnicas.lambda_recuperacion(resultados["dijkstra_ponderado"])
    lam = lambda_km if lambda_km is not None else 1.0
    sorteo = sortear(inst.prob, semilla)
    caidas = sorteo.caidas(g)
    por_tecnica, en_rutas_a, en_rutas_n = {}, set(), set()
    for k, res in resultados.items():
        if res.ruta is None:
            continue
        en_rutas_a.update(res.ruta.aristas)
        en_rutas_n.update(res.ruta.nodos)
        intacta = not (set(res.ruta.aristas) & caidas)
        vuelo = resiliencia_t3.volar(inst, secuencia, res.tramos, sorteo, autonomia, inst.costo_lagrange(lam),
                                     prob_deteccion)
        rec = {"exito": vuelo.exito, "motivo": vuelo.motivo, "km": vuelo.km, "replanificaciones": vuelo.replanificaciones,
               "perdido_en": vuelo.perdido_en, "desvios": vuelo.desvios,
               "coordenadas": None if intacta else [[round(g.nodos[n].lat, 6), round(g.nodos[n].lon, 6)]
                                                    for n in vuelo.recorrido]}
        por_tecnica[k] = {"nombre": TECNICAS[k], "intacta": intacta,
                          "primer_fallo": sorteo.primer_fallo(res.ruta.nodos, res.ruta.aristas), "recuperacion": rec}
    fall_a, fall_n = sorteo.aristas_falladas(), sorteo.nodos_fallados()
    return {
        "semilla": semilla,
        "regla": "falla si n > umbral, con n ~ U[0, 100) y umbral = 100 * (1 - p)",
        "prob_deteccion": prob_deteccion,
        "autonomia_km": round(autonomia, 4),
        "lambda_recuperacion_km": lam,
        "n_tramos": len(sorteo.aristas), "n_nodos": len(sorteo.nodos),
        "tramos_fallados": [{"id": a, **sorteo.aristas[a].a_dict()} for a in sorted(fall_a)],
        "nodos_fallados": [{"id": n, "lat": round(g.nodos[n].lat, 6), "lon": round(g.nodos[n].lon, 6),
                            **sorteo.nodos[n].a_dict()} for n in sorted(fall_n)],
        "tiradas_rutas": {"aristas": {a: sorteo.aristas[a].a_dict() for a in sorted(en_rutas_a)},
                          "nodos": {n: sorteo.nodos[n].a_dict() for n in sorted(en_rutas_n)}},
        "por_tecnica": por_tecnica,
        "advertencias": prep["advertencias"],
    }

"""Servicio de ruteo: lo usan el sitio web (POST /api/rutas) y BD/rutas_ejemplo.py.

Dado (origen, destino) y las preferencias del usuario (o las por defecto):
1. Reconstruye el grafo desde la BD y aplica las restricciones duras.
2. Línea base: 2 rutas con pgr_dijkstra, solo por km (rúbrica 8).
3. Propuesta: pgr_KSP + selección resiliente del par (rúbrica 9).
4. Resiliencia de ambos pares sobre N escenarios de fallas y su diferencial (rúbrica 10 y 11.2).
5. Si guardar=True, deja las rutas y la evaluación en las tablas rutas y evaluaciones.
"""
from __future__ import annotations

from dataclasses import asdict

from psycopg.types.json import Jsonb

from comun.resiliencia import evaluar, focos_bd
from comun.rutas import (dijkstra_dos_rutas_pgr, elevacion_nodo, grafo_desde_bd, guardar_ruta,
                         propuesta_pgr, ruta_a_dict, viento_bd)
from ruteo.config import ParametrosAlgoritmo, Preferencias
from ruteo.pesos import aristas_excluidas, costo_km, costo_propuesta, mision_admisible


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


def resolver_mision(conn, secuencia: list[int], prefs: Preferencias = Preferencias(),
                   params: ParametrosAlgoritmo = ParametrosAlgoritmo(),
                   n_escenarios: int = 100, n_fallas: int = 3, guardar: bool = True) -> dict:
    """Calcula cada tramo obligatorio y evalúa la misión completa, sin saltar observaciones."""
    if len(secuencia) < 2 or len(set(secuencia)) != len(secuencia):
        return {"error": "La misión debe contener puntos distintos en un orden definido."}
    s, t = secuencia[0], secuencia[-1]
    elevacion = elevacion_nodo(conn, s)
    g = grafo_desde_bd(conn, elevacion)
    if any(n not in g.nodos for n in secuencia):
        return {"error": "Algún punto de la misión no existe en el grafo."}
    viento, viento_info = viento_bd(conn, prefs.altura_vuelo_m)
    excluidas = aristas_excluidas(g, prefs)
    costo_p = costo_propuesta(g, prefs, viento)
    costo_d = costo_km(g)
    salida: dict = {
        "modo": "mision", "origen": s, "destino": t, "secuencia_mision": secuencia,
        "preferencias": asdict(prefs), "parametros_algoritmo": asdict(params),
        "elevacion_origen_m": elevacion, "viento": viento_info,
        "aristas_excluidas": sorted(excluidas), "tramos": [], "advertencias": [],
    }
    if not mision_admisible(viento, prefs):
        salida["advertencias"].append(
            f"Misión no admisible: viento de {viento.velocidad_m_s} m/s a la altura de vuelo supera el máximo "
            f"de {prefs.viento_max_m_s} m/s. Las rutas se muestran solo como referencia.")

    pares_dijkstra: list[list] = []
    pares_propuesta: list[list] = []
    etiquetas = ["A"] + [f"P{i}" for i in range(1, len(secuencia) - 1)] + ["B"]
    for indice, (a, b) in enumerate(zip(secuencia, secuencia[1:])):
        dijkstra = dijkstra_dos_rutas_pgr(conn, a, b, excluidas)
        if not dijkstra:
            return {"error": f"No hay ruta admisible para el tramo {indice + 1}: {a} → {b}."}
        seleccion = propuesta_pgr(conn, g, a, b, prefs, params, viento, excluidas, dijkstra[0])
        propuesta = [r for r in (seleccion.principal, seleccion.alternativa) if r is not None] if seleccion else []
        pares_dijkstra.append(dijkstra)
        pares_propuesta.append(propuesta)
        if len(dijkstra) < 2:
            salida["advertencias"].append(f"El tramo {indice + 1} tiene una sola ruta Dijkstra distinta.")
        if len(propuesta) < 2:
            salida["advertencias"].append(f"El tramo {indice + 1} tiene menos de dos rutas propuestas válidas.")
        salida["tramos"].append({
            "numero": indice + 1, "origen": a, "destino": b,
            "etiqueta": f"{etiquetas[indice]} → {etiquetas[indice + 1]}",
            "dijkstra": [ruta_a_dict(g, r, costo_d) for r in dijkstra],
            "propuesta": [ruta_a_dict(g, r, costo_p) for r in propuesta],
            "seleccion": _redondear({"J": seleccion.puntaje, **seleccion.detalle}) if seleccion else None,
        })

    focos, origen_focos = focos_bd(conn, g)
    evaluacion = evaluar(g, s, t, prefs, viento, pares_dijkstra[0], pares_propuesta[0],
                        focos, n_escenarios, n_fallas, secuencia=secuencia,
                        pares_dijkstra=pares_dijkstra, pares_propuesta=pares_propuesta)
    evaluacion.update(origen_focos=origen_focos, n_focos=len(focos))
    salida["resiliencia"] = evaluacion

    if guardar and "error" not in evaluacion:
        for tramo in salida["tramos"]:
            for metodo in ("dijkstra", "propuesta"):
                for rango, ruta in enumerate(tramo[metodo], start=1):
                    ruta["id_bd"] = guardar_ruta(conn, metodo, rango, tramo["origen"], tramo["destino"],
                                                ruta, salida["preferencias"])
        dif = evaluacion["diferencial_C_vs_A"]
        salida["id_evaluacion"] = conn.execute(
            """INSERT INTO evaluaciones (origen, destino, n_escenarios, n_fallas, r_par_dijkstra, r_par_propuesta,
                   r_mision_dijkstra, r_mision_replan, r_mision_propuesta, delta_r_pp, p_mcnemar, parametros)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (s, t, evaluacion["n_escenarios"], n_fallas, evaluacion["r_par"]["dijkstra"],
             evaluacion["r_par"]["propuesta"], evaluacion["r_mision"]["A_dijkstra_fijo"],
             evaluacion["r_mision"]["D_dijkstra_replan"], evaluacion["r_mision"]["C_propuesta"],
             dif["delta_R_pp"], dif["p_mcnemar"],
             Jsonb({"modo": "mision", "secuencia_mision": secuencia,
                    "preferencias": salida["preferencias"], "origen_focos": origen_focos})),
        ).fetchone()[0]
        conn.commit()
    return salida

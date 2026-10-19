"""Métrica de resiliencia de k = 2 rutas y diferencial entre métodos (rúbrica 10 y 11.2).

Para un par (origen, destino) se generan N escenarios de fallas con semilla
(ruteo.fallas.generar_escenario: discos con radio y aparición diferida).

- R_par(método)  = fracción de escenarios en que al menos una de sus 2 rutas
                   no toca ninguna falla (calidad del par precalculado).
- R_mision(estr.) = fracción de escenarios en que el UAV llega al destino
                   dentro del presupuesto (1 + beta) * L*, descubriendo las
                   fallas en vuelo (ruteo.simulador). A = par Dijkstra fijo,
                   D = Dijkstra que replanifica (ablación), C = propuesta.
- Diferencial:   Delta R = R(C) - R(A) en puntos porcentuales, con la prueba
                 exacta de McNemar (los escenarios son los mismos: pareada).

Los focos de las fallas son incendios de guerra del período de evaluación
(posteriores a la fecha de corte), distintos de los que fijaron los pesos.
"""
from __future__ import annotations

from dataclasses import replace

from comun.ajustes import bbox
from ruteo.algoritmos import Ruta
from ruteo.config import SEMILLAS, Configuracion, ParametrosFallas, Preferencias
from ruteo.fallas import generar_escenario, generar_focos
from ruteo.grafo import Grafo
from ruteo.metricas import diferencial, mcnemar_exacta, tasa
from ruteo.pesos import Viento, aristas_excluidas
from ruteo.simulador import ESTRATEGIAS, ejecutar_mision, largo_minimo_mision

# En orden de preferencia; se usa la primera que tenga puntos dentro del AOI.
CONSULTAS_FOCOS = [
    ("incendios_guerra_evaluacion",
     "SELECT ST_Y(geom), ST_X(geom) FROM amz_incendios WHERE guerra AND periodo = 'evaluacion'"
     " AND geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)"),
    ("incendios_guerra_historicos",
     "SELECT ST_Y(geom), ST_X(geom) FROM amz_incendios WHERE guerra AND periodo = 'historico'"
     " AND geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)"),
    ("eventos_ucdp",
     "SELECT ST_Y(geom), ST_X(geom) FROM amz_eventos WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)"),
]


def focos_bd(conn, g: Grafo) -> tuple[list[tuple[float, float]], str]:
    """Focos de amenaza dentro del AOI, en km locales. Sin datos reales, focos sintéticos."""
    sur, oeste, norte, este = bbox(0.0)
    for origen, consulta in CONSULTAS_FOCOS:
        filas = conn.execute(consulta, (oeste, sur, este, norte)).fetchall()
        if filas:
            return [g.proy.a_xy(lat, lon) for lat, lon in filas], origen
    return generar_focos(g, ParametrosFallas().n_focos, semilla=8), "sinteticos"


def _alguna_libre(par: list[Ruta | None], afectadas: frozenset[int]) -> bool:
    return any(r is not None and not (set(r.aristas) & afectadas) for r in par)


def evaluar(g: Grafo, s: int, t: int, prefs: Preferencias, viento: Viento | None,
            par_dijkstra: list[Ruta | None], par_propuesta: list[Ruta | None],
            focos: list[tuple[float, float]], n_escenarios: int = 100, n_fallas: int = 3,
            prob_foco: float = 0.5) -> dict:
    cfg = Configuracion(preferencias=prefs,
                        fallas=replace(ParametrosFallas(), n_fallas=n_fallas, prob_foco=prob_foco))
    largo_min = largo_minimo_mision(g, [s, t], aristas_excluidas(g, prefs))
    if largo_min is None:
        return {"error": "No hay ruta admisible entre origen y destino."}
    presupuesto = (1 + prefs.presupuesto_extra) * largo_min
    estrategias = {k: ESTRATEGIAS[k]() for k in ("A", "D", "C")}
    resultados = {e.nombre: [] for e in estrategias.values()}
    libres_dij, libres_prop = [], []
    semillas = list(SEMILLAS["sitio"])[:n_escenarios]
    for semilla in semillas:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, [s, t], semilla)
        afectadas = esc.todas_afectadas()
        libres_dij.append(_alguna_libre(par_dijkstra, afectadas))
        libres_prop.append(_alguna_libre(par_propuesta, afectadas))
        for e in estrategias.values():
            resultados[e.nombre].append(ejecutar_mision(g, cfg, [s, t], esc, e, presupuesto, viento))

    nombre = {k: e.nombre for k, e in estrategias.items()}
    r_mision = {k: round(tasa([r.exito for r in resultados[nombre[k]]]), 4) for k in estrategias}
    gana_par = sum(1 for p, d in zip(libres_prop, libres_dij) if p and not d)
    pierde_par = sum(1 for p, d in zip(libres_prop, libres_dij) if d and not p)
    r_par_d, r_par_p = tasa(libres_dij), tasa(libres_prop)
    return {
        "n_escenarios": len(semillas),
        "n_fallas": n_fallas,
        "prob_foco": prob_foco,
        "semillas": [semillas[0], semillas[-1]] if semillas else [],
        "largo_minimo_km": round(largo_min, 3),
        "presupuesto_km": round(presupuesto, 3),
        "r_par": {"dijkstra": round(r_par_d, 4), "propuesta": round(r_par_p, 4)},
        "delta_r_par_pp": round(100 * (r_par_p - r_par_d), 2),
        "p_mcnemar_par": round(mcnemar_exacta(gana_par, pierde_par), 5),
        "r_mision": {"A_dijkstra_fijo": r_mision["A"], "D_dijkstra_replan": r_mision["D"],
                     "C_propuesta": r_mision["C"]},
        "diferencial_C_vs_A": diferencial(resultados, nombre["C"], nombre["A"], largo_min),
        "diferencial_C_vs_D": diferencial(resultados, nombre["C"], nombre["D"], largo_min),
    }

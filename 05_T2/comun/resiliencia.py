"""Métrica de resiliencia de k = 2 rutas y diferencial entre métodos (rúbrica 10 y 11.2).

Para un par (origen, destino) o una secuencia de puntos obligatorios se generan N escenarios de fallas con semilla
(ruteo.fallas.generar_escenario: discos con radio y aparición diferida).

- R_par(método)  = fracción de escenarios en que cada tramo conserva al menos
                   una de sus 2 rutas precalculadas libre de fallas. En una
                   consulta de un solo tramo coincide con la métrica original.
- R_mision(estr.) = fracción de escenarios en que el UAV visita los puntos
                   obligatorios en orden y llega al destino dentro del
                   presupuesto (1 + beta) * L*, descubriendo fallas en vuelo.
                   A = par Dijkstra fijo,
                   D = Dijkstra que replanifica (ablación), C = propuesta.
- Diferencial:   Delta R = R(C) - R(A) en puntos porcentuales, con la prueba
                 exacta de McNemar (los escenarios son los mismos: pareada).

Los focos de las fallas son incendios de guerra del período de evaluación
(posteriores a la fecha de corte), distintos de los que fijaron los pesos.
"""
from __future__ import annotations

from dataclasses import replace

from comun.ajustes import BUFFER_KM, bbox
from ruteo.algoritmos import Ruta
from ruteo.config import SEMILLAS, Configuracion, ParametrosFallas, Preferencias
from ruteo.fallas import generar_escenario, generar_focos
from ruteo.grafo import Grafo
from ruteo.metricas import diferencial, mcnemar_exacta, tasa
from ruteo.pesos import Viento, aristas_excluidas
from ruteo.simulador import ESTRATEGIAS, ejecutar_mision, largo_minimo_mision

# En orden de preferencia; se usa la primera que tenga puntos en la ventana de búsqueda.
# La ventana es el AOI + BUFFER_KM, la MISMA con que Amenazas/*.py filtró las descargas: si aquí se
# usara el AOI estricto, los focos que caen en el anillo del buffer serían invisibles y la primera
# consulta devolvería vacío, haciendo caer la selección al período histórico (ver focos_bd).
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
    """Focos de amenaza en el AOI + BUFFER_KM, en km locales. Sin datos reales, focos sintéticos.

    La ventana incluye el buffer a propósito: una falla centrada justo fuera del AOI igual alcanza
    tramos de la malla, y son los incendios del período de evaluación los que deben originar las
    fallas (PROPUESTA_TECNICA §2). Con el AOI estricto esa primera consulta puede quedar vacía y la
    evaluación terminaría usando los mismos incendios históricos que fijaron los pesos de riesgo.
    """
    sur, oeste, norte, este = bbox(BUFFER_KM)
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
            prob_foco: float = 0.5, *, secuencia: list[int] | None = None,
            pares_dijkstra: list[list[Ruta | None]] | None = None,
            pares_propuesta: list[list[Ruta | None]] | None = None) -> dict:
    """Evalúa un tramo o la misión completa con los mismos escenarios para todos los métodos.

    En una misión, R_par exige que cada tramo conserve al menos una alternativa libre.
    R_mision ejecuta la secuencia completa de puntos obligatorios.
    """
    secuencia = [s, t] if secuencia is None else secuencia
    pares_dijkstra = [par_dijkstra] if pares_dijkstra is None else pares_dijkstra
    pares_propuesta = [par_propuesta] if pares_propuesta is None else pares_propuesta
    if (len(secuencia) < 2 or secuencia[0] != s or secuencia[-1] != t
            or len(pares_dijkstra) != len(secuencia) - 1
            or len(pares_propuesta) != len(secuencia) - 1):
        raise ValueError("La secuencia y los pares de rutas deben cubrir los mismos tramos de misión.")
    cfg = Configuracion(preferencias=prefs,
                        fallas=replace(ParametrosFallas(), n_fallas=n_fallas, prob_foco=prob_foco))
    largo_min = largo_minimo_mision(g, secuencia, aristas_excluidas(g, prefs))
    if largo_min is None:
        return {"error": "No hay ruta admisible entre origen y destino."}
    presupuesto = (1 + prefs.presupuesto_extra) * largo_min
    estrategias = {k: ESTRATEGIAS[k]() for k in ("A", "D", "C")}
    resultados = {e.nombre: [] for e in estrategias.values()}
    libres_dij, libres_prop = [], []
    semillas = list(SEMILLAS["sitio"])[:n_escenarios]
    for semilla in semillas:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, secuencia, semilla)
        afectadas = esc.todas_afectadas()
        libres_dij.append(all(_alguna_libre(par, afectadas) for par in pares_dijkstra))
        libres_prop.append(all(_alguna_libre(par, afectadas) for par in pares_propuesta))
        for e in estrategias.values():
            resultados[e.nombre].append(ejecutar_mision(g, cfg, secuencia, esc, e, presupuesto, viento))

    nombre = {k: e.nombre for k, e in estrategias.items()}
    r_mision = {k: round(tasa([r.exito for r in resultados[nombre[k]]]), 4) for k in estrategias}
    gana_par = sum(1 for p, d in zip(libres_prop, libres_dij) if p and not d)
    pierde_par = sum(1 for p, d in zip(libres_prop, libres_dij) if d and not p)
    r_par_d, r_par_p = tasa(libres_dij), tasa(libres_prop)
    return {
        "secuencia_mision": secuencia,
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

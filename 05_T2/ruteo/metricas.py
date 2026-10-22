"""Métricas de resiliencia (rúbrica 10 y 11.2).

R_mision = misiones completadas dentro del presupuesto / misiones evaluadas
R_par    = tramos en que al menos una ruta del par precalculado queda libre
           de todas las fallas del escenario / tramos evaluados
Delta R  = R_metodo - R_referencia, en puntos porcentuales (pp)

La comparación es pareada (mismos escenarios), por eso se informa también la
prueba exacta de McNemar sobre los escenarios discordantes.
"""
from __future__ import annotations

from math import comb
from statistics import mean

from .algoritmos import Ruta
from .fallas import Escenario
from .flota import ResultadoFlota, km_a_s
from .simulador import ResultadoMision


def tasa(valores: list[bool]) -> float:
    return sum(valores) / len(valores) if valores else 0.0


def r_par(pares: list[tuple[Ruta | None, Ruta | None]], escenario: Escenario) -> float:
    afectadas = escenario.todas_afectadas()
    libres = []
    for par in pares:
        rutas = [r for r in par if r is not None]
        libres.append(any(not (set(r.aristas) & afectadas) for r in rutas))
    return tasa(libres)


def mcnemar_exacta(b: int, c: int) -> float:
    """p-valor bilateral exacto: b = solo el método gana, c = solo la referencia gana."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def resumir(resultados: dict[str, list[ResultadoMision]], largo_minimo_km: float) -> dict:
    """Resumen por estrategia: tasa de éxito, km y sobrelongitud entre misiones exitosas."""
    salida = {}
    for nombre, lista in resultados.items():
        exitosas = [r for r in lista if r.exito]
        fallidas = [r for r in lista if not r.exito]
        motivos: dict[str, int] = {}
        for r in fallidas:
            motivos[r.motivo] = motivos.get(r.motivo, 0) + 1
        salida[nombre] = {
            "n": len(lista),
            "R_mision": round(tasa([r.exito for r in lista]), 4),
            "km_medio_exitosas": round(mean(r.km for r in exitosas), 3) if exitosas else None,
            "sobrelongitud_media_exitosas": round(mean(r.km / largo_minimo_km - 1 for r in exitosas), 4) if exitosas else None,
            "replanificaciones_media": round(mean(r.replanificaciones for r in lista), 3) if lista else None,
            "fraccion_puntos_en_fallidas": round(mean(r.puntos_visitados / r.total_puntos for r in fallidas), 4) if fallidas else None,
            "tiempo_calculo_ms_medio": round(mean(r.tiempo_calculo_ms for r in lista), 2) if lista else None,
            "motivos_fallo": motivos,
        }
    return salida


def diferencial(resultados: dict[str, list[ResultadoMision]], metodo: str, referencia: str, largo_minimo_km: float) -> dict:
    m, r = resultados[metodo], resultados[referencia]
    gana = sum(1 for a, b in zip(m, r) if a.exito and not b.exito)
    pierde = sum(1 for a, b in zip(m, r) if b.exito and not a.exito)
    ambos = [(a, b) for a, b in zip(m, r) if a.exito and b.exito]
    rm, rr = tasa([x.exito for x in m]), tasa([x.exito for x in r])
    return {
        "metodo": metodo,
        "referencia": referencia,
        "delta_R_pp": round(100 * (rm - rr), 2),
        "delta_R_relativo": round((rm - rr) / rr, 4) if rr else None,
        "solo_metodo_completa": gana,
        "solo_referencia_completa": pierde,
        "p_mcnemar": round(mcnemar_exacta(gana, pierde), 5),
        # km extra del método frente a la referencia en misiones que ambos completan (comparación pareada)
        "km_extra_medio_pareado": round(mean(a.km - b.km for a, b in ambos), 3) if ambos else None,
        "km_extra_relativo_minimo": round(mean(a.km - b.km for a, b in ambos) / largo_minimo_km, 4) if ambos else None,
    }


# ---------------------------------------------------------------- flota (ruteo/flota.py)
#
# R_uav        = misiones de UAV completadas / misiones de UAV (todos los UAV de todos los escenarios)
# R_seguidores = lo mismo, solo para los UAV 2..N: son los que pueden aprovechar un aviso
# R_flota      = escenarios en que al menos un UAV completa la inspección
# La prueba de McNemar se aplica sobre pares (escenario, UAV); los UAV de un mismo
# escenario no son independientes, así que el p-valor es orientativo.


def seguidores(resultados: dict[str, list[ResultadoFlota]]) -> dict[str, list[ResultadoMision]]:
    return {k: [u for r in v for u in r.uavs if u.indice > 0] for k, v in resultados.items()}


def todos_los_uav(resultados: dict[str, list[ResultadoFlota]]) -> dict[str, list[ResultadoMision]]:
    return {k: [u for r in v for u in r.uavs] for k, v in resultados.items()}


def resumir_flota(resultados: dict[str, list[ResultadoFlota]], largo_minimo_km: float,
                  velocidad_m_s: float) -> dict:
    salida = {}
    for nombre, lista in resultados.items():
        uavs = [u for r in lista for u in r.uavs]
        lideres = [u for u in uavs if u.indice == 0]
        resto = [u for u in uavs if u.indice > 0]
        exitosas = [u for u in uavs if u.exito]
        motivos: dict[str, int] = {}
        for u in uavs:
            if not u.exito:
                motivos[u.motivo] = motivos.get(u.motivo, 0) + 1
        # Demora desde el evento (detección o pérdida del UAV) hasta que cada otro UAV se entera.
        demoras = [km_a_s(t - a.t_evento_km, velocidad_m_s)
                   for r in lista for a in r.avisos for i, t in a.recepciones.items() if i != a.origen]
        por_tipo = {tipo: [km_a_s(t - a.t_evento_km, velocidad_m_s) for r in lista for a in r.avisos
                           if a.tipo == tipo for i, t in a.recepciones.items() if i != a.origen]
                    for tipo in ("deteccion", "silencio")}
        salida[nombre] = {
            "n_escenarios": len(lista),
            "R_uav": round(tasa([u.exito for u in uavs]), 4),
            "R_lider": round(tasa([u.exito for u in lideres]), 4),
            "R_seguidores": round(tasa([u.exito for u in resto]), 4),
            "R_flota_alguno": round(tasa([r.completadas > 0 for r in lista]), 4),
            "R_flota_todos": round(tasa([r.completadas == len(r.uavs) for r in lista]), 4),
            "perdidos_media": round(mean(r.perdidos for r in lista), 3),
            "avisos_media": round(mean(len(r.avisos) for r in lista), 3),
            "replan_por_aviso_media": round(mean(u.replan_por_aviso for u in uavs), 3),
            "replanificaciones_media": round(mean(u.replanificaciones for u in uavs), 3),
            "demora_aviso_media_s": round(mean(demoras), 2) if demoras else None,
            "demora_por_tipo_media_s": {k: round(mean(v), 2) if v else None for k, v in por_tipo.items()},
            "recepciones_inmediatas": round(tasa([d == 0 for d in demoras]), 4) if demoras else None,
            "km_medio_exitosas": round(mean(u.km for u in exitosas), 3) if exitosas else None,
            "sobrelongitud_media_exitosas": round(mean(u.km / largo_minimo_km - 1 for u in exitosas), 4) if exitosas else None,
            "tiempo_calculo_ms_medio": round(mean(u.tiempo_calculo_ms for u in uavs), 2) if uavs else None,
            "motivos_fallo": motivos,
        }
    return salida

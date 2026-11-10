"""Métrica de resiliencia de cada técnica de ruteo (Tarea 3, punto 8).

Sobre N sorteos 0-100 (ruteo/sorteo.py), LOS MISMOS para las cuatro técnicas (comparación pareada),
se simula el vuelo de la ruta de cada técnica:

- El UAV sigue su ruta. Antes de entrar a un tramo, o al nodo en que termina, que falló en el
  sorteo, lo nota con probabilidad p_det (mismo supuesto que la flota de la Tarea 2):
    * si lo nota, lo marca como caído y replanifica desde donde está con Dijkstra ponderado
      (costo c + lambda * l) sobre lo que sabe que sigue en pie;
    * si no lo nota, entra y se pierde (la falla del sistema ocurre con el UAV dentro).
  Si la nueva ruta no existe o se pasa de la autonomía, la misión fracasa.
- La decisión "lo nota / no lo nota" depende solo de la semilla y del elemento que falló, no de la
  técnica: dos técnicas que se topan con la misma falla viven lo mismo.

Métricas por técnica:
- Fiabilidad F = prod(1 - p) de tramos y nodos de la ruta (analítica).
- Intacta = fracción de sorteos sin ninguna falla en la ruta: debe acercarse a F (valida el sorteo).
- Resiliencia R (principal) = fracción de sorteos en que la misión se completa dentro de la
  autonomía. Suma lo que la ruta absorbe (no topa fallas) y lo que se recupera (las rodea).
La política de recuperación es la misma para todas, así que la diferencia de R se debe a la ruta
inicial que eligió cada técnica. Se informa además el diferencial frente a pgr_dijkstra en metros,
con la prueba exacta de McNemar sobre los sorteos discordantes.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from .algoritmos import Costo, Ruta, dijkstra
from .metricas import mcnemar_exacta, tasa
from .modelo_t3 import Instancia, ResultadoTecnica
from .sorteo import Sorteo, sortear

REFERENCIA = "dijkstra_m"
DESPLAZAMIENTO_NODO = 10_000_000  # separa las claves de nodos de las de tramos en la decisión de detección


def detecta(semilla: int, clave: int, p_det: float) -> bool:
    """¿El UAV nota esta falla antes de entrar? Determinista por (semilla, elemento)."""
    return random.Random(semilla * 1_000_003 + clave).random() < p_det


@dataclass
class Vuelo:
    exito: bool
    motivo: str                 # completada | perdido | sin_alternativa | autonomia | sin_ruta | bucle
    km: float
    replanificaciones: int
    detectadas: int
    recorrido: list[int]
    perdido_en: dict | None = None
    desvios: list[dict] = field(default_factory=list)  # dónde notó cada falla y se desvió


def volar(inst: Instancia, secuencia: list[int], tramos: list[Ruta], sorteo: Sorteo, autonomia_km: float,
          costo_reaccion: Costo, p_det: float) -> Vuelo:
    g = inst.g
    planes = {(r.nodos[0], r.nodos[-1]): r for r in tramos}
    pos, km, replans, notadas = secuencia[0], 0.0, 0, 0
    conocidas: set[int] = set()
    recorrido, desvios = [pos], []
    pasos, max_pasos = 0, 4 * len(g.nodos)

    def fin(exito: bool, motivo: str, perdido_en=None) -> Vuelo:
        return Vuelo(exito, motivo, round(km, 4), replans, notadas, recorrido, perdido_en, desvios)

    def replanificar(t: int) -> Ruta | None:
        return dijkstra(g, pos, t, costo_reaccion, set(inst.excluidas) | conocidas)

    for t in secuencia[1:]:
        plan = planes.get((pos, t)) or replanificar(t)
        if plan is None:
            return fin(False, "sin_ruta")
        i = 0
        while pos != t:
            pasos += 1
            if pasos > max_pasos:
                return fin(False, "bucle")
            aid, v = plan.aristas[i], plan.nodos[i + 1]
            falla_tramo, falla_nodo = sorteo.aristas[aid].falla, sorteo.nodos[v].falla
            if aid in conocidas or falla_tramo or falla_nodo:
                if aid not in conocidas:
                    tipo, ident = ("tramo", aid) if falla_tramo else ("nodo", v)
                    clave = aid if falla_tramo else DESPLAZAMIENTO_NODO + v
                    if not detecta(sorteo.semilla, clave, p_det):
                        return fin(False, "perdido", {"tipo": tipo, "id": ident, "desde_nodo": pos})
                    notadas += 1
                    conocidas.add(aid)
                    if falla_nodo:
                        conocidas.update(a for _, a in g.ady[v])
                    desvios.append({"tipo": tipo, "id": ident, "en_nodo": pos})
                plan = replanificar(t)
                replans += 1
                if plan is None:
                    return fin(False, "sin_alternativa")
                i = 0
                continue
            km += g.aristas[aid].largo_km
            pos = v
            i += 1
            recorrido.append(pos)
            if km > autonomia_km + 1e-9:
                return fin(False, "autonomia")
    return fin(True, "completada")


def evaluar(inst: Instancia, secuencia: list[int], resultados: dict[str, ResultadoTecnica],
            autonomia_km: float, semillas: list[int], costo_reaccion: Costo, p_det: float = 0.5) -> dict:
    t0 = time.perf_counter()
    g = inst.g
    rutas = {k: r for k, r in resultados.items() if r.ruta is not None}
    exitos: dict[str, list[bool]] = {k: [] for k in rutas}
    intactas = {k: 0 for k in rutas}
    recuperadas = {k: 0 for k in rutas}
    motivos: dict[str, dict[str, int]] = {k: {} for k in rutas}
    for semilla in semillas:
        sorteo = sortear(inst.prob, semilla)
        caidas = sorteo.caidas(g)
        for k, r in rutas.items():
            if not (set(r.ruta.aristas) & caidas):
                intactas[k] += 1
                ok = r.ruta.largo_km(g) <= autonomia_km + 1e-9
                exitos[k].append(ok)
                if not ok:
                    motivos[k]["autonomia"] = motivos[k].get("autonomia", 0) + 1
                continue
            vuelo = volar(inst, secuencia, r.tramos, sorteo, autonomia_km, costo_reaccion, p_det)
            exitos[k].append(vuelo.exito)
            if vuelo.exito:
                recuperadas[k] += 1
            else:
                motivos[k][vuelo.motivo] = motivos[k].get(vuelo.motivo, 0) + 1
    n = len(semillas)
    resumen = {k: {
        "resiliencia": round(tasa(exitos[k]), 4),
        "sin_recuperar": round(intactas[k] / n, 4) if n else None,
        "fiabilidad": round(inst.prob.fiabilidad(rutas[k].ruta.nodos, rutas[k].ruta.aristas), 4),
        "recuperadas": recuperadas[k],
        "motivos_fallo": motivos[k],
    } for k in rutas}
    mas = max(resumen, key=lambda k: (resumen[k]["resiliencia"], resumen[k]["fiabilidad"],
                                      -rutas[k].ruta.largo_km(g))) if resumen else None
    difs = {}
    if REFERENCIA in rutas:
        ref = exitos[REFERENCIA]
        for k in rutas:
            if k == REFERENCIA:
                continue
            gana = sum(1 for a, b in zip(exitos[k], ref) if a and not b)
            pierde = sum(1 for a, b in zip(exitos[k], ref) if b and not a)
            difs[k] = {"delta_R_pp": round(100 * (tasa(exitos[k]) - tasa(ref)), 2), "solo_tecnica_completa": gana,
                       "solo_dijkstra_m_completa": pierde, "p_mcnemar": round(mcnemar_exacta(gana, pierde), 5)}
    return {
        "n_sorteos": n,
        "semillas": [semillas[0], semillas[-1]] if semillas else [],
        "prob_deteccion": p_det,
        "por_tecnica": resumen,
        "mas_resiliente": mas,
        "diferencial_vs_dijkstra_m": difs,
        "politica_recuperacion": "Dijkstra ponderado (costo c + lambda * l) sobre lo que el UAV sabe que sigue en pie",
        "tiempo_ms": round(1000 * (time.perf_counter() - t0), 1),
    }

"""Simulación de misiones de inspección y estrategias comparadas.

Estrategias (PROPUESTA_TECNICA.md §6):
  A  dijkstra_fijo     Par Dijkstra-km calculado antes de salir; ante bloqueo
                       retrocede al último nodo común y toma la ruta 2.
  B  yen_fijo          Igual que A, pero el par son las 2 rutas más cortas de Yen.
  D  dijkstra_replan   Ablación: Dijkstra-km recalculado desde la posición
                       actual, solo quitando los tramos vistos bloqueados.
  C  propuesta         Yen + selección resiliente del par + replanificación
                       con penalización del entorno incierto del bloqueo y
                       control de presupuesto.
  C0 / C1              Ablaciones de C sin penalización del entorno / sin
                       control de presupuesto (v1 del diseño).

Reglas comunes: mismo grafo admisible, misión, escenario y presupuesto de km.
El UAV observa el estado de los tramos incidentes al nodo donde está; no
conoce fallas lejanas. Éxito = todos los puntos visitados en orden y destino
alcanzado con km recorridos <= presupuesto.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

from .algoritmos import Ruta, dijkstra, dijkstra_dos_rutas, seleccionar_par, yen
from .config import Configuracion
from .fallas import Escenario
from .grafo import Grafo
from .pesos import Viento, aristas_excluidas, costo_km, costo_propuesta


@dataclass
class Contexto:
    g: Grafo
    cfg: Configuracion
    viento: Viento | None
    excluidas: frozenset[int]
    conocidas: set[int] = field(default_factory=set)       # tramos vistos bloqueados
    penalizadas: dict[int, float] = field(default_factory=dict)
    evitar: set[int] = field(default_factory=set)          # zona avisada por silencio de otro UAV (ruteo/flota.py)
    presupuesto_km: float = math.inf
    km: float = 0.0        # recorridos hasta ahora
    cola_km: float = 0.0   # km mínimos de los tramos posteriores al objetivo actual

    @classmethod
    def nuevo(cls, g: Grafo, cfg: Configuracion, viento: Viento | None = None) -> "Contexto":
        return cls(g, cfg, viento, aristas_excluidas(g, cfg.preferencias))

    def no_transitables(self) -> set[int]:
        return set(self.excluidas) | self.conocidas | self.evitar

    def holgura_km(self) -> float:
        """km disponibles para llegar al objetivo actual sin comprometer el resto de la misión."""
        return self.presupuesto_km - self.km - self.cola_km


class Estrategia:
    nombre = "base"
    precalculada = False  # True: planifica toda la misión antes de salir, sin conocimiento

    def planificar(self, ctx: Contexto, s: int, t: int) -> tuple[Ruta | None, Ruta | None]:
        raise NotImplementedError

    def al_descubrir(self, ctx: Contexto, nuevas: list[int]) -> None:
        pass

    def reaccionar(self, ctx: Contexto, pos: int, t: int, tramo: "EstadoTramo") -> Ruta | None:
        raise NotImplementedError


@dataclass
class EstadoTramo:
    principal: Ruta
    alternativa: Ruta | None
    nodos: list[int]       # recorridos en el tramo actual, desde su origen
    aristas: list[int]
    alternativa_usada: bool = False


class ParFijo(Estrategia):
    precalculada = True

    def reaccionar(self, ctx, pos, t, tramo):
        alt = tramo.alternativa
        if alt is None or tramo.alternativa_usada:
            return None
        tramo.alternativa_usada = True
        # Último nodo recorrido que también pertenece a la ruta alternativa (al menos el origen).
        en_alt = {n: i for i, n in enumerate(alt.nodos)}
        i_rec = max(i for i, n in enumerate(tramo.nodos) if n in en_alt)
        regreso_nodos = tramo.nodos[i_rec:][::-1]
        regreso_aristas = tramo.aristas[i_rec:][::-1]
        j = en_alt[tramo.nodos[i_rec]]
        nueva = Ruta(regreso_nodos + alt.nodos[j + 1:], regreso_aristas + alt.aristas[j:])
        if any(a in ctx.conocidas for a in nueva.aristas):
            return None
        return nueva


class DijkstraFijo(ParFijo):
    nombre = "A_dijkstra_fijo"

    def planificar(self, ctx, s, t):
        rutas = dijkstra_dos_rutas(ctx.g, s, t, costo_km(ctx.g), ctx.excluidas)
        return (rutas[0] if rutas else None), (rutas[1] if len(rutas) > 1 else None)


class YenFijo(ParFijo):
    nombre = "B_yen_fijo"

    def planificar(self, ctx, s, t):
        rutas = yen(ctx.g, s, t, 2, costo_km(ctx.g), ctx.excluidas)
        return (rutas[0] if rutas else None), (rutas[1] if len(rutas) > 1 else None)


class DijkstraReplan(Estrategia):
    nombre = "D_dijkstra_replan"

    def planificar(self, ctx, s, t):
        return dijkstra(ctx.g, s, t, costo_km(ctx.g), ctx.no_transitables()), None

    def reaccionar(self, ctx, pos, t, tramo):
        return dijkstra(ctx.g, pos, t, costo_km(ctx.g), ctx.no_transitables())


class Propuesta(Estrategia):
    nombre = "C_propuesta"

    def __init__(self, penalizar_entorno: bool = True, controlar_presupuesto: bool = True):
        self.penalizar_entorno = penalizar_entorno
        self.controlar_presupuesto = controlar_presupuesto
        self._vecindad: dict[int, list[int]] = {}
        if not penalizar_entorno:
            self.nombre = "C0_propuesta_sin_entorno"
        elif not controlar_presupuesto:
            self.nombre = "C1_propuesta_sin_control_presupuesto"

    def _costo(self, ctx: Contexto):
        return costo_propuesta(ctx.g, ctx.cfg.preferencias, ctx.viento, ctx.penalizadas)

    def planificar(self, ctx, s, t):
        bloq = ctx.no_transitables()
        candidatas = yen(ctx.g, s, t, ctx.cfg.algoritmo.k_candidatas, self._costo(ctx), bloq)
        if not candidatas:
            return None, None
        mas_corta = dijkstra(ctx.g, s, t, costo_km(ctx.g), bloq)
        if mas_corta.clave() not in {r.clave() for r in candidatas}:
            candidatas.append(mas_corta)
        if self.controlar_presupuesto:
            caben = [r for r in candidatas if r.largo_km(ctx.g) <= ctx.holgura_km()]
            candidatas = caben or [mas_corta]
        sel = seleccionar_par(ctx.g, candidatas, mas_corta.largo_km(ctx.g), self._costo(ctx),
                              ctx.cfg.preferencias, ctx.cfg.algoritmo)
        return sel.principal, sel.alternativa

    def _vecinas(self, ctx: Contexto, aid: int) -> list[int]:
        if aid not in self._vecindad:
            rho2 = ctx.cfg.algoritmo.radio_incertidumbre_km ** 2
            mx, my = ctx.g.punto_medio_xy(aid)
            self._vecindad[aid] = [
                b for b in ctx.g.aristas
                if (ctx.g.punto_medio_xy(b)[0] - mx) ** 2 + (ctx.g.punto_medio_xy(b)[1] - my) ** 2 <= rho2
            ]
        return self._vecindad[aid]

    def al_descubrir(self, ctx, nuevas):
        if not self.penalizar_entorno:
            return
        factor = 1 + ctx.cfg.algoritmo.penalizacion_incertidumbre
        for aid in nuevas:
            for b in self._vecinas(ctx, aid):
                ctx.penalizadas[b] = factor

    def reaccionar(self, ctx, pos, t, tramo):
        bloq = ctx.no_transitables()
        ruta = dijkstra(ctx.g, pos, t, self._costo(ctx), bloq)
        if ruta is not None and self.controlar_presupuesto and ruta.largo_km(ctx.g) > ctx.holgura_km():
            # El desvío prudente no cabe en la holgura: se prioriza completar la misión.
            ruta = dijkstra(ctx.g, pos, t, costo_km(ctx.g), bloq)
        return ruta


ESTRATEGIAS = {
    "A": DijkstraFijo,
    "B": YenFijo,
    "C": Propuesta,
    "C0": lambda: Propuesta(penalizar_entorno=False),
    "C1": lambda: Propuesta(controlar_presupuesto=False),
    "D": DijkstraReplan,
}


@dataclass
class ResultadoMision:
    estrategia: str
    exito: bool
    motivo: str
    km: float
    replanificaciones: int
    puntos_visitados: int
    total_puntos: int
    tiempo_calculo_ms: float
    recorrido: list[int]


def ejecutar_mision(
    g: Grafo,
    cfg: Configuracion,
    secuencia: list[int],
    escenario: Escenario,
    estrategia: Estrategia,
    presupuesto_km: float,
    viento: Viento | None = None,
) -> ResultadoMision:
    ctx = Contexto.nuevo(g, cfg, viento)
    ctx.presupuesto_km = presupuesto_km
    tramos_min = [dijkstra(g, s, t, costo_km(g), ctx.excluidas) for s, t in zip(secuencia, secuencia[1:])]
    tramos_min = [r.largo_km(g) if r else math.inf for r in tramos_min]
    pos, km, replans = secuencia[0], 0.0, 0
    recorrido = [pos]
    calculo = 0.0
    max_pasos = 20 * len(g.nodos)
    pasos = 0

    def cronometrar(fn, *args):
        nonlocal calculo
        t0 = time.perf_counter()
        r = fn(*args)
        calculo += time.perf_counter() - t0
        return r

    planes = None
    if estrategia.precalculada:
        planes = [cronometrar(estrategia.planificar, ctx, s, t) for s, t in zip(secuencia, secuencia[1:])]

    def terminar(exito: bool, motivo: str, visitados: int) -> ResultadoMision:
        return ResultadoMision(estrategia.nombre, exito, motivo, round(km, 4), replans, visitados,
                               len(secuencia) - 1, round(calculo * 1000, 2), recorrido)

    for idx, t in enumerate(secuencia[1:]):
        ctx.cola_km = sum(tramos_min[idx + 1:])
        principal, alternativa = planes[idx] if planes else cronometrar(estrategia.planificar, ctx, pos, t)
        if principal is None:
            return terminar(False, "sin_ruta", idx)
        tramo = EstadoTramo(principal, alternativa, [pos], [])
        plan, k = principal, 0
        while pos != t:
            pasos += 1
            if pasos > max_pasos:
                return terminar(False, "bucle", idx)
            nuevas = [aid for _, aid in g.ady[pos] if aid not in ctx.conocidas and escenario.bloqueada(aid, km)]
            if nuevas:
                ctx.conocidas.update(nuevas)
                estrategia.al_descubrir(ctx, nuevas)
            aid = plan.aristas[k]
            if aid in ctx.conocidas:
                plan = cronometrar(estrategia.reaccionar, ctx, pos, t, tramo)
                replans += 1
                if plan is None:
                    # Atrapado: la falla se activó con el UAV dentro de su radio y cerró todas sus salidas.
                    atrapado = all(a in ctx.conocidas for _, a in g.ady[pos])
                    return terminar(False, "atrapado" if atrapado else "sin_alternativa", idx)
                k = 0
                continue
            km += g.aristas[aid].largo_km
            ctx.km = km
            pos = plan.nodos[k + 1]
            k += 1
            recorrido.append(pos)
            tramo.nodos.append(pos)
            tramo.aristas.append(aid)
            if km > presupuesto_km + 1e-9:
                return terminar(False, "presupuesto", idx)
    return terminar(True, "completada", len(secuencia) - 1)


def largo_minimo_mision(g: Grafo, secuencia: list[int], bloqueadas=frozenset()) -> float | None:
    """Suma de caminos mínimos en km entre puntos consecutivos (None si algún tramo es imposible)."""
    total = 0.0
    for s, t in zip(secuencia, secuencia[1:]):
        r = dijkstra(g, s, t, costo_km(g), bloqueadas)
        if r is None:
            return None
        total += r.largo_km(g)
    return total

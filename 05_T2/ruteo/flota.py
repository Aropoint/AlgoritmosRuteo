"""Flota de UAV con aviso compartido de interferencia y cambio de ruta en tiempo real.

Retoma la idea de la reunión con el profesor y de CLUN-LSR: cuando un UAV
detecta interferencia, avisa al resto, y los demás cambian su ruta en ese
momento, antes de llegar a la zona.

Modelo (abstracto, de simulación):
- N UAV (3 a 5) hacen la misma misión A -> P1 -> ... -> B. Salen de A cada
  `separacion_km` y vuelan a la misma velocidad, así que el reloj se mide en km
  a velocidad de crucero (1 km = 1000 / v segundos).
- Las zonas de interferencia son las fallas de fallas.py y se activan con el
  reloj de la misión. Para el primer UAV, ese reloj coincide con sus km
  recorridos, por eso con un solo UAV se reproduce simulador.ejecutar_mision.
- Detección: al llegar a un nodo, el UAV revisa los tramos que salen de él; si
  alguno cruza una zona activa, la detecta en el borde (con prob_deteccion).
- Aviso por detección: si el UAV conserva enlace (no está rodeado por la zona),
  difunde de inmediato los tramos afectados. Como en CLUN-LSR, el aviso se
  retransmite de UAV en UAV, y por la estación en A, entre quienes están dentro
  de `alcance_com_km`; quien está fuera de alcance lo recibe al reconectarse.
- Aviso por silencio: un UAV que queda dentro de una zona deja de emitir su
  beacon. Tras `beacons_para_alerta` beacons perdidos, la flota marca el entorno
  de su última posición (radio rho) como zona a evitar si hay alternativa.
- Reacción en tiempo real: quien recibe el aviso incorpora los tramos (y su
  estrategia aplica su propia regla, p. ej. C penaliza el entorno). Si su ruta
  restante cruza lo avisado, replanifica en ese instante desde el nodo hacia el
  que vuela, sin esperar a toparse con el bloqueo.

Estrategias: A, D y C sin aviso (cada UAV aprende solo lo que ve) y D_A, C_A con
aviso. D_A - D mide el valor del aviso; C_A - D_A, lo que aporta encima la
selección resiliente de rutas.
"""
from __future__ import annotations

import heapq
import math
import random
import time
from dataclasses import dataclass, field
from itertools import count

from .algoritmos import Ruta, dijkstra
from .config import Configuracion
from .fallas import Escenario, aristas_en_disco
from .grafo import Grafo
from .pesos import Viento, costo_km
from .simulador import (Contexto, DijkstraFijo, DijkstraReplan, Estrategia, EstadoTramo, Propuesta,
                        ResultadoMision)

# clave -> (fábrica de la estrategia, comparte avisos, nombre en resultados)
ESTRATEGIAS_FLOTA = {
    "A": (DijkstraFijo, False, "A_dijkstra_fijo"),
    "D": (DijkstraReplan, False, "D_dijkstra_replan"),
    "C": (Propuesta, False, "C_propuesta"),
    "D_A": (DijkstraReplan, True, "D_A_dijkstra_replan_aviso"),
    "C_A": (Propuesta, True, "C_A_propuesta_aviso"),
}


def km_a_s(km: float, velocidad_m_s: float) -> float:
    return km * 1000.0 / velocidad_m_s


@dataclass
class Aviso:
    id: int
    tipo: str                    # deteccion | silencio
    origen: int                  # UAV que detectó, o UAV que quedó en silencio
    t_km: float                  # instante en que se emite
    nodo: int                    # posición informada
    bloqueadas: frozenset[int]   # tramos vistos bloqueados (deteccion)
    evitar: frozenset[int]       # entorno de la última posición (silencio)
    t_evento_km: float = 0.0     # detección, o pérdida del UAV (el silencio se declara después)
    recepciones: dict[int, float] = field(default_factory=dict)  # UAV -> instante de recepción


@dataclass
class ResultadoUAV(ResultadoMision):
    indice: int = 0
    lanzamiento_km: float = 0.0
    replan_por_aviso: int = 0
    avisos_recibidos: int = 0
    perdido: bool = False
    tiempos_km: list[float] = field(default_factory=list)  # instante de llegada a cada nodo de `recorrido`
    eventos: list[dict] = field(default_factory=list)


@dataclass
class ResultadoFlota:
    estrategia: str
    con_avisos: bool
    uavs: list[ResultadoUAV]
    avisos: list[Aviso]
    fin_km: float

    @property
    def completadas(self) -> int:
        return sum(u.exito for u in self.uavs)

    @property
    def perdidos(self) -> int:
        return sum(u.perdido for u in self.uavs)


@dataclass
class _UAV:
    indice: int
    ctx: Contexto
    lanzamiento_km: float
    pos: int
    estado: str = "espera"       # espera | volando | completada | fallida | perdido
    motivo: str = ""
    destino_idx: int = 0         # tramo de misión en curso: va de secuencia[i] a secuencia[i + 1]
    plan: Ruta | None = None
    k: int = 0                   # plan.nodos[k] = nodo actual, o al que vuela si está en un tramo
    tramo: EstadoTramo | None = None
    en_arista: tuple[int, int, int, float, float] | None = None  # (arista, desde, hacia, salida, llegada)
    plan_ignora_evitar: bool = False
    replans: int = 0
    replans_aviso: int = 0
    pasos: int = 0
    puntos: int = 0
    calculo_s: float = 0.0
    avisos: set[int] = field(default_factory=set)
    recorrido: list[int] = field(default_factory=list)
    tiempos: list[float] = field(default_factory=list)
    eventos: list[dict] = field(default_factory=list)


class SimuladorFlota:
    def __init__(self, g: Grafo, cfg: Configuracion, secuencia: list[int], escenario: Escenario,
                 estrategia: Estrategia, presupuesto_km: float, con_avisos: bool,
                 viento: Viento | None = None, nombre: str | None = None):
        self.g, self.cfg, self.sec, self.esc = g, cfg, secuencia, escenario
        self.estrategia, self.presupuesto, self.con_avisos = estrategia, presupuesto_km, con_avisos
        self.nombre = nombre or estrategia.nombre
        fl = cfg.flota
        self.timeout_km = fl.beacons_para_alerta * fl.intervalo_beacon_s * cfg.preferencias.velocidad_crucero_m_s / 1000
        self.max_pasos = 20 * len(g.nodos)
        self.base_xy = g.nodos[secuencia[0]].xy
        self.base_avisos: set[int] = set()
        self.avisos: list[Aviso] = []
        self._heap: list = []
        self._seq = count()
        self._deteccion: dict[tuple[int, int], bool] = {}
        self.uavs = []
        for i in range(fl.n_uav):
            ctx = Contexto.nuevo(g, cfg, viento)
            ctx.presupuesto_km = presupuesto_km
            self.uavs.append(_UAV(i, ctx, i * fl.separacion_km, secuencia[0]))
        excl = self.uavs[0].ctx.excluidas
        minimos = [dijkstra(g, s, t, costo_km(g), excl) for s, t in zip(secuencia, secuencia[1:])]
        self.tramos_min = [r.largo_km(g) if r else math.inf for r in minimos]
        self.planes = None
        if estrategia.precalculada:
            t0 = time.perf_counter()
            ctx0 = Contexto.nuevo(g, cfg, viento)
            self.planes = [estrategia.planificar(ctx0, s, t) for s, t in zip(secuencia, secuencia[1:])]
            dt = time.perf_counter() - t0
            for u in self.uavs:
                u.calculo_s += dt  # cada UAV calcularía su propio par antes de salir

    # ---------------------------------------------------------------- bucle de eventos
    def ejecutar(self) -> ResultadoFlota:
        for u in self.uavs:
            self._programar(u.lanzamiento_km, 0, "nodo", u.indice)
        t = 0.0
        while self._heap:
            t, _, _, tipo, i, dato = heapq.heappop(self._heap)
            if tipo == "nodo":
                self._en_nodo(self.uavs[i], t)
            elif tipo == "silencio":
                self._aviso_por_silencio(self.uavs[i], dato, t)
            if self.con_avisos:
                self._difundir(t)
        return self._resultado(t)

    def _programar(self, t: float, prioridad: int, tipo: str, i: int, dato=None) -> None:
        heapq.heappush(self._heap, (t, prioridad, next(self._seq), tipo, i, dato))

    # ---------------------------------------------------------------- movimiento de un UAV
    def _en_nodo(self, u: _UAV, t: float) -> None:
        nuevo_tramo = False
        if u.estado == "espera":
            u.estado = "volando"
            u.recorrido.append(u.pos)
            u.tiempos.append(t)
            u.eventos.append({"t_km": t, "tipo": "despegue", "nodo": u.pos})
            nuevo_tramo = True
        else:
            aid, _, llegada, _, _ = u.en_arista
            u.en_arista = None
            u.pos = llegada
            u.recorrido.append(llegada)
            u.tiempos.append(t)
            u.tramo.nodos.append(llegada)
            u.tramo.aristas.append(aid)
        if u.pos == self.sec[u.destino_idx + 1]:
            u.destino_idx += 1
            u.puntos += 1
            if u.destino_idx == len(self.sec) - 1:
                self._terminar(u, t, "completada", "completada")
                return
            nuevo_tramo = True
        if nuevo_tramo:
            idx = u.destino_idx
            u.ctx.cola_km = sum(self.tramos_min[idx + 1:])
            ignora = False
            if self.planes:
                principal, alternativa = self.planes[idx]
            else:
                (principal, alternativa), ignora = self._planificar(u, u.pos, self.sec[idx + 1])
            if principal is None:
                self._terminar(u, t, "fallida", "sin_ruta")
                return
            u.tramo = EstadoTramo(principal, alternativa, [u.pos], [])
            u.plan, u.k, u.plan_ignora_evitar = principal, 0, ignora
            u.eventos.append({"t_km": t, "tipo": "plan", "nodo": u.pos, "nodos": principal.nodos})
        self._avanzar(u, t)

    def _avanzar(self, u: _UAV, t: float) -> None:
        g, ctx, esc = self.g, u.ctx, self.esc
        while True:
            u.pasos += 1
            if u.pasos > self.max_pasos:
                self._terminar(u, t, "fallida", "bucle")
                return
            incidentes = g.ady[u.pos]
            nuevas = [aid for _, aid in incidentes
                      if aid not in ctx.conocidas and esc.bloqueada(aid, t) and self._detecta(u, aid)]
            if nuevas:
                ctx.conocidas.update(nuevas)
                self.estrategia.al_descubrir(ctx, nuevas)
                u.eventos.append({"t_km": t, "tipo": "deteccion", "nodo": u.pos, "aristas": sorted(nuevas)})
                rodeado = all(esc.bloqueada(a, t) for _, a in incidentes)  # dentro de la zona: sin enlace
                if self.con_avisos and not rodeado:
                    self._emitir(u, t, "deteccion", frozenset(nuevas), frozenset())
            aid = u.plan.aristas[u.k]
            if aid in ctx.conocidas or (aid in ctx.evitar and not u.plan_ignora_evitar):
                ruta, ignora = self._reaccionar(u, u.pos)
                u.replans += 1
                if ruta is None:
                    if all(a in ctx.conocidas for _, a in incidentes):
                        self._perder(u, t, "atrapado")
                    else:
                        self._terminar(u, t, "fallida", "sin_alternativa")
                    return
                u.eventos.append({"t_km": t, "tipo": "replan", "nodo": u.pos, "nodos": ruta.nodos})
                u.plan, u.k, u.plan_ignora_evitar = ruta, 0, ignora
                continue
            if esc.bloqueada(aid, t):
                # Tramo bloqueado que no detectó: entra a la zona y pierde el enlace.
                self._perder(u, t, "perdido_en_interferencia")
                return
            largo = g.aristas[aid].largo_km
            ctx.km += largo
            siguiente = u.plan.nodos[u.k + 1]
            u.k += 1
            if ctx.km > self.presupuesto + 1e-9:
                self._terminar(u, t, "fallida", "presupuesto")
                return
            u.en_arista = (aid, u.pos, siguiente, t, t + largo)
            self._programar(t + largo, 0, "nodo", u.indice)
            return

    def _detecta(self, u: _UAV, aid: int) -> bool:
        p = self.cfg.flota.prob_deteccion
        if p >= 1:
            return True
        clave = (u.indice, aid)
        if clave not in self._deteccion:  # sorteo fijo por escenario, UAV y tramo: igual para todas las estrategias
            semilla = self.esc.semilla * 1_000_003 + u.indice * 10_007 + aid
            self._deteccion[clave] = random.Random(semilla).random() < p
        return self._deteccion[clave]

    def _con_respaldo(self, u: _UAV, calcular):
        """Calcula evitando la zona avisada por silencio; si así no hay ruta, la ignora.

        Devuelve (resultado, ignora_evitar)."""
        t0 = time.perf_counter()
        r = calcular()
        ignora = False
        sin_ruta = r is None or (isinstance(r, tuple) and r[0] is None)
        if sin_ruta and u.ctx.evitar:
            guardada, u.ctx.evitar = u.ctx.evitar, set()
            r = calcular()
            u.ctx.evitar = guardada
            ignora = True
        u.calculo_s += time.perf_counter() - t0
        return r, ignora

    def _planificar(self, u: _UAV, s: int, t_obj: int):
        return self._con_respaldo(u, lambda: self.estrategia.planificar(u.ctx, s, t_obj))

    def _reaccionar(self, u: _UAV, desde: int):
        objetivo = self.sec[u.destino_idx + 1]
        return self._con_respaldo(u, lambda: self.estrategia.reaccionar(u.ctx, desde, objetivo, u.tramo))

    def _terminar(self, u: _UAV, t: float, estado: str, motivo: str) -> None:
        u.estado, u.motivo = estado, motivo
        u.eventos.append({"t_km": t, "tipo": motivo, "nodo": u.pos})

    def _perder(self, u: _UAV, t: float, motivo: str) -> None:
        self._terminar(u, t, "perdido", motivo)
        if self.con_avisos:
            self._programar(t + self.timeout_km, 1, "silencio", u.indice, (u.pos, t))

    # ---------------------------------------------------------------- avisos
    def _emitir(self, u: _UAV, t: float, tipo: str, bloqueadas, evitar, conocen=None,
                t_evento: float | None = None) -> Aviso:
        aviso = Aviso(len(self.avisos), tipo, u.indice, t, u.pos, bloqueadas, evitar,
                      t if t_evento is None else t_evento)
        self.avisos.append(aviso)
        for i in (conocen if conocen is not None else [u.indice]):
            if i == "base":
                self.base_avisos.add(aviso.id)
            else:
                self.uavs[i].avisos.add(aviso.id)
                aviso.recepciones[i] = t
        if tipo == "deteccion":
            u.eventos.append({"t_km": t, "tipo": "aviso_enviado", "aviso": aviso.id})
        return aviso

    def _aviso_por_silencio(self, perdido: _UAV, dato: tuple[int, float], t: float) -> None:
        """Lo emiten quienes estaban en alcance de su última posición y dejaron de oír su beacon."""
        nodo, t_perdida = dato
        xy = self.g.nodos[nodo].xy
        oyentes = next(c for c in self._componentes(t, extra=xy) if "fantasma" in c) - {"fantasma"}
        if not oyentes:
            return
        rho = self.cfg.algoritmo.radio_incertidumbre_km
        zona = aristas_en_disco(self.g, xy[0], xy[1], rho)
        aviso = self._emitir(perdido, t, "silencio", frozenset(), zona, conocen=[], t_evento=t_perdida)
        for m in sorted(oyentes, key=str):
            if m == "base":
                self.base_avisos.add(aviso.id)
            else:
                self._recibir(self.uavs[m], aviso, t)

    def _posicion(self, u: _UAV, t: float) -> tuple[float, float]:
        if u.estado == "espera":
            return self.base_xy
        if u.en_arista is not None:
            _, a, b, t0, t1 = u.en_arista
            f = 0.0 if t1 <= t0 else min(max((t - t0) / (t1 - t0), 0.0), 1.0)
            (xa, ya), (xb, yb) = self.g.nodos[a].xy, self.g.nodos[b].xy
            return xa + f * (xb - xa), ya + f * (yb - ya)
        return self.g.nodos[u.pos].xy

    def _componentes(self, t: float, extra=None) -> list[set]:
        """Grupos conectados por radio (multisalto). La estación en A participa como relé."""
        miembros = [("base", self.base_xy)]
        miembros += [(u.indice, self._posicion(u, t)) for u in self.uavs if u.estado != "perdido"]
        if extra is not None:
            miembros.append(("fantasma", extra))
        alcance = self.cfg.flota.alcance_com_km
        padre = {m: m for m, _ in miembros}

        def raiz(x):
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x

        for i, (a, pa) in enumerate(miembros):
            for b, pb in miembros[i + 1:]:
                if alcance is None or math.dist(pa, pb) <= alcance:
                    padre[raiz(a)] = raiz(b)
        grupos: dict = {}
        for m, _ in miembros:
            grupos.setdefault(raiz(m), set()).add(m)
        return list(grupos.values())

    def _difundir(self, t: float) -> None:
        if not self.avisos:
            return
        for grupo in self._componentes(t):
            conocidos = set()
            for m in grupo:
                conocidos |= self.base_avisos if m == "base" else self.uavs[m].avisos
            for m in grupo:
                if m == "base":
                    self.base_avisos |= conocidos
                    continue
                u = self.uavs[m]
                for aid in sorted(conocidos - u.avisos):
                    self._recibir(u, self.avisos[aid], t)

    def _recibir(self, u: _UAV, aviso: Aviso, t: float) -> None:
        u.avisos.add(aviso.id)
        aviso.recepciones[u.indice] = t
        u.eventos.append({"t_km": t, "tipo": "aviso_recibido", "aviso": aviso.id, "de": aviso.origen,
                          "clase": aviso.tipo})
        if u.estado not in ("espera", "volando"):
            return  # solo retransmite
        ctx = u.ctx
        antes = set(ctx.penalizadas)
        nuevas = set(aviso.bloqueadas) - ctx.conocidas
        if nuevas:
            ctx.conocidas.update(nuevas)
            self.estrategia.al_descubrir(ctx, sorted(nuevas))
        nuevas_evitar = set(aviso.evitar) - ctx.evitar - ctx.conocidas
        ctx.evitar.update(nuevas_evitar)
        if u.estado == "volando":
            self._replanificar_en_vuelo(u, t, aviso, nuevas | nuevas_evitar | (set(ctx.penalizadas) - antes))

    def _replanificar_en_vuelo(self, u: _UAV, t: float, aviso: Aviso, afectadas: set[int]) -> None:
        """Cambio de ruta en tiempo real: no espera a llegar al bloqueo."""
        if u.en_arista is None or not afectadas:
            return
        hacia = u.en_arista[2]
        if hacia == self.sec[u.destino_idx + 1] or not (set(u.plan.aristas[u.k:]) & afectadas):
            return
        ruta, ignora = self._reaccionar(u, hacia)
        if ruta is None or ruta.clave() == tuple(u.plan.nodos[u.k:]):
            return
        u.plan, u.k, u.plan_ignora_evitar = ruta, 0, ignora
        u.replans += 1
        u.replans_aviso += 1
        u.eventos.append({"t_km": t, "tipo": "replan_aviso", "aviso": aviso.id, "desde": hacia,
                          "nodos": ruta.nodos})

    # ---------------------------------------------------------------- resultado
    def _resultado(self, fin_km: float) -> ResultadoFlota:
        salida = []
        for u in self.uavs:
            if u.estado in ("espera", "volando"):  # no debería ocurrir: el bucle termina cada UAV
                u.estado, u.motivo = "fallida", "inconclusa"
            salida.append(ResultadoUAV(
                self.nombre, u.estado == "completada", u.motivo, round(u.ctx.km, 4), u.replans, u.puntos,
                len(self.sec) - 1, round(u.calculo_s * 1000, 2), u.recorrido,
                indice=u.indice, lanzamiento_km=u.lanzamiento_km, replan_por_aviso=u.replans_aviso,
                avisos_recibidos=sum(1 for a in self.avisos if u.indice in a.recepciones and a.origen != u.indice),
                perdido=u.estado == "perdido", tiempos_km=u.tiempos, eventos=u.eventos))
        return ResultadoFlota(self.nombre, self.con_avisos, salida, self.avisos, fin_km)


def ejecutar_flota(g: Grafo, cfg: Configuracion, secuencia: list[int], escenario: Escenario, clave: str,
                   presupuesto_km: float, viento: Viento | None = None) -> ResultadoFlota:
    fabrica, con_avisos, nombre = ESTRATEGIAS_FLOTA[clave]
    sim = SimuladorFlota(g, cfg, secuencia, escenario, fabrica(), presupuesto_km, con_avisos, viento, nombre)
    return sim.ejecutar()


def linea_de_tiempo(g: Grafo, res: ResultadoFlota, escenario: Escenario, velocidad_m_s: float) -> dict:
    """Recorridos con marca de tiempo para animar la flota en el sitio (segundos desde el primer despegue)."""
    seg = lambda km: round(km_a_s(km, velocidad_m_s), 1)

    def punto(n: int) -> list[float]:
        return [round(g.nodos[n].lat, 6), round(g.nodos[n].lon, 6)]

    uavs = []
    for u in res.uavs:
        eventos = []
        for e in u.eventos:
            d = {k: v for k, v in e.items() if k not in ("t_km", "nodos", "aristas")}
            d["t_s"] = seg(e["t_km"])
            if "nodo" in e:
                d["pos"] = punto(e["nodo"])
            if "desde" in e:
                d["pos"] = punto(e["desde"])
            if "nodos" in e:
                d["ruta"] = [punto(n) for n in e["nodos"]]
            eventos.append(d)
        uavs.append({
            "indice": u.indice, "exito": u.exito, "motivo": u.motivo, "perdido": u.perdido, "km": u.km,
            "replanificaciones": u.replanificaciones, "replan_por_aviso": u.replan_por_aviso,
            "despegue_s": seg(u.lanzamiento_km),
            "trayectoria": [{"t_s": seg(t), "pos": punto(n)} for n, t in zip(u.recorrido, u.tiempos_km)],
            "eventos": eventos,
        })
    fallas = escenario.a_json(g)["fallas"]
    for f in fallas:
        f["inicio_s"] = seg(f["inicio_km"])
        f.pop("aristas", None)
    avisos = [{
        "id": a.id, "tipo": a.tipo, "origen": a.origen, "t_s": seg(a.t_km), "pos": punto(a.nodo),
        "recepciones": {str(i): seg(t) for i, t in sorted(a.recepciones.items())},
    } for a in res.avisos]
    return {"estrategia": res.estrategia, "con_avisos": res.con_avisos, "fin_s": seg(res.fin_km),
            "uavs": uavs, "avisos": avisos, "fallas": fallas}

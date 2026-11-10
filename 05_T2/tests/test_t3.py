"""Pruebas de la Tarea 3: probabilidad de falla, sorteo 0-100, las cuatro técnicas y la resiliencia.

Solo biblioteca estándar, salvo las del MILP, que se omiten si gurobipy no está instalado.
Ejecutar desde 05_T2:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ruteo.algoritmos import Ruta, dijkstra, distancias  # noqa: E402
from ruteo.config import Considerar, ParametrosACO, Preferencias  # noqa: E402
from ruteo.geo import ProyeccionLocal, punto_en_poligono, segmento_toca_poligono  # noqa: E402
from ruteo.grafo import Grafo  # noqa: E402
from ruteo.hormigas import aco  # noqa: E402
from ruteo.modelo_t3 import Instancia, lagrange, por_tramos  # noqa: E402
from ruteo.optimizacion import disponible, milp  # noqa: E402
from ruteo.pesos import excluidas_con_motivo, motivo_exclusion  # noqa: E402
from ruteo.probabilidad import (Probabilidades, ZonaAmenaza, calcular, combinar, log_supervivencia,  # noqa: E402
                                p_desde_tasa, umbral_falla)
from ruteo.resiliencia_t3 import evaluar  # noqa: E402
from ruteo.sorteo import sortear  # noqa: E402

LAT0, LON0 = 46.975, 31.995


def cuadricula(filas: int, columnas: int, paso_km: float = 1.0) -> Grafo:
    proy = ProyeccionLocal(LAT0, LON0)
    g = Grafo(proy)
    for f in range(filas):
        for c in range(columnas):
            lat, lon = proy.a_latlon(c * paso_km, f * paso_km)
            g.agregar_nodo(f * columnas + c, lat, lon)
    for f in range(filas):
        for c in range(columnas):
            u = f * columnas + c
            if c + 1 < columnas:
                g.agregar_arista(u, u + 1)
            if f + 1 < filas:
                g.agregar_arista(u, u + columnas)
    return g


def arista(g: Grafo, u: int, v: int) -> int:
    return next(a for w, a in g.ady[u] if w == v)


def instancia(g: Grafo, p_aristas: dict[int, float] | None = None, excluidas=frozenset()) -> Instancia:
    prob = Probabilidades({a: (p_aristas or {}).get(a, 0.0) for a in g.aristas}, {n: 0.0 for n in g.nodos})
    return Instancia(g, Preferencias(), prob, frozenset(excluidas), None, Considerar(viento=False))


def caminos(g: Grafo, s: int, t: int, excluidas=frozenset()):
    """Fuerza bruta: todos los caminos simples s-t como Ruta."""
    salida = []

    def dfs(nodos, aristas, vistos):
        u = nodos[-1]
        if u == t:
            salida.append(Ruta(list(nodos), list(aristas)))
            return
        for v, a in g.ady[u]:
            if v not in vistos and a not in excluidas:
                vistos.add(v)
                dfs(nodos + [v], aristas + [a], vistos)
                vistos.remove(v)

    dfs([s], [], {s})
    return salida


def optimo_restringido(inst: Instancia, s: int, t: int, autonomia: float, l_max: float) -> float | None:
    mejor = None
    for r in caminos(inst.g, s, t, inst.excluidas):
        km = r.largo_km(inst.g)
        l = sum(inst.l(a, r.nodos[i], r.nodos[i + 1]) for i, a in enumerate(r.aristas))
        if km <= autonomia + 1e-9 and l <= l_max + 1e-9:
            c = sum(inst.c(a, r.nodos[i], r.nodos[i + 1]) for i, a in enumerate(r.aristas))
            mejor = c if mejor is None else min(mejor, c)
    return mejor


class TestProbabilidad(unittest.TestCase):
    def test_tasa_y_combinacion(self):
        self.assertEqual(p_desde_tasa(0.0, 5.0), 0.0)
        self.assertLess(p_desde_tasa(0.1, 0.5), p_desde_tasa(0.1, 1.0))  # más largo, más expuesto
        self.assertAlmostEqual(combinar([0.1, 0.2]), 1 - 0.9 * 0.8)
        self.assertEqual(combinar([]), 0.0)
        self.assertAlmostEqual(math.exp(-(log_supervivencia(0.1) + log_supervivencia(0.2))), 0.9 * 0.8)
        self.assertEqual(umbral_falla(0.0), 100.0)
        self.assertEqual(umbral_falla(1.0), 0.0)

    def test_calcular_respeta_activas_zonas_y_obligatorios(self):
        g = cuadricula(1, 3)
        for a in g.aristas.values():
            a.atributos["pf"] = {"eventos": 0.1, "incendios": 0.2, "gnss": 0.0}
        for n in g.nodos.values():
            n.atributos["pf"] = {"eventos": 0.05, "incendios": 0.0, "gnss": 0.0}
        solo_eventos = calcular(g, ["eventos"])
        self.assertAlmostEqual(solo_eventos.aristas[0], 0.1)
        ambas = calcular(g, ["eventos", "incendios"])
        self.assertAlmostEqual(ambas.aristas[0], 1 - 0.9 * 0.8)
        # Zona de amenaza sobre el nodo 1: afecta a sus dos tramos y al nodo, y solo si se considera.
        lat, lon = g.nodos[1].lat, g.nodos[1].lon
        zona = [ZonaAmenaza(lat, lon, 0.2, 0.5)]
        con = calcular(g, ["zonas_usuario"], zona)
        self.assertAlmostEqual(con.aristas[0], 0.5)
        self.assertAlmostEqual(con.nodos[1], 0.5)
        self.assertEqual(calcular(g, [], zona).aristas[0], 0.0)
        self.assertEqual(calcular(g, ["eventos"], obligatorios=[0, 2]).nodos[0], 0.0)

    def test_fiabilidad_de_ruta(self):
        g = cuadricula(1, 3)
        prob = Probabilidades({0: 0.1, 1: 0.2}, {0: 0.0, 1: 0.5, 2: 0.0})
        self.assertAlmostEqual(prob.fiabilidad([0, 1, 2], [0, 1]), 0.9 * 0.8 * 0.5)
        self.assertAlmostEqual(prob.l_arco(0, 1), log_supervivencia(0.1) + log_supervivencia(0.5))


class TestGeometriaYExclusiones(unittest.TestCase):
    def test_poligono(self):
        cuadrado = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.assertTrue(punto_en_poligono((0.5, 0.5), cuadrado))
        self.assertFalse(punto_en_poligono((1.5, 0.5), cuadrado))
        self.assertTrue(segmento_toca_poligono((-1, 0.5), (2, 0.5), cuadrado))   # lo cruza sin vértices dentro
        self.assertFalse(segmento_toca_poligono((-1, 2), (2, 2), cuadrado))

    def test_motivo_respeta_considerar(self):
        prefs = Preferencias(altura_vuelo_m=60, margen_vertical_m=10)
        atributos = {"edificio_m": 45.0, "relieve_m": 8.0, "en_zona_restringida": False}
        self.assertEqual(motivo_exclusion(atributos, prefs), "edificio")                 # 53 >= 50
        self.assertIsNone(motivo_exclusion(atributos, prefs, Considerar(relieve=False)))  # 45 < 50
        self.assertEqual(motivo_exclusion({"edificio_m": None, "relieve_m": 55.0}, prefs), "relieve")
        self.assertEqual(motivo_exclusion({"en_zona_restringida": True}, prefs), "zona_publicada")
        self.assertIsNone(motivo_exclusion({"en_zona_restringida": True}, prefs, Considerar(zonas_publicadas=False)))

    def test_zona_prohibida_del_usuario(self):
        g = cuadricula(1, 3)
        zona = [(0.4, -0.2), (0.6, -0.2), (0.6, 0.2), (0.4, 0.2)]  # corta el tramo 0-1
        motivos = excluidas_con_motivo(g, Preferencias(), Considerar(), [zona])
        self.assertEqual(motivos, {arista(g, 0, 1): "zona_usuario"})
        self.assertEqual(excluidas_con_motivo(g, Preferencias(), Considerar(zonas_usuario=False), [zona]), {})


class TestSorteo(unittest.TestCase):
    def test_umbral_y_determinismo(self):
        prob = Probabilidades({0: 0.0, 1: 1.0, 2: 0.3}, {0: 0.0})
        a, b = sortear(prob, 123), sortear(prob, 123)
        self.assertEqual(a.aristas, b.aristas)
        self.assertFalse(a.aristas[0].falla)  # p = 0 nunca falla
        self.assertTrue(a.aristas[1].falla)   # p = 1 siempre falla
        t = a.aristas[2]
        self.assertEqual(t.falla, t.n > t.umbral)
        self.assertAlmostEqual(t.umbral, 70.0)

    def test_frecuencia_cercana_a_p(self):
        prob = Probabilidades({0: 0.25}, {})
        fallas = sum(sortear(prob, s).aristas[0].falla for s in range(4000))
        self.assertAlmostEqual(fallas / 4000, 0.25, delta=0.03)

    def test_nodo_caido_inutiliza_sus_tramos(self):
        g = cuadricula(1, 3)
        prob = Probabilidades({a: 0.0 for a in g.aristas}, {0: 0.0, 1: 1.0, 2: 0.0})
        self.assertEqual(sortear(prob, 1).caidas(g), frozenset(g.aristas))


class TestTecnicas(unittest.TestCase):
    """Cuadrícula 3 x 4 con un corredor corto riesgoso (fila de abajo) y desvíos seguros."""

    def setUp(self):
        self.g = cuadricula(3, 4)
        riesgo = {arista(self.g, 0, 1): 0.3, arista(self.g, 1, 2): 0.3, arista(self.g, 2, 3): 0.3}
        self.inst = instancia(self.g, riesgo)
        self.s, self.t = 0, 3

    def test_distancias_hacia_origen(self):
        d = distancias(self.g, self.t, self.inst.d, hacia_origen=True)
        self.assertAlmostEqual(d[self.s], 3.0, places=6)

    def test_lagrange_cumple_r_min(self):
        l_max = -math.log(0.9)
        r, det = lagrange(self.inst, self.s, self.t, 10.0, l_max)
        self.assertTrue(det["cumple_fiabilidad"])
        self.assertGreater(det["lambda_km"], 0)
        self.assertGreaterEqual(self.inst.prob.fiabilidad(r.nodos, r.aristas), 0.9 - 1e-9)
        r0, det0 = lagrange(self.inst, self.s, self.t, 10.0, -math.log(0.3))  # R_min holgado: lambda = 0
        self.assertEqual(det0["lambda_km"], 0.0)
        self.assertAlmostEqual(r0.largo_km(self.g), 3.0, places=6)

    def test_aco_camino_simple_determinista_y_optimo(self):
        l_max = -math.log(0.9)
        params = ParametrosACO(n_hormigas=20, iteraciones=40, semilla=3)
        r1, det1 = aco(self.inst, self.s, self.t, 10.0, l_max, params)
        r2, _ = aco(self.inst, self.s, self.t, 10.0, l_max, params)
        self.assertEqual(r1.nodos, r2.nodos)
        self.assertEqual(len(set(r1.nodos)), len(r1.nodos))
        self.assertEqual((r1.nodos[0], r1.nodos[-1]), (self.s, self.t))
        self.assertTrue(det1["factible"])
        optimo = optimo_restringido(self.inst, self.s, self.t, 10.0, l_max)
        costo = sum(self.inst.c(a, r1.nodos[i], r1.nodos[i + 1]) for i, a in enumerate(r1.aristas))
        self.assertAlmostEqual(costo, optimo, places=6)

    def test_por_tramos_con_punto_intermedio(self):
        res = por_tramos("x", self.inst, [0, 5, 3], 20.0, 0.5,
                         lambda s, t, b, l: (dijkstra(self.g, s, t, self.inst.d), {}))
        self.assertEqual(res.ruta.nodos[0], 0)
        self.assertIn(5, res.ruta.nodos)
        self.assertEqual(res.ruta.nodos[-1], 3)
        self.assertEqual(len(res.tramos), 2)

    @unittest.skipUnless(disponible(), "gurobipy no está instalado")
    def test_milp_igual_a_fuerza_bruta(self):
        for r_min, autonomia in ((0.9, 10.0), (0.5, 10.0), (0.9, 5.0)):
            l_max = -math.log(r_min)
            ruta, det = milp(self.inst, self.s, self.t, autonomia, l_max)
            optimo = optimo_restringido(self.inst, self.s, self.t, autonomia, l_max)
            with self.subTest(r_min=r_min, autonomia=autonomia):
                self.assertEqual(det["estado"], "óptimo")
                self.assertFalse(det["modelo_secundario"])
                self.assertAlmostEqual(det["objetivo"], optimo, places=6)
                self.assertLessEqual(det["n_variables"], det["limite_licencia"])
                self.assertEqual(len(set(ruta.nodos)), len(ruta.nodos))

    @unittest.skipUnless(disponible(), "gurobipy no está instalado")
    def test_milp_infactible_resuelve_maxima_fiabilidad(self):
        ruta, det = milp(self.inst, self.s, self.t, 3.0, -math.log(0.99))  # solo cabe el corredor riesgoso
        self.assertTrue(det["modelo_secundario"])
        self.assertAlmostEqual(ruta.largo_km(self.g), 3.0, places=6)

    @unittest.skipUnless(disponible(), "gurobipy no está instalado")
    def test_milp_sin_restricciones_igual_a_dijkstra(self):
        inst = instancia(self.g)
        ruta, det = milp(inst, self.s, self.t, 100.0, 100.0)
        self.assertAlmostEqual(det["objetivo"], dijkstra(self.g, self.s, self.t, inst.c).largo_km(self.g), places=6)


class TestResiliencia(unittest.TestCase):
    def setUp(self):
        from ruteo.modelo_t3 import ResultadoTecnica
        g = self.g = cuadricula(3, 4)
        riesgo = {arista(g, 0, 1): 0.5, arista(g, 1, 2): 0.5, arista(g, 2, 3): 0.5}
        self.inst = instancia(g, riesgo)
        self.corta = Ruta([0, 1, 2, 3], [arista(g, 0, 1), arista(g, 1, 2), arista(g, 2, 3)])
        segura = Ruta([0, 4, 5, 6, 7, 3], [arista(g, 0, 4), arista(g, 4, 5), arista(g, 5, 6),
                                           arista(g, 6, 7), arista(g, 7, 3)])
        self.res = {"dijkstra_m": ResultadoTecnica("dijkstra_m", self.corta, [self.corta], 0, {}),
                    "milp_gurobi": ResultadoTecnica("milp_gurobi", segura, [segura], 0, {})}

    def test_ruta_segura_es_mas_resiliente(self):
        ev = evaluar(self.inst, [0, 3], self.res, 8.0, list(range(300)), self.inst.costo_lagrange(5.0), p_det=0.5)
        r = ev["por_tecnica"]
        self.assertEqual(ev["mas_resiliente"], "milp_gurobi")
        self.assertEqual(r["milp_gurobi"]["resiliencia"], 1.0)
        self.assertAlmostEqual(r["dijkstra_m"]["sin_recuperar"], 0.125, delta=0.05)  # 0,5^3
        self.assertGreater(r["dijkstra_m"]["resiliencia"], r["dijkstra_m"]["sin_recuperar"])  # algunas se recuperan
        self.assertLess(r["dijkstra_m"]["resiliencia"], 1.0)                                  # y otras se pierden
        self.assertIn("perdido", r["dijkstra_m"]["motivos_fallo"])
        self.assertGreater(ev["diferencial_vs_dijkstra_m"]["milp_gurobi"]["delta_R_pp"], 0)

    def test_deteccion_perfecta_y_nula(self):
        semillas = list(range(200))
        siempre = evaluar(self.inst, [0, 3], self.res, 8.0, semillas, self.inst.costo_lagrange(5.0), p_det=1.0)
        nunca = evaluar(self.inst, [0, 3], self.res, 8.0, semillas, self.inst.costo_lagrange(5.0), p_det=0.0)
        self.assertEqual(siempre["por_tecnica"]["dijkstra_m"]["resiliencia"], 1.0)  # siempre ve la falla y la rodea
        r = nunca["por_tecnica"]["dijkstra_m"]
        self.assertEqual(r["resiliencia"], r["sin_recuperar"])                     # sin aviso, solo vuelve si queda intacta

    def test_volar_se_desvia_al_notar_la_falla(self):
        from ruteo.probabilidad import Probabilidades as P
        from ruteo.resiliencia_t3 import volar
        prob = P({a: (1.0 if a == arista(self.g, 1, 2) else 0.0) for a in self.g.aristas}, {n: 0.0 for n in self.g.nodos})
        inst = Instancia(self.g, Preferencias(), prob, frozenset(), None, Considerar(viento=False))
        v = volar(inst, [0, 3], [self.corta], sortear(prob, 7), 8.0, inst.costo_lagrange(1.0), p_det=1.0)
        self.assertTrue(v.exito)
        self.assertEqual(v.replanificaciones, 1)
        self.assertEqual(v.desvios[0]["en_nodo"], 1)
        perdido = volar(inst, [0, 3], [self.corta], sortear(prob, 7), 8.0, inst.costo_lagrange(1.0), p_det=0.0)
        self.assertEqual((perdido.exito, perdido.motivo), (False, "perdido"))


if __name__ == "__main__":
    unittest.main()

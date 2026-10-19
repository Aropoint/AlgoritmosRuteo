"""Pruebas del núcleo de ruteo. Ejecutar desde 05_T2:  python -m unittest discover -s tests -v"""
from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from itertools import count
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ruteo.algoritmos import Ruta, dijkstra, dijkstra_dos_rutas, seleccionar_par, solape_espacial, yen  # noqa: E402
from ruteo.config import Configuracion, ParametrosFallas, ParametrosMalla, Preferencias  # noqa: E402
from ruteo.fallas import Escenario, Falla, generar_escenario, generar_focos  # noqa: E402
from ruteo.geo import ProyeccionLocal, haversine_km  # noqa: E402
from ruteo.grafo import Grafo, generar_malla, nodos_mision  # noqa: E402
from ruteo.pesos import Viento, arista_admisible, costo_km, factor_viento  # noqa: E402
from ruteo.simulador import ESTRATEGIAS, ejecutar_mision, largo_minimo_mision  # noqa: E402

LAT0, LON0 = 46.975, 31.995


def grafo_cuadricula(filas: int, columnas: int, paso_km: float = 1.0, diagonales: bool = False) -> Grafo:
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
            if diagonales and f + 1 < filas and c + 1 < columnas:
                g.agregar_arista(u, u + columnas + 1)
    return g


def ruta_por_nodos(g: Grafo, nodos: list[int]) -> Ruta:
    aristas = [next(a for v, a in g.ady[u] if v == w) for u, w in zip(nodos, nodos[1:])]
    return Ruta(nodos, aristas)


def caminos_simples(g: Grafo, s: int, t: int) -> list[float]:
    """Fuerza bruta: longitudes de todos los caminos simples s-t."""
    largos = []

    def dfs(u, visitados, largo):
        if u == t:
            largos.append(largo)
            return
        for v, aid in g.ady[u]:
            if v not in visitados:
                visitados.add(v)
                dfs(v, visitados, largo + g.aristas[aid].largo_km)
                visitados.remove(v)

    dfs(s, {s}, 0.0)
    return sorted(largos)


class PruebasAlgoritmos(unittest.TestCase):
    def test_dijkstra_camino_minimo(self):
        g = grafo_cuadricula(3, 3)
        r = dijkstra(g, 0, 8, costo_km(g))
        self.assertAlmostEqual(r.largo_km(g), 4.0, places=2)
        self.assertEqual(r.nodos[0], 0)
        self.assertEqual(r.nodos[-1], 8)

    def test_dijkstra_respeta_bloqueos(self):
        g = grafo_cuadricula(1, 3)
        self.assertIsNone(dijkstra(g, 0, 2, costo_km(g), {0}))

    def test_yen_coincide_con_fuerza_bruta(self):
        g = grafo_cuadricula(3, 4, diagonales=True)
        k = 10
        rutas = yen(g, 0, 11, k, costo_km(g))
        esperados = caminos_simples(g, 0, 11)[:k]
        self.assertEqual(len(rutas), k)
        for r, e in zip(rutas, esperados):
            self.assertAlmostEqual(r.largo_km(g), e, places=6)
        self.assertEqual(len({r.clave() for r in rutas}), k, "rutas repetidas")
        for r in rutas:
            self.assertEqual(len(set(r.nodos)), len(r.nodos), "ruta con ciclo")

    def test_yen_devuelve_menos_si_no_hay_mas(self):
        g = grafo_cuadricula(1, 4)
        self.assertEqual(len(yen(g, 0, 3, 5, costo_km(g))), 1)

    def test_dijkstra_dos_rutas_disjuntas_en_aristas(self):
        g = grafo_cuadricula(3, 3)
        r1, r2 = dijkstra_dos_rutas(g, 0, 8, costo_km(g))
        self.assertFalse(set(r1.aristas) & set(r2.aristas))
        self.assertLessEqual(r1.largo_km(g), r2.largo_km(g))

    def test_solape_espacial(self):
        g = grafo_cuadricula(5, 5)
        abajo = dijkstra(g, 0, 4, costo_km(g))
        arriba = ruta_por_nodos(g, [0, 5, 10, 15, 20, 21, 22, 23, 24, 19, 14, 9, 4])
        self.assertAlmostEqual(solape_espacial(g, abajo, abajo, 0.4), 1.0)
        self.assertLess(solape_espacial(g, abajo, arriba, 0.4), 0.5)

    def test_seleccion_prefiere_corredor_separado(self):
        # Cuadrícula 5 x 6 (paso 0.5 km). r1 = fila inferior; r2 = desvío por la fila 1 (mismo corredor);
        # r3 = rodeo por la fila superior (corredor separado). El par elegido debe ser (r1, r3).
        g = grafo_cuadricula(5, 6, paso_km=0.5)
        r1 = ruta_por_nodos(g, [0, 1, 2, 3, 4, 5])
        r2 = ruta_por_nodos(g, [0, 6, 7, 8, 9, 10, 11, 5])
        r3 = ruta_por_nodos(g, [0, 6, 12, 18, 24, 25, 26, 27, 28, 29, 23, 17, 11, 5])
        params = replace(Configuracion().algoritmo, peso_longitud=0.5, d_separacion_km=0.6)
        sel = seleccionar_par(g, [r1, r2, r3], r1.largo_km(g), costo_km(g),
                              Preferencias(desvio_max=2.0, peso_riesgo=0.0), params)
        self.assertEqual(sel.principal.clave(), r1.clave())
        self.assertEqual(sel.alternativa.clave(), r3.clave())

    def test_seleccion_respeta_desvio_maximo(self):
        g = grafo_cuadricula(5, 6, paso_km=0.5)
        r1 = ruta_por_nodos(g, [0, 1, 2, 3, 4, 5])
        r3 = ruta_por_nodos(g, [0, 6, 12, 18, 24, 25, 26, 27, 28, 29, 23, 17, 11, 5])
        sel = seleccionar_par(g, [r1, r3], r1.largo_km(g), costo_km(g),
                              Preferencias(desvio_max=0.35), Configuracion().algoritmo)
        self.assertIsNone(sel.alternativa)  # r3 mide 2.6 veces r1: fuera del desvío permitido


class PruebasPesos(unittest.TestCase):
    def test_viento(self):
        g = grafo_cuadricula(1, 2)  # tramo 0 -> 1 hacia el este
        prefs = Preferencias()
        self.assertEqual(factor_viento(g, 0, 1, None, prefs), 1.0)
        self.assertGreater(factor_viento(g, 0, 1, Viento(6, 90), prefs), 1.0)  # viento desde el este: de frente
        self.assertLess(factor_viento(g, 0, 1, Viento(6, 270), prefs), 1.0)    # viento de cola

    def test_restricciones(self):
        prefs = Preferencias(altura_vuelo_m=60, margen_vertical_m=10)
        self.assertTrue(arista_admisible({}, prefs))
        self.assertTrue(arista_admisible({"altura_max_edificio_m": 30}, prefs))
        self.assertFalse(arista_admisible({"altura_max_edificio_m": 55}, prefs))
        self.assertFalse(arista_admisible({"en_zona_restringida": True}, prefs))
        self.assertTrue(arista_admisible({"en_zona_restringida": True}, Preferencias(respetar_zonas_restringidas=False)))


def escenario_manual(g: Grafo, fallas: list[tuple[set[int], float]]) -> Escenario:
    ids = count()
    lista, afectadas = [], {}
    for aristas, inicio in fallas:
        f = Falla(next(ids), 0, 0, 0.1, inicio)
        lista.append(f)
        afectadas[f.id] = frozenset(aristas)
    return Escenario(0, lista, afectadas)


class PruebasSimulador(unittest.TestCase):
    def setUp(self):
        self.g = grafo_cuadricula(3, 3)
        self.cfg = Configuracion()
        self.sec = [0, 8]

    def correr(self, clave, esc, presupuesto=100.0):
        return ejecutar_mision(self.g, self.cfg, self.sec, esc, ESTRATEGIAS[clave](), presupuesto)

    def test_sin_fallas_todas_completan(self):
        esc = escenario_manual(self.g, [])
        for clave in ESTRATEGIAS:
            r = self.correr(clave, esc)
            self.assertTrue(r.exito, clave)
            self.assertAlmostEqual(r.km, 4.0, places=2)

    def test_bloqueo_y_alternativas(self):
        ruta_a = dijkstra(self.g, 0, 8, costo_km(self.g))
        bloqueo = {ruta_a.aristas[-1]}  # se descubre recién en el penúltimo nodo
        esc = escenario_manual(self.g, [(bloqueo, 0.0)])
        a = self.correr("A", esc)
        d = self.correr("D", esc)
        self.assertTrue(a.exito)
        self.assertTrue(d.exito)
        self.assertGreaterEqual(a.replanificaciones, 1)
        self.assertLessEqual(d.km, a.km)  # D replanifica en el lugar; A retrocede

    def test_presupuesto(self):
        ruta_a = dijkstra(self.g, 0, 8, costo_km(self.g))
        esc = escenario_manual(self.g, [({ruta_a.aristas[-1]}, 0.0)])
        r = self.correr("A", esc, presupuesto=4.5)
        self.assertFalse(r.exito)
        self.assertEqual(r.motivo, "presupuesto")

    def test_atrapado(self):
        # El nodo central (4) queda aislado cuando el UAV ya está en él.
        g = self.g
        incidentes = {a for _, a in g.ady[4]}
        esc = escenario_manual(g, [(incidentes, 1.0 + 1e-6)])
        r = ejecutar_mision(g, self.cfg, [0, 4, 8], esc, ESTRATEGIAS["D"](), 100.0)
        self.assertFalse(r.exito)
        self.assertEqual(r.motivo, "atrapado")


class PruebasEscenario(unittest.TestCase):
    def test_fallas_reproducibles_y_sin_cubrir_puntos(self):
        cfg = Configuracion(malla=ParametrosMalla(espaciado_km=0.6))
        g = generar_malla(cfg.malla)
        self.assertTrue(g.conexo())
        sec = nodos_mision(g, cfg.mision)
        focos = generar_focos(g, 3, 1)
        params = ParametrosFallas(n_fallas=6, radio_max_km=0.8)
        largo = largo_minimo_mision(g, sec)
        e1 = generar_escenario(g, focos, params, largo, sec, 42)
        e2 = generar_escenario(g, focos, params, largo, sec, 42)
        self.assertEqual(e1.fallas, e2.fallas)
        for f in e1.fallas:
            for n in sec:
                x, y = g.nodos[n].xy
                self.assertGreater((x - f.x) ** 2 + (y - f.y) ** 2, f.radio_km ** 2)

    def test_largo_aristas_en_km(self):
        g = generar_malla(ParametrosMalla())
        a = next(iter(g.aristas.values()))
        nu, nv = g.nodos[a.u], g.nodos[a.v]
        self.assertAlmostEqual(a.largo_km, haversine_km(nu.lat, nu.lon, nv.lat, nv.lon))
        self.assertTrue(0.2 < a.largo_km < 1.2)


if __name__ == "__main__":
    unittest.main()

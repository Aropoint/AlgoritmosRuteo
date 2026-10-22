"""Pruebas de la flota con aviso compartido. Ejecutar desde 05_T2:  python -m unittest discover -s tests -v"""
from __future__ import annotations

import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ruteo.config import Configuracion, ParametrosFallas, ParametrosFlota, ParametrosMalla  # noqa: E402
from ruteo.fallas import generar_escenario, generar_focos  # noqa: E402
from ruteo.flota import ejecutar_flota, linea_de_tiempo  # noqa: E402
from ruteo.geo import ProyeccionLocal  # noqa: E402
from ruteo.grafo import Grafo, generar_malla, nodos_mision  # noqa: E402
from ruteo.simulador import ESTRATEGIAS, ejecutar_mision, largo_minimo_mision  # noqa: E402
from test_ruteo import LAT0, LON0, escenario_manual  # noqa: E402

A, W, X, B, Y, Z = range(6)


def grafo_desvio() -> Grafo:
    """Corredor corto A-W-X-B y desvío W-Y-Z-B (km):

        A --1-- W --1-- X --1-- B
                |               |
                1               1
                |               |
                Y ------2------ Z
    """
    proy = ProyeccionLocal(LAT0, LON0)
    g = Grafo(proy)
    for nid, (x, y) in enumerate([(0, 0), (1, 0), (2, 0), (3, 0), (1, -1), (3, -1)]):
        g.agregar_nodo(nid, *proy.a_latlon(x, y))
    for u, v in [(A, W), (W, X), (X, B), (W, Y), (Y, Z), (Z, B)]:
        g.agregar_arista(u, v)
    return g


def arista(g: Grafo, u: int, v: int) -> int:
    return next(a for w, a in g.ady[u] if w == v)


class PruebasFlota(unittest.TestCase):
    def setUp(self):
        self.g = grafo_desvio()
        self.sec = [A, B]
        self.bloqueo = escenario_manual(self.g, [({arista(self.g, X, B)}, 0.0)])

    def flota(self, clave, esc, **parametros):
        cfg = Configuracion(flota=ParametrosFlota(**parametros))
        return ejecutar_flota(self.g, cfg, self.sec, esc, clave, 100.0)

    def test_sin_fallas_todos_completan(self):
        for clave in ("A", "D", "C", "D_A", "C_A"):
            r = self.flota(clave, escenario_manual(self.g, []), n_uav=3, prob_deteccion=1.0)
            self.assertEqual(r.completadas, 3, clave)
            self.assertEqual(r.avisos, [], clave)
            for u in r.uavs:
                self.assertAlmostEqual(u.km, 3.0, places=1)

    def test_aviso_cambia_la_ruta_en_vuelo(self):
        # El líder detecta X-B en X (t = 2 km). El seguidor salió en t = 1,5 y va de A a W:
        # con aviso replanifica en el aire y toma W-Y-Z-B sin pasar por X.
        con = self.flota("D_A", self.bloqueo, n_uav=2, separacion_km=1.5, prob_deteccion=1.0)
        sin = self.flota("D", self.bloqueo, n_uav=2, separacion_km=1.5, prob_deteccion=1.0)
        lider, seguidor = con.uavs
        self.assertEqual(len(con.avisos), 1)
        aviso = con.avisos[0]
        self.assertEqual((aviso.tipo, aviso.origen, aviso.nodo), ("deteccion", 0, X))
        self.assertAlmostEqual(aviso.recepciones[1], aviso.t_km)  # inmediato
        self.assertTrue(seguidor.exito)
        self.assertEqual(seguidor.replan_por_aviso, 1)
        self.assertNotIn(X, seguidor.recorrido)
        self.assertAlmostEqual(seguidor.km, 5.0, places=1)
        # Sin aviso, el seguidor repite el error del líder: llega a X y retrocede.
        self.assertIn(X, sin.uavs[1].recorrido)
        self.assertAlmostEqual(sin.uavs[1].km, 7.0, places=1)
        self.assertAlmostEqual(lider.km, sin.uavs[0].km)

    def test_seguidor_en_tierra_planifica_con_el_aviso(self):
        r = self.flota("D_A", self.bloqueo, n_uav=2, separacion_km=3.0, prob_deteccion=1.0)
        seguidor = r.uavs[1]
        self.assertEqual(seguidor.replan_por_aviso, 0)  # el aviso llegó antes de despegar
        self.assertEqual(seguidor.recorrido, [A, W, Y, Z, B])

    def test_silencio_del_lider_avisa_tras_el_timeout(self):
        # Sin detección previa, el líder entra a X-B y queda sin enlace. Tras 3 beacons perdidos
        # la flota marca el entorno de X y el seguidor lo evita.
        con = self.flota("D_A", self.bloqueo, n_uav=2, separacion_km=1.5, prob_deteccion=0.0)
        sin = self.flota("D", self.bloqueo, n_uav=2, separacion_km=1.5, prob_deteccion=0.0)
        self.assertTrue(con.uavs[0].perdido)
        self.assertEqual(con.uavs[0].motivo, "perdido_en_interferencia")
        aviso = con.avisos[0]
        timeout_km = 3 * 2.0 * 12.0 / 1000
        self.assertEqual(aviso.tipo, "silencio")
        self.assertAlmostEqual(aviso.t_km - aviso.t_evento_km, timeout_km)
        self.assertIn(arista(self.g, X, B), aviso.evitar)
        self.assertTrue(con.uavs[1].exito)
        self.assertNotIn(X, con.uavs[1].recorrido)
        self.assertTrue(sin.uavs[1].perdido)  # sin aviso, el seguidor también se pierde

    def test_aviso_se_retransmite_por_la_flota(self):
        # Con alcance de 1 km, el líder (en X) no alcanza al tercer UAV (a 1,5 km), pero el
        # segundo UAV queda entre ambos y retransmite el aviso en el mismo instante.
        r = self.flota("D_A", self.bloqueo, n_uav=3, separacion_km=0.75, alcance_com_km=1.0, prob_deteccion=1.0)
        aviso = r.avisos[0]
        self.assertEqual(sorted(aviso.recepciones), [0, 1, 2])
        self.assertAlmostEqual(aviso.recepciones[2], aviso.t_km)
        self.assertNotIn(X, r.uavs[2].recorrido)

    def test_sin_alcance_el_aviso_no_llega(self):
        r = self.flota("D_A", self.bloqueo, n_uav=2, separacion_km=1.5, alcance_com_km=0.3, prob_deteccion=1.0)
        aviso = r.avisos[0]
        self.assertFalse(1 in aviso.recepciones and math.isclose(aviso.recepciones[1], aviso.t_km))
        self.assertIn(X, r.uavs[1].recorrido)

    def test_linea_de_tiempo(self):
        r = self.flota("D_A", self.bloqueo, n_uav=2, separacion_km=1.5, prob_deteccion=1.0)
        lt = linea_de_tiempo(self.g, r, self.bloqueo, 12.0)
        self.assertEqual(len(lt["uavs"]), 2)
        self.assertEqual(lt["uavs"][1]["despegue_s"], 125.0)  # 1,5 km a 12 m/s
        tipos = {e["tipo"] for e in lt["uavs"][1]["eventos"]}
        self.assertIn("replan_aviso", tipos)
        self.assertIn("ruta", next(e for e in lt["uavs"][1]["eventos"] if e["tipo"] == "replan_aviso"))


class PruebasFlotaUnUAV(unittest.TestCase):
    def test_un_uav_reproduce_el_simulador(self):
        """Con un UAV y detección perfecta, la flota debe coincidir con ejecutar_mision."""
        cfg = Configuracion(malla=ParametrosMalla(espaciado_km=0.6), fallas=ParametrosFallas(n_fallas=5))
        cfg1 = replace(cfg, flota=ParametrosFlota(n_uav=1, prob_deteccion=1.0))
        g = generar_malla(cfg.malla)
        sec = nodos_mision(g, cfg.mision)
        focos = generar_focos(g, 4, 8)
        largo = largo_minimo_mision(g, sec)
        for semilla in range(15):
            esc = generar_escenario(g, focos, cfg.fallas, largo, sec, semilla)
            for clave in ("A", "D", "C"):
                a = ejecutar_mision(g, cfg, sec, esc, ESTRATEGIAS[clave](), 1.6 * largo)
                b = ejecutar_flota(g, cfg1, sec, esc, clave, 1.6 * largo).uavs[0]
                self.assertEqual((a.exito, a.motivo, a.km, a.replanificaciones, a.puntos_visitados),
                                 (b.exito, b.motivo, b.km, b.replanificaciones, b.puntos_visitados),
                                 f"semilla {semilla}, estrategia {clave}")


if __name__ == "__main__":
    unittest.main()

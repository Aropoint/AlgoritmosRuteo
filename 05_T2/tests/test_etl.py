"""Pruebas de las transformaciones del ETL y las restricciones (comun/transformar.py).

Solo biblioteca estándar: no requieren red ni BD.  Ejecutar desde 05_T2:
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.transformar import (altura_estimada_m, anillo_cerrado, celda_roja_gpsjam,  # noqa: E402
                               direccion_media_grados, obstaculo_relativo_m, parsear_altura_m,
                               parsear_niveles, pct_malo_gpsjam, percentil, viento_a_altura)
from ruteo.config import Preferencias  # noqa: E402
from ruteo.pesos import arista_admisible  # noqa: E402


class TestOSM(unittest.TestCase):
    def test_parsear_altura(self):
        self.assertEqual(parsear_altura_m("12"), 12.0)
        self.assertEqual(parsear_altura_m("12.5 m"), 12.5)
        self.assertEqual(parsear_altura_m("12,5"), 12.5)
        self.assertAlmostEqual(parsear_altura_m("40 ft"), 12.19, places=2)
        self.assertAlmostEqual(parsear_altura_m("40'"), 12.19, places=2)
        self.assertIsNone(parsear_altura_m(None))
        self.assertIsNone(parsear_altura_m("alto"))
        self.assertIsNone(parsear_altura_m("0"))

    def test_parsear_niveles(self):
        self.assertEqual(parsear_niveles("5"), 5)
        self.assertEqual(parsear_niveles("5;9"), 9)
        self.assertIsNone(parsear_niveles(""))
        self.assertIsNone(parsear_niveles("sin dato"))

    def test_altura_estimada_prioriza_height(self):
        self.assertEqual(altura_estimada_m(20.0, 3), (20.0, "height"))
        self.assertEqual(altura_estimada_m(None, 4), (12.0, "building:levels"))
        self.assertEqual(altura_estimada_m(None, None), (None, None))

    def test_anillo_cerrado(self):
        self.assertEqual(anillo_cerrado([[0, 0], [1, 0], [1, 1]]), [[0, 0], [1, 0], [1, 1], [0, 0]])
        self.assertIsNone(anillo_cerrado([[0, 0], [1, 0]]))


class TestGPSJam(unittest.TestCase):
    def test_formula_publicada(self):
        # Un solo avión con problemas no tiñe la celda: se resta 1.
        self.assertEqual(pct_malo_gpsjam(9, 1), 0.0)
        self.assertAlmostEqual(pct_malo_gpsjam(8, 2), 10.0)
        self.assertIsNone(pct_malo_gpsjam(0, 0))

    def test_regla_roja_estricta(self):
        self.assertFalse(celda_roja_gpsjam(8, 2))   # exactamente 10 %: no es roja
        self.assertTrue(celda_roja_gpsjam(7, 3))    # 20 %
        self.assertFalse(celda_roja_gpsjam(0, 0))


class TestViento(unittest.TestCase):
    def test_direccion_media_circular(self):
        self.assertAlmostEqual(direccion_media_grados([350, 10]), 0.0, places=1)
        self.assertAlmostEqual(direccion_media_grados([80, 100]), 90.0, places=1)
        self.assertIsNone(direccion_media_grados([]))
        self.assertIsNone(direccion_media_grados([0, 180]))  # se anulan

    def test_percentil_como_postgres(self):
        self.assertEqual(percentil([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(percentil([5], 0.95), 5)
        self.assertIsNone(percentil([], 0.5))

    def test_ley_potencial(self):
        self.assertAlmostEqual(viento_a_altura(10, 100, 100), 10)
        self.assertLess(viento_a_altura(10, 100, 60), 10)
        self.assertGreater(viento_a_altura(10, 100, 60), 9)


class TestObstaculo(unittest.TestCase):
    def test_sin_datos_no_bloquea(self):
        self.assertIsNone(obstaculo_relativo_m(None, None, None))
        self.assertIsNone(obstaculo_relativo_m(None, 50.0, None))

    def test_relieve_mas_edificio(self):
        self.assertEqual(obstaculo_relativo_m(20.0, 45.0, 30.0), 35.0)
        self.assertEqual(obstaculo_relativo_m(None, 45.0, 30.0), 15.0)
        self.assertEqual(obstaculo_relativo_m(20.0, None, 30.0), 20.0)
        self.assertEqual(obstaculo_relativo_m(10.0, 20.0, 30.0), 0.0)  # tramo más bajo que el despegue

    def test_regla_de_admisibilidad(self):
        prefs = Preferencias()  # 60 m de vuelo, 10 m de margen -> límite 50 m
        self.assertTrue(arista_admisible({"altura_max_edificio_m": obstaculo_relativo_m(30.0, 40.0, 30.0)}, prefs))
        self.assertFalse(arista_admisible({"altura_max_edificio_m": obstaculo_relativo_m(30.0, 50.0, 30.0)}, prefs))
        self.assertTrue(arista_admisible({}, prefs))


if __name__ == "__main__":
    unittest.main()

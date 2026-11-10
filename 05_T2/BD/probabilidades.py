"""Genera la probabilidad de falla de cada tramo y de cada nodo a partir de cada amenaza (Tarea 3, punto 5).

Ejecuta BD/probabilidades.sql (modelo de tasa de falla por km) y deja:
- en la BD: columnas pf_eventos, pf_incendios, pf_gnss y pf_total de `aristas` y `nodos`;
- en BD/salida/probabilidades.json: el mismo detalle por amenaza, con el umbral de falla 0-100 que usa
  el sorteo del punto 7 (estructura en BD/ESTRUCTURA_probabilidades_json.md).

Modelo:  p_i = 1 - exp(-lambda_i^max * r_i * L),  p = 1 - prod_i (1 - p_i)
con r_i la intensidad de la amenaza (BD/pesos.sql), L el largo del tramo o la exposición del nodo y
lambda_i^max un supuesto abstracto de la tabla parametros_pesos.

Va después de BD/asignar_pesos.py.  Uso (dentro del contenedor app):  python BD/probabilidades.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import ahora_utc, guardar_json  # noqa: E402
from comun.bd import conectar  # noqa: E402
from ruteo.probabilidad import AMENAZAS, umbral_falla  # noqa: E402

SQL = Path(__file__).resolve().parent / "probabilidades.sql"
SALIDA = Path(__file__).resolve().parent / "salida" / "probabilidades.json"
INTENSIDAD = {"eventos": "r_eventos", "incendios": "r_incendios", "gnss": "p_gnss"}


def _elemento(fila: tuple, columnas: list[str]) -> dict:
    d = dict(zip(columnas, fila))
    p_total = float(d["pf_total"])
    salida = {k: d[k] for k in columnas if k in ("id", "tipo", "source", "target", "largo_km")}
    salida["intensidad"] = {a: float(d[INTENSIDAD[a]]) for a in AMENAZAS}
    salida["p_falla"] = {**{a: float(d[f"pf_{a}"]) for a in AMENAZAS}, "total": p_total}
    salida["umbral_falla"] = round(umbral_falla(p_total), 4)
    return salida


def main() -> None:
    with conectar() as conn:
        conn.execute(SQL.read_text(encoding="utf-8"))
        parametros = dict(conn.execute(
            """SELECT clave, valor FROM parametros_pesos
               WHERE clave LIKE 'lambda_%' OR clave = 'exposicion_nodo_km' ORDER BY clave""").fetchall())
        cols_a = ["id", "source", "target", "largo_km", "r_eventos", "r_incendios", "p_gnss",
                  "pf_eventos", "pf_incendios", "pf_gnss", "pf_total"]
        aristas = [_elemento(f, cols_a) for f in conn.execute(
            f"SELECT {', '.join(cols_a)} FROM aristas ORDER BY id")]
        cols_n = ["id", "tipo", "r_eventos", "r_incendios", "p_gnss", "pf_eventos", "pf_incendios", "pf_gnss", "pf_total"]
        nodos = [_elemento(f, cols_n) for f in conn.execute(f"SELECT {', '.join(cols_n)} FROM nodos ORDER BY id")]

    def resumen(elementos: list[dict]) -> dict:
        r = {}
        for clave in (*AMENAZAS, "total"):
            valores = [e["p_falla"][clave] for e in elementos]
            r[clave] = {"min": min(valores, default=0), "media": round(sum(valores) / len(valores), 6) if valores else 0,
                        "max": max(valores, default=0), "con_p_mayor_0": sum(1 for v in valores if v > 0)}
        return r

    datos = {
        "tipo": "probabilidades_falla",
        "metadatos": {
            "fuente": "BD/probabilidades.sql sobre las amenazas cargadas (UCDP, incendios de guerra, GPSJam)",
            "generado_utc": ahora_utc(),
            "modelo": "p_i = 1 - exp(-lambda_i^max * r_i * L); p_total = 1 - prod_i (1 - p_i)",
            "parametros": {k: float(v) for k, v in parametros.items()},
            "umbral": "umbral_falla = 100 * (1 - p_total): en el sorteo 0-100 hay falla si el número supera el umbral",
            "advertencias": [
                "Los lambda_i^max son supuestos académicos abstractos, no tasas medidas de un UAV real.",
                "Las amenazas se tratan como independientes.",
                "GPSJam no distingue tramos dentro del AOI: una sola celda H3 lo cubre entero.",
            ],
            "resumen": {"aristas": resumen(aristas), "nodos": resumen(nodos)},
        },
        "aristas": aristas,
        "nodos": nodos,
    }
    guardar_json(SALIDA, datos)
    ra, rn = datos["metadatos"]["resumen"]["aristas"], datos["metadatos"]["resumen"]["nodos"]
    print(f"Parámetros: {datos['metadatos']['parametros']}")
    for clave in (*AMENAZAS, "total"):
        print(f"  p_{clave:9}  tramos: media {ra[clave]['media']:.5f}, máx {ra[clave]['max']:.5f}"
              f" ({ra[clave]['con_p_mayor_0']} con p > 0) · nodos: máx {rn[clave]['max']:.5f}")
    print(f"{len(aristas)} tramos y {len(nodos)} nodos -> {SALIDA}")


if __name__ == "__main__":
    main()

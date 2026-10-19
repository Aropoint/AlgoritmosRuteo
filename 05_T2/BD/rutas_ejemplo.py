"""Rutas de ejemplo para la misión cargada (rúbrica 8 y 9, y punto 8 del enunciado).

Desde el inicio hasta el destino de la tabla `mision`, con las preferencias por defecto:
- 2 rutas con pgr_dijkstra y costo = distancia en km (peor caso: sin metadata ni amenazas en el costo),
- 2 rutas del método propuesto (pgr_KSP + selección resiliente),
- su resiliencia sobre 100 escenarios de fallas y el diferencial entre métodos.

Guarda las rutas en las tablas `rutas` y `evaluaciones`, y el resultado en
BD/salida/rutas_ejemplo.json (estructura en BD/ESTRUCTURA_rutas_ejemplo_json.md),
que el sitio web muestra al abrirse.

Uso (dentro del contenedor app):  python BD/rutas_ejemplo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from comun.ajustes import ahora_utc, guardar_json  # noqa: E402
from comun.bd import conectar  # noqa: E402
from comun.servicio import resolver  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "rutas_ejemplo.json"


def main() -> None:
    with conectar() as conn:
        s, t = conn.execute(
            """SELECT (SELECT nodo_id FROM mision ORDER BY orden LIMIT 1),
                      (SELECT nodo_id FROM mision ORDER BY orden DESC LIMIT 1)"""
        ).fetchone()
        if s is None or t is None:
            raise SystemExit("La tabla mision está vacía: ejecuta Infraestructura/cargar_infraestructura.py.")
        resultado = resolver(conn, s, t)
    if "error" in resultado:
        raise SystemExit(resultado["error"])
    resultado["generado_utc"] = ahora_utc()
    guardar_json(SALIDA, resultado)

    print(f"Misión {s} -> {t}")
    for metodo in ("dijkstra", "propuesta"):
        for i, r in enumerate(resultado[metodo], start=1):
            print(f"  {metodo} ruta {i}: {r['largo_km']} km, riesgo medio {r['riesgo_medio']}, {len(r['aristas'])} tramos")
    ev = resultado["resiliencia"]
    dif = ev["diferencial_C_vs_A"]
    print(f"  R_par Dijkstra {ev['r_par']['dijkstra']} / propuesta {ev['r_par']['propuesta']}")
    print(f"  R_mision A {ev['r_mision']['A_dijkstra_fijo']} / D {ev['r_mision']['D_dijkstra_replan']}"
          f" / C {ev['r_mision']['C_propuesta']};  Delta R (C-A) = {dif['delta_R_pp']} pp (p = {dif['p_mcnemar']})")
    for aviso in resultado["advertencias"]:
        print(f"  aviso: {aviso}")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()

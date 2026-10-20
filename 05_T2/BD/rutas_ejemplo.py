"""Rutas de ejemplo para la misión cargada (rúbrica 8 y 9, y punto 8 del enunciado).

Para cada par consecutivo de la tabla `mision`, con las preferencias por defecto:
- 2 rutas con pgr_dijkstra y costo = distancia en km,
- 2 rutas del método propuesto (pgr_KSP + selección resiliente),
- resiliencia de la misión completa sobre 100 escenarios de fallas.

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
from comun.servicio import resolver_mision  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "rutas_ejemplo.json"


def main() -> None:
    with conectar() as conn:
        secuencia = [fila[0] for fila in conn.execute("SELECT nodo_id FROM mision ORDER BY orden")]
        if len(secuencia) < 2:
            raise SystemExit("La tabla mision está incompleta: ejecuta Infraestructura/cargar_infraestructura.py.")
        resultado = resolver_mision(conn, secuencia)
    if "error" in resultado:
        raise SystemExit(resultado["error"])
    resultado["generado_utc"] = ahora_utc()
    guardar_json(SALIDA, resultado)

    print(f"Misión {' -> '.join(map(str, secuencia))}")
    for tramo in resultado["tramos"]:
        for metodo in ("dijkstra", "propuesta"):
            for i, r in enumerate(tramo[metodo], start=1):
                print(f"  {tramo['etiqueta']} {metodo} ruta {i}: {r['largo_km']} km, "
                      f"riesgo medio {r['riesgo_medio']}, {len(r['aristas'])} aristas")
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

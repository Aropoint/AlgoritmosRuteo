"""Pipeline ETL completo. Lo invoca main.py (raíz) dentro del contenedor `main` de docker compose.

Orden: esquema -> infraestructura -> 3 metadata -> 3 amenazas -> pesos -> rutas de ejemplo -> diagrama.
Cada fuente externa es opcional: si su descarga falla, el pipeline sigue y el
peso o la restricción correspondiente queda neutro (un dato ausente no bloquea).
Los pasos obligatorios (esquema, infraestructura, pesos, rutas) detienen el pipeline.

Uso:
    python pipeline.py                  # todo
    python pipeline.py --sin-descarga   # no llama a las APIs: carga los JSON que ya existen
    python pipeline.py --solo bd,infra  # solo esos grupos (bd, infra, metadata, amenazas, pesos, rutas, diagrama)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent

# (grupo, script, es_extraccion, obligatorio)
PASOS = [
    ("bd", "BD/crear_bd.py", False, True),
    ("infra", "Infraestructura/generar_infraestructura.py", False, True),
    ("infra", "Infraestructura/cargar_infraestructura.py", False, True),
    ("metadata", "Metadata/osm_edificios.py", True, False),
    ("metadata", "Metadata/cargar_osm_edificios.py", False, False),
    ("metadata", "Metadata/elevacion.py", True, False),
    ("metadata", "Metadata/cargar_elevacion.py", False, False),
    ("metadata", "Metadata/viento.py", True, False),
    ("metadata", "Metadata/cargar_viento.py", False, False),
    ("amenazas", "Amenazas/gpsjam.py", True, False),
    ("amenazas", "Amenazas/cargar_gpsjam.py", False, False),
    ("amenazas", "Amenazas/incendios_guerra.py", True, False),
    ("amenazas", "Amenazas/cargar_incendios_guerra.py", False, False),
    ("amenazas", "Amenazas/ucdp_eventos.py", True, False),
    ("amenazas", "Amenazas/cargar_ucdp_eventos.py", False, False),
    ("pesos", "BD/asignar_pesos.py", False, True),
    ("rutas", "BD/rutas_ejemplo.py", False, True),
    ("diagrama", "BD/diagrama_bd.py", False, False),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sin-descarga", action="store_true", help="no ejecuta los scripts de extracción")
    ap.add_argument("--solo", default="", help="grupos separados por coma")
    args = ap.parse_args()
    grupos = {g.strip() for g in args.solo.split(",") if g.strip()}

    resumen = []
    for grupo, script, extraccion, obligatorio in PASOS:
        if grupos and grupo not in grupos:
            continue
        if extraccion and args.sin_descarga:
            resumen.append((script, "omitido", 0.0))
            continue
        print(f"\n=== {script}", flush=True)
        t0 = time.perf_counter()
        ok = subprocess.run([sys.executable, script], cwd=BASE).returncode == 0
        resumen.append((script, "ok" if ok else "FALLÓ", time.perf_counter() - t0))
        if not ok and obligatorio:
            print(f"\nPaso obligatorio fallido: {script}. Se detiene el pipeline.")
            break

    print("\n=== Resumen")
    for script, estado, seg in resumen:
        print(f"  {estado:8} {seg:6.1f} s  {script}")
    fallos = [s for s, e, _ in resumen if e == "FALLÓ"]
    if fallos:
        print("\nLas fuentes que fallaron quedan sin datos (peso o restricción neutros). "
              "Reintenta con:  docker compose run --rm app python pipeline.py --solo metadata,amenazas,pesos,rutas")
    obligatorios = {s for _, s, _, o in PASOS if o}
    return 1 if any(f in obligatorios for f in fallos) else 0


if __name__ == "__main__":
    sys.exit(main())

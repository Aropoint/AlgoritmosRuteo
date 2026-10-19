"""Asigna restricciones y pesos a las aristas desde la metadata y las amenazas cargadas (rúbrica 5.2 y 6.1).

Ejecuta BD/pesos.sql e imprime un resumen. Va después de todas las cargas.

Uso (dentro del contenedor app):  python BD/asignar_pesos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.bd import conectar  # noqa: E402

PESOS = Path(__file__).resolve().parent / "pesos.sql"


def main() -> None:
    with conectar() as conn:
        conn.execute(PESOS.read_text(encoding="utf-8"))
        r = conn.execute(
            """SELECT count(*), count(altura_max_edificio_m), count(terreno_max_m),
                      min(terreno_max_m), max(terreno_max_m), max(altura_max_edificio_m),
                      count(*) FILTER (WHERE riesgo > 0), avg(riesgo), max(r_eventos), max(r_incendios), max(p_gnss)
               FROM aristas"""
        ).fetchone()
    total, con_altura, con_terreno, t_min, t_max, h_max, con_riesgo, r_medio, m_ev, m_inc, m_gnss = r
    print(f"Aristas: {total}")
    print(f"  con edificio con altura conocida a <= buffer: {con_altura} (máx. {h_max} m)")
    print(f"  con terreno: {con_terreno} (de {t_min} a {t_max} m)")
    print(f"  con riesgo > 0: {con_riesgo}; riesgo medio {r_medio or 0:.4f}")
    print(f"  máximos por componente: eventos {m_ev}, incendios {m_inc}, gnss {m_gnss}")


if __name__ == "__main__":
    main()

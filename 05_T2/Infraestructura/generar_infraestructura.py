"""Genera la infraestructura (nodos y aristas del grafo de navegación) como JSON.

Rúbrica punto 1. La malla es sintética y geolocalizada sobre el AOI de
ruteo/config.py; los atributos de riesgo provienen de eventos históricos
(sintéticos mientras no se carguen las fuentes de Amenazas/).

Uso:  python 05_T2/Infraestructura/generar_infraestructura.py
Salida: 05_T2/Infraestructura/salida/infraestructura.json
Estructura: ESTRUCTURA_infraestructura_json.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from ruteo.config import AOI, Configuracion  # noqa: E402
from ruteo.fallas import eventos_historicos, generar_focos  # noqa: E402
from ruteo.grafo import generar_malla, nodos_mision  # noqa: E402
from ruteo.pesos import asignar_riesgo  # noqa: E402


def main() -> None:
    cfg = Configuracion()
    g = generar_malla(cfg.malla)
    secuencia = nodos_mision(g, cfg.mision)
    focos = generar_focos(g, cfg.fallas.n_focos, cfg.malla.semilla + 1)
    eventos = eventos_historicos(g, focos, cfg.fallas, cfg.malla.semilla + 2)
    asignar_riesgo(g, eventos, cfg.fallas.sigma_foco_km)

    datos = g.a_json()
    datos["metadatos"] = {
        "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aoi": AOI,
        "parametros_malla": cfg.a_dict()["malla"],
        "secuencia_mision": secuencia,
        "origen_riesgo": "sintetico",  # cambiar a la fuente real cuando Amenazas/ esté implementada
        "advertencia": "Malla sintética de simulación académica; no representa corredores aéreos reales ni un plan de vuelo.",
    }
    salida = Path(__file__).resolve().parent / "salida"
    salida.mkdir(exist_ok=True)
    ruta = salida / "infraestructura.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(g.nodos)} nodos, {len(g.aristas)} aristas, misión {secuencia} -> {ruta}")


if __name__ == "__main__":
    main()

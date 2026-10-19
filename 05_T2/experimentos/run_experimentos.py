"""Experimento comparativo: A (Dijkstra fijo), B (Yen fijo), D (Dijkstra + replan) y C (propuesta).

Uso (desde la raíz del repo o desde 05_T2):
    python 05_T2/experimentos/run_experimentos.py                      # evaluación, parámetros por defecto
    python 05_T2/experimentos/run_experimentos.py --conjunto ajuste    # escenarios para calibrar
    python 05_T2/experimentos/run_experimentos.py --sensibilidad       # barrido prob_foco x n_fallas

Salida: 05_T2/resultados/<nombre>.json (estructura en resultados/README.md).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from ruteo.config import AOI, SEMILLAS, Configuracion  # noqa: E402
from ruteo.fallas import eventos_historicos, generar_escenario, generar_focos  # noqa: E402
from ruteo.grafo import generar_malla, nodos_mision  # noqa: E402
from ruteo.metricas import diferencial, r_par, resumir, tasa  # noqa: E402
from ruteo.pesos import aristas_excluidas, asignar_riesgo  # noqa: E402
from ruteo.simulador import ESTRATEGIAS, Contexto, ejecutar_mision, largo_minimo_mision  # noqa: E402

SALIDA = BASE / "resultados"


def preparar(cfg: Configuracion):
    """Grafo, misión y pesos de riesgo. Focos y eventos históricos dependen solo de la semilla de la malla."""
    g = generar_malla(cfg.malla)
    secuencia = nodos_mision(g, cfg.mision)
    focos = generar_focos(g, cfg.fallas.n_focos, cfg.malla.semilla + 1)
    eventos = eventos_historicos(g, focos, cfg.fallas, cfg.malla.semilla + 2)
    asignar_riesgo(g, eventos, cfg.fallas.sigma_foco_km)
    return g, secuencia, focos, eventos


def correr(cfg: Configuracion, semillas, claves: list[str], etiqueta: str) -> dict:
    g, secuencia, focos, _ = preparar(cfg)
    excluidas = aristas_excluidas(g, cfg.preferencias)
    largo_min = largo_minimo_mision(g, secuencia, excluidas)
    presupuesto = (1 + cfg.preferencias.presupuesto_extra) * largo_min
    estrategias = {k: ESTRATEGIAS[k]() for k in claves}

    # Pares precalculados sin conocimiento de fallas, para R_par.
    pares = {}
    for k in ("A", "B", "C"):
        if k in estrategias:
            ctx = Contexto.nuevo(g, cfg)
            pares[k] = [estrategias[k].planificar(ctx, s, t) for s, t in zip(secuencia, secuencia[1:])]

    resultados = {e.nombre: [] for e in estrategias.values()}
    r_pares = {k: [] for k in pares}
    oraculo = []
    descartadas = 0
    t0 = time.perf_counter()
    for semilla in semillas:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, secuencia, semilla)
        descartadas += esc.descartadas
        # Referencia con conocimiento perfecto y fallas activas desde el inicio. No es una cota
        # estricta: ignora fallas que se activan con el UAV dentro (atrapado) o después de pasar.
        lo = largo_minimo_mision(g, secuencia, excluidas | esc.todas_afectadas())
        oraculo.append(lo is not None and lo <= presupuesto + 1e-9)
        for k, par in pares.items():
            r_pares[k].append(r_par(par, esc))
        for e in estrategias.values():
            resultados[e.nombre].append(ejecutar_mision(g, cfg, secuencia, esc, e, presupuesto))

    nombres = {k: e.nombre for k, e in estrategias.items()}
    diferenciales = []
    if "A" in nombres:
        for k in ("B", "D", "C0", "C1", "C"):
            if k in nombres:
                diferenciales.append(diferencial(resultados, nombres[k], nombres["A"], largo_min))
    if "C" in nombres and "D" in nombres:
        diferenciales.append(diferencial(resultados, nombres["C"], nombres["D"], largo_min))

    return {
        "etiqueta": etiqueta,
        "configuracion": cfg.a_dict(),
        "aoi": AOI,
        "grafo": {"nodos": len(g.nodos), "aristas": len(g.aristas), "excluidas_por_restriccion": len(excluidas)},
        "secuencia_mision": secuencia,
        "largo_minimo_km": round(largo_min, 4),
        "presupuesto_km": round(presupuesto, 4),
        "n_escenarios": len(resultados[next(iter(resultados))]),
        "fallas_remuestreadas": descartadas,
        "R_oraculo_estatico": round(tasa(oraculo), 4),
        "R_par": {nombres[k]: round(sum(v) / len(v), 4) for k, v in r_pares.items()},
        "resumen": resumir(resultados, largo_min),
        "diferenciales": diferenciales,
        "segundos": round(time.perf_counter() - t0, 1),
    }


def imprimir(res: dict) -> None:
    print(f"\n== {res['etiqueta']} | escenarios={res['n_escenarios']} | L*={res['largo_minimo_km']} km "
          f"| presupuesto={res['presupuesto_km']} km | oráculo={res['R_oraculo_estatico']:.3f} | {res['segundos']} s")
    print(f"{'estrategia':28} {'R_mision':>8} {'R_par':>7} {'km_exit':>8} {'sobrelong':>9} {'replan':>6} {'ms':>8}")
    for nombre, s in res["resumen"].items():
        rp = res["R_par"].get(nombre)
        print(f"{nombre:28} {s['R_mision']:8.3f} {('%.3f' % rp) if rp is not None else '-':>7} "
              f"{s['km_medio_exitosas'] or 0:8.2f} {s['sobrelongitud_media_exitosas'] or 0:9.3f} "
              f"{s['replanificaciones_media']:6.2f} {s['tiempo_calculo_ms_medio']:8.1f}")
    for d in res["diferenciales"]:
        print(f"  {d['metodo']} vs {d['referencia']}: ΔR={d['delta_R_pp']:+.1f} pp "
              f"(gana {d['solo_metodo_completa']}, pierde {d['solo_referencia_completa']}, p={d['p_mcnemar']}) "
              f"km extra pareado={d['km_extra_medio_pareado']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conjunto", choices=SEMILLAS, default="evaluacion")
    ap.add_argument("--n", type=int, help="limitar el número de escenarios")
    ap.add_argument("--prob-foco", type=float)
    ap.add_argument("--n-fallas", type=int)
    ap.add_argument("--presupuesto", type=float, help="beta: km máximos = (1 + beta) * misión mínima")
    ap.add_argument("--estrategias", default="A,B,D,C0,C1,C")
    ap.add_argument("--sensibilidad", action="store_true", help="barrido prob_foco in {0, 0.5, 0.8} x n_fallas in {1, 3, 5}")
    args = ap.parse_args()

    semillas = list(SEMILLAS[args.conjunto])[: args.n] if args.n else list(SEMILLAS[args.conjunto])
    claves = args.estrategias.split(",")
    SALIDA.mkdir(exist_ok=True)

    base = Configuracion()
    if args.prob_foco is not None or args.n_fallas is not None:
        base.fallas = replace(base.fallas,
                              prob_foco=base.fallas.prob_foco if args.prob_foco is None else args.prob_foco,
                              n_fallas=base.fallas.n_fallas if args.n_fallas is None else args.n_fallas)

    if args.presupuesto is not None:
        base.preferencias = replace(base.preferencias, presupuesto_extra=args.presupuesto)

    if not args.sensibilidad:
        etiqueta = f"{args.conjunto}_pf{base.fallas.prob_foco}_nf{base.fallas.n_fallas}_b{base.preferencias.presupuesto_extra}"
        res = correr(base, semillas, claves, etiqueta)
        imprimir(res)
        (SALIDA / f"{etiqueta}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    todos = []
    for pf in (0.0, 0.5, 0.8):
        for nf in (1, 3, 5):
            cfg = Configuracion(preferencias=base.preferencias)
            cfg.fallas = replace(cfg.fallas, prob_foco=pf, n_fallas=nf)
            res = correr(cfg, semillas, claves, f"{args.conjunto}_pf{pf}_nf{nf}_b{cfg.preferencias.presupuesto_extra}")
            imprimir(res)
            todos.append(res)
    (SALIDA / f"sensibilidad_{args.conjunto}.json").write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

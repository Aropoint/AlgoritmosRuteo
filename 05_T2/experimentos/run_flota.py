"""Experimento de flota: N UAV con y sin aviso compartido de interferencia (ruteo/flota.py).

Compara A, D y C sin aviso (cada UAV aprende solo) contra D_A y C_A, que avisan
al resto y cambian de ruta en tiempo real. Las fallas son las mismas del
experimento de un UAV (mismas semillas), así que la comparación es pareada.

Uso (desde la raíz del repo o desde 05_T2):
    python 05_T2/experimentos/run_flota.py --conjunto ajuste             # 4 UAV, parámetros por defecto
    python 05_T2/experimentos/run_flota.py --conjunto ajuste --n-uav 3
    python 05_T2/experimentos/run_flota.py --conjunto ajuste --sensibilidad  # n_uav x prob_deteccion

Salida: 05_T2/resultados/flota_<etiqueta>.json (estructura en resultados/README.md).
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_experimentos import preparar  # noqa: E402

from ruteo.config import AOI, SEMILLAS, Configuracion  # noqa: E402
from ruteo.fallas import generar_escenario  # noqa: E402
from ruteo.flota import ESTRATEGIAS_FLOTA, ejecutar_flota  # noqa: E402
from ruteo.metricas import diferencial, resumir_flota, seguidores, todos_los_uav  # noqa: E402
from ruteo.pesos import aristas_excluidas  # noqa: E402
from ruteo.simulador import largo_minimo_mision  # noqa: E402

SALIDA = BASE / "resultados"

# (método, referencia): qué aporta el aviso, y qué aporta la selección encima del aviso
COMPARACIONES = [("D_A", "D"), ("C_A", "D_A"), ("C_A", "D"), ("C_A", "C"), ("C_A", "A"), ("D", "A")]


def correr(cfg: Configuracion, semillas, claves: list[str], etiqueta: str) -> dict:
    g, secuencia, focos, _ = preparar(cfg)
    excluidas = aristas_excluidas(g, cfg.preferencias)
    largo_min = largo_minimo_mision(g, secuencia, excluidas)
    presupuesto = (1 + cfg.preferencias.presupuesto_extra) * largo_min
    nombres = {k: ESTRATEGIAS_FLOTA[k][2] for k in claves}
    resultados = {nombres[k]: [] for k in claves}
    t0 = time.perf_counter()
    for semilla in semillas:
        esc = generar_escenario(g, focos, cfg.fallas, largo_min, secuencia, semilla)
        for k in claves:
            resultados[nombres[k]].append(ejecutar_flota(g, cfg, secuencia, esc, k, presupuesto))

    por_seguidor, por_uav = seguidores(resultados), todos_los_uav(resultados)
    diferenciales = []
    for m, r in COMPARACIONES:
        if m in nombres and r in nombres:
            d = diferencial(por_seguidor, nombres[m], nombres[r], largo_min)
            d["poblacion"] = "seguidores"
            diferenciales.append(d)
            d = diferencial(por_uav, nombres[m], nombres[r], largo_min)
            d["poblacion"] = "todos_los_uav"
            diferenciales.append(d)

    return {
        "etiqueta": etiqueta,
        "configuracion": cfg.a_dict(),
        "aoi": AOI,
        "grafo": {"nodos": len(g.nodos), "aristas": len(g.aristas), "excluidas_por_restriccion": len(excluidas)},
        "secuencia_mision": secuencia,
        "largo_minimo_km": round(largo_min, 4),
        "presupuesto_km": round(presupuesto, 4),
        "n_escenarios": len(semillas),
        "resumen": resumir_flota(resultados, largo_min, cfg.preferencias.velocidad_crucero_m_s),
        "diferenciales": diferenciales,
        "segundos": round(time.perf_counter() - t0, 1),
    }


def imprimir(res: dict) -> None:
    fl = res["configuracion"]["flota"]
    print(f"\n== {res['etiqueta']} | {fl['n_uav']} UAV cada {fl['separacion_km']} km | "
          f"escenarios={res['n_escenarios']} | L*={res['largo_minimo_km']} km | {res['segundos']} s")
    print(f"{'estrategia':28} {'R_uav':>6} {'lider':>6} {'segui':>6} {'flota':>6} {'perd':>5} "
          f"{'avisos':>6} {'replAv':>6} {'demora_s':>8}")
    for nombre, s in res["resumen"].items():
        demora = s["demora_aviso_media_s"]
        print(f"{nombre:28} {s['R_uav']:6.3f} {s['R_lider']:6.3f} {s['R_seguidores']:6.3f} "
              f"{s['R_flota_alguno']:6.3f} {s['perdidos_media']:5.2f} {s['avisos_media']:6.2f} "
              f"{s['replan_por_aviso_media']:6.2f} {('%.1f' % demora) if demora is not None else '-':>8}")
    for d in res["diferenciales"]:
        if d["poblacion"] == "seguidores":
            print(f"  seguidores {d['metodo']} vs {d['referencia']}: ΔR={d['delta_R_pp']:+.1f} pp "
                  f"(gana {d['solo_metodo_completa']}, pierde {d['solo_referencia_completa']}, p={d['p_mcnemar']})")


def configurar(base: Configuracion, **cambios) -> Configuracion:
    cfg = Configuracion(preferencias=base.preferencias, fallas=base.fallas, flota=base.flota)
    if cambios:
        cfg.flota = replace(cfg.flota, **cambios)
    return cfg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conjunto", choices=SEMILLAS, default="evaluacion")
    ap.add_argument("--n", type=int, help="limitar el número de escenarios")
    ap.add_argument("--n-uav", type=int, choices=range(1, 6), metavar="{1..5}")
    ap.add_argument("--separacion", type=float, help="km entre lanzamientos")
    ap.add_argument("--alcance", type=float, help="alcance de radio en km (0 = sin límite)")
    ap.add_argument("--prob-deteccion", type=float)
    ap.add_argument("--prob-foco", type=float)
    ap.add_argument("--n-fallas", type=int)
    ap.add_argument("--presupuesto", type=float, help="beta: km máximos = (1 + beta) * misión mínima")
    ap.add_argument("--estrategias", default=",".join(ESTRATEGIAS_FLOTA))
    ap.add_argument("--sensibilidad", action="store_true", help="barrido n_uav in {3, 4, 5} x prob_deteccion in {1, 0.5, 0}")
    args = ap.parse_args()

    semillas = list(SEMILLAS[args.conjunto])[: args.n] if args.n else list(SEMILLAS[args.conjunto])
    claves = args.estrategias.split(",")
    SALIDA.mkdir(exist_ok=True)

    base = Configuracion()
    base.fallas = replace(base.fallas,
                          prob_foco=base.fallas.prob_foco if args.prob_foco is None else args.prob_foco,
                          n_fallas=base.fallas.n_fallas if args.n_fallas is None else args.n_fallas)
    if args.presupuesto is not None:
        base.preferencias = replace(base.preferencias, presupuesto_extra=args.presupuesto)
    cambios = {}
    if args.n_uav is not None:
        cambios["n_uav"] = args.n_uav
    if args.separacion is not None:
        cambios["separacion_km"] = args.separacion
    if args.alcance is not None:
        cambios["alcance_com_km"] = args.alcance or None
    if args.prob_deteccion is not None:
        cambios["prob_deteccion"] = args.prob_deteccion
    base = configurar(base, **cambios)

    def etiqueta(cfg: Configuracion) -> str:
        return (f"{args.conjunto}_u{cfg.flota.n_uav}_pd{cfg.flota.prob_deteccion}"
                f"_pf{cfg.fallas.prob_foco}_nf{cfg.fallas.n_fallas}_b{cfg.preferencias.presupuesto_extra}")

    if not args.sensibilidad:
        res = correr(base, semillas, claves, etiqueta(base))
        imprimir(res)
        (SALIDA / f"flota_{res['etiqueta']}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    todos = []
    for pd in (1.0, 0.5, 0.0):
        for n in (3, 4, 5):
            cfg = configurar(base, n_uav=n, prob_deteccion=pd)
            res = correr(cfg, semillas, claves, etiqueta(cfg))
            imprimir(res)
            todos.append(res)
    nombre = f"flota_sensibilidad_{args.conjunto}_pf{base.fallas.prob_foco}_nf{base.fallas.n_fallas}.json"
    (SALIDA / nombre).write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

"""Caso de ejemplo de la Tarea 3 (punto 9): ruta alternativa frente a una amenaza.

1. Etapa 1: inicio -> destino de la misión con el perfil "Inspección de daños" y las cuatro técnicas,
   con R_min = R_MIN_CASO: sin la amenaza la ruta más corta ya cumple, así que las técnicas parten de
   la misma ruta y lo que cambie después se debe solo a la amenaza.
2. Etapa 2: aparece una zona de amenaza abstracta (disco de RADIO_M con p = P_ZONA) centrada en el
   punto que está a la mitad de la ruta de pgr_dijkstra en metros. El centro se CALCULA, no se elige a
   mano. pgr_dijkstra en metros, que solo mira la distancia, la sigue cruzando; las técnicas que
   consideran amenazas toman una alternativa.
3. Sorteo ilustrativo: la primera semilla del rango de sorteos en que la ruta de pgr_dijkstra (m) no
   completa la misión y la del MILP sí. Se rotula así ("elegido para ilustrar"); las cifras de
   resiliencia, en cambio, son las de los 300 sorteos, no las de esa semilla.
4. Se verifica que se cumplen los objetivos iniciales: evitar la amenaza sin violar la autonomía ni la
   fiabilidad mínima, con más resiliencia que la ruta más corta.

Salida: BD/salida/caso_ejemplo.json (estructura en BD/ESTRUCTURA_caso_ejemplo_json.md), que el sitio carga
con el botón "Cargar caso de ejemplo". Uso (dentro del contenedor app):  python BD/caso_ejemplo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from comun.ajustes import ahora_utc, centro_aoi, guardar_json  # noqa: E402
from comun.bd import conectar  # noqa: E402
from comun.servicio import mision_bd, resolver_t3, sortear_t3  # noqa: E402
from ruteo.config import PERFILES, SEMILLAS, Preferencias  # noqa: E402
from ruteo.geo import ProyeccionLocal, dist_punto_segmento, haversine_km  # noqa: E402
from ruteo.probabilidad import ZonaAmenaza  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "caso_ejemplo.json"
PERFIL = "inspeccion"
R_MIN_CASO = 0.70
RADIO_M = 400.0
P_ZONA = 0.6
CON_AMENAZAS = ("milp_gurobi", "dijkstra_ponderado", "aco")


def punto_a_mitad(coords: list[list[float]]) -> tuple[float, float]:
    """Punto de la polilínea [[lat, lon], ...] a la mitad de su largo."""
    tramos = [haversine_km(*a, *b) for a, b in zip(coords, coords[1:])]
    objetivo, acumulado = sum(tramos) / 2, 0.0
    for (a, b), largo in zip(zip(coords, coords[1:]), tramos):
        if acumulado + largo >= objetivo:
            f = (objetivo - acumulado) / largo if largo else 0.0
            return round(a[0] + f * (b[0] - a[0]), 6), round(a[1] + f * (b[1] - a[1]), 6)
        acumulado += largo
    return tuple(coords[-1])


def cruza(coords: list[list[float]], zona: ZonaAmenaza) -> bool:
    proy = ProyeccionLocal(*centro_aoi())
    c = proy.a_xy(zona.lat, zona.lon)
    xy = [proy.a_xy(lat, lon) for lat, lon in coords]
    return any(dist_punto_segmento(c, a, b) <= zona.radio_km for a, b in zip(xy, xy[1:]))


def resumen(res: dict, zona: ZonaAmenaza) -> dict:
    salida = {}
    for t in res["tecnicas"]:
        if "coordenadas" not in t:
            salida[t["clave"]] = {"error": t["error"]}
            continue
        salida[t["clave"]] = {k: t.get(k) for k in ("largo_km", "fiabilidad", "resiliencia", "sin_recuperar",
                                                     "tiempo_ms", "cumple_autonomia", "cumple_fiabilidad")}
        salida[t["clave"]]["cruza_zona"] = cruza(t["coordenadas"], zona)
    return {"tecnicas": salida, "mas_resiliente": res.get("mas_resiliente"),
            "autonomia_km": res["autonomia_km"], "r_min": res["r_min"]}


def main() -> None:
    valores = {k: v for k, v in PERFILES[PERFIL].items() if k != "nombre"}
    prefs = Preferencias(**{**valores, "prob_exito_min": R_MIN_CASO})
    with conectar() as conn:
        mision = mision_bd(conn)
        s, t = mision[0], mision[-1]
        o, d = (conn.execute("SELECT ST_Y(geom), ST_X(geom) FROM nodos WHERE id = %s", (n,)).fetchone() for n in (s, t))
        etapa1 = resolver_t3(conn, [s, t], prefs, guardar=False)
        if "error" in etapa1:
            raise SystemExit(etapa1["error"])
        corta = next(x for x in etapa1["tecnicas"] if x["clave"] == "dijkstra_m")
        lat, lon = punto_a_mitad(corta["coordenadas"])
        zona = ZonaAmenaza(lat, lon, RADIO_M / 1000, P_ZONA)
        etapa2 = resolver_t3(conn, [s, t], prefs, zonas_amenaza=[zona], guardar=True)
        rutas = {x["clave"]: x["nodos"] for x in etapa2["tecnicas"] if "nodos" in x}
        elegido, sorteo = None, None
        for semilla in list(SEMILLAS["sorteos"])[:500]:
            so = sortear_t3(conn, [s, t], semilla, prefs, zonas_amenaza=[zona], rutas_nodos=rutas,
                            lambda_km=etapa2["lambda_recuperacion_km"])
            pt = so["por_tecnica"]
            if not pt["dijkstra_m"]["recuperacion"]["exito"] and pt["milp_gurobi"]["recuperacion"]["exito"]:
                elegido, sorteo = semilla, so
                break

    r1, r2 = resumen(etapa1, zona), resumen(etapa2, zona)
    t2 = r2["tecnicas"]
    mejor = r2["mas_resiliente"]
    objetivos = [
        {"texto": "Las tres técnicas que consideran amenazas toman una ruta que no cruza la zona.",
         "cumple": all(not t2[k].get("cruza_zona", True) for k in CON_AMENAZAS)},
        {"texto": "pgr_dijkstra en metros, que solo mira la distancia, sigue cruzando la zona.",
         "cumple": bool(t2["dijkstra_m"].get("cruza_zona"))},
        {"texto": f"La ruta más resiliente ({mejor}) cumple la autonomía y la fiabilidad mínima R_min = {prefs.prob_exito_min}.",
         "cumple": bool(mejor and t2[mejor].get("cumple_autonomia") and t2[mejor].get("cumple_fiabilidad"))},
        {"texto": "La más resiliente supera la resiliencia de pgr_dijkstra en metros frente a la misma amenaza.",
         "cumple": bool(mejor and (t2[mejor].get("resiliencia") or 0) > (t2["dijkstra_m"].get("resiliencia") or 0))},
    ]
    datos = {
        "tipo": "caso_ejemplo_t3",
        "generado_utc": ahora_utc(),
        "descripcion": (f"Inicio → destino de la misión (nodos {s} → {t}), perfil «{PERFILES[PERFIL]['nombre']}». "
                        f"R_min = {R_MIN_CASO}: sin la amenaza la ruta más corta ya cumple. Etapa 2: zona de amenaza abstracta "
                        f"de {RADIO_M:.0f} m con p = {P_ZONA} centrada en la mitad "
                        "de la ruta de pgr_dijkstra (m)."),
        "perfil": PERFIL,
        "preferencias": etapa2["preferencias"],
        "origen": {"nodo": s, "lat": round(o[0], 6), "lon": round(o[1], 6)},
        "destino": {"nodo": t, "lat": round(d[0], 6), "lon": round(d[1], 6)},
        "zona_amenaza": {"lat": lat, "lon": lon, "radio_m": RADIO_M, "p": P_ZONA,
                         "criterio": "centro en el punto a la mitad de la ruta de pgr_dijkstra (m) de la etapa 1"},
        "etapa1": r1,
        "etapa2": r2,
        "sorteo": {"semilla": elegido,
                   "criterio": "elegido para ilustrar: primera semilla en que pgr_dijkstra (m) no completa y el MILP sí",
                   "por_tecnica": ({k: {"intacta": v["intacta"], "exito": v["recuperacion"]["exito"],
                                        "motivo": v["recuperacion"]["motivo"]} for k, v in sorteo["por_tecnica"].items()}
                                   if sorteo else None)},
        "objetivos": objetivos,
        "id_evaluacion": etapa2.get("id_evaluacion"),
    }
    guardar_json(SALIDA, datos)
    print(f"Caso de ejemplo {s} -> {t}; zona en ({lat}, {lon}), r = {RADIO_M:.0f} m, p = {P_ZONA}")
    for etapa, r in (("etapa 1", r1), ("etapa 2", r2)):
        print(f"  {etapa} (más resiliente: {r['mas_resiliente']})")
        for k, v in r["tecnicas"].items():
            print(f"    {k:20} {v.get('largo_km')} km  F = {v.get('fiabilidad')}  R = {v.get('resiliencia')}"
                  f"  cruza la zona: {v.get('cruza_zona')}")
    print(f"  sorteo ilustrativo: semilla {elegido}")
    for o_ in objetivos:
        print(f"  [{'ok' if o_['cumple'] else 'NO'}] {o_['texto']}")
    print(f"-> {SALIDA}")


if __name__ == "__main__":
    main()

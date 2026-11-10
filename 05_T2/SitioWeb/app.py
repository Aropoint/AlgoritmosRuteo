"""Sitio web (Tareas 2 y 3): API + mapa Leaflet.

- GET  /                      página con el mapa (static/index.html)
- GET  /api/estado            tablas cargadas y fuentes
- GET  /api/capas/{nombre}    capas GeoJSON: aristas, nodos, mision, edificios, zonas_restringidas, gpsjam,
                              incendios, eventos
- GET  /api/preferencias      preferencias por defecto (rúbrica 6.2) y viento de la ventana
- GET  /api/ejemplo           rutas de ejemplo de la misión (BD/rutas_ejemplo.py: pgr_dijkstra y propuesta)
- POST /api/rutas             Tarea 2: 2 rutas Dijkstra + 2 de la propuesta (Yen) + resiliencia
- POST /api/flota             Tarea 2: 3 a 5 UAV sin aviso y con aviso compartido, animable

Tarea 3:
- GET  /api/t3/perfiles       perfiles de aplicación, casillas "Considerar" y parámetros de ACO por defecto
- POST /api/t3/rutas          las 4 técnicas (pgr_dijkstra en m, MILP Gurobi, pgr_dijkstra ponderado, ACO)
                              con tiempo de cómputo, fiabilidad y resiliencia (puntos 3, 5, 6 y 8)
- POST /api/t3/sorteo         sorteo 0-100 con semilla: qué falla y cómo se recupera cada ruta (punto 7)
- GET  /api/t3/caso_ejemplo   caso de ejemplo del punto 9 (BD/caso_ejemplo.py)

Uso (dentro del contenedor web):  uvicorn SitioWeb.app:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, fields
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from comun.bd import conectar  # noqa: E402
from comun.rutas import viento_bd  # noqa: E402
from comun.servicio import (mision_bd, nodo_mas_cercano, resolver, resolver_t3, simular_flota,  # noqa: E402
                            sortear_t3)
from ruteo.config import (AOI, PERFILES, Considerar, ParametrosACO, ParametrosFlota,  # noqa: E402
                          ParametrosResiliencia, Preferencias)
from ruteo.probabilidad import ZonaAmenaza  # noqa: E402

ESTATICO = Path(__file__).resolve().parent / "static"
EJEMPLO = BASE / "BD" / "salida" / "rutas_ejemplo.json"
CASO_EJEMPLO = BASE / "BD" / "salida" / "caso_ejemplo.json"

app = FastAPI(title="Ruteo resiliente de UAV", version="2.0")
app.mount("/static", StaticFiles(directory=ESTATICO), name="static")

# Cada capa es una consulta que devuelve (geometría GeoJSON, propiedades JSON).
CAPAS = {
    "aristas": """SELECT ST_AsGeoJSON(geom), json_build_object('id', id, 'largo_m', round(largo_m::numeric, 1),
                         'riesgo', riesgo, 'r_eventos', r_eventos, 'r_incendios', r_incendios, 'p_gnss', p_gnss,
                         'pf_eventos', pf_eventos, 'pf_incendios', pf_incendios, 'pf_gnss', pf_gnss,
                         'pf_total', pf_total, 'altura_max_edificio_m', altura_max_edificio_m,
                         'terreno_max_m', terreno_max_m, 'en_zona_restringida', en_zona_restringida)
                  FROM aristas""",
    "nodos": """SELECT ST_AsGeoJSON(geom), json_build_object('id', id, 'tipo', tipo, 'elevacion_m', elevacion_m,
                       'pf_eventos', pf_eventos, 'pf_incendios', pf_incendios, 'pf_gnss', pf_gnss, 'pf_total', pf_total)
                FROM nodos""",
    "zonas_restringidas": """SELECT ST_AsGeoJSON(geom), json_build_object('osm_id', osm_id, 'clase', clase,
                                    'nombre', nombre, 'buffer_m', buffer_m)
                             FROM meta_zonas_restringidas""",
    "mision": """SELECT ST_AsGeoJSON(n.geom), json_build_object('id', n.id, 'orden', m.orden, 'rol', m.rol,
                        'elevacion_m', n.elevacion_m)
                 FROM mision m JOIN nodos n ON n.id = m.nodo_id""",
    "edificios": """SELECT ST_AsGeoJSON(ST_SimplifyPreserveTopology(geom, 0.00001), 6),
                           json_build_object('osm_id', osm_id, 'tipo', tipo_edificio, 'altura_m', altura_estimada_m,
                                             'origen_altura', origen_altura)
                    FROM meta_edificios""",
    "gpsjam": """SELECT ST_AsGeoJSON(geom), json_build_object('h3', h3, 'dias_con_datos', dias_con_datos,
                        'dias_rojos', dias_rojos, 'frac_dias_rojos', frac_dias_rojos, 'pct_malo_medio', pct_malo_medio,
                        'contiene_aoi', contiene_aoi)
                 FROM amz_gpsjam_celdas""",
    "incendios": """SELECT ST_AsGeoJSON(geom), json_build_object('fecha', fecha, 'periodo', periodo, 'guerra', guerra)
                    FROM amz_incendios WHERE guerra""",
    "eventos": """SELECT ST_AsGeoJSON(geom), json_build_object('id', id, 'fecha', fecha_inicio,
                         'tipo_violencia', tipo_violencia, 'muertes', muertes_estimadas, 'lugar', lugar)
                  FROM amz_eventos""",
}


class Punto(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class PreferenciasEntrada(BaseModel):
    """Preferencias del usuario; las que no se envían toman el valor por defecto de ruteo.config.Preferencias."""
    altura_vuelo_m: float | None = Field(None, gt=0, le=500)
    margen_vertical_m: float | None = Field(None, ge=0, le=100)
    respetar_zonas_restringidas: bool | None = None
    viento_max_m_s: float | None = Field(None, gt=0, le=60)
    velocidad_crucero_m_s: float | None = Field(None, gt=1, le=60)
    desvio_max: float | None = Field(None, ge=0, le=3)
    presupuesto_extra: float | None = Field(None, ge=0, le=3)
    peso_riesgo: float | None = Field(None, ge=0, le=10)
    autonomia_km: float | None = Field(None, gt=0, le=100)       # Tarea 3; vacío = (1 + beta) * misión mínima
    prob_exito_min: float | None = Field(None, gt=0, lt=1)       # Tarea 3: R_min


class SolicitudRutas(BaseModel):
    origen: Punto
    destino: Punto
    preferencias: PreferenciasEntrada = PreferenciasEntrada()
    n_fallas: int = Field(3, ge=1, le=10)
    n_escenarios: int = Field(100, ge=10, le=100)


class SolicitudFlota(BaseModel):
    """Secuencia simulada: origen, puntos de observación y destino.

    Cada parte que no se envía se toma de la misión de la BD, así que la flota **siempre** recorre
    puntos de observación: marcar origen y destino cambia de dónde sale y a dónde llega, no la
    inspección. Para cambiar los puntos intermedios se envía `puntos`; una lista vacía los quita.
    """
    origen: Punto | None = None
    destino: Punto | None = None
    puntos: list[Punto] | None = Field(None, max_length=8)
    preferencias: PreferenciasEntrada = PreferenciasEntrada()
    n_uav: int = Field(4, ge=3, le=5)
    separacion_km: float = Field(1.0, ge=0.1, le=5)
    prob_deteccion: float = Field(0.5, ge=0, le=1)
    alcance_com_km: float | None = Field(3.0, gt=0, le=20)
    n_fallas: int = Field(3, ge=1, le=10)
    n_escenarios: int = Field(30, ge=5, le=100)
    semilla: int | None = None


class ZonaProhibidaEntrada(BaseModel):
    """Polígono dibujado por el usuario: ningún tramo que lo toque es sobrevolable (punto 2)."""
    vertices: list[Punto] = Field(min_length=3, max_length=60)


class ZonaAmenazaEntrada(BaseModel):
    """Disco abstracto dibujado por el usuario con su probabilidad de falla (puntos 5 y 9)."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radio_m: float = Field(gt=10, le=3000)
    p: float = Field(gt=0, lt=1)


class ConsiderarEntrada(BaseModel):
    """Casillas "Considerar" del panel de control (punto 4); las que no se envían quedan activas."""
    edificios: bool | None = None
    relieve: bool | None = None
    viento: bool | None = None
    zonas_publicadas: bool | None = None
    eventos: bool | None = None
    incendios: bool | None = None
    gnss: bool | None = None
    zonas_usuario: bool | None = None


class ACOEntrada(BaseModel):
    n_hormigas: int | None = Field(None, ge=2, le=200)
    iteraciones: int | None = Field(None, ge=1, le=400)
    alfa: float | None = Field(None, ge=0, le=10)
    beta: float | None = Field(None, ge=0, le=10)
    gamma: float | None = Field(None, ge=0, le=10)
    rho: float | None = Field(None, gt=0, lt=1)
    semilla: int | None = Field(None, ge=0, le=10**9)


class SolicitudT3(BaseModel):
    """Consulta de la Tarea 3: destino (y puntos intermedios opcionales) más las restricciones del usuario."""
    origen: Punto
    destino: Punto
    puntos: list[Punto] = Field(default_factory=list, max_length=8)
    preferencias: PreferenciasEntrada = PreferenciasEntrada()
    considerar: ConsiderarEntrada = ConsiderarEntrada()
    zonas_prohibidas: list[ZonaProhibidaEntrada] = Field(default_factory=list, max_length=10)
    zonas_amenaza: list[ZonaAmenazaEntrada] = Field(default_factory=list, max_length=10)
    aco: ACOEntrada = ACOEntrada()
    n_sorteos: int = Field(300, ge=0, le=2000)
    prob_deteccion: float = Field(0.5, ge=0, le=1)   # prob. de notar una falla antes de entrar (punto 8)


class SolicitudSorteo(SolicitudT3):
    semilla: int = Field(ge=0, le=10**9)
    rutas: dict[str, list[int]] | None = None        # nodos de la ruta de cada técnica, tal como los mostró el sitio
    lambda_recuperacion_km: float | None = Field(None, ge=0, le=1e5)


def _preferencias(entrada: PreferenciasEntrada) -> Preferencias:
    valores = {k: v for k, v in entrada.model_dump().items() if v is not None}
    return Preferencias(**{f.name: valores.get(f.name, getattr(Preferencias(), f.name)) for f in fields(Preferencias)})


def _desde(clase, entrada: BaseModel):
    """Dataclass con los valores enviados y el resto por defecto."""
    valores = {k: v for k, v in entrada.model_dump().items() if v is not None}
    return clase(**valores)


def _consulta_t3(conn, solicitud: SolicitudT3) -> dict:
    nodo = lambda p: nodo_mas_cercano(conn, p.lat, p.lon)
    secuencia: list[int] = []
    for n in [nodo(solicitud.origen), *(nodo(p) for p in solicitud.puntos), nodo(solicitud.destino)]:
        if not secuencia or secuencia[-1] != n:
            secuencia.append(n)
    if len(secuencia) < 2:
        raise HTTPException(422, "El origen y el destino caen sobre el mismo nodo: sepáralos más.")
    if len(set(secuencia)) != len(secuencia):
        raise HTTPException(422, "Dos puntos de la misión caen sobre el mismo nodo del grafo; muévelos o quita uno.")
    return {
        "secuencia": secuencia,
        "prefs": _preferencias(solicitud.preferencias),
        "considerar": _desde(Considerar, solicitud.considerar),
        "zonas_prohibidas": [[(v.lat, v.lon) for v in z.vertices] for z in solicitud.zonas_prohibidas],
        "zonas_amenaza": [ZonaAmenaza(z.lat, z.lon, z.radio_m / 1000, z.p) for z in solicitud.zonas_amenaza],
        "params_aco": _desde(ParametrosACO, solicitud.aco),
    }


@app.get("/")
def inicio():
    return FileResponse(ESTATICO / "index.html")


@app.get("/api/estado")
def estado():
    with conectar() as conn:
        conteos = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in (
            "nodos", "aristas", "mision", "meta_edificios", "meta_elevacion", "meta_viento",
            "amz_gpsjam_celdas", "amz_incendios", "amz_eventos", "rutas", "evaluaciones")}
        fuentes = [dict(zip(("clave", "tipo", "nombre", "licencia", "descargado_utc"), f)) for f in conn.execute(
            "SELECT clave, tipo, nombre, licencia, descargado_utc::text FROM fuentes ORDER BY tipo, clave")]
    return {"aoi": AOI, "conteos": conteos, "fuentes": fuentes}


@app.get("/api/capas/{nombre}")
def capa(nombre: str):
    if nombre not in CAPAS:
        raise HTTPException(404, f"Capa desconocida: {nombre}")
    with conectar() as conn:
        filas = conn.execute(CAPAS[nombre]).fetchall()
    return {"type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": json.loads(g), "properties": p} for g, p in filas]}


@app.get("/api/preferencias")
def preferencias():
    prefs = Preferencias()
    with conectar() as conn:
        _, viento = viento_bd(conn, prefs.altura_vuelo_m)
    return {"preferencias": asdict(prefs), "viento": viento}


@app.get("/api/ejemplo")
def ejemplo():
    if not EJEMPLO.exists():
        return JSONResponse({"error": "Aún no se generan las rutas de ejemplo (BD/rutas_ejemplo.py)."}, status_code=404)
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


@app.post("/api/rutas")
def rutas(solicitud: SolicitudRutas):
    prefs = _preferencias(solicitud.preferencias)
    with conectar() as conn:
        s = nodo_mas_cercano(conn, solicitud.origen.lat, solicitud.origen.lon)
        t = nodo_mas_cercano(conn, solicitud.destino.lat, solicitud.destino.lon)
        resultado = resolver(conn, s, t, prefs, n_escenarios=solicitud.n_escenarios, n_fallas=solicitud.n_fallas)
    if "error" in resultado and "dijkstra" not in resultado:
        raise HTTPException(422, resultado["error"])
    return resultado


def _secuencia_flota(conn, solicitud: SolicitudFlota) -> list[int]:
    """Origen, puntos de observación y destino; lo que no venga en la solicitud lo pone la misión.

    Así, marcar origen y destino nunca borra la inspección: la flota sigue pasando por los puntos
    intermedios. Dos marcas que caen sobre el mismo nodo del grafo se colapsan en una.
    """
    mision = mision_bd(conn)
    if len(mision) < 2:
        raise HTTPException(422, "La misión de la base de datos no tiene inicio y destino.")
    nodo = lambda p: nodo_mas_cercano(conn, p.lat, p.lon)
    inicio = nodo(solicitud.origen) if solicitud.origen else mision[0]
    fin = nodo(solicitud.destino) if solicitud.destino else mision[-1]
    medios = [nodo(p) for p in solicitud.puntos] if solicitud.puntos is not None else mision[1:-1]

    secuencia: list[int] = []
    for n in [inicio, *medios, fin]:
        if not secuencia or secuencia[-1] != n:  # marcas contiguas sobre el mismo nodo
            secuencia.append(n)
    if len(secuencia) < 2:
        raise HTTPException(422, "El origen y el destino caen sobre el mismo nodo: sepáralos más.")
    if len(set(secuencia)) != len(secuencia):
        raise HTTPException(422, "Dos puntos de la misión caen sobre el mismo nodo del grafo; "
                                 "muévelos o quita uno.")
    return secuencia


@app.post("/api/flota")
def flota(solicitud: SolicitudFlota):
    prefs = _preferencias(solicitud.preferencias)
    params = ParametrosFlota(n_uav=solicitud.n_uav, separacion_km=solicitud.separacion_km,
                             alcance_com_km=solicitud.alcance_com_km, prob_deteccion=solicitud.prob_deteccion)
    with conectar() as conn:
        secuencia = _secuencia_flota(conn, solicitud)
        editada = secuencia != mision_bd(conn)
        resultado = simular_flota(conn, secuencia, prefs, params, n_fallas=solicitud.n_fallas,
                                  n_escenarios=solicitud.n_escenarios, semilla=solicitud.semilla)
    if "error" in resultado:
        raise HTTPException(422, resultado["error"])
    resultado["secuencia_editada"] = editada
    return resultado


# ---------------------------------------------------------------------------
# Tarea 3
# ---------------------------------------------------------------------------

@app.get("/api/t3/perfiles")
def perfiles_t3():
    return {"perfiles": PERFILES, "preferencias": asdict(Preferencias()), "considerar": asdict(Considerar()),
            "aco": asdict(ParametrosACO()), "resiliencia": asdict(ParametrosResiliencia())}


@app.post("/api/t3/rutas")
def rutas_t3(solicitud: SolicitudT3):
    with conectar() as conn:
        c = _consulta_t3(conn, solicitud)
        resultado = resolver_t3(conn, c["secuencia"], c["prefs"], c["considerar"], c["zonas_prohibidas"],
                                c["zonas_amenaza"], c["params_aco"],
                                ParametrosResiliencia(solicitud.n_sorteos, solicitud.prob_deteccion))
    if "error" in resultado and "tecnicas" not in resultado:
        raise HTTPException(422, resultado["error"])
    return resultado


@app.post("/api/t3/sorteo")
def sorteo_t3(solicitud: SolicitudSorteo):
    with conectar() as conn:
        c = _consulta_t3(conn, solicitud)
        resultado = sortear_t3(conn, c["secuencia"], solicitud.semilla, c["prefs"], c["considerar"],
                               c["zonas_prohibidas"], c["zonas_amenaza"], solicitud.rutas,
                               solicitud.lambda_recuperacion_km, c["params_aco"], solicitud.prob_deteccion)
    if "error" in resultado:
        raise HTTPException(422, resultado["error"])
    return resultado


@app.get("/api/t3/caso_ejemplo")
def caso_ejemplo_t3():
    if not CASO_EJEMPLO.exists():
        return JSONResponse({"error": "Aún no se genera el caso de ejemplo (BD/caso_ejemplo.py)."}, status_code=404)
    return json.loads(CASO_EJEMPLO.read_text(encoding="utf-8"))

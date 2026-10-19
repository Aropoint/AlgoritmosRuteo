"""Sitio web (rúbrica punto 7, 8 y criterio 11): API + mapa Leaflet.

- GET  /                      página con el mapa (static/index.html)
- GET  /api/estado            tablas cargadas y fuentes
- GET  /api/capas/{nombre}    capas GeoJSON: aristas, mision, edificios, gpsjam, incendios, eventos
- GET  /api/preferencias      preferencias por defecto (rúbrica 6.2) y viento de la ventana
- GET  /api/ejemplo           rutas de ejemplo de la misión (BD/rutas_ejemplo.py: pgr_dijkstra y propuesta)
- POST /api/rutas             (origen, destino, preferencias) -> 2 rutas Dijkstra + 2 de la propuesta + resiliencia

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
from comun.servicio import nodo_mas_cercano, resolver  # noqa: E402
from ruteo.config import AOI, Preferencias  # noqa: E402

ESTATICO = Path(__file__).resolve().parent / "static"
EJEMPLO = BASE / "BD" / "salida" / "rutas_ejemplo.json"

app = FastAPI(title="Ruteo resiliente de UAV", version="2.0")
app.mount("/static", StaticFiles(directory=ESTATICO), name="static")

# Cada capa es una consulta que devuelve (geometría GeoJSON, propiedades JSON).
CAPAS = {
    "aristas": """SELECT ST_AsGeoJSON(geom), json_build_object('id', id, 'largo_km', round(largo_km::numeric, 3),
                         'riesgo', riesgo, 'r_eventos', r_eventos, 'r_incendios', r_incendios, 'p_gnss', p_gnss,
                         'altura_max_edificio_m', altura_max_edificio_m, 'terreno_max_m', terreno_max_m)
                  FROM aristas""",
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


class SolicitudRutas(BaseModel):
    origen: Punto
    destino: Punto
    preferencias: PreferenciasEntrada = PreferenciasEntrada()
    n_fallas: int = Field(3, ge=1, le=10)
    n_escenarios: int = Field(100, ge=10, le=100)


def _preferencias(entrada: PreferenciasEntrada) -> Preferencias:
    valores = {k: v for k, v in entrada.model_dump().items() if v is not None}
    return Preferencias(**{f.name: valores.get(f.name, getattr(Preferencias(), f.name)) for f in fields(Preferencias)})


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

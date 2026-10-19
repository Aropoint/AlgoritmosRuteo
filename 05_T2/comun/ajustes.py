"""Parámetros compartidos del ETL: AOI, ventana temporal, rutas y archivos JSON.

Las fechas son fijas (no "hoy") para que la descarga sea reproducible. Se
cambian con variables de entorno; ver .env.example en la raíz del repo.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # 05_T2
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from ruteo.config import AOI  # noqa: E402

# Descargas crudas reutilizables (CSV de GPSJam, The Economist, UCDP). Git las ignora.
CACHE = BASE / ".cache"
INFRAESTRUCTURA_JSON = BASE / "Infraestructura" / "salida" / "infraestructura.json"


def _fecha(nombre: str, defecto: str) -> date:
    return date.fromisoformat(os.getenv(nombre, defecto))


FECHA_CORTE = _fecha("FECHA_CORTE", "2024-12-31")            # fin del período histórico
INICIO_HISTORICO = _fecha("INICIO_HISTORICO", "2022-02-24")  # inicio de la invasión a gran escala
VENTANA_DIAS = int(os.getenv("VENTANA_DIAS", "30"))          # GPSJam y viento: días que terminan en el corte
DIAS_EVALUACION = int(os.getenv("DIAS_EVALUACION", "180"))   # incendios posteriores al corte: focos de fallas
BUFFER_KM = float(os.getenv("BUFFER_KM", "5"))               # margen alrededor del AOI para las amenazas


def inicio_ventana() -> date:
    return FECHA_CORTE - timedelta(days=VENTANA_DIAS - 1)


def fin_evaluacion() -> date:
    return FECHA_CORTE + timedelta(days=DIAS_EVALUACION)


def bbox(buffer_km: float = 0.0) -> tuple[float, float, float, float]:
    """(sur, oeste, norte, este) del AOI, ampliado en buffer_km por lado."""
    lat0 = (AOI["sur"] + AOI["norte"]) / 2
    dlat = buffer_km / 111.32
    dlon = buffer_km / (111.32 * math.cos(math.radians(lat0)))
    return AOI["sur"] - dlat, AOI["oeste"] - dlon, AOI["norte"] + dlat, AOI["este"] + dlon


def centro_aoi() -> tuple[float, float]:
    return (AOI["sur"] + AOI["norte"]) / 2, (AOI["oeste"] + AOI["este"]) / 2


def en_bbox(lat: float, lon: float, caja: tuple[float, float, float, float]) -> bool:
    sur, oeste, norte, este = caja
    return sur <= lat <= norte and oeste <= lon <= este


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def guardar_json(ruta: Path, datos, compacto: bool = False) -> Path:
    """compacto=True para archivos grandes (edificios, incendios): sin sangría."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":")) if compacto \
        else json.dumps(datos, ensure_ascii=False, indent=1)
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def leer_json(ruta: Path):
    if not ruta.exists():
        raise SystemExit(f"No existe {ruta}. Ejecuta primero el script de extracción correspondiente.")
    return json.loads(ruta.read_text(encoding="utf-8"))


def relativa(ruta: Path) -> str:
    """Ruta relativa a 05_T2, para registrar de qué archivo salió cada carga."""
    return ruta.resolve().relative_to(BASE).as_posix()

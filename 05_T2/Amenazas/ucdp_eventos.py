"""Amenaza 3: eventos de violencia organizada cerca del AOI (UCDP GED, vía HDX) -> JSON.

UCDP (Uppsala Conflict Data Program) georreferencia cada evento con su fecha,
tipo de violencia, víctimas estimadas y precisión del lugar. Se usa el CSV de
Ucrania publicado en HDX (sin credenciales), filtrado al AOI + BUFFER_KM, al
período [INICIO_HISTORICO, FECHA_CORTE] y a eventos con lugar preciso
(where_prec <= PRECISION_MAX: 1 = lugar exacto, 2 = a menos de 25 km).

Uso en el ruteo (peso, rúbrica 5.2): densidad de eventos alrededor de cada tramo -> r_eventos.
Alternativa con más detalle (subtipo "Air/drone strike"): ACLED, que exige cuenta de nivel Research.

Uso (dentro del contenedor app):  python Amenazas/ucdp_eventos.py [--refrescar]
Salida: Amenazas/salida/ucdp_eventos.json (estructura en ESTRUCTURA_ucdp_eventos_json.md)
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun.ajustes import (BUFFER_KM, CACHE, FECHA_CORTE, INICIO_HISTORICO, ahora_utc, bbox,  # noqa: E402
                           en_bbox, guardar_json)
from comun.red import descargar, descargar_a_archivo  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "salida" / "ucdp_eventos.json"
PAQUETE_HDX = "https://data.humdata.org/api/3/action/package_show?id=ucdp-data-for-ukraine"
PRECISION_MAX = int(os.getenv("UCDP_PRECISION_MAX", "2"))


def url_csv() -> str:
    """URL vigente del CSV según la API de HDX (cambia cuando HDX publica una versión nueva)."""
    paquete = json.loads(descargar(PAQUETE_HDX))["result"]
    for recurso in paquete["resources"]:
        if recurso.get("format", "").upper() == "CSV" or recurso["url"].endswith(".csv"):
            return recurso["url"]
    raise SystemExit("HDX no lista un CSV en el paquete ucdp-data-for-ukraine.")


def _entero(valor: str) -> int | None:
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return None


def main() -> None:
    url = url_csv()
    archivo = descargar_a_archivo(url, CACHE / "ucdp" / "conflict_data_ukr.csv", refrescar="--refrescar" in sys.argv)
    caja = bbox(BUFFER_KM)
    eventos, leidas, imprecisos = [], 0, 0
    with archivo.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            if fila.get("id", "").startswith("#"):  # fila de etiquetas HXL, si la hubiera
                continue
            leidas += 1
            try:
                lat, lon = float(fila["latitude"]), float(fila["longitude"])
                inicio = date.fromisoformat(fila["date_start"][:10])
            except (KeyError, ValueError):
                continue
            if not en_bbox(lat, lon, caja) or not (INICIO_HISTORICO <= inicio <= FECHA_CORTE):
                continue
            precision = _entero(fila.get("where_prec"))
            if precision is None or precision > PRECISION_MAX:
                imprecisos += 1
                continue
            eventos.append({
                "id": _entero(fila["id"]),
                "fecha_inicio": inicio.isoformat(),
                "fecha_fin": fila.get("date_end", "")[:10] or None,
                "tipo_violencia": _entero(fila.get("type_of_violence")),
                "precision_lugar": precision,
                "precision_fecha": _entero(fila.get("date_prec")),
                "muertes_estimadas": _entero(fila.get("best")),
                "adm1": fila.get("adm_1") or None,
                "adm2": fila.get("adm_2") or None,
                "lugar": fila.get("where_coordinates") or None,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
            })

    salida = {
        "tipo": "amenaza_eventos_ucdp",
        "crs": "EPSG:4326",
        "metadatos": {
            "fuente": "UCDP Georeferenced Event Dataset (GED), Ucrania, vía HDX",
            "url": url,
            "licencia": "CC BY-IGO según HDX (UCDP: CC BY 4.0). Citar Sundberg y Melander (2013) y Davies et al.",
            "generado_utc": ahora_utc(),
            "parametros": {"bbox": dict(zip(("sur", "oeste", "norte", "este"), caja)), "buffer_km": BUFFER_KM,
                           "desde": INICIO_HISTORICO.isoformat(), "hasta": FECHA_CORTE.isoformat(),
                           "precision_lugar_max": PRECISION_MAX},
            "conteos": {"filas_leidas": leidas, "eventos": len(eventos), "descartados_por_precision": imprecisos},
            "advertencias": [
                "El CSV de HDX llega hasta 2024-12-31; fechas de corte posteriores no agregan eventos.",
                "Eventos con la misma localidad comparten coordenadas (centroide del lugar).",
                "UCDP registra eventos con al menos una víctima mortal: no cubre todos los ataques.",
            ],
        },
        "eventos": eventos,
    }
    guardar_json(SALIDA, salida)
    print(f"{len(eventos)} eventos en el AOI ({imprecisos} descartados por precisión) de {leidas} filas -> {SALIDA}")


if __name__ == "__main__":
    main()

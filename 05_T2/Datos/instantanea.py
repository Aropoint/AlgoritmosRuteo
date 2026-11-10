"""Instantánea versionada de los JSON descargados (Tarea 3, punto 1: replicar la ejecución desde GitLab).

Los JSON de Metadata/salida/ y Amenazas/salida/ se regeneran descargando de seis APIs públicas, pero
Overpass llegó a tardar 614 s y a responder HTTP 502. Para que `docker compose up` desde un clon limpio
reproduzca exactamente la misma BD que se muestra en el video, se versiona una copia comprimida de esos
JSON en Datos/instantanea/, con un MANIFIESTO.json (tamaño, SHA-256 y fecha de cada descarga).

    python Datos/instantanea.py crear       # salida/*.json -> Datos/instantanea/*.json.gz + MANIFIESTO.json
    python Datos/instantanea.py restaurar   # Datos/instantanea/*.json.gz -> salida/*.json (verifica el SHA-256)

pipeline.py --instantanea ejecuta "restaurar" antes de cargar y omite las descargas; main.py lo usa
cuando USAR_INSTANTANEA=1 (valor por defecto en docker-compose.yml). Con USAR_INSTANTANEA=0 se descarga
todo de nuevo.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # 05_T2
CARPETA = Path(__file__).resolve().parent / "instantanea"
MANIFIESTO = CARPETA / "MANIFIESTO.json"
ARCHIVOS = [  # ruta relativa a 05_T2 del JSON que se versiona
    "Metadata/salida/osm_edificios.json",
    "Metadata/salida/elevacion.json",
    "Metadata/salida/viento.json",
    "Metadata/salida/zonas_restringidas.json",
    "Amenazas/salida/gpsjam.json",
    "Amenazas/salida/incendios_guerra.json",
    "Amenazas/salida/ucdp_eventos.json",
]


def _sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def _comprimido(relativo: str) -> Path:
    return CARPETA / (Path(relativo).name + ".gz")


def crear() -> None:
    CARPETA.mkdir(exist_ok=True)
    entradas = []
    for relativo in ARCHIVOS:
        origen = BASE / relativo
        if not origen.exists():
            raise SystemExit(f"Falta {relativo}: ejecuta primero el pipeline con descarga.")
        datos = origen.read_bytes()
        meta = json.loads(datos).get("metadatos", {})
        # mtime=0: el .gz no cambia si el JSON no cambia (git no ve diferencias falsas).
        _comprimido(relativo).write_bytes(gzip.compress(datos, compresslevel=9, mtime=0))
        entradas.append({"archivo": relativo, "comprimido": _comprimido(relativo).name, "bytes": len(datos),
                         "bytes_comprimido": _comprimido(relativo).stat().st_size, "sha256": _sha256(datos),
                         "fuente": meta.get("fuente"), "descargado_utc": meta.get("generado_utc"),
                         "licencia": meta.get("licencia")})
        print(f"  {relativo}: {len(datos) / 1e6:.2f} MB -> {_comprimido(relativo).stat().st_size / 1e6:.2f} MB")
    MANIFIESTO.write_text(json.dumps({"descripcion": __doc__.strip().splitlines()[0], "archivos": entradas},
                                     ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entradas)} archivos -> {CARPETA}")


def restaurar() -> None:
    if not MANIFIESTO.exists():
        raise SystemExit(f"No existe {MANIFIESTO}: no hay instantánea versionada.")
    entradas = json.loads(MANIFIESTO.read_text(encoding="utf-8"))["archivos"]
    for e in entradas:
        datos = gzip.decompress((CARPETA / e["comprimido"]).read_bytes())
        if _sha256(datos) != e["sha256"]:
            raise SystemExit(f"{e['comprimido']}: el SHA-256 no coincide con el MANIFIESTO (archivo dañado).")
        destino = BASE / e["archivo"]
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        print(f"  {e['archivo']} ({e['bytes'] / 1e6:.2f} MB, descargado {e['descargado_utc']})")
    print(f"{len(entradas)} archivos restaurados desde la instantánea (SHA-256 verificado).")


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    if accion == "crear":
        crear()
    elif accion == "restaurar":
        restaurar()
    else:
        raise SystemExit("Uso: python Datos/instantanea.py crear|restaurar")

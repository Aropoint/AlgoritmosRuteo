"""Descargas HTTP con reintentos, User-Agent identificable y caché en disco."""
from __future__ import annotations

import gzip
import time
from pathlib import Path

import requests

UA = {"User-Agent": "ruteo-uav-udp/2.0 (proyecto academico, curso Algoritmos de Ruteo)"}
REINTENTAR = {429, 500, 502, 503, 504}


class NoEncontrado(Exception):
    """HTTP 404: el recurso no existe (por ejemplo, un día sin archivo en GPSJam)."""


def descargar(url: str, params: dict | None = None, data: dict | None = None,
              timeout: int = 120, intentos: int = 4) -> bytes:
    """GET (o POST si hay `data`). Reintenta con espera creciente ante 429/5xx y errores de red."""
    ultimo: Exception | None = None
    for i in range(intentos):
        try:
            if data is None:
                r = requests.get(url, params=params, headers=UA, timeout=timeout)
            else:
                r = requests.post(url, params=params, data=data, headers=UA, timeout=timeout)
            if r.status_code == 404:
                raise NoEncontrado(url)
            if r.status_code in REINTENTAR:
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            contenido = r.content
            if contenido[:2] == b"\x1f\x8b":  # algunos servidores entregan gzip sin Content-Encoding
                contenido = gzip.decompress(contenido)
            return contenido
        except NoEncontrado:
            raise
        except requests.RequestException as e:
            ultimo = e
            espera = 10 * (i + 1)
            print(f"  aviso: {url} falló ({e}); reintento en {espera} s")
            time.sleep(espera)
    raise RuntimeError(f"No se pudo descargar {url}: {ultimo}")


def descargar_a_archivo(url: str, destino: Path, refrescar: bool = False, timeout: int = 300) -> Path:
    """Descarga en streaming (archivos grandes) y reutiliza la copia si ya existe."""
    if destino.exists() and destino.stat().st_size > 0 and not refrescar:
        print(f"  usando caché {destino.name}")
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".parcial")
    with requests.get(url, headers=UA, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with temporal.open("wb") as f:
            for bloque in r.iter_content(chunk_size=1 << 20):
                f.write(bloque)
    temporal.replace(destino)
    return destino

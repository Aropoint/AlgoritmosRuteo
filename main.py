"""Orquestador de la Tarea 2 (punto 9 del enunciado). Corre DENTRO de Docker: `docker compose up`
lo ejecuta en el servicio `main`; en el equipo solo hace falta Docker con Compose v2.

1. Ejecuta 05_T2/pipeline.py: esquema, infraestructura, descarga y carga de las 3 metadata y las
   3 amenazas, pesos, rutas de ejemplo (pgr_dijkstra y pgr_KSP) y diagrama de la BD.
2. Levanta el sitio web (FastAPI + Leaflet), que queda en http://localhost:8000 (o WEB_PORT).

Variables de entorno (en .env o antes del comando):
    SIN_DESCARGA=1   reutiliza los JSON ya generados (no llama a las APIs)
    SOLO_SITIO=1     no corre el pipeline: levanta el sitio sobre la BD existente

Uso, desde la raíz del repositorio:
    docker compose up --build            # todo
    docker compose run --rm pruebas      # pruebas unitarias
    docker compose down                  # detiene (los datos de la BD se conservan)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

APP = Path(os.environ.get("APP_DIR", "/app"))


def activa(nombre: str) -> bool:
    return os.environ.get(nombre, "").strip().lower() in {"1", "true", "si", "sí", "yes"}


def main() -> None:
    if not (APP / "pipeline.py").exists():
        sys.exit("main.py corre dentro de Docker. Desde la raíz del repositorio:  docker compose up --build")

    if activa("SOLO_SITIO"):
        print("SOLO_SITIO=1: se omite el pipeline y se usa la BD existente.", flush=True)
    else:
        comando = [sys.executable, "pipeline.py"] + (["--sin-descarga"] if activa("SIN_DESCARGA") else [])
        print("$", " ".join(["python", *comando[1:]]), flush=True)
        if subprocess.run(comando, cwd=APP).returncode != 0:
            sys.exit("El pipeline falló en un paso obligatorio; revisa el resumen de arriba.")

    print(f"\nSitio web: http://localhost:{os.environ.get('WEB_PORT', '8000')}"
          "  (detener: docker compose down)", flush=True)
    os.chdir(APP)
    os.execvp("uvicorn", ["uvicorn", "SitioWeb.app:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()

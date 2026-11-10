"""Orquestador de las Tareas 2 y 3. Corre DENTRO de Docker: `docker compose up` lo ejecuta en el
servicio `main`; en el equipo solo hace falta Docker con Compose v2.

1. Ejecuta pipeline.py (misma carpeta): esquema, infraestructura, metadata y amenazas (desde la
   instantánea versionada o descargándolas), pesos, probabilidad de falla de tramos y nodos, rutas de
   ejemplo, caso de ejemplo de la Tarea 3 y diagrama de la BD.
2. Levanta el sitio web (FastAPI + Leaflet), que queda en http://localhost:8000 (o WEB_PORT).

Variables de entorno (en .env o antes del comando):
    USAR_INSTANTANEA=1  (por defecto) restaura los JSON de Datos/instantanea/: misma BD que el video, sin red
    USAR_INSTANTANEA=0  descarga todo de las APIs (Overpass puede tardar más de 10 min)
    SIN_DESCARGA=1      con USAR_INSTANTANEA=0: reutiliza los JSON locales ya generados
    SOLO_SITIO=1        no corre el pipeline: levanta el sitio sobre la BD existente

Uso, desde esta carpeta (donde están main.py y docker-compose.yml):
    docker compose up --build            # todo
    docker compose run --rm pruebas      # pruebas unitarias
    docker compose down                  # detiene (los datos de la BD se conservan)
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent


def activa(nombre: str) -> bool:
    return os.environ.get(nombre, "").strip().lower() in {"1", "true", "si", "sí", "yes"}


def main() -> None:
    # pipeline.py está al lado también fuera de Docker: lo que distingue el contenedor es /.dockerenv
    if not Path("/.dockerenv").exists():
        sys.exit("main.py corre dentro de Docker. Desde esta carpeta:  docker compose up --build")

    if activa("SOLO_SITIO"):
        print("SOLO_SITIO=1: se omite el pipeline y se usa la BD existente.", flush=True)
    else:
        if activa("USAR_INSTANTANEA"):
            opcion = ["--instantanea"]
        else:
            opcion = ["--sin-descarga"] if activa("SIN_DESCARGA") else []
        comando = [sys.executable, "pipeline.py", *opcion]
        print("$", " ".join(["python", *comando[1:]]), flush=True)
        if subprocess.run(comando, cwd=APP).returncode != 0:
            sys.exit("El pipeline falló en un paso obligatorio; revisa el resumen de arriba.")

    print(f"\nSitio web: http://localhost:{os.environ.get('WEB_PORT', '8000')}"
          "  (detener: docker compose down)", flush=True)
    os.chdir(APP)
    os.execvp("uvicorn", ["uvicorn", "SitioWeb.app:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()

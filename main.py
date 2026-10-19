"""Orquestador de la Tarea 2 (punto 9 del enunciado): descarga, carga en la BD y sitio web, todo en Docker.

1. Crea .env con una contraseña aleatoria si no existe.
2. Levanta la BD (PostgreSQL 17 + PostGIS 3.5 + pgRouting 3.8) y espera a que esté sana.
3. Construye la imagen de la aplicación (05_T2/Dockerfile).
4. Ejecuta 05_T2/pipeline.py en el contenedor: esquema, infraestructura, 3 metadata,
   3 amenazas, cargas, pesos, rutas de ejemplo (pgr_dijkstra y pgr_KSP) y diagrama de la BD.
5. Levanta el sitio web en http://localhost:8000 (o WEB_PORT).

Uso:
    python main.py                  # todo
    python main.py --sin-descarga   # reutiliza los JSON ya generados (no llama a las APIs)
    python main.py --solo-sitio     # solo levanta la BD y el sitio
    python main.py --pruebas        # corre las pruebas unitarias en el contenedor
    python main.py --detener        # detiene los contenedores (los datos de la BD se conservan)

Requiere Docker con Compose v2. Este archivo solo usa la biblioteca estándar de Python.
"""
from __future__ import annotations

import argparse
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ENV = RAIZ / ".env"
ENV_EJEMPLO = RAIZ / ".env.example"


def compose(*args: str, check: bool = True) -> int:
    cmd = ["docker", "compose", *args]
    print("$", " ".join(cmd), flush=True)
    codigo = subprocess.run(cmd, cwd=RAIZ).returncode
    if check and codigo != 0:
        sys.exit(f"Falló: {' '.join(cmd)} (código {codigo})")
    return codigo


def preparar_env() -> None:
    if ENV.exists():
        return
    texto = ENV_EJEMPLO.read_text(encoding="utf-8").replace("CAMBIAR_ESTA_PASSWORD", secrets.token_urlsafe(18))
    ENV.write_text(texto, encoding="utf-8")
    print(f"Creado {ENV.name} con una contraseña aleatoria (no se sube al repositorio).")


def verificar_docker() -> None:
    if shutil.which("docker") is None:
        sys.exit("No se encontró Docker. Instala Docker Desktop (o Docker Engine con Compose v2).")
    if subprocess.run(["docker", "info"], capture_output=True).returncode != 0:
        sys.exit("Docker está instalado pero el motor no responde: abre Docker Desktop y espera a que diga 'Engine running'.")


def puerto_web() -> str:
    for linea in ENV.read_text(encoding="utf-8").splitlines():
        if linea.startswith("WEB_PORT="):
            return linea.split("=", 1)[1].strip() or "8000"
    return "8000"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sin-descarga", action="store_true")
    ap.add_argument("--solo-sitio", action="store_true")
    ap.add_argument("--pruebas", action="store_true")
    ap.add_argument("--detener", action="store_true")
    args = ap.parse_args()

    verificar_docker()
    if args.detener:
        compose("--profile", "tareas", "down")
        return
    preparar_env()

    compose("up", "-d", "--wait", "db")
    compose("--profile", "tareas", "build", "app")  # `web` usa la misma imagen
    if args.pruebas:
        compose("--profile", "tareas", "run", "--rm", "app", "python", "-m", "unittest", "discover", "-s", "tests", "-v")
        return
    if not args.solo_sitio:
        pipeline = ["--profile", "tareas", "run", "--rm", "app", "python", "pipeline.py"]
        if args.sin_descarga:
            pipeline.append("--sin-descarga")
        if compose(*pipeline, check=False) != 0:
            sys.exit("El pipeline falló en un paso obligatorio; revisa el resumen de arriba.")
    compose("up", "-d", "--force-recreate", "web")
    print(f"\nSitio web: http://localhost:{puerto_web()}")
    print("Detener todo: python main.py --detener")


if __name__ == "__main__":
    main()

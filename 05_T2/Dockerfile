# Imagen de la aplicación: ETL de metadata y amenazas, cargadores, ruteo y sitio web.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1

# graphviz dibuja el diagrama de la BD (rúbrica punto 0); librsvg2-bin aporta rsvg-convert, que
# rasteriza a PNG el SVG una vez que BD/diagrama_bd.py le reemplaza el trazado de las aristas.
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Por defecto corre las pruebas. docker-compose.yml (raíz) define los servicios que usan esta imagen:
# main (main.py: pipeline y sitio), pruebas y app (comandos sueltos).
CMD ["python", "-m", "unittest", "discover", "-s", "tests"]

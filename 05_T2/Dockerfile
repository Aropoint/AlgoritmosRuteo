# Imagen de la aplicación: ETL de metadata y amenazas, cargadores, ruteo y sitio web.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1

# graphviz: dibuja el diagrama de la BD (rúbrica punto 0)
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Por defecto corre las pruebas; main.py (raíz) invoca los demás comandos.
CMD ["python", "-m", "unittest", "discover", "-s", "tests"]

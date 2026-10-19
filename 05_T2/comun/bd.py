"""Conexión a PostgreSQL/PostGIS y registro de la procedencia de cada carga."""
from __future__ import annotations

import psycopg
from psycopg.types.json import Jsonb


def conectar() -> psycopg.Connection:
    """psycopg toma PGHOST, PGPORT, PGDATABASE, PGUSER y PGPASSWORD del entorno (docker-compose.yml)."""
    return psycopg.connect("")


def registrar_fuente(cur: psycopg.Cursor, clave: str, tipo: str, metadatos: dict, archivo: str) -> int:
    """Inserta o actualiza la fila de `fuentes` y devuelve su id.

    `metadatos` es el bloque `metadatos` del JSON: fuente, url, licencia,
    generado_utc y parametros (estructura común a todos los JSON del ETL).
    """
    cur.execute(
        """
        INSERT INTO fuentes (clave, tipo, nombre, url, licencia, descargado_utc, parametros, archivo_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (clave) DO UPDATE SET
            tipo = EXCLUDED.tipo, nombre = EXCLUDED.nombre, url = EXCLUDED.url,
            licencia = EXCLUDED.licencia, descargado_utc = EXCLUDED.descargado_utc,
            parametros = EXCLUDED.parametros, archivo_json = EXCLUDED.archivo_json,
            cargado_utc = now()
        RETURNING id
        """,
        (
            clave, tipo, metadatos.get("fuente"), metadatos.get("url"), metadatos.get("licencia"),
            metadatos.get("generado_utc"), Jsonb(metadatos.get("parametros", {})), archivo,
        ),
    )
    return cur.fetchone()[0]

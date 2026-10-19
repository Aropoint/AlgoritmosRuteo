"""Utilidades compartidas por el ETL, los cargadores, el pipeline y el sitio web.

- ajustes: AOI, fechas de corte, rutas de salida y lectura/escritura de JSON.
- transformar: transformaciones puras (solo biblioteca estándar, con pruebas).
- red: descargas HTTP con reintentos.
- bd: conexión a PostgreSQL y registro de fuentes.
- rutas: pgr_dijkstra (línea base) y pgr_KSP + selección resiliente (propuesta).
- resiliencia: métrica de resiliencia del par de rutas y diferencial entre métodos.
"""

"""Núcleo de ruteo físico resiliente de UAV (Tarea 2).

Módulos:
- geo: distancias y proyección local.
- grafo: grafo de navegación geolocalizado y malla sintética.
- pesos: restricciones y costos derivados de metadata y amenazas.
- algoritmos: Dijkstra, Yen y selección resiliente de pares de rutas.
- fallas: modelo de fallas espaciales reproducibles.
- simulador: ejecución de misiones con las estrategias comparadas.
- metricas: tasas de misión, disponibilidad de pares y diferenciales.

Solo usa la biblioteca estándar para que los experimentos puedan
reproducirse sin Docker; pgRouting replica la línea base en la BD.
"""

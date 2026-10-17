import os
import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("Define OPENWEATHER_API_KEY en el entorno antes de ejecutar esta prueba.")  # Crear cuenta gratuita en openweathermap.org
LAT, LON = -33.45, -70.66    # Coordenadas de Santiago

url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Extracción de parámetros clave
    viento_m_s = data.get("wind", {}).get("speed", 0)
    lluvia_mm_h = data.get("rain", {}).get("1h", 0)  # Lluvia en la última hora
    visibilidad_m = data.get("visibility", 10000)
    
    print("=== METADATA CLIMÁTICA ===")
    print(f"Velocidad del Viento: {viento_m_s} m/s")
    print(f"Precipitación: {lluvia_mm_h} mm/h")
    print(f"Visibilidad: {visibilidad_m} metros")
else:
    print(f"Error {response.status_code}: {response.text}")
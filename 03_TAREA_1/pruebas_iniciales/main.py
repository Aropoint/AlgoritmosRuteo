import os
import requests

API_KEY = os.getenv("OPENTOPOGRAPHY_API_KEY")
if not API_KEY:
    raise RuntimeError("Define OPENTOPOGRAPHY_API_KEY en el entorno antes de ejecutar esta prueba.")

API_URL = "https://portal.opentopography.org/API/globaldem"

params = {
    "demtype": "SRTMGL3",       # resolución 90m, suficiente para tu caso de uso
    "south": -33.6,
    "north": -33.3,
    "west": -70.8,
    "east": -70.5,
    "outputFormat": "GTiff",
    "API_Key": API_KEY
}

response = requests.get(API_URL, params=params)

if response.status_code == 200:
    with open("terreno.tif", "wb") as f:
        f.write(response.content)
    print("DEM descargado correctamente")
else:
    print("Error:", response.status_code, response.text)
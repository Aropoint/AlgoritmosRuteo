import pandas as pd
import numpy as np

# Simulación de consulta a base de datos espectral por coordenada
def obtener_ruido_base_dBm(lat, lon):
    # En zonas urbanas densas el ruido de fondo es mayor (-85 dBm) que en zonas rurales (-100 dBm)
    distancia_centro = np.sqrt((lat - (-33.45))**2 + (lon - (-70.66))**2)
    return -85.0 if distancia_centro < 0.1 else -100.0

# Parámetros del enlace UAV (Potencia recibida de señal útil P_r = -70 dBm, Sin Jammer activo)
P_r = -70.0  # dBm
lat_uav, lon_uav = -33.44, -70.65  # Zona urbana

N_bg_dBm = obtener_ruido_base_dBm(lat_uav, lon_uav)

# Convertir dBm a miliwatts para calcular SINR
P_r_mW = 10 ** (P_r / 10)
N_bg_mW = 10 ** (N_bg_dBm / 10)

SINR_real = 10 * np.log10(P_r_mW / N_bg_mW)

print("=== ITU / REGISTRO DE ESPECTRO: PRUEBA DE SINR ===")
print(f"Piso de ruido ambiental en ({lat_uav}, {lon_uav}): {N_bg_dBm} dBm")
print(f"Calidad del enlace (SINR sin Jammer): {SINR_real:.2f} dB")
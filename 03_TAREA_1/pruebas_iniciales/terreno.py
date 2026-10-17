import rasterio
import matplotlib.pyplot as plt
import numpy as np

# 1. Abrir el archivo GeoTIFF
with rasterio.open("terreno.tif") as dataset:
    # Leer la primera banda (matriz de elevación)
    elevacion = dataset.read(1)
    
    # Imprimir características clave del terreno
    print("=== METADATOS DEL TERRENO ===")
    print(f"Dimensiones de la grilla (Filas x Columnas): {elevacion.shape}")
    print(f"Sistema de Coordenadas (CRS): {dataset.crs}")
    print(f"Límites de la zona (Bounding Box): {dataset.bounds}")
    print(f"Altitud Mínima: {np.min(elevacion)} metros")
    print(f"Altitud Máxima: {np.max(elevacion)} metros")
    print(f"Altitud Promedio: {np.mean(elevacion):.2f} metros")

    # 2. Mapear las coordenadas geográficas a la matriz
    # Ejemplo: Obtener la altitud exacta de un punto (Latitud, Longitud)
    lat, lon = -33.45, -70.66  # Santiago Centro aprox.
    row, col = dataset.index(lon, lat)
    altitud_punto = elevacion[row, col]
    print(f"\nAltitud estimada en ({lat}, {lon}): {altitud_punto} metros sobre el nivel del mar")

    # 3. Visualizar el terreno como mapa de calor topográfico
    plt.figure(figsize=(10, 8))
    plt.imshow(elevacion, cmap='terrain')
    plt.colorbar(label='Altitud (metros m.s.n.m.)')
    plt.title('Modelo Digital de Elevación (DEM) - Zona de Estudio')
    plt.xlabel('Celdas Eje X (Longitud)')
    plt.ylabel('Celdas Eje Y (Latitud)')
    # Reemplazar plt.show() por:
    plt.savefig("mapa_terreno.png", dpi=300, bbox_inches='tight')
    print("Imagen guardada exitosamente como 'mapa_terreno.png'")
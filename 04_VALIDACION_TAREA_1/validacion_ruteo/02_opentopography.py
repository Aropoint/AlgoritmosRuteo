"""Metadata: DEM real de OpenTopography + estadísticas y mapa para evidencia."""
import json
import requests
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from common import env, bbox, OUT, save_json

key = env("OPENTOPOGRAPHY_API_KEY", required=True)
s,w,n,e = bbox()
url="https://portal.opentopography.org/API/globaldem"
params={"demtype":"SRTMGL3","south":s,"north":n,"west":w,"east":e,"outputFormat":"GTiff","API_Key":key}
r=requests.get(url,params=params,timeout=120)
print("HTTP",r.status_code,"Content-Type",r.headers.get("content-type"))
r.raise_for_status()
tif=OUT/"terreno.tif"; tif.write_bytes(r.content)

with rasterio.open(tif) as ds:
    elev=ds.read(1, masked=True)
    stats={
        "shape": list(elev.shape), "crs": str(ds.crs), "bounds": list(ds.bounds),
        "min_m": float(elev.min()), "max_m": float(elev.max()), "mean_m": float(elev.mean())
    }
    lat=float(env("POINT_LAT","-33.45")); lon=float(env("POINT_LON","-70.66"))
    row,col=ds.index(lon,lat)
    stats["sample_point"]={"lat":lat,"lon":lon,"elevation_m":float(elev[row,col])}
    save_json("opentopography_stats.json",stats)
    plt.figure(figsize=(9,6)); plt.imshow(elev); plt.colorbar(label="Elevación (m)")
    plt.title("DEM OpenTopography - evidencia"); plt.tight_layout()
    plt.savefig(OUT/"opentopography_dem.png",dpi=180); plt.close()
print(json.dumps(stats,indent=2,ensure_ascii=False))
print("Archivos: evidencia/terreno.tif, opentopography_stats.json, opentopography_dem.png")

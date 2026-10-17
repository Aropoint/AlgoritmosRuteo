"""Amenaza: dataset diario observado de GPSJam (no API REST documentada).
Convierte celdas H3 a polígonos GeoJSON para análisis espacial.
"""
from datetime import datetime, timezone, timedelta
import io, json, requests
import pandas as pd
import h3
from common import env, OUT

date=env("GPSJAM_DATE") or (datetime.now(timezone.utc)-timedelta(days=1)).date().isoformat()
url=f"https://gpsjam.org/data/{date}-h3_4.csv"
r=requests.get(url,timeout=60)
print("URL",url,"HTTP",r.status_code); r.raise_for_status()
(OUT/f"gpsjam_{date}_raw.csv").write_bytes(r.content)
df=pd.read_csv(io.BytesIO(r.content))
required={"hex","count_good_aircraft","count_bad_aircraft"}
if not required.issubset(df.columns):
    raise SystemExit(f"Columnas inesperadas: {df.columns.tolist()}")
# Fórmula publicada por GPSJam; resta 1 a bad para compensar un artefacto metodológico descrito por el sitio.
den=(df.count_good_aircraft+df.count_bad_aircraft).replace(0,float('nan'))
df["percent_bad"]=100*((df.count_bad_aircraft-1).clip(lower=0))/den

def boundary(cell):
    try: pts=h3.cell_to_boundary(cell)  # v4 -> (lat,lng)
    except AttributeError: pts=h3.h3_to_geo_boundary(cell)  # v3
    xy=[[float(lng),float(lat)] for lat,lng in pts]; xy.append(xy[0]); return xy
features=[]
for _,row in df.iterrows():
    try: coords=boundary(str(row["hex"]))
    except Exception: continue
    p=float(row["percent_bad"]) if row["percent_bad"]==row["percent_bad"] else None
    features.append({"type":"Feature","properties":{"h3":str(row["hex"]),"good":int(row["count_good_aircraft"]),"bad":int(row["count_bad_aircraft"]),"percent_bad":p},"geometry":{"type":"Polygon","coordinates":[coords]}})
geo={"type":"FeatureCollection","features":features}
(OUT/f"gpsjam_{date}.geojson").write_text(json.dumps(geo,ensure_ascii=False),encoding="utf-8")
print("Filas",len(df),"Polígonos",len(features),"%bad>10:",int((df.percent_bad>10).sum()))
print("CAVEAT: GPSJam infiere degradación GNSS desde ADS-B; no demuestra jamming de la radio de datos 2.4 GHz.")

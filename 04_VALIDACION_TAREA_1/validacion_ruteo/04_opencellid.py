"""Metadata candidata: densidad de celdas. Acceso puede exigir aportar datos o whitelist.
No interpretar densidad celular como ocupación medida del canal Wi-Fi de 2.4 GHz.
"""
import requests
from common import env,bbox,save_json,save_csv
key=env("OPENCELLID_API_KEY",required=True); s,w,n,e=bbox(); B=f"{s},{w},{n},{e}"
base="https://opencellid.org/cell"

def small_bbox_around_point():
    lat=float(env("POINT_LAT","-33.45")); lon=float(env("POINT_LON","-70.66"))
    d=0.008
    return f"{lat-d},{lon-d},{lat+d},{lon+d}"

size=requests.get(f"{base}/getInAreaSize",params={"key":key,"BBOX":B,"format":"json"},timeout=30)
print("getInAreaSize HTTP",size.status_code)
if size.status_code==403:
    print("403: la key puede requerir whitelist/contribución. Esto es una limitación de factibilidad, no un error del script.")
    print(size.text[:1000]); raise SystemExit(2)
size.raise_for_status(); size_data=size.json()
if size_data.get("code")==3:
    B=small_bbox_around_point()
    print("BBOX demasiado grande para OpenCellID; reintentando con bbox pequeño centrado en POINT_LAT/POINT_LON.")
    size=requests.get(f"{base}/getInAreaSize",params={"key":key,"BBOX":B,"format":"json"},timeout=30)
    print("getInAreaSize retry HTTP",size.status_code)
    size.raise_for_status(); size_data=size.json()
save_json("opencellid_size.json",size_data); print("Conteo:",size_data)

r=requests.get(f"{base}/getInArea",params={"key":key,"BBOX":B,"format":"json","limit":50},timeout=30)
print("getInArea HTTP",r.status_code); r.raise_for_status(); d=r.json(); save_json("opencellid_raw.json",d)
rows=[]
for c in d.get("cells",[]) if isinstance(d,dict) else []:
    rows.append({k:c.get(k) for k in ["lat","lon","radio","mcc","mnc","lac","cellid","range","samples","averageSignalStrength"]})
save_csv("opencellid_cells.csv",rows)
print(f"Celdas detalladas guardadas: {len(rows)}")

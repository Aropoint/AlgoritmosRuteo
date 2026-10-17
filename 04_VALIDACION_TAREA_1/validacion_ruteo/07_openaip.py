"""Amenaza/geofence: espacios aéreos de OpenAIP. Endpoint actual api.core.openaip.net.
Filtra tipos 1=Restricted, 2=Danger, 3=Prohibited y exporta geometrías Polygon/MultiPolygon.
"""
import json, requests
from common import env, bbox, OUT, save_json
key=env("OPENAIP_API_KEY",required=True); country=env("OPENAIP_COUNTRY")
s,w,n,e=bbox(); url="https://api.core.openaip.net/api/airspaces"
headers={"x-openaip-api-key":key}
params={"limit":100,"page":1}
if country: params["country"]=country
else: params["bbox"]=f"{w},{s},{e},{n}"
all_items=[]
for page in range(1,6):
    params["page"]=page
    r=requests.get(url,headers=headers,params=params,timeout=60)
    print("page",page,"HTTP",r.status_code); r.raise_for_status(); d=r.json()
    if page==1: save_json("openaip_raw_page1.json",d)
    if isinstance(d,list): items=d
    elif isinstance(d,dict): items=d.get("items") or d.get("data") or d.get("results") or []
    else: items=[]
    if not isinstance(items,list): break
    all_items.extend(items)
    if len(items)<100: break
features=[]
for x in all_items:
    typ=x.get("type")
    try: typ_int=int(typ)
    except (TypeError,ValueError): typ_int=None
    if typ_int not in {1,2,3}: continue
    geom=x.get("geometry")
    if not isinstance(geom,dict) or geom.get("type") not in {"Polygon","MultiPolygon"}: continue
    features.append({"type":"Feature","properties":{"id":x.get("_id") or x.get("id"),"name":x.get("name"),"type":typ_int,"icaoClass":x.get("icaoClass") or x.get("class"),"country":x.get("country")},"geometry":geom})
path=OUT/"openaip_restricted.geojson"
path.write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False),encoding="utf-8")
print(f"Airspaces descargados: {len(all_items)}; Restricted/Danger/Prohibited con polígonos: {len(features)}")
print("Evidencia:",path)

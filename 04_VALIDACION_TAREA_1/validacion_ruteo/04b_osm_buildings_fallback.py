"""Fallback recomendado para la 3ª metadata: edificios de OpenStreetMap vía Overpass.
Genera polígonos reales de clutter/obstrucción, más defendibles para propagación/LOS que 'congestión celular'.
"""
import requests
from common import env, bbox, save_json, OUT

def small_bbox_around_point():
    lat=float(env("POINT_LAT","-33.45")); lon=float(env("POINT_LON","-70.66"))
    d=0.008
    return lat-d, lon-d, lat+d, lon+d

def fetch_buildings(s,w,n,e):
    query=f'''[out:json][timeout:90];
(
 way["building"]({s},{w},{n},{e});
 relation["building"]({s},{w},{n},{e});
);
out geom;'''
    return requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data":query},
        headers={"User-Agent":"validacion-ruteo-uav/1.0"},
        timeout=120,
    )

s,w,n,e=bbox()
r=fetch_buildings(s,w,n,e)
print("HTTP",r.status_code)
if r.status_code in {400,406,429,504}:
    print("BBOX/consulta no aceptada por Overpass; reintentando con bbox pequeño centrado en POINT_LAT/POINT_LON.")
    r=fetch_buildings(*small_bbox_around_point())
    print("HTTP retry",r.status_code)
r.raise_for_status(); d=r.json(); save_json("osm_buildings_raw.json",d)
features=[]
for x in d.get("elements",[]):
    geom=x.get("geometry") or []
    if x.get("type")=="way" and len(geom)>=4:
        coords=[[p["lon"],p["lat"]] for p in geom]
        if coords[0]!=coords[-1]: coords.append(coords[0])
        features.append({"type":"Feature","properties":{"osm_id":x.get("id"),"name":x.get("tags",{}).get("name"),"building":x.get("tags",{}).get("building")},"geometry":{"type":"Polygon","coordinates":[coords]}})
geo={"type":"FeatureCollection","features":features}
(OUT/"osm_buildings.geojson").write_text(__import__('json').dumps(geo,ensure_ascii=False),encoding="utf-8")
print(f"Elementos OSM: {len(d.get('elements',[]))}; polígonos simples exportados: {len(features)}")
print("Evidencia: osm_buildings.geojson (base geoespacial con Polygon)")

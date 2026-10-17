"""Amenaza contextual: eventos ACLED con OAuth actual. Guarda puntos GeoJSON."""
import json, requests
from common import env, save_json, OUT
user=env("ACLED_USERNAME",required=True); password=env("ACLED_PASSWORD",required=True)
t=requests.post("https://acleddata.com/oauth/token",data={
    "username":user,"password":password,"grant_type":"password","client_id":"acled","scope":"authenticated"
},timeout=30)
print("Token HTTP",t.status_code); t.raise_for_status(); token=t.json()["access_token"]
country=env("ACLED_COUNTRY","Ukraine"); d0=env("ACLED_DATE_FROM","2026-08-01"); d1=env("ACLED_DATE_TO","2026-09-03")
params={"_format":"json","country":country,"event_date":f"{d0}|{d1}","event_date_where":"BETWEEN","limit":500}
def fetch_events(params):
    r=requests.get("https://acleddata.com/api/acled/read",headers={"Authorization":f"Bearer {token}"},params=params,timeout=60)
    print("API HTTP",r.status_code); r.raise_for_status(); return r.json()

d=fetch_events(params)
rows=d.get("data",[]) if isinstance(d,dict) else []
if not rows:
    recency_date=(d.get("data_query_restrictions",{}).get("date_recency",{}) or {}).get("date") if isinstance(d,dict) else None
    if recency_date:
        print(f"Sin eventos en rango configurado; reintentando con fecha disponible reportada por ACLED: {recency_date}.")
        params["event_date"]=f"{recency_date}|{recency_date}"
        d=fetch_events(params)
        rows=d.get("data",[]) if isinstance(d,dict) else []
save_json("acled_raw.json",d)
features=[]
for x in rows:
    try: lat=float(x["latitude"]); lon=float(x["longitude"])
    except (KeyError,TypeError,ValueError): continue
    props={k:x.get(k) for k in ["event_id_cnty","event_date","event_type","sub_event_type","country","admin1","location","fatalities"]}
    features.append({"type":"Feature","properties":props,"geometry":{"type":"Point","coordinates":[lon,lat]}})
(OUT/"acled_events.geojson").write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False),encoding="utf-8")
print(f"Eventos: {len(rows)}; puntos válidos: {len(features)}")
print("Para ruteo: convertir puntos a buffers con radio/ventana temporal EXPLÍCITOS; ACLED no mide interferencia RF.")

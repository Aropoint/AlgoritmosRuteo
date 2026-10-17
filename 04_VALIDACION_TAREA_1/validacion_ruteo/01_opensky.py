"""Evidencia de infraestructura: posiciones de aeronaves desde OpenSky.
Usarlas como trazas de movilidad/posición sustitutas; NO son una red UAV real ni miden enlaces RF.
"""
import requests
from common import env, bbox, save_json, save_csv, haversine_km

AUTH_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API_URL = "https://opensky-network.org/api/states/all"

cid, secret = env("OPENSKY_CLIENT_ID"), env("OPENSKY_CLIENT_SECRET")
headers = {}
if cid and secret:
    t = requests.post(AUTH_URL, data={
        "grant_type": "client_credentials", "client_id": cid, "client_secret": secret
    }, timeout=30)
    t.raise_for_status()
    headers["Authorization"] = f"Bearer {t.json()['access_token']}"
    print("OAuth2 OpenSky: OK (token obtenido; no se imprime).")
else:
    print("OpenSky: consulta anónima (menor cuota).")

def fetch_states(params=None):
    r = requests.get(API_URL, headers=headers, params=params, timeout=30)
    print("HTTP", r.status_code)
    print("Rate headers:", {k:v for k,v in r.headers.items() if "rate" in k.lower() or "credit" in k.lower()})
    r.raise_for_status()
    return r.json()


def valid_rows(data):
    rows=[]
    for st in data.get("states") or []:
        if len(st) < 17 or st[5] is None or st[6] is None:
            continue
        rows.append({
            "icao24": st[0], "callsign": (st[1] or "").strip(), "origin_country": st[2],
            "longitude": st[5], "latitude": st[6], "baro_altitude_m": st[7],
            "on_ground": st[8], "velocity_m_s": st[9], "true_track_deg": st[10],
            "geo_altitude_m": st[13], "category": st[17] if len(st) > 17 else None,
        })
    return rows


s, w, n, e = bbox()
params = {"lamin": s, "lomin": w, "lamax": n, "lomax": e}
print("Consulta OpenSky con bbox configurado.")
data = fetch_states(params)
rows = valid_rows(data)

if not rows and headers:
    print("BBOX sin posiciones válidas; reintentando consulta global autenticada con datos reales de OpenSky.")
    data = fetch_states()
    rows = valid_rows(data)

save_json("opensky_raw.json", data)
save_csv("opensky_nodes.csv", rows)
print(f"Nodos/posiciones válidas: {len(rows)} -> evidencia/opensky_nodes.csv")

rng = env("COMM_RANGE_KM")
if rng:
    rng=float(rng); edges=[]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            d=haversine_km(a["latitude"],a["longitude"],b["latitude"],b["longitude"])
            if d <= rng:
                edges.append({"source":a["icao24"],"target":b["icao24"],"distance_km":round(d,3)})
    save_csv("opensky_candidate_edges.csv", edges)
    print(f"Aristas candidatas derivadas por <= {rng} km: {len(edges)}")
    print("ADVERTENCIA: son aristas simuladas por proximidad, no enlaces observados por OpenSky.")

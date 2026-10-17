"""Metadata meteorológica actual. Para 2.4 GHz, priorizar viento/movilidad; lluvia aporta poco a la atenuación en distancias cortas."""
import requests
from common import env, save_json
key=env("OPENWEATHER_API_KEY",required=True)
lat=float(env("POINT_LAT","-33.45")); lon=float(env("POINT_LON","-70.66"))
url="https://api.openweathermap.org/data/2.5/weather"
r=requests.get(url,params={"lat":lat,"lon":lon,"appid":key,"units":"metric"},timeout=30)
print("HTTP",r.status_code); r.raise_for_status(); d=r.json(); save_json("openweather_raw.json",d)
summary={
 "lat":d.get("coord",{}).get("lat"), "lon":d.get("coord",{}).get("lon"),
 "temp_c":d.get("main",{}).get("temp"), "humidity_pct":d.get("main",{}).get("humidity"),
 "pressure_hpa":d.get("main",{}).get("pressure"), "visibility_m":d.get("visibility"),
 "wind_speed_m_s":d.get("wind",{}).get("speed"), "wind_deg":d.get("wind",{}).get("deg"),
 "wind_gust_m_s":d.get("wind",{}).get("gust"),
 "rain_1h_mm":(d.get("rain") or {}).get("1h"), "clouds_pct":d.get("clouds",{}).get("all")
}
save_json("openweather_summary.json",summary)
print(summary); print("Evidencia: openweather_raw.json + openweather_summary.json")

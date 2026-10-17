from __future__ import annotations
import csv
import json
import math
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OUT = Path(__file__).resolve().parent / "evidencia"
OUT.mkdir(exist_ok=True)


def env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise SystemExit(f"Falta variable {name}. Cópiala en .env; nunca la dejes hardcodeada.")
    return value


def bbox():
    return tuple(float(env(k, d)) for k, d in [
        ("BBOX_S", "-33.60"), ("BBOX_W", "-70.80"),
        ("BBOX_N", "-33.30"), ("BBOX_E", "-70.50")])


def save_json(name: str, data) -> Path:
    p = OUT / name
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def save_csv(name: str, rows: list[dict]) -> Path:
    p = OUT / name
    if not rows:
        p.write_text("", encoding="utf-8")
        return p
    fields = sorted({k for row in rows for k in row.keys()})
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    return p


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1); dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

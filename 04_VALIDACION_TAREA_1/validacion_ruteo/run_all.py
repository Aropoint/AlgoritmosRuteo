"""Ejecuta todas las validaciones y deja un resumen. Las fuentes con credenciales/whitelist pueden fallar de forma esperable."""
from __future__ import annotations
import subprocess, sys, json
from pathlib import Path
BASE=Path(__file__).resolve().parent
scripts=[
 "01_opensky.py","02_opentopography.py","03_openweather.py",
 "04_opencellid.py","04b_osm_buildings_fallback.py",
 "05_gpsjam.py","06_acled.py","07_openaip.py"
]
results=[]
for s in scripts:
    print("\n"+"="*70+f"\n{s}\n"+"="*70)
    p=subprocess.run([sys.executable,str(BASE/s)],cwd=BASE,text=True,capture_output=True)
    print(p.stdout)
    if p.stderr: print(p.stderr,file=sys.stderr)
    results.append({"script":s,"ok":p.returncode==0,"returncode":p.returncode,
                    "stdout_tail":p.stdout[-1500:],"stderr_tail":p.stderr[-1000:]})
(BASE/"evidencia"/"resumen_validacion.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
print("\nRESUMEN")
for x in results: print(("OK  " if x["ok"] else "FAIL"),x["script"])
print("Detalle: evidencia/resumen_validacion.json")

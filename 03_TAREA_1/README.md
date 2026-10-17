# Material de la Tarea 1

Esta carpeta documenta la propuesta **anterior a la reunión con el profesor**. El problema tratado era recuperar rutas de comunicación entre UAV mediante CLUN-LSR y estudiar si fuentes geoespaciales podían enriquecer el escenario. No contiene un algoritmo de trayectorias físicas evaluado.

## Archivos

| Ruta | Uso |
|---|---|
| [`informes/Informe_Ruteo_APO_DPC_AML-1.pdf`](informes/Informe_Ruteo_APO_DPC_AML-1.pdf) | PDF presentado en la primera entrega. |
| [`informes/Informe_Ruteo_APO_DPC_AML_corregido.tex`](informes/Informe_Ruteo_APO_DPC_AML_corregido.tex) | Fuente LaTeX corregida que se conserva; no consta aprobación posterior del ayudante y no debe confundirse con el PDF entregado. |
| [`CONTEXTO_PROYECTO_CODEX.md`](CONTEXTO_PROYECTO_CODEX.md) | Plan y decisiones originales; se mantiene como antecedente histórico. |
| [`referencias/Tecnicas_de_Intercepcion_Telefonica.pdf`](referencias/Tecnicas_de_Intercepcion_Telefonica.pdf) | Archivo local del informe de la Biblioteca del Congreso Nacional *Jamming: Caracterización y estatus legal en Chile y otros países* (2024). El nombre del archivo no coincide con el título del informe. |
| [`pruebas_iniciales/`](pruebas_iniciales/) | Pruebas exploratorias previas al paquete de validación. |

## Pruebas iniciales

Desde `03_TAREA_1/pruebas_iniciales/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENTOPOGRAPHY_API_KEY='TU_CLAVE'
export OPENWEATHER_API_KEY='TU_CLAVE'
python main.py
python terreno.py
python OpeanWeather.py
python SpectrumITU.py
```

`main.py` descarga `terreno.tif` para un sector de Santiago; `terreno.py` lee ese archivo y guarda `mapa_terreno.png`. `OpeanWeather.py` consulta condiciones puntuales. `SpectrumITU.py` calcula un ejemplo con valores **simulados** de ruido y potencia: no consulta una base espectral de la UIT ni mide jamming real. Los archivos de relieve y mapa incluidos son resultados históricos; volver a ejecutar puede cambiarlos.

Para compilar `Informe_Ruteo_APO_DPC_AML_corregido.tex`, ejecuta LaTeX desde `03_TAREA_1/informes/`; su figura apunta al mapa de `pruebas_iniciales/`. El PDF entregado ya está disponible sin compilar.

Si vas a continuar el proyecto, empieza por el [enfoque actual de la Tarea 2](../01_PROYECTO_ACTUAL/CONTEXTO_PARA_EL_GRUPO_TAREA_2.md) y por la [guía del paquete de validación](../04_VALIDACION_TAREA_1/REPRODUCIBILIDAD_Y_DATOS.md).

# Resultados de experimentos

Los genera `experimentos/run_experimentos.py`. Nombre del archivo: `<conjunto>_pf<prob_foco>_nf<n_fallas>_b<β>.json`. Con `--sensibilidad`, el archivo es `sensibilidad_<conjunto>.json`: una lista de objetos con la misma estructura.

| Campo | Descripción |
|---|---|
| `etiqueta` | Conjunto y parámetros variados. |
| `configuracion` | Copia completa de `Configuracion` (malla, misión, preferencias, algoritmo, fallas). |
| `aoi` | Recorte geográfico. |
| `grafo` | `nodos`, `aristas`, `excluidas_por_restriccion`. |
| `secuencia_mision` | `id` de nodos `[A, P1…Pm, B]`. |
| `largo_minimo_km` | `L*`: misión mínima en km sin fallas. |
| `presupuesto_km` | `(1 + β) · L*`. |
| `n_escenarios`, `fallas_remuestreadas` | Escenarios simulados y discos que se volvieron a muestrear por cubrir un punto obligatorio. |
| `R_oraculo_estatico` | Fracción de escenarios factibles con conocimiento perfecto (referencia, no cota estricta). |
| `R_par` | Por estrategia precalculable (A, B, C): fracción de tramos con al menos una ruta del par libre de fallas. |
| `resumen.<estrategia>` | `R_mision`, `km_medio_exitosas`, `sobrelongitud_media_exitosas` (`km/L* − 1`), `replanificaciones_media`, `fraccion_puntos_en_fallidas`, `tiempo_calculo_ms_medio` y `motivos_fallo` (`sin_ruta`, `sin_alternativa`, `atrapado`, `presupuesto`, `bucle`). |
| `diferenciales[]` | `delta_R_pp` y `delta_R_relativo`; `solo_metodo_completa` y `solo_referencia_completa` (escenarios discordantes); `p_mcnemar`; `km_extra_medio_pareado` y `km_extra_relativo_minimo` (solo misiones que ambos completan). |
| `segundos` | Duración de la corrida. |

Los archivos actuales corresponden **solo al conjunto de ajuste** (semillas 0–99).

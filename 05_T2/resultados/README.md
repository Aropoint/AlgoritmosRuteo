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

## Flota con aviso compartido

Los genera `experimentos/run_flota.py`, y la explicación está en PROPUESTA_TECNICA §10.

- **Nombre del archivo:** `flota_<conjunto>_u<n_uav>_pd<prob_deteccion>_pf<prob_foco>_nf<n_fallas>_b<β>.json`.
- **Con `--sensibilidad`:** el archivo es `flota_sensibilidad_<conjunto>_pf<prob_foco>_nf<n_fallas>.json`, una lista que barre `n_uav ∈ {3, 4, 5}` × `prob_deteccion ∈ {1, 0,5, 0}`.
- **Escenarios:** se usan las mismas semillas que en el caso de un UAV, así que la comparación entre estrategias es pareada.

| Campo | Descripción |
|---|---|
| `configuracion.flota` | `n_uav`, `separacion_km`, `alcance_com_km`, `intervalo_beacon_s`, `beacons_para_alerta`, `prob_deteccion`. |
| `resumen.<estrategia>` | Tasas de éxito, pérdidas, avisos, demora, km y motivos de fallo (detalle en la tabla siguiente). |
| `diferenciales[]` | Los mismos campos que arriba, con `poblacion`: `seguidores` o `todos_los_uav`. Pares: D_A−D (valor del aviso), C_A−D_A (aporte de la selección encima del aviso), C_A−D, C_A−C, C_A−A y D−A. |

Campos de `resumen.<estrategia>`:

| Grupo | Campos |
|---|---|
| Tasas de éxito | `R_uav` (todos los UAV), `R_lider`, `R_seguidores` (UAV 2..N), `R_flota_alguno` (al menos un UAV completa) y `R_flota_todos` |
| Pérdidas y avisos | `perdidos_media`, `avisos_media` y `replan_por_aviso_media` (cambios de ruta en vuelo) |
| Demora del aviso | `demora_aviso_media_s` (desde la detección o la pérdida del UAV), `demora_por_tipo_media_s` y `recepciones_inmediatas` |
| Recorrido y cálculo | `km_medio_exitosas`, `sobrelongitud_media_exitosas` y `tiempo_calculo_ms_medio` |
| Motivos de fallo | `motivos_fallo`: se agregan `perdido_en_interferencia` y `atrapado` |

Los archivos actuales corresponden **solo al conjunto de ajuste** (semillas 0–99).

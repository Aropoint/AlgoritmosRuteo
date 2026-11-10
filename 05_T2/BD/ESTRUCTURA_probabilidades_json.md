# Estructura de `salida/probabilidades.json`

Lo genera `BD/probabilidades.py` (Tarea 3, punto 5), que ejecuta `BD/probabilidades.sql` después de `BD/asignar_pesos.py`. Contiene la **probabilidad de falla de cada tramo y de cada nodo**, por amenaza y combinada, y el umbral que usa el sorteo 0–100 del punto 7. Los mismos valores quedan en las columnas `pf_*` de las tablas `aristas` y `nodos`.

## Modelo

Para cada amenaza *i* (UCDP, incendios de guerra, GPSJam) y cada elemento:

```
lambda_i = lambda_i^max * r_i                  tasa de falla por km (r_i = intensidad en [0, 1])
tramo e:  p_i(e) = 1 - exp(-lambda_i * largo_km(e))
nodo v:   p_i(v) = 1 - exp(-lambda_i * exposicion_nodo_km)
p_total  = 1 - prod_i (1 - p_i)                (amenazas independientes)
umbral   = 100 * (1 - p_total)                 en el sorteo hay falla si n ~ U[0, 100) supera el umbral
```

`r_i` sale de `BD/pesos.sql`: densidad gaussiana normalizada de eventos UCDP (σ = 1 km) y de incendios de guerra del período histórico (σ = 0,5 km), y la fracción de días en rojo de la celda GPSJam. En los nodos se calcula con el mismo núcleo, normalizado por el máximo de los tramos. `lambda_i^max` y `exposicion_nodo_km` están en la tabla `parametros_pesos`: son **supuestos académicos abstractos**, no tasas medidas.

El sitio no usa `p_total` directamente: vuelve a combinar las componentes en cada consulta, con solo las amenazas que el usuario marcó como «Considerar», y les suma las zonas de amenaza que dibujó (`ruteo/probabilidad.py`).

## Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | string | Siempre `"probabilidades_falla"`. |
| `metadatos` | object | Modelo, parámetros, advertencias y resumen. |
| `aristas` | array | Un objeto por tramo (618 con la malla por defecto). |
| `nodos` | array | Un objeto por nodo (196). |

## `aristas[]` y `nodos[]`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | int | `id` del tramo o del nodo en la BD (el mismo de pgRouting). |
| `source`, `target`, `largo_km` | int, int, float | Solo en tramos: extremos y largo. |
| `tipo` | string | Solo en nodos: `navegacion`, `inicio`, `observacion` o `destino`. |
| `intensidad` | object | `eventos`, `incendios`, `gnss`: la intensidad `r_i` en [0, 1]. |
| `p_falla` | object | `eventos`, `incendios`, `gnss` y `total`: probabilidades en [0, 1]. |
| `umbral_falla` | float | `100 * (1 - p_falla.total)`, en [0, 100]. |

## `metadatos`

| Campo | Descripción |
|---|---|
| `fuente`, `generado_utc` | Script y fecha de la generación. |
| `modelo` | La fórmula, en texto. |
| `parametros` | `lambda_eventos_por_km`, `lambda_incendios_por_km`, `lambda_gnss_por_km` y `exposicion_nodo_km`. |
| `umbral` | La regla del sorteo. |
| `advertencias` | Supuestos abstractos, independencia entre amenazas y GPSJam sin variación dentro del AOI. |
| `resumen` | Por tramos y por nodos: mínimo, media, máximo y cuántos tienen p > 0, para cada amenaza y el total. |

## Valores de la corrida actual

Con los parámetros por defecto (λ = 0,12; 0,10 y 0,03 por km): `p_total` de los tramos tiene media 0,018 y máximo 0,100; el de los nodos, máximo 0,0065. Una ruta de 8,5 km queda con una fiabilidad de entre 0,74 y 0,88, según por dónde pase.

# Validación técnica y conceptual de la propuesta

## Veredicto general
La idea **sí es factible como extensión experimental de CLUN-LSR**, pero conviene presentarla como una **capa geoespacial de disponibilidad/riesgo aplicada al grafo de comunicaciones**, no como si las APIs midieran directamente jamming de la radio de datos.

El paper trabaja con ruteo de paquetes entre UAV. Su núcleo es: detectar jamming desde la capa de enlace, excluir nodos afectados y seleccionar rutas con información de vecinos. La mejora propuesta debe terminar traduciéndose a **nodos/aristas disponibles, bloqueados o penalizados**.

## Matriz de fuentes
| Rol | Fuente | Acceso | Qué devuelve | Factibilidad técnica | Impacto real en CLUN-LSR | Recomendación |
|---|---|---|---|---|---|---|
| Infraestructura | OpenSky | REST + OAuth2/anon | posiciones, velocidad, rumbo | Alta | Media | Usar como traza sustituta de movilidad, no como red UAV real |
| Metadata 1 | OpenTopography | API key | DEM GeoTIFF | Alta | Alta | Mantener; sirve para LOS/difracción y forma no ideal de cobertura |
| Metadata 2 | OpenWeather Current | API key | viento, lluvia, visibilidad, humedad | Alta | Media | Mantener para evidencia; justificar principalmente viento/movilidad |
| Metadata 3 | OpenCellID | API key + posible whitelist/contribución | torres/celdas | Condicional | Baja-media | No llamarlo “congestión 2.4 GHz”; reemplazo preferido: OSM Buildings |
| Amenaza 1 | GPSJam | dataset diario | H3 con precisión GNSS degradada | Media | Media | Mantener como EW/GNSS contextual, no como jamming RF probado |
| Amenaza 2 | ACLED | OAuth | eventos de conflicto, lat/lon | Alta tras registro | Media | Mantener; convertir puntos a buffers/ventanas temporales justificadas |
| Amenaza 3 | OpenAIP | API key | airspaces con Polygon/MultiPolygon | Alta | Media-alta | Mantener; representa geofence que puede quitar/reubicar nodos |
| BD geoespacial | PostGIS | local | geometrías + ST_Intersects/etc. | Alta | Alta metodológica | Comprometerse explícitamente a usarla |

## Correcciones urgentes al informe
1. **ACLED:** eliminar el endpoint clásico `api.acleddata.com?...key&email`. El acceso programático actual usa OAuth en `https://acleddata.com/oauth/token` y luego `https://acleddata.com/api/acled/read` con `Authorization: Bearer ...`.
2. **OpenAIP:** usar `https://api.core.openaip.net/api/airspaces` y API key (`x-openaip-api-key` o `apiKey`). No asumir que `type` viene como string; en la API actual se representa mediante códigos enumerados.
3. **OpenWeather:** para Current Weather, la capa gratuita publicada actualmente indica 60 llamadas/min y 1.000.000/mes. “1.000/día” corresponde a otros productos/pay-per-call, no a Current Weather Free.
4. **OpenCellID:** bajar factibilidad de “alta” a **media/condicionada**. La API comunitaria exige contribuir datos o whitelist; estudiantes/investigación pueden solicitar excepción. Además, densidad celular NO es ocupación medida del canal Wi-Fi 2.4 GHz.
5. **GPSJam:** describirlo como dataset/mapa diario basado en exactitud de navegación ADS-B. El propio sitio advierte que rojo/amarillo no demuestra necesariamente GPS jamming.
6. **Base geoespacial:** no dejar “PostGIS o GeoJSON”. GeoJSON es un formato, no una BD. Escribir: “Se utilizará PostgreSQL + PostGIS y se cargarán polígonos de OpenAIP/GPSJam”.
7. **OpenSky:** decir “trazas geolocalizadas de movilidad aérea usadas como sustituto experimental”. Las aristas no vienen de OpenSky: se derivan por alcance, link budget y/o LOS.

## Ajuste recomendado de hipótesis
> Si el grafo de comunicaciones de CLUN-LSR se enriquece con condiciones geoespaciales que afectan la disponibilidad de enlaces y con capas de amenazas temporales que bloquean o penalizan nodos/aristas, entonces las rutas alternativas entre un mismo par origen-destino reducirán su exposición acumulada a zonas de riesgo respecto de una selección basada únicamente en información topológica y de jamming idealizado, manteniendo costos de conectividad aceptables.

Esto es más medible que afirmar simplemente “será más realista”.

## Cómo convertir las APIs en decisiones de ruteo
Una opción fiel al paper es no reemplazar su métrica, sino modificar el grafo antes de Dijkstra:

- `OpenTopography -> LOS_ij`: si un enlace queda obstruido, se elimina o penaliza.
- `OpenWeather -> movilidad`: viento modifica posición/velocidad esperada o estabilidad del enlace.
- `OSM Buildings/OpenCellID -> clutter`: incrementa pérdida o incertidumbre del enlace.
- `GPSJam -> polígono EW`: eleva riesgo de navegación/operación de nodos dentro de la celda.
- `ACLED -> punto + buffer + ventana temporal`: eleva riesgo contextual.
- `OpenAIP -> Polygon/MultiPolygon`: nodo dentro de geofence se invalida o debe reubicarse.

Luego, sobre los enlaces/nodos sobrevivientes, conservar la idea del peso CLUN-LSR basado en vecinos de dos saltos. Alternativamente definir una extensión multiobjetivo, pero sus pesos deben quedar explícitos y ser objeto de experimento.

## Evidencia mínima para las diapositivas
Para cada fuente mostrar 3 cosas en una sola diapositiva o anexo:
1. Request/endpoint (sin mostrar claves).
2. HTTP 200 o archivo descargado exitosamente.
3. 3–5 campos/geométricas que realmente usarán en el algoritmo.

Para PostGIS mostrar:
```sql
SELECT PostGIS_Version();
SELECT GeometryType(geom), COUNT(*) FROM openaip_zonas GROUP BY 1;
```
y una consulta `ST_Intersects` con una ruta de prueba.

## Caso de estudio
Evitar usar Santiago como caso final si quieren demostrar GPSJam/ACLED vinculados a conflicto. Para la presentación puede servir para validar OpenTopography/OpenWeather/OpenSky. Para Tarea 2, escoger **una sola AOI y ventana temporal** donde haya cobertura simultánea de OpenSky, GPSJam, ACLED y OpenAIP. Hacer un piloto de un día antes de comprometer la zona.

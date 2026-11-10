"""Parámetros del escenario, preferencias por defecto y parámetros experimentales.

Todos los valores se fijan ANTES de evaluar (ver PROPUESTA_TECNICA.md §8).
Son supuestos académicos de simulación, no límites aeronáuticos reales.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# Área de estudio provisional: recorte urbano de referencia en Mykolaiv (Ucrania).
# Los puntos de misión se definen por posición relativa dentro del AOI, no por
# instalaciones concretas: la misión es sintética.
AOI = {
    "nombre": "Mykolaiv (referencia provisional)",
    "sur": 46.945,
    "oeste": 31.950,
    "norte": 47.005,
    "este": 32.040,
}


@dataclass(frozen=True)
class ParametrosMalla:
    espaciado_km: float = 0.5        # distancia nominal entre puntos de navegación
    jitter: float = 0.25             # desplazamiento aleatorio relativo al espaciado
    diagonales: bool = True          # conectar vecinos diagonales (8-vecindad)
    fraccion_eliminada: float = 0.12  # aristas retiradas al azar (sin desconectar)
    semilla: int = 7


@dataclass(frozen=True)
class Mision:
    """Secuencia fija: inicio -> puntos de observación -> destino.

    Coordenadas relativas (fx, fy) en [0, 1] dentro del AOI; se asocian al
    nodo de navegación más cercano.
    """
    inicio: tuple[float, float] = (0.08, 0.10)
    observacion: tuple[tuple[float, float], ...] = ((0.35, 0.70), (0.65, 0.30), (0.80, 0.75))
    destino: tuple[float, float] = (0.92, 0.92)


@dataclass(frozen=True)
class Preferencias:
    """Restricciones de usuario (rúbrica 6.1) con sus valores por defecto (6.2)."""
    altura_vuelo_m: float = 60.0           # tramos sobre edificios >= altura - margen se excluyen
    margen_vertical_m: float = 10.0
    respetar_zonas_restringidas: bool = True
    viento_max_m_s: float = 12.0           # sobre este valor la misión no es admisible
    velocidad_crucero_m_s: float = 12.0    # para el factor de viento de frente
    desvio_max: float = 0.35               # alfa: estiramiento máximo de candidatas vs. la más corta
    presupuesto_extra: float = 0.60        # beta: km máximos = (1 + beta) * misión mínima sin fallas
    peso_riesgo: float = 1.0               # w_R: aversión a sectores con amenazas históricas
    # Tarea 3 (restricciones que impone la aplicación del usuario)
    autonomia_km: float | None = None      # km máximos de vuelo; None = (1 + beta) * misión mínima
    prob_exito_min: float = 0.85           # R_min: fiabilidad mínima prod(1 - p) de la ruta


@dataclass(frozen=True)
class ParametrosAlgoritmo:
    k_candidatas: int = 8          # K de Yen
    peso_longitud: float = 1.0     # w_L en J(p, q)
    peso_solape: float = 1.0       # w_S en J(p, q)
    d_separacion_km: float = 0.4   # distancia bajo la cual dos tramos se consideran "el mismo corredor"
    radio_incertidumbre_km: float = 0.6  # rho: entorno penalizado alrededor de un tramo bloqueado
    penalizacion_incertidumbre: float = 3.0  # gamma: costo x (1 + gamma) dentro de ese entorno


@dataclass(frozen=True)
class ParametrosFallas:
    n_fallas: int = 3
    radio_min_km: float = 0.25
    radio_max_km: float = 0.60
    prob_foco: float = 0.5          # fracción de fallas generadas cerca de focos de amenaza
    sigma_foco_km: float = 0.5
    inicio_max_frac: float = 0.8    # aparición en [0, 0.8] * longitud mínima de la misión
    n_focos: int = 4
    n_eventos_historicos: int = 60  # eventos usados SOLO para estimar pesos de riesgo


@dataclass(frozen=True)
class ParametrosFlota:
    """Flota con aviso compartido (ruteo/flota.py). Supuestos de simulación, no de un UAV real."""
    n_uav: int = 4                      # 3 a 5 UAV sobre la misma misión
    separacion_km: float = 1.0          # entre lanzamientos, en km a velocidad de crucero (≈ 83 s a 12 m/s)
    alcance_com_km: float | None = 3.0  # alcance de radio UAV-UAV; el aviso se retransmite por la flota. None = sin límite
    intervalo_beacon_s: float = 2.0     # cada UAV emite un "sigo vivo" periódico
    beacons_para_alerta: int = 3        # beacons perdidos seguidos para declarar silencio
    # Prob. de notar la interferencia en el borde, antes de entrar. Con 1 cada UAV esquiva solo y el
    # aviso únicamente ahorra km; con 0 la zona solo se conoce por el silencio de quien entró. Se barre {0, 0.5, 1}.
    prob_deteccion: float = 0.5


@dataclass(frozen=True)
class Considerar:
    """Qué metadata y amenazas entran al cálculo (casillas "Considerar" del panel de control, punto 4)."""
    edificios: bool = True          # altura de edificios OSM como obstáculo
    relieve: bool = True            # perfil del terreno como obstáculo
    viento: bool = True             # factor de viento de frente en el costo
    zonas_publicadas: bool = True   # aeródromos y helipuertos OSM como zona no sobrevolable
    eventos: bool = True            # amenaza UCDP en la probabilidad de falla
    incendios: bool = True          # amenaza de incendios de guerra
    gnss: bool = True               # amenaza GPSJam
    zonas_usuario: bool = True      # zonas prohibidas y de amenaza dibujadas por el usuario

    def amenazas(self) -> tuple[str, ...]:
        return tuple(k for k in ("eventos", "incendios", "gnss", "zonas_usuario") if getattr(self, k))


@dataclass(frozen=True)
class ParametrosResiliencia:
    """Sorteos 0-100 y vuelo simulado de la métrica de resiliencia (ruteo/resiliencia_t3.py, punto 8)."""
    n_sorteos: int = 300
    # Prob. de notar que el tramo o nodo siguiente falló antes de entrar (mismo supuesto que la flota de la
    # Tarea 2). Si lo nota se desvía; si no, entra y el UAV se pierde.
    prob_deteccion: float = 0.5


@dataclass(frozen=True)
class ParametrosACO:
    """Colonia de hormigas (ruteo/hormigas.py). Valores fijados antes de evaluar."""
    n_hormigas: int = 40
    iteraciones: int = 80
    alfa: float = 1.0            # peso de la feromona
    beta: float = 3.0            # peso de la heurística de distancia (costo del arco + costo que falta hasta t)
    gamma: float = 2.0           # peso de la heurística de fiabilidad (1 - p) del arco
    rho: float = 0.1             # evaporación
    sin_mejora: int = 20         # corte: iteraciones seguidas sin mejorar
    penalizacion: float = 10.0   # M: castigo por violar la fiabilidad mínima o la autonomía
    semilla: int = 1


# Perfiles de aplicación (Tarea 3, punto 3): restricciones que impone el uso que el usuario le da al UAV.
# Supuestos académicos; "personalizado" deja los valores por defecto de Preferencias.
PERFILES = {
    "inspeccion": {"nombre": "Inspección de daños", "altura_vuelo_m": 60.0, "margen_vertical_m": 10.0,
                   "prob_exito_min": 0.85, "peso_riesgo": 1.0, "velocidad_crucero_m_s": 12.0},
    "entrega": {"nombre": "Entrega de insumos médicos", "altura_vuelo_m": 80.0, "margen_vertical_m": 15.0,
                "prob_exito_min": 0.92, "peso_riesgo": 2.0, "velocidad_crucero_m_s": 15.0},
    "personalizado": {"nombre": "Personalizado"},
}


@dataclass
class Configuracion:
    malla: ParametrosMalla = field(default_factory=ParametrosMalla)
    mision: Mision = field(default_factory=Mision)
    preferencias: Preferencias = field(default_factory=Preferencias)
    algoritmo: ParametrosAlgoritmo = field(default_factory=ParametrosAlgoritmo)
    fallas: ParametrosFallas = field(default_factory=ParametrosFallas)
    flota: ParametrosFlota = field(default_factory=ParametrosFlota)

    def a_dict(self) -> dict:
        return asdict(self)


# Rangos de semillas separados: el ajuste de parámetros nunca ve los escenarios de evaluación.
# "sitio" lo usa la plataforma web para la demostración, sin tocar los otros dos conjuntos.
SEMILLAS = {
    "ajuste": range(0, 100),
    "evaluacion": range(10_000, 10_300),
    "sitio": range(20_000, 20_100),
    "sorteos": range(30_000, 32_000),  # Tarea 3: sorteos 0-100 de la resiliencia por técnica (punto 8)
}

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


@dataclass
class Configuracion:
    malla: ParametrosMalla = field(default_factory=ParametrosMalla)
    mision: Mision = field(default_factory=Mision)
    preferencias: Preferencias = field(default_factory=Preferencias)
    algoritmo: ParametrosAlgoritmo = field(default_factory=ParametrosAlgoritmo)
    fallas: ParametrosFallas = field(default_factory=ParametrosFallas)

    def a_dict(self) -> dict:
        return asdict(self)


# Rangos de semillas separados: el ajuste de parámetros nunca ve los escenarios de evaluación.
# "sitio" lo usa la plataforma web para la demostración, sin tocar los otros dos conjuntos.
SEMILLAS = {
    "ajuste": range(0, 100),
    "evaluacion": range(10_000, 10_300),
    "sitio": range(20_000, 20_100),
}

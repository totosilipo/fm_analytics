"""
FM DataLab v3 - utils_common (façade)
=======================================
Re-exporta todo desde los módulos nuevos para que las páginas
existentes no necesiten cambiar ninguna línea de importación.

Las páginas siguen haciendo:
    from utils_common import inject_css, sidebar_carga_datos, ...

y todo sigue funcionando igual. La lógica real ahora vive en:
    ui/estilos.py        → inject_css, COMMON_CSS
    ui/componentes.py    → sidebar_carga_datos
    data/loader.py       → limpiar_data, cargar_csv
    data/filtros.py      → extraer_posiciones_jugador, filtrar_por_posicion, ...
    domain/perfiles.py   → PERFILES, PESOS_MAP, validar_stats_perfil, render_perfil_preview
    domain/similitud.py  → SimilitudComparatorV3, compute_similarity_v3, ranking_jugadores
"""

# ── UI ────────────────────────────────────────────────────────────────────────
from ui.estilos     import inject_css, COMMON_CSS
from ui.componentes import sidebar_carga_datos

# ── Data ──────────────────────────────────────────────────────────────────────
from data.loader  import limpiar_data, cargar_csv
from data.filtros import (
    extraer_posiciones_jugador,
    filtrar_por_posicion,
    obtener_posiciones_unicas,
    filtrar_minutos,
)

# ── Domain ────────────────────────────────────────────────────────────────────
from domain.perfiles import (
    PERFILES,
    PESOS_MAP,
    validar_stats_perfil,
    render_perfil_preview,
)
from domain.similitud import (
    PercentileThresholds,
    SimilitudComparatorV3,
    compute_similarity_v3,
    ranking_jugadores,
)

__all__ = [
    # ui
    "inject_css", "COMMON_CSS", "sidebar_carga_datos",
    # data
    "limpiar_data", "cargar_csv",
    "extraer_posiciones_jugador", "filtrar_por_posicion",
    "obtener_posiciones_unicas", "filtrar_minutos",
    # domain
    "PERFILES", "PESOS_MAP", "validar_stats_perfil", "render_perfil_preview",
    "PercentileThresholds", "SimilitudComparatorV3",
    "compute_similarity_v3", "ranking_jugadores",
]

"""
FM DataLab v3 - Perfiles
=========================
Definición de perfiles tácticos, pesos y helpers de validación/render.
Sin dependencias de Streamlit salvo render_perfil_preview (HTML puro).
"""

import pandas as pd


# ── Perfiles tácticos ────────────────────────────────────────────────────────

PERFILES = {
    "lateral": {
        "nombre": "Lateral",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "cen.c/i", "rob/90", "ent p", "dist/90", "pcg %"],
    },
    "carrilero": {
        "nombre": "Carrilero",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "cen.c/i", "ent p", "dist/90", "tir/90", "asis/90", "cen i/90"],
    },
    "carrilero_org": {
        "nombre": "Carrilero Organizador",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "ent p", "pos perd/90", "asis/90"],
    },
    "central": {
        "nombre": "Central",
        "stats": ["rob/90", "ent p", "pcg %", "pres c/90",
                  "cab g/90", "entr/90", "desp/90", "rechazos/90"],
    },
    "central_salida": {
        "nombre": "Central con Salida",
        "stats": ["rob/90", "ent p", "pcg %", "pres c/90", "cab g/90",
                  "desp/90", "rechazos/90", "pases prog/90", "% de pases"],
    },
    "central_avanzado": {
        "nombre": "Central Avanzado",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90", "rob/90",
                  "ent p", "pcg %", "cab g/90", "entr/90", "desp/90",
                  "rechazos/90", "ps i/90"],
    },
    "mc_defensivo": {
        "nombre": "Mediocampista Defensivo",
        "stats": ["rob/90", "ent p", "pcg %", "pases prog/90",
                  "% de pases", "ps i/90", "pos perd/90", "pos gan/90"],
    },
    "organizador_def": {
        "nombre": "Organizador Defensivo",
        "stats": ["reg/90", "kp/90", "pases prog/90", "% de pases",
                  "ps i/90", "pos perd/90", "ent p", "pcg %", "pos gan/90"],
    },
    "todoterreno": {
        "nombre": "Todoterreno",
        "stats": ["ent p", "pres c/90", "reg/90", "% de pases", "tir/90",
                  "asis/90", "dist/90", "pos gan/90"],
    },
    "extremo": {
        "nombre": "Extremo",
        "stats": ["goles por 90 minutos", "kp/90", "reg/90", "cen.c/i",
                  "pos perd/90", "pres c/90", "tir/90", "asis/90", "cen i/90"],
    },
    "delantero_interior": {
        "nombre": "Delantero Interior",
        "stats": ["goles por 90 minutos", "reg/90", "cen.c/i", "pos perd/90",
                  "pres c/90", "tir/90", "xg/90", "asis/90", "cen i/90"],
    },
    "mediapunta": {
        "nombre": "Mediapunta",
        "stats": ["goles por 90 minutos", "kp/90", "reg/90", "pos perd/90",
                  "tir/90", "asis/90", "% de pases", "ps i/90"],
    },
    "organizador_adel": {
        "nombre": "Organizador Adelantado",
        "stats": ["kp/90", "reg/90", "pos perd/90", "tir/90", "asis/90",
                  "% de pases", "ps i/90", "oc c/90"],
    },
    "delantero_apoyo": {
        "nombre": "Delantero de Apoyo",
        "stats": ["kp/90", "reg/90", "tir/90", "% conv", "asis/90",
                  "ps i/90", "oc c/90"],
    },
    "delantero_centro": {
        "nombre": "Delantero Centro",
        "stats": ["reg/90", "tir/90", "% conv", "oc c/90",
                  "xg/90", "goles por 90 minutos", "cab g/90", "tirp/90"],
    },
    "delantero_torre": {
        "nombre": "Delantero Torre",
        "stats": ["tir/90", "% conv", "oc c/90", "xg/90",
                  "goles por 90 minutos", "cab g/90", "tirp/90",
                  "cab p/90", "% de pases"],
    },
}

PESOS_MAP = {"Bajo": 0.5, "Medio": 1.0, "Alto": 2.0}


# ── Helpers ──────────────────────────────────────────────────────────────────

def validar_stats_perfil(df: pd.DataFrame, perfil: dict) -> list:
    """Retorna las stats del perfil que existen en el DataFrame."""
    return [s for s in perfil["stats"] if s in df.columns]


def render_perfil_preview(perfil: dict, stats_disponibles: list) -> str:
    """
    Renderiza un preview HTML de las stats del perfil.
    Las stats disponibles se muestran en verde, las faltantes en gris.
    Retorna HTML string — renderizar con st.markdown(..., unsafe_allow_html=True).
    """
    badges = ""
    for stat in perfil["stats"]:
        if stat in stats_disponibles:
            badges += (
                f'<span class="perfil-badge" '
                f'style="border-color:rgba(78,205,196,0.4);color:#4ecdc4;">✓ {stat}</span>'
            )
        else:
            badges += (
                f'<span class="perfil-badge" '
                f'style="border-color:rgba(122,158,171,0.2);color:#4a6070;'
                f'background:rgba(0,0,0,0.1);">✗ {stat}</span>'
            )

    n_ok    = len(stats_disponibles)
    n_total = len(perfil["stats"])
    color_pct = (
        "#22c55e" if n_ok == n_total
        else ("#f5c518" if n_ok >= n_total * 0.7 else "#ef4444")
    )

    return f"""
<div class="stat-preview-box">
  <div class="stat-preview-title">
    Stats del perfil · <span style="color:{color_pct};">{n_ok}/{n_total} disponibles</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:4px;">{badges}</div>
</div>
"""

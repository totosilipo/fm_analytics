"""
FM DataLab v3 - Streamlit Edition
===================================
Réplica exacta del script prueba_sim.py en interfaz web
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine, euclidean
from dataclasses import dataclass
from typing import Optional
import io
import plotly.graph_objects as go
import re

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="FM DataLab v3 - Similitud",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILOS CSS
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&family=JetBrains+Mono&display=swap');
:root {
    --bg-dark:#1a2332; --bg-mid:#1e2d3d; --teal-glow:#2a6b6b;
    --accent:#4ecdc4; --accent-dim:#3aada5; --text:#e8f4f4;
    --text-muted:#7a9eab; --border:rgba(78,205,196,0.15);
}
html,body,[class*="css"],.stApp { background-color:var(--bg-dark)!important; color:var(--text); font-family:'DM Sans','Segoe UI',sans-serif; }
h1 { color:var(--accent); font-family:'DM Serif Display',Georgia,serif; border-bottom:2px solid var(--border); padding-bottom:10px; }
h2,h3 { color:var(--accent); font-family:'DM Serif Display',Georgia,serif; }
p,label,.stMarkdown p { color:var(--text); }
section[data-testid="stSidebar"] { background-color:var(--bg-mid)!important; border-right:1px solid var(--border); }
[data-testid="stMetricValue"] { font-size:26px; color:var(--accent); font-family:'JetBrains Mono','Courier New',monospace; }
[data-testid="stMetricLabel"] { color:var(--text-muted); }
.stButton>button { background-color:transparent!important; color:var(--accent)!important; font-weight:600; border-radius:24px; border:2px solid var(--accent)!important; padding:8px 24px; transition:all 0.25s; }
.stButton>button:hover { background-color:var(--accent)!important; color:var(--bg-dark)!important; }
[data-testid="baseButton-primary"] { background-color:var(--accent)!important; color:var(--bg-dark)!important; }
.stSelectbox>div>div,.stMultiSelect>div>div { background-color:var(--bg-mid)!important; color:var(--text)!important; border-color:var(--border)!important; }
div[data-testid="stDataFrame"] { border-radius:8px; border:1px solid var(--border); }
.info-box { background-color:var(--bg-mid); padding:15px; border-radius:8px; border-left:4px solid var(--accent); margin:10px 0; }
.warning-box { background-color:#2d1a1a; padding:15px; border-radius:8px; border-left:4px solid #ef4444; margin:10px 0; }
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG INICIAL
# =========================

STATS = [
    "xg/90", "goles por 90 minutos", "kp/90", "pases prog/90", "% de pases",
    "reg/90", "cen.c/i", "rob/90", "ent p", "pcg %", "cen c/90", "pos perd/90",
    "pres c/90", "cab g/90", "tir/90", "% conv", "asis/90", "oc c/90",
    "asie/90", "entr/90", "cab clv/90", "gleq/90", "dist/90", "min/par",
    "eneq/90", "xg -sp/90", "cen i/90", "desp/90", "dsr/90", "pres i/90",
    "pos gan/90", "rechazos/90", "% de disparos", "tirp/90", "ps i/90", "cab p/90"
]

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

PESOS_MAP = {
    "Bajo": 0.5,
    "Medio": 1.0,
    "Alto": 2.0
}

POSICIONES_BASE = {"POR", "DF", "CR", "MD", "ME", "MP", "DL"}

# =========================
# COMPARADOR V3
# =========================

@dataclass
class PercentileThresholds:
    p10: float
    p25: float
    p40: float
    p50: float
    p60: float
    p75: float
    p90: float
    min: float
    max: float
    mean: float
    std: float


class SimilitudComparatorV3:
    def __init__(self):
        self.percentile_thresholds: dict = {}
        self.fitted = False

    def fit(self, df_pool: pd.DataFrame, stats: list):
        self.stats = stats
        self.percentile_thresholds = {}
        for stat in stats:
            if stat not in df_pool.columns:
                continue
            col = df_pool[stat].dropna()
            if len(col) == 0:
                continue
            self.percentile_thresholds[stat] = PercentileThresholds(
                p10=np.percentile(col, 10), p25=np.percentile(col, 25),
                p40=np.percentile(col, 40), p50=np.percentile(col, 50),
                p60=np.percentile(col, 60), p75=np.percentile(col, 75),
                p90=np.percentile(col, 90), min=np.min(col), max=np.max(col),
                mean=np.mean(col), std=np.std(col)
            )
        self.fitted = True

    def _categorize_value_fine(self, value: float, stat_name: str) -> int:
        if pd.isna(value): return 0
        if stat_name not in self.percentile_thresholds: return 0
        t = self.percentile_thresholds[stat_name]
        if value <= t.p10: return -3
        elif value <= t.p25: return -2
        elif value <= t.p40: return -1
        elif value <= t.p60: return 0
        elif value <= t.p75: return 1
        elif value <= t.p90: return 2
        else: return 3

    def categorize_player(self, player_stats: dict) -> np.ndarray:
        return np.array([self._categorize_value_fine(player_stats.get(stat, np.nan), stat) for stat in self.stats])

    def categorize_dataframe(self, df_stats: pd.DataFrame) -> np.ndarray:
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat in df_stats.columns:
                result[:, i] = df_stats[stat].apply(lambda x: self._categorize_value_fine(x, stat))
        return result

    def normalize_player(self, player_stats: dict) -> np.ndarray:
        normalized = []
        for stat in self.stats:
            value = player_stats.get(stat, np.nan)
            if pd.isna(value) or stat not in self.percentile_thresholds:
                normalized.append(0.0); continue
            t = self.percentile_thresholds[stat]
            if t.std == 0: normalized.append(0.0)
            else: normalized.append(np.clip((value - t.mean) / t.std, -3, 3))
        return np.array(normalized)

    def normalize_dataframe(self, df_stats: pd.DataFrame) -> np.ndarray:
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat not in df_stats.columns or stat not in self.percentile_thresholds: continue
            t = self.percentile_thresholds[stat]
            if t.std == 0: continue
            col = df_stats[stat].fillna(t.mean)
            result[:, i] = np.clip((col - t.mean) / t.std, -3, 3)
        return result

    def mae_similarity(self, vec1, vec2):
        return 1 - (np.mean(np.abs(vec1 - vec2)) / 3)

    def euclidean_similarity(self, vec1, vec2):
        dist = euclidean(vec1, vec2)
        return 1 - (dist / np.sqrt(len(vec1) * 36))

    def pearson_similarity(self, vec1, vec2):
        if np.std(vec1) == 0 or np.std(vec2) == 0: return 0.5
        try:
            corr, _ = pearsonr(vec1, vec2)
            return (corr + 1) / 2
        except: return 0.5

    def ordinal_similarity(self, cat1, cat2):
        return 1 - (np.mean(np.abs(cat1 - cat2)) / 6)

    def hybrid_similarity_score(self, cat1, cat2, norm1, norm2):
        return (0.40 * self.mae_similarity(norm1, norm2) +
                0.25 * self.euclidean_similarity(norm1, norm2) +
                0.20 * self.pearson_similarity(norm1, norm2) +
                0.15 * self.ordinal_similarity(cat1, cat2))


# =========================
# FUNCIONES DE CARGA
# =========================

def limpiar_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (df[col].astype(str).str.replace("%", "", regex=False)
                       .str.replace(",", ".", regex=False).str.strip())
            df[col] = df[col].replace(["-", "nan", ""], np.nan)
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df


@st.cache_data
def cargar_data(uploaded_file) -> pd.DataFrame:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        return limpiar_data(df)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None


# =========================
# FUNCIONES DE FILTRADO
# =========================

def extraer_posiciones_jugador(posicion_str: str) -> list:
    if not posicion_str or pd.isna(posicion_str): return []
    posiciones_limpias = []
    texto_normalizado = str(posicion_str).upper().replace('.', ',').replace(';', ',')
    grupos = texto_normalizado.split(',')
    for grupo in grupos:
        grupo = grupo.strip()
        if not grupo: continue
        if '(' in grupo:
            base, roles_str = grupo.split('(', 1)
            bases = [b.strip() for b in base.split('/') if b.strip()]
            roles_validos = list(dict.fromkeys(re.findall(r'[DCI]', roles_str)))
            for b in bases:
                if roles_validos:
                    for r in roles_validos: posiciones_limpias.append(f"{b}({r})")
                else: posiciones_limpias.append(b)
        else:
            posiciones_limpias.extend([b.strip() for b in grupo.split('/') if b.strip()])
    return list(dict.fromkeys(posiciones_limpias))


def filtrar_posicion(df: pd.DataFrame, posicion: str) -> pd.DataFrame:
    def tiene_posicion(pos_str):
        if not pos_str or pd.isna(pos_str): return False
        buscar = posicion.upper().strip()
        if '(' in buscar:
            base_buscar = buscar.split('(')[0].strip()
            rol_buscar = buscar.split('(')[1].replace(')', '').strip()
            for grupo in str(pos_str).split(','):
                grupo = grupo.strip()
                parte_base = grupo.split('(')[0].strip()
                roles = list(grupo.split('(')[1].replace(')', '').strip()) if '(' in grupo else []
                for token in parte_base.split('/'):
                    if token.strip().upper() == base_buscar and rol_buscar in roles: return True
            return False
        else:
            bases = [t.split('(')[0].strip().upper()
                     for grupo in str(pos_str).split(',')
                     for t in grupo.split('/')]
            return buscar in bases

    col_pos = next((c for c in df.columns if c in ['posición','posicion','pos','position']), None)
    if col_pos: df = df[df[col_pos].apply(tiene_posicion)]
    return df


def filtrar_minutos(df, query_jugador, porcentaje, min_col="minutos"):
    stats = {}
    if min_col not in df.columns:
        stats['warning'] = f"Columna '{min_col}' no encontrada"
        return df, stats
    query_minutos = query_jugador.get(min_col, None)
    if query_minutos is None or pd.isna(query_minutos):
        stats['warning'] = "El jugador no tiene datos de minutos"
        return df, stats
    query_minutos = float(query_minutos)
    min_minutos = query_minutos * (porcentaje / 100)
    len_anterior = len(df)
    filtrado = df[df[min_col] >= min_minutos].reset_index(drop=True)
    stats.update({'query_minutos': query_minutos, 'porcentaje': porcentaje,
                  'min_minutos': min_minutos, 'excluidos': len_anterior - len(filtrado),
                  'pool_final': len(filtrado)})
    if len(filtrado) < 30:
        stats['warning'] = f"Pool con menos de 30 jugadores ({len(filtrado)}). Resultados menos precisos."
    return filtrado, stats


def validar_stats_perfil(df, perfil):
    return [stat for stat in perfil["stats"] if stat in df.columns]


# =========================
# CÁLCULO DE SIMILITUD
# =========================

def compute_similarity_v3(comparator, cat_pool, cat_query, norm_pool, norm_query):
    n = cat_pool.shape[0]
    mae_sim = np.zeros(n); euclidean_sim = np.zeros(n)
    pearson_sim = np.zeros(n); ordinal_sim = np.zeros(n); hybrid_sim = np.zeros(n)
    for i in range(n):
        mae_sim[i] = comparator.mae_similarity(norm_pool[i], norm_query)
        euclidean_sim[i] = comparator.euclidean_similarity(norm_pool[i], norm_query)
        pearson_sim[i] = comparator.pearson_similarity(norm_pool[i], norm_query)
        ordinal_sim[i] = comparator.ordinal_similarity(cat_pool[i], cat_query)
        hybrid_sim[i] = comparator.hybrid_similarity_score(cat_pool[i], cat_query, norm_pool[i], norm_query)
    return mae_sim, euclidean_sim, pearson_sim, ordinal_sim, hybrid_sim


def ranking_jugadores(df_pool, mae_sim, euclidean_sim, pearson_sim, ordinal_sim, hybrid_sim, query_nombre):
    result = df_pool.copy()
    result["sim_mae"] = (mae_sim * 100).round(1)
    result["sim_euclidiana"] = (euclidean_sim * 100).round(1)
    result["sim_pearson"] = (pearson_sim * 100).round(1)
    result["sim_ordinal"] = (ordinal_sim * 100).round(1)
    result["similitud"] = (hybrid_sim * 100).round(1)
    result = result[result["jugador"].str.lower() != query_nombre.lower()]
    return result.sort_values(by="similitud", ascending=False).reset_index(drop=True)


# =========================
# VISUALIZACIÓN DE BARRAS ESTILO FM
# =========================

def render_barra_fm(jugadores_data: list, stats_perfil: list, df_ref: pd.DataFrame) -> str:
    """
    Genera HTML con barras estilo FM para comparar jugadores.
    jugadores_data: lista de (nombre, row_series)
    stats_perfil: lista de stats a mostrar
    df_ref: DataFrame de referencia para calcular percentiles (máximos)
    """
    # Colores para cada jugador
    COLORES_JUGADORES = [
        {"barra": "#4ecdc4", "texto": "#4ecdc4", "fondo": "rgba(78,205,196,0.12)"},
        {"line": "#ef4444", "barra": "#ef4444", "texto": "#ef4444", "fondo": "rgba(239,68,68,0.12)"},
        {"line": "#8b5cf6", "barra": "#a78bfa", "texto": "#a78bfa", "fondo": "rgba(139,92,246,0.12)"},
        {"line": "#fb923c", "barra": "#fb923c", "texto": "#fb923c", "fondo": "rgba(251,146,60,0.12)"},
    ]

    # Calcular máximos del pool para normalizar barras (p95 para evitar outliers extremos)
    maximos = {}
    for s in stats_perfil:
        if s in df_ref.columns:
            col = df_ref[s].dropna()
            maximos[s] = float(np.percentile(col, 95)) if len(col) > 0 else 1.0
            if maximos[s] == 0:
                maximos[s] = 1.0

    n_jugadores = len(jugadores_data)

    # Colores de encabezado de cada jugador
    header_cells = ""
    for idx, (nombre, _) in enumerate(jugadores_data):
        c = COLORES_JUGADORES[idx % len(COLORES_JUGADORES)]
        header_cells += f"""
        <th style="padding:10px 16px;text-align:center;color:{c['texto']};
                   font-weight:700;font-size:13px;font-family:'DM Sans',sans-serif;
                   border-bottom:2px solid {c['barra']};white-space:nowrap;min-width:180px;">
            {nombre}
        </th>"""

    rows_html = ""
    for stat in stats_perfil:
        if stat not in df_ref.columns:
            continue

        # Label de la stat
        stat_td = f"""<td style="padding:10px 14px;color:#7a9eab;font-size:12px;
                        font-family:'JetBrains Mono',monospace;white-space:nowrap;
                        border-bottom:1px solid rgba(78,205,196,0.08);min-width:140px;
                        vertical-align:middle;">{stat}</td>"""

        celdas = ""
        for idx, (nombre, row) in enumerate(jugadores_data):
            c = COLORES_JUGADORES[idx % len(COLORES_JUGADORES)]
            val = row.get(stat, None)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                val_num = 0.0
                val_str = "—"
            else:
                val_num = float(val)
                val_str = f"{val_num:.2f}"

            maximo = maximos.get(stat, 1.0)
            pct_barra = min(100, max(0, (val_num / maximo) * 100)) if maximo > 0 else 0

            # Barra estilo FM: fondo oscuro + barra de color + valor a la derecha
            celdas += f"""
            <td style="padding:8px 14px;border-bottom:1px solid rgba(78,205,196,0.08);
                       vertical-align:middle;min-width:180px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:3px;
                                height:14px;overflow:hidden;position:relative;">
                        <div style="width:{pct_barra:.1f}%;height:100%;
                                    background:{c['barra']};border-radius:3px;
                                    transition:width 0.3s ease;"></div>
                    </div>
                    <span style="color:{c['texto']};font-family:'JetBrains Mono',monospace;
                                 font-size:12px;font-weight:700;min-width:38px;
                                 text-align:right;">{val_str}</span>
                </div>
            </td>"""

        rows_html += f"<tr>{stat_td}{celdas}</tr>"

    html = f"""
    <div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(78,205,196,0.2);
                margin:16px 0;background:#1a2332;">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr>
                    <th style="padding:10px 14px;text-align:left;color:#4ecdc4;
                               font-size:11px;font-family:'DM Sans',sans-serif;
                               font-weight:600;letter-spacing:1px;text-transform:uppercase;
                               border-bottom:2px solid rgba(78,205,196,0.3);
                               background:#1e2d3d;">ESTADÍSTICA</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    return html


# =========================
# SPIDER GRAPH (usa stats del perfil)
# =========================

def crear_spider_perfil(jugadores_data: list, stats_perfil: list, df_ref: pd.DataFrame) -> go.Figure:
    """
    Spider graph usando exactamente las stats del perfil elegido.
    """
    import math as _math

    stats_disponibles = [s for s in stats_perfil if s in df_ref.columns]
    N = len(stats_disponibles)
    if N < 3:
        return None

    def _pct(val, stat):
        col = df_ref[stat].dropna()
        if len(col) == 0 or col.max() == col.min(): return 0.5
        return float(np.clip((col < float(val or 0)).sum() / len(col), 0.05, 0.95))

    promedios = {s: float(df_ref[s].dropna().mean()) for s in stats_disponibles}
    angles = [_math.pi / 2 - 2 * _math.pi * i / N for i in range(N)]

    fig = go.Figure()

    # Grilla
    for nivel in [0.2, 0.4, 0.6, 0.8, 1.0]:
        xs = [nivel * _math.cos(a) for a in angles] + [nivel * _math.cos(angles[0])]
        ys = [nivel * _math.sin(a) for a in angles] + [nivel * _math.sin(angles[0])]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
            line=dict(color='rgba(78,205,196,0.15)', width=1),
            showlegend=False, hoverinfo='skip'))

    # Ejes
    for a in angles:
        fig.add_trace(go.Scatter(x=[0, _math.cos(a)], y=[0, _math.sin(a)], mode='lines',
            line=dict(color='rgba(78,205,196,0.2)', width=1),
            showlegend=False, hoverinfo='skip'))

    # Labels
    for stat, angle in zip(stats_disponibles, angles):
        lx = 1.18 * _math.cos(angle)
        ly = 1.18 * _math.sin(angle)
        xanchor = 'left' if lx > 0.1 else ('right' if lx < -0.1 else 'center')
        fig.add_annotation(x=lx, y=ly, text=stat, showarrow=False,
            font=dict(color='#c8e6e4', size=10), xanchor=xanchor, yanchor='middle')

    # Promedio (línea amarilla punteada)
    vals_prom = [_pct(promedios.get(s, 0), s) for s in stats_disponibles]
    xs_p = [v * _math.cos(a) for v, a in zip(vals_prom, angles)]
    ys_p = [v * _math.sin(a) for v, a in zip(vals_prom, angles)]
    hover_p = [f"<b>{s}</b><br>Promedio: {promedios.get(s,0):.2f}" for s in stats_disponibles]
    fig.add_trace(go.Scatter(
        x=xs_p + [xs_p[0]], y=ys_p + [ys_p[0]],
        mode='lines+markers', name='Promedio lista',
        line=dict(color='#f5c518', width=2, dash='dot'),
        marker=dict(color='#f5c518', size=7),
        fill='toself', fillcolor='rgba(245,197,24,0.08)',
        text=hover_p + [hover_p[0]],
        hovertemplate='%{text}<extra></extra>'
    ))

    COLORES_SPIDER = [
        {"line": "#4ecdc4", "fill": "rgba(78,205,196,0.15)"},
        {"line": "#ef4444", "fill": "rgba(239,68,68,0.15)"},
        {"line": "#8b5cf6", "fill": "rgba(139,92,246,0.15)"},
        {"line": "#fb923c", "fill": "rgba(251,146,60,0.15)"},
    ]

    for idx, (nombre, row) in enumerate(jugadores_data):
        vals = [_pct(float(row.get(s, 0) or 0), s) for s in stats_disponibles]
        xs = [v * _math.cos(a) for v, a in zip(vals, angles)]
        ys = [v * _math.sin(a) for v, a in zip(vals, angles)]
        hover_j = [
            f"<b>{s}</b><br>{nombre}: {float(row.get(s,0) or 0):.2f}<br>Promedio: {promedios.get(s,0):.2f}"
            for s in stats_disponibles
        ]
        c = COLORES_SPIDER[idx % len(COLORES_SPIDER)]
        fig.add_trace(go.Scatter(
            x=xs + [xs[0]], y=ys + [ys[0]],
            mode='lines+markers', name=nombre,
            line=dict(color=c["line"], width=2.5),
            marker=dict(color=c["line"], size=8),
            fill='toself', fillcolor=c["fill"],
            text=hover_j + [hover_j[0]],
            hovertemplate='%{text}<extra></extra>'
        ))

    fig.update_layout(
        paper_bgcolor='#1e2d3d', plot_bgcolor='#1e2d3d',
        font=dict(color='#c8e6e4', size=11),
        height=580, margin=dict(l=80, r=80, t=40, b=40),
        showlegend=True,
        legend=dict(bgcolor='#0d2a27', bordercolor='#4ecdc4', borderwidth=1,
                    font=dict(color='#c8e6e4'), x=0.01, y=0.01),
        xaxis=dict(visible=False, range=[-1.45, 1.45]),
        yaxis=dict(visible=False, range=[-1.45, 1.45], scaleanchor='x', scaleratio=1),
    )
    return fig


# =========================
# INTERFAZ STREAMLIT
# =========================

def main():
    st.markdown("# 🔍 Análisis de Similitud")
    st.markdown("### *Encontrá jugadores similares basándote en perfiles específicos*")
    st.markdown("---")

    with st.sidebar:
        st.markdown("## 🔍 Similitud")
        if st.button("← Volver al Home", use_container_width=True):
            st.switch_page("fm_datalab_home.py")
        st.markdown("---")
        st.markdown("## 📁 Carga de Datos")
        uploaded_file = st.file_uploader(
            "Seleccioná tu CSV de Football Manager",
            type=["csv"], help="Archivo CSV exportado desde FM con separador ';'"
        )
        if uploaded_file:
            df = cargar_data(uploaded_file)
            if df is not None:
                st.success(f"✅ {len(df)} jugadores cargados")
                st.info(f"📊 {len(df.columns)} columnas detectadas")
                st.session_state['df'] = df
            else:
                st.error("❌ Error al cargar el archivo")
                return
        elif 'df' in st.session_state:
            df = st.session_state['df']
            st.success("✅ Usando datos cargados previamente")
        else:
            st.info("👆 Cargá tu archivo CSV para comenzar")
            st.markdown("---")
            st.markdown("""
            **Formato esperado:**
            - Separador: `;`
            - Encoding: UTF-8
            - Columnas requeridas: `jugador`, `posición`, `minutos`
            """)
            return

    df = st.session_state.get('df')
    if df is None:
        st.warning("⚠️ Esperando carga de archivo...")
        return

    st.markdown("## 🎯 Configuración del Análisis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 1️⃣ Jugador a Analizar")
        jugadores_disponibles = sorted(df["jugador"].dropna().unique())
        jugador_nombre = st.selectbox("Seleccioná el jugador", jugadores_disponibles,
            help="Jugador del cual querés encontrar similares")
        jugador_elegido = df[df["jugador"] == jugador_nombre].iloc[0]
        st.markdown(f"**Jugador:** {jugador_nombre}")
        if "posición" in df.columns and not pd.isna(jugador_elegido.get("posición")):
            st.markdown(f"**Posición:** {jugador_elegido['posición']}")
        if "edad" in df.columns and not pd.isna(jugador_elegido.get("edad")):
            st.markdown(f"**Edad:** {int(jugador_elegido['edad'])} años")
        if "minutos" in df.columns and not pd.isna(jugador_elegido.get("minutos")):
            st.markdown(f"**Minutos:** {int(jugador_elegido['minutos'])}")

    with col2:
        st.markdown("### 2️⃣ Perfil de Análisis")
        perfil_key = st.selectbox("Seleccioná el perfil", list(PERFILES.keys()),
            format_func=lambda x: PERFILES[x]["nombre"],
            help="Conjunto de estadísticas a analizar")
        perfil = PERFILES[perfil_key]
        stats = validar_stats_perfil(df, perfil)
        st.markdown(f"**Perfil:** {perfil['nombre']}")
        st.markdown(f"**Stats disponibles:** {len(stats)}/{len(perfil['stats'])}")
        if len(stats) < len(perfil['stats']):
            faltantes = set(perfil['stats']) - set(stats)
            st.warning(f"⚠️ Stats faltantes: {', '.join(faltantes)}")

    st.markdown("---")
    st.markdown("## ⚙️ Filtros")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎭 Filtro por Posición")
        usar_posicion = st.checkbox("Filtrar por posición específica", value=True)
        posicion_elegida = None
        if usar_posicion and "posición" in df.columns:
            posiciones_jugador = extraer_posiciones_jugador(jugador_elegido.get("posición", ""))
            if posiciones_jugador:
                posicion_elegida = st.selectbox("Seleccioná la posición para filtrar",
                    options=posiciones_jugador,
                    help="Mostrará solo jugadores que puedan jugar en esta posición")
                st.success(f"✅ Filtrando por: **{posicion_elegida}**")
            else:
                st.warning("⚠️ No se pudieron detectar posiciones del jugador")
                usar_posicion = False

    with col2:
        st.markdown("### ⏱️ Filtro por Minutos")
        usar_minutos = st.checkbox("Filtrar por minutos jugados", value=True)
        porcentaje_minutos = 50
        if usar_minutos and "minutos" in df.columns:
            query_minutos = jugador_elegido.get("minutos", None)
            if query_minutos and not pd.isna(query_minutos):
                porcentaje_minutos = st.slider("% mínimo de minutos", min_value=0, max_value=100,
                    value=50, step=5,
                    help=f"Mínimo {int(query_minutos * 0.5)} minutos (50% de {int(query_minutos)})")
            else:
                st.warning("⚠️ El jugador no tiene datos de minutos")
                usar_minutos = False

    st.markdown("---")
    st.markdown("## ⚖️ Ponderación de Estadísticas")
    usar_pesos = st.checkbox("Personalizar importancia de estadísticas", value=False,
        help="Permite darle más peso a ciertas estadísticas")
    pesos = np.ones(len(stats))
    if usar_pesos:
        st.markdown("**Definí la importancia de cada estadística:**")
        cols_per_row = 3
        pesos_dict = {}
        for i in range(0, len(stats), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(stats):
                    stat = stats[i + j]
                    with col:
                        peso = st.select_slider(stat, options=["Bajo", "Medio", "Alto"],
                            value="Medio", key=f"peso_{stat}")
                        pesos_dict[stat] = PESOS_MAP[peso]
        pesos = np.array([pesos_dict[stat] for stat in stats])

    st.markdown("---")

    # ========================
    # FIX 3: selector de filas
    # ========================
    col_rows1, col_rows2 = st.columns([3, 1])
    with col_rows2:
        top_n = st.selectbox("Mostrar top", [5, 10, 15, 20, 30, 50, "Todos"],
            index=2, help="Cantidad de jugadores similares a mostrar en la tabla")

    if st.button("🔍 CALCULAR SIMILITUDES", type="primary", use_container_width=True):
        with st.spinner("Procesando..."):
            df_pool = df.copy()
            if usar_posicion and posicion_elegida:
                df_pool = filtrar_posicion(df_pool, posicion_elegida)
                st.info(f"🎭 Pool filtrado por posición {posicion_elegida}: {len(df_pool)} jugadores")
            filtro_stats = {}
            if usar_minutos:
                df_pool, filtro_stats = filtrar_minutos(df_pool, jugador_elegido, porcentaje_minutos)
                if 'warning' in filtro_stats:
                    st.warning(f"⚠️ {filtro_stats['warning']}")
                else:
                    st.info(f"⏱️ Umbral: {filtro_stats['porcentaje']:.0f}% → mínimo {filtro_stats['min_minutos']:.0f} minutos")
                    st.info(f"👥 Jugadores excluidos: {filtro_stats['excluidos']} | Pool final: {filtro_stats['pool_final']}")

            comparator = SimilitudComparatorV3()
            comparator.fit(df_pool, stats)
            cat_pool = comparator.categorize_dataframe(df_pool[stats])
            norm_pool = comparator.normalize_dataframe(df_pool[stats])
            query_stats = {stat: jugador_elegido.get(stat, np.nan) for stat in stats}
            cat_query = comparator.categorize_player(query_stats)
            norm_query = comparator.normalize_player(query_stats)
            cat_pool_w = cat_pool.astype(float) * pesos
            cat_query_w = cat_query.astype(float) * pesos
            norm_pool_w = norm_pool * pesos
            norm_query_w = norm_query * pesos
            mae_sim, euclidean_sim, pearson_sim, ordinal_sim, hybrid_sim = compute_similarity_v3(
                comparator, cat_pool_w, cat_query_w, norm_pool_w, norm_query_w)
            resultados = ranking_jugadores(df_pool, mae_sim, euclidean_sim, pearson_sim,
                ordinal_sim, hybrid_sim, jugador_elegido["jugador"])

            st.session_state['resultados'] = resultados
            st.session_state['jugador_nombre'] = jugador_nombre
            st.session_state['perfil_nombre'] = perfil['nombre']
            st.session_state['stats_usadas'] = stats      # stats del perfil elegido
            st.session_state['df_pool_ref'] = df_pool     # pool para normalizar barras

    # =========================
    # MOSTRAR RESULTADOS
    # =========================

    if 'resultados' in st.session_state:
        st.markdown("---")
        resultados = st.session_state['resultados']
        stats_usadas = st.session_state.get('stats_usadas', stats)
        df_pool_ref = st.session_state.get('df_pool_ref', df)

        st.markdown(f"## 📊 Resultados: similares a **{st.session_state['jugador_nombre']}**")
        st.markdown(f"**Perfil:** {st.session_state['perfil_nombre']}")

        top1 = resultados.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("🥇 Más Similar", top1['jugador'])
        with col2: st.metric("Similitud Híbrida", f"{top1['similitud']:.1f}%")
        with col3: st.metric("MAE", f"{top1['sim_mae']:.1f}%")
        with col4: st.metric("Pearson", f"{top1['sim_pearson']:.1f}%")

        st.markdown("### 📋 Ranking")

        # FIX 3: aplicar top_n
        top_n_val = top_n if top_n != "Todos" else len(resultados)
        resultados_mostrar = resultados.head(int(top_n_val))

        columnas_display = ["jugador", "similitud", "sim_mae", "sim_pearson", "sim_euclidiana", "sim_ordinal"]
        for col in ["posición", "edad", "minutos"]:
            if col in resultados_mostrar.columns:
                columnas_display.insert(1, col)
        df_display = resultados_mostrar[columnas_display].copy()
        if "edad" in df_display.columns:
            df_display["edad"] = df_display["edad"].apply(lambda x: f"{int(x)}" if not pd.isna(x) else "N/A")
        if "minutos" in df_display.columns:
            df_display["minutos"] = df_display["minutos"].apply(lambda x: f"{int(x)}" if not pd.isna(x) else "N/A")
        df_display = df_display.rename(columns={
            "jugador": "Jugador", "posición": "Posición", "edad": "Edad", "minutos": "Minutos",
            "similitud": "Híbrida %", "sim_mae": "MAE %", "sim_pearson": "Pearson %",
            "sim_euclidiana": "Euclidiana %", "sim_ordinal": "Ordinal %"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True,
            column_config={
                "Híbrida %": st.column_config.ProgressColumn("Híbrida %", format="%.1f%%", min_value=0, max_value=100),
                "MAE %": st.column_config.NumberColumn("MAE %", format="%.1f"),
                "Pearson %": st.column_config.NumberColumn("Pearson %", format="%.1f"),
                "Euclidiana %": st.column_config.NumberColumn("Euclidiana %", format="%.1f"),
                "Ordinal %": st.column_config.NumberColumn("Ordinal %", format="%.1f"),
            })

        st.markdown("---")
        st.markdown("""
        **📖 Leyenda:**
        - **Híbrida:** 40% MAE + 25% Euclidiana + 20% Pearson + 15% Ordinal
        - **MAE:** Diferencia promedio absoluta · **Pearson:** Correlación lineal
        - **Euclidiana:** Distancia en espacio normalizado · **Ordinal:** Similitud por percentiles
        """)

        # =========================
        # COMPARACIÓN VISUAL
        # =========================

        st.markdown("---")
        st.markdown("## 📊 Comparación Visual")
        st.markdown("*Seleccioná hasta 4 jugadores para comparar sus estadísticas del perfil*")

        if 'jugadores_similitud_comparar' not in st.session_state:
            st.session_state['jugadores_similitud_comparar'] = []

        jugadores_disponibles_comp = [st.session_state['jugador_nombre']] + resultados['jugador'].head(int(top_n_val)).tolist()

        cols_sel = st.columns(4)
        for i in range(4):
            with cols_sel[i]:
                jugador_select = st.selectbox(
                    f"Jugador {i+1}",
                    options=["Ninguno"] + jugadores_disponibles_comp,
                    key=f"select_comp_{i}",
                    index=1 if i == 0 else 0
                )
                if jugador_select != "Ninguno":
                    if i >= len(st.session_state['jugadores_similitud_comparar']):
                        st.session_state['jugadores_similitud_comparar'].append(jugador_select)
                    else:
                        st.session_state['jugadores_similitud_comparar'][i] = jugador_select
                elif i < len(st.session_state['jugadores_similitud_comparar']):
                    st.session_state['jugadores_similitud_comparar'] = st.session_state['jugadores_similitud_comparar'][:i]

        jugadores_comparar = [j for j in st.session_state['jugadores_similitud_comparar']
                              if j in df['jugador'].values]

        if len(jugadores_comparar) > 0:
            jdata = [(nombre, df[df['jugador'] == nombre].iloc[0])
                     for nombre in jugadores_comparar if len(df[df['jugador'] == nombre]) > 0]

            if jdata:
                tab1, tab2 = st.tabs(["📊 Spider Graph", "📋 Barras estilo FM"])

                with tab1:
                    # FIX 1: spider usa stats del perfil elegido
                    fig = crear_spider_perfil(jdata, stats_usadas, df_pool_ref)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("⚠️ Se necesitan al menos 3 estadísticas del perfil disponibles en el dataset.")

                with tab2:
                    # FIX 2: tabla de barras estilo FM
                    st.markdown(f"**Stats del perfil: {st.session_state['perfil_nombre']}**")
                    html_barras = render_barra_fm(jdata, stats_usadas, df_pool_ref)
                    st.markdown(html_barras, unsafe_allow_html=True)
                    st.caption("Las barras representan el valor relativo al percentil 95 del pool. Valores iguales = barras iguales.")

        # Botón de descarga
        st.markdown("---")
        csv = resultados.head(int(top_n_val)).to_csv(index=False, encoding='utf-8-sig', sep=';')
        st.download_button(
            label="📥 Descargar Resultados (CSV)",
            data=csv,
            file_name=f"fm_similares_{jugador_nombre.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )


if __name__ == "__main__":
    main()

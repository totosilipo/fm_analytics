"""
FM DataLab v3 - Módulo Común
=============================
CSS centralizado, funciones compartidas, lógica de carga unificada.
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.spatial.distance import euclidean
from dataclasses import dataclass
import re
import streamlit as st

# ═══════════════════════════════════════════════════════════════
# CSS CENTRALIZADO
# ═══════════════════════════════════════════════════════════════

COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --bg-dark:    #1a2332;
    --bg-mid:     #1e2d3d;
    --bg-card:    #223044;
    --teal-glow:  #2a6b6b;
    --accent:     #4ecdc4;
    --accent-dim: #3aada5;
    --accent-glow:rgba(78,205,196,0.18);
    --text:       #e8f4f4;
    --text-muted: #7a9eab;
    --border:     rgba(78,205,196,0.15);
    --border-mid: rgba(78,205,196,0.30);
    --danger:     #ef4444;
    --warn:       #f5c518;
    --font-display:'DM Serif Display', Georgia, serif;
    --font-body:   'DM Sans', 'Segoe UI', sans-serif;
    --font-mono:   'JetBrains Mono', 'Courier New', monospace;
}

/* ── Base ── */
html, body, [class*="css"], .stApp {
    background-color: var(--bg-dark) !important;
    color: var(--text);
    font-family: var(--font-body);
}

/* ── Tipografía ── */
h1 {
    color: var(--accent);
    font-family: var(--font-display);
    border-bottom: 2px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 4px;
}
h2, h3 {
    color: var(--accent);
    font-family: var(--font-display);
}
p, label, .stMarkdown p {
    color: var(--text);
    font-family: var(--font-body);
}
code, .stCode {
    font-family: var(--font-mono) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-mid) !important;
    border-right: 1px solid var(--border);
}

/* ── Métricas ── */
[data-testid="stMetricValue"] {
    font-size: 26px;
    color: var(--accent);
    font-family: var(--font-mono);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted);
    font-family: var(--font-body);
}

/* ── Botones ── */
.stButton > button {
    background-color: transparent !important;
    color: var(--accent) !important;
    font-family: var(--font-body);
    font-weight: 600;
    border-radius: 24px;
    border: 2px solid var(--accent) !important;
    padding: 8px 24px;
    transition: all 0.25s;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    background-color: var(--accent) !important;
    color: var(--bg-dark) !important;
    box-shadow: 0 0 16px var(--accent-glow);
}
[data-testid="baseButton-primary"] {
    background-color: var(--accent) !important;
    color: var(--bg-dark) !important;
    font-weight: 700 !important;
}
[data-testid="baseButton-primary"]:hover {
    background-color: var(--accent-dim) !important;
    box-shadow: 0 0 20px var(--accent-glow);
}

/* ── Inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stFileUploader > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background-color: var(--bg-mid) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── Tablas Streamlit ── */
div[data-testid="stDataFrame"] {
    border-radius: 8px;
    border: 1px solid var(--border);
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    color: var(--text-muted) !important;
    font-weight: 600;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Cajas de estado custom ── */
.fm-info {
    background: linear-gradient(135deg, var(--bg-mid), #1d3040);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 3px solid var(--accent);
    margin: 8px 0;
    font-family: var(--font-body);
    font-size: 0.9rem;
    color: var(--text);
}
.fm-success {
    background: linear-gradient(135deg, #1a2e25, #1e3a2e);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 3px solid #22c55e;
    margin: 8px 0;
    font-size: 0.9rem;
    color: #86efac;
}
.fm-warning {
    background: linear-gradient(135deg, #2d2a1a, #332e1a);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 3px solid var(--warn);
    margin: 8px 0;
    font-size: 0.9rem;
    color: #fde68a;
}
.fm-danger {
    background: linear-gradient(135deg, #2d1a1a, #331e1e);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 3px solid var(--danger);
    margin: 8px 0;
    font-size: 0.9rem;
    color: #fca5a5;
}

/* ── Pill de archivo cargado ── */
.archivo-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border-mid);
    border-radius: 20px;
    padding: 6px 14px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--accent);
    margin: 6px 0;
}
.archivo-pill .dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #22c55e;
}

/* ── Badge de perfil ── */
.perfil-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-glow);
    border: 1px solid var(--border-mid);
    border-radius: 6px;
    padding: 4px 10px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--accent);
    margin: 3px 2px;
}

/* ── Stat preview box ── */
.stat-preview-box {
    background: var(--bg-mid);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
}
.stat-preview-title {
    color: var(--text-muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: var(--font-mono);
    margin-bottom: 10px;
}

/* ── Animación de entrada hero ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-wrap { animation: fadeSlideUp 0.5s ease both; }
.modo-card { animation: fadeSlideUp 0.5s ease both; }
.modo-card:nth-child(2) { animation-delay: 0.1s; }
.modo-card:nth-child(3) { animation-delay: 0.2s; }
</style>
"""

def inject_css():
    """Inyecta el CSS global. Llamar al inicio de cada página."""
    st.markdown(COMMON_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CARGA DE DATOS UNIFICADA
# ═══════════════════════════════════════════════════════════════

def limpiar_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza el DataFrame."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (
                df[col].astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = df[col].replace(["-", "nan", ""], np.nan)
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df


def _detectar_separador(contenido: bytes) -> str:
    """Detecta el separador del CSV probando ';' y ',' ."""
    muestra = contenido[:4096].decode("utf-8-sig", errors="ignore")
    return ";" if muestra.count(";") >= muestra.count(",") else ","


def cargar_csv(uploaded_file) -> tuple:
    """
    Carga un CSV con detección automática de separador.
    Retorna (df, separador_usado, error_msg).
    """
    try:
        contenido = uploaded_file.read()
        uploaded_file.seek(0)
        sep = _detectar_separador(contenido)
        df = pd.read_csv(uploaded_file, sep=sep, encoding="utf-8-sig")
        df = limpiar_data(df)

        # Validar columnas mínimas
        cols_req = {"jugador"}
        faltantes = cols_req - set(df.columns)
        if faltantes:
            return None, sep, f"Faltan columnas requeridas: {', '.join(faltantes)}"

        return df, sep, None
    except Exception as e:
        return None, None, str(e)


def sidebar_carga_datos(pagina: str = "") -> pd.DataFrame | None:
    """
    Componente de sidebar unificado para carga de datos.
    Muestra el estado actual del archivo y permite reemplazarlo.
    Retorna el DataFrame activo o None.
    """
    st.markdown("## 📁 Datos")

    df_actual = st.session_state.get("df", None)
    nombre_archivo = st.session_state.get("nombre_archivo", None)

    # Mostrar estado del archivo actual
    if df_actual is not None and nombre_archivo:
        st.markdown(
            f'<div class="archivo-pill"><span class="dot"></span>{nombre_archivo}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="fm-success">✅ {len(df_actual):,} jugadores · {len(df_actual.columns)} columnas</div>',
            unsafe_allow_html=True
        )
        reemplazar = st.checkbox("Cargar otro archivo", value=False, key=f"reemplazar_{pagina}")
    else:
        reemplazar = True

    if reemplazar:
        uploaded_file = st.file_uploader(
            "Seleccioná tu CSV de Football Manager",
            type=["csv"],
            help="CSV exportado desde FM. Se detecta automáticamente el separador (';' o ',')",
            key=f"uploader_{pagina}"
        )
        if uploaded_file is not None:
            df_nuevo, sep, error = cargar_csv(uploaded_file)
            if error:
                st.markdown(
                    f'<div class="fm-danger">❌ Error al cargar: {error}</div>',
                    unsafe_allow_html=True
                )
                return df_actual  # Devolver el anterior si hay
            else:
                st.session_state["df"] = df_nuevo
                st.session_state["nombre_archivo"] = uploaded_file.name
                st.session_state["sep_usado"] = sep
                # Limpiar resultados anteriores al cargar nuevo archivo
                for key in ["resultados", "jugadores_similitud_comparar",
                            "ultima_busqueda_hash", "df_pool_ref"]:
                    st.session_state.pop(key, None)
                st.markdown(
                    f'<div class="fm-success">✅ Cargado con separador "{sep}"</div>',
                    unsafe_allow_html=True
                )
                st.rerun()

    st.markdown("---")

    if df_actual is None:
        st.markdown("""
        <div class="fm-info">
        <strong>Formato esperado:</strong><br>
        · Separador: <code>;</code> o <code>,</code> (auto-detectado)<br>
        · Encoding: UTF-8<br>
        · Columna requerida: <code>jugador</code>
        </div>
        """, unsafe_allow_html=True)
        return None

    return df_actual


# ═══════════════════════════════════════════════════════════════
# FILTROS DE POSICIÓN (versión avanzada, compartida)
# ═══════════════════════════════════════════════════════════════

def extraer_posiciones_jugador(posicion_str: str) -> list:
    """
    Extrae todas las posiciones con rol de un string de posición FM.
    Ej: 'MP (DI). DL (C)' → ['MP(D)', 'MP(I)', 'DL(C)']
    """
    if not posicion_str or pd.isna(posicion_str):
        return []
    posiciones_limpias = []
    texto = str(posicion_str).upper().replace(".", ",").replace(";", ",")
    for grupo in texto.split(","):
        grupo = grupo.strip()
        if not grupo:
            continue
        if "(" in grupo:
            base, roles_str = grupo.split("(", 1)
            bases = [b.strip() for b in base.split("/") if b.strip()]
            roles = list(dict.fromkeys(re.findall(r"[DCI]", roles_str)))
            for b in bases:
                for r in roles:
                    posiciones_limpias.append(f"{b}({r})")
                if not roles:
                    posiciones_limpias.append(b)
        else:
            posiciones_limpias.extend([b.strip() for b in grupo.split("/") if b.strip()])
    return list(dict.fromkeys(posiciones_limpias))


def _jugador_tiene_posicion(pos_str: str, buscar: str) -> bool:
    """
    Comprueba si un jugador tiene una posición específica.
    Soporta búsqueda con rol exacto (ej: 'MD(D)') o solo base (ej: 'MD').
    """
    if not pos_str or pd.isna(pos_str):
        return False
    buscar = buscar.upper().strip()
    texto = str(pos_str).upper().replace(".", ",").replace(";", ",")

    if "(" in buscar:
        base_buscar = buscar.split("(")[0].strip()
        rol_buscar  = buscar.split("(")[1].replace(")", "").strip()
        for grupo in texto.split(","):
            grupo = grupo.strip()
            parte_base = grupo.split("(")[0].strip() if "(" in grupo else grupo
            roles = list(grupo.split("(")[1].replace(")", "")) if "(" in grupo else []
            for token in parte_base.split("/"):
                if token.strip() == base_buscar and rol_buscar in roles:
                    return True
        return False
    else:
        # Búsqueda por base: reconstruir todas las bases del string
        bases = []
        for grupo in texto.split(","):
            grupo = grupo.strip()
            parte_base = grupo.split("(")[0].strip() if "(" in grupo else grupo
            bases.extend([t.strip() for t in parte_base.split("/")])
        return buscar in bases


def filtrar_por_posicion(df: pd.DataFrame, posicion: str) -> pd.DataFrame:
    """Filtra el DataFrame usando el filtro avanzado de posición."""
    col_pos = next(
        (c for c in df.columns if c in ["posición", "posicion", "pos", "position"]),
        None
    )
    if col_pos is None:
        return df
    return df[df[col_pos].apply(lambda x: _jugador_tiene_posicion(x, posicion))].copy()


def obtener_posiciones_unicas(df: pd.DataFrame) -> list:
    """
    Extrae todas las posiciones únicas con rol del dataset completo.
    Usa el parser avanzado para consistencia con Similitud.
    """
    col_pos = next(
        (c for c in df.columns if c in ["posición", "posicion", "pos", "position"]),
        None
    )
    if col_pos is None:
        return []
    todas = []
    for ps in df[col_pos].dropna().unique():
        todas.extend(extraer_posiciones_jugador(ps))
    return sorted(set(todas))


def filtrar_minutos(df, query_jugador, porcentaje, min_col="minutos"):
    """Filtra por minutos relativos al jugador de referencia."""
    info = {}
    if min_col not in df.columns:
        info["warning"] = f"Columna '{min_col}' no encontrada"
        return df, info
    qmin = query_jugador.get(min_col, None)
    if qmin is None or pd.isna(qmin):
        info["warning"] = "El jugador no tiene datos de minutos"
        return df, info
    qmin = float(qmin)
    umbral = qmin * (porcentaje / 100)
    antes = len(df)
    filtrado = df[df[min_col] >= umbral].reset_index(drop=True)
    info.update({"query_minutos": qmin, "porcentaje": porcentaje,
                 "min_minutos": umbral, "excluidos": antes - len(filtrado),
                 "pool_final": len(filtrado)})
    if len(filtrado) < 30:
        info["warning"] = f"Pool con menos de 30 jugadores ({len(filtrado)}). Resultados menos precisos."
    return filtrado, info


# ═══════════════════════════════════════════════════════════════
# PERFILES
# ═══════════════════════════════════════════════════════════════

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


def validar_stats_perfil(df: pd.DataFrame, perfil: dict) -> list:
    """Retorna las stats del perfil que existen en el DataFrame."""
    return [s for s in perfil["stats"] if s in df.columns]


def render_perfil_preview(perfil: dict, stats_disponibles: list) -> str:
    """
    Renderiza un preview visual de las stats del perfil.
    Las stats disponibles se muestran en verde, las faltantes en gris.
    """
    badges = ""
    for stat in perfil["stats"]:
        if stat in stats_disponibles:
            badges += f'<span class="perfil-badge" style="border-color:rgba(78,205,196,0.4);color:#4ecdc4;">✓ {stat}</span>'
        else:
            badges += f'<span class="perfil-badge" style="border-color:rgba(122,158,171,0.2);color:#4a6070;background:rgba(0,0,0,0.1);">✗ {stat}</span>'
    n_ok = len(stats_disponibles)
    n_total = len(perfil["stats"])
    color_pct = "#22c55e" if n_ok == n_total else ("#f5c518" if n_ok >= n_total * 0.7 else "#ef4444")
    return f"""
    <div class="stat-preview-box">
        <div class="stat-preview-title">Stats del perfil · <span style="color:{color_pct};">{n_ok}/{n_total} disponibles</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;">{badges}</div>
    </div>
    """


# ═══════════════════════════════════════════════════════════════
# COMPARADOR V3
# ═══════════════════════════════════════════════════════════════

@dataclass
class PercentileThresholds:
    p10: float; p25: float; p40: float; p50: float
    p60: float; p75: float; p90: float
    min: float; max: float; mean: float; std: float


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
                p90=np.percentile(col, 90), min=float(np.min(col)),
                max=float(np.max(col)), mean=float(np.mean(col)),
                std=float(np.std(col))
            )
        self.fitted = True

    def _cat(self, value, stat):
        if pd.isna(value) or stat not in self.percentile_thresholds:
            return 0
        t = self.percentile_thresholds[stat]
        if value <= t.p10: return -3
        elif value <= t.p25: return -2
        elif value <= t.p40: return -1
        elif value <= t.p60: return 0
        elif value <= t.p75: return 1
        elif value <= t.p90: return 2
        else: return 3

    def categorize_player(self, player_stats):
        return np.array([self._cat(player_stats.get(s, np.nan), s) for s in self.stats])

    def categorize_dataframe(self, df_stats):
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat in df_stats.columns:
                result[:, i] = df_stats[stat].apply(lambda x: self._cat(x, stat))
        return result

    def normalize_player(self, player_stats):
        out = []
        for stat in self.stats:
            v = player_stats.get(stat, np.nan)
            if pd.isna(v) or stat not in self.percentile_thresholds:
                out.append(0.0); continue
            t = self.percentile_thresholds[stat]
            out.append(float(np.clip((v - t.mean) / t.std, -3, 3)) if t.std != 0 else 0.0)
        return np.array(out)

    def normalize_dataframe(self, df_stats):
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat not in df_stats.columns or stat not in self.percentile_thresholds:
                continue
            t = self.percentile_thresholds[stat]
            if t.std == 0: continue
            result[:, i] = np.clip((df_stats[stat].fillna(t.mean) - t.mean) / t.std, -3, 3)
        return result

    def mae_sim(self, a, b):   return 1 - np.mean(np.abs(a - b)) / 3
    def euc_sim(self, a, b):
        d = euclidean(a, b)
        return 1 - d / np.sqrt(len(a) * 36)
    def pear_sim(self, a, b):
        if np.std(a) == 0 or np.std(b) == 0: return 0.5
        try:
            c, _ = pearsonr(a, b); return (c + 1) / 2
        except: return 0.5
    def ord_sim(self, a, b):   return 1 - np.mean(np.abs(a - b)) / 6
    def hybrid(self, c1, c2, n1, n2):
        return 0.40*self.mae_sim(n1,n2) + 0.25*self.euc_sim(n1,n2) + \
               0.20*self.pear_sim(n1,n2) + 0.15*self.ord_sim(c1,c2)


def compute_similarity_v3(comparator, cat_pool, cat_query, norm_pool, norm_query):
    n = cat_pool.shape[0]
    mae_s = np.zeros(n); euc_s = np.zeros(n)
    pear_s = np.zeros(n); ord_s = np.zeros(n); hyb_s = np.zeros(n)
    for i in range(n):
        mae_s[i]  = comparator.mae_sim(norm_pool[i], norm_query)
        euc_s[i]  = comparator.euc_sim(norm_pool[i], norm_query)
        pear_s[i] = comparator.pear_sim(norm_pool[i], norm_query)
        ord_s[i]  = comparator.ord_sim(cat_pool[i], cat_query)
        hyb_s[i]  = comparator.hybrid(cat_pool[i], cat_query, norm_pool[i], norm_query)
    return mae_s, euc_s, pear_s, ord_s, hyb_s


def ranking_jugadores(df_pool, mae_s, euc_s, pear_s, ord_s, hyb_s, query_nombre):
    result = df_pool.copy()
    result["sim_mae"]       = (mae_s  * 100).round(1)
    result["sim_euclidiana"]= (euc_s  * 100).round(1)
    result["sim_pearson"]   = (pear_s * 100).round(1)
    result["sim_ordinal"]   = (ord_s  * 100).round(1)
    result["similitud"]     = (hyb_s  * 100).round(1)
    result = result[result["jugador"].str.lower() != query_nombre.lower()]
    return result.sort_values("similitud", ascending=False).reset_index(drop=True)
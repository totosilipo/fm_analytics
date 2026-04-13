"""
FM DataLab v3 - Home
====================
Página principal con selector de modos
"""

import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="FM DataLab v3 - Home",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS con paleta oficial
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --bg-dark:    #1a2332;
    --bg-mid:     #1e2d3d;
    --teal-glow:  #2a6b6b;
    --accent:     #4ecdc4;
    --accent-dim: #3aada5;
    --text:       #e8f4f4;
    --text-muted: #7a9eab;
    --border:     rgba(78,205,196,0.15);
    --font-display: 'DM Serif Display', Georgia, serif;
    --font-body:    'DM Sans', 'Segoe UI', sans-serif;
    --font-mono:    'JetBrains Mono', 'Courier New', monospace;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg-dark) !important;
    color: var(--text);
    font-family: var(--font-body);
}

h1, h2, h3 {
    font-family: var(--font-display);
    color: var(--accent);
}

p, label, .stMarkdown p {
    color: var(--text);
    font-family: var(--font-body);
}

section[data-testid="stSidebar"] {
    background-color: var(--bg-mid) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stMetricValue"] {
    font-size: 26px;
    color: var(--accent);
    font-family: var(--font-mono);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted);
    font-family: var(--font-body);
}

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
}
[data-testid="baseButton-primary"] {
    background-color: var(--accent) !important;
    color: var(--bg-dark) !important;
}

.stSelectbox > div > div,
.stFileUploader > div {
    background-color: var(--bg-mid) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Hero */
.hero-wrap {
    text-align: center;
    padding: 40px 20px 10px 20px;
}
.hero-fm {
    font-family: var(--font-display);
    font-size: 4rem;
    font-weight: 900;
    color: var(--text);
    line-height: 1;
    margin: 0;
}
.hero-datalab {
    font-family: var(--font-display);
    font-size: 3rem;
    font-style: italic;
    color: var(--accent);
    line-height: 1;
    margin: 0;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1.05rem;
    margin-top: 14px;
    font-family: var(--font-body);
}

/* Stat box */
.stat-box {
    background: var(--bg-mid);
    border-radius: 12px;
    padding: 22px 16px;
    text-align: center;
    border: 1px solid var(--border);
}
.stat-num {
    font-size: 2.2rem;
    font-weight: bold;
    color: var(--accent);
    font-family: var(--font-mono);
    display: block;
}
.stat-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: var(--font-body);
}

/* Modo card */
.modo-card {
    background: var(--bg-mid);
    border-radius: 14px;
    padding: 28px 24px;
    border: 1px solid var(--border);
    transition: border-color 0.25s, box-shadow 0.25s;
    height: 100%;
}
.modo-card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 24px rgba(78,205,196,0.12);
}
.modo-icono { font-size: 2.4rem; text-align: center; margin-bottom: 12px; }
.modo-tag {
    background: var(--accent);
    color: var(--bg-dark);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 10px;
    font-family: var(--font-mono);
}
.modo-titulo {
    color: var(--text);
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 6px;
    font-family: var(--font-display);
}
.modo-desc {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
    font-family: var(--font-body);
}

/* Steps */
.step-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 18px 0;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--text-muted);
    font-size: 0.8rem;
    font-family: var(--font-mono);
}
.step-num {
    background: var(--teal-glow);
    color: var(--accent);
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700;
}
.step-sep { color: var(--teal-glow); font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNCIONES DE CARGA
# =========================

def limpiar_data(df: pd.DataFrame) -> pd.DataFrame:
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


def cargar_data(uploaded_file) -> pd.DataFrame:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        return limpiar_data(df)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None


# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.markdown("## 📁 Carga de Datos")

    uploaded_file = st.file_uploader(
        "Seleccioná tu CSV de Football Manager",
        type=["csv"],
        help="Archivo CSV exportado desde FM con separador ';'"
    )

    if uploaded_file:
        df = cargar_data(uploaded_file)
        if df is not None:
            st.success(f"✅ {len(df)} jugadores cargados")
            st.info(f"📊 {len(df.columns)} columnas detectadas")
            st.session_state['df'] = df
            st.session_state['archivo_cargado'] = True

            st.markdown("---")
            st.markdown("### 📋 Resumen")

            if 'jugador' in df.columns:
                st.metric("Jugadores", len(df['jugador'].dropna().unique()))
            if 'posición' in df.columns:
                st.metric("Posiciones únicas", df['posición'].dropna().nunique())
            if 'minutos' in df.columns:
                st.metric("Minutos totales", f"{int(df['minutos'].sum()):,}")
        else:
            st.error("❌ Error al cargar el archivo")
    else:
        st.info("👆 Cargá tu archivo CSV para comenzar")
        st.markdown("---")
        st.markdown("""
        **Formato esperado:**
        - Separador: `;`
        - Encoding: UTF-8
        - Columnas mínimas: `jugador`, `posición`, `minutos`
        """)

# =========================
# HERO
# =========================

st.markdown("""
<div class="hero-wrap">
    <p class="hero-fm">FM</p>
    <p class="hero-datalab">DataLab v3</p>
    <p class="hero-sub">Análisis avanzado de jugadores · Football Manager</p>
    <div class="step-row">
        <div class="step-item"><div class="step-num">1</div> Cargar CSV</div>
        <div class="step-sep">›</div>
        <div class="step-item"><div class="step-num">2</div> Seleccionar Jugador</div>
        <div class="step-sep">›</div>
        <div class="step-item"><div class="step-num">3</div> Aplicar Filtros</div>
        <div class="step-sep">›</div>
        <div class="step-item"><div class="step-num">4</div> Ponderar Stats</div>
        <div class="step-sep">›</div>
        <div class="step-item"><div class="step-num">5</div> Ranking</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# CONTENIDO SEGÚN ESTADO
# =========================

if not st.session_state.get('archivo_cargado', False):
    st.info("👈 **Cargá tu archivo CSV desde el panel lateral para comenzar**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">🔍</div>
            <span class="modo-tag">SIMILITUD</span>
            <p class="modo-titulo">Encontrar similares</p>
            <p class="modo-desc">16 perfiles · 5 métricas · filtros avanzados · ponderación personalizable</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">⚖️</div>
            <span class="modo-tag">COMPARACIÓN</span>
            <p class="modo-titulo">Explorar dataset</p>
            <p class="modo-desc">Tabla completa · spider graphs · comparar hasta 4 jugadores · ranking</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">📊</div>
            <span class="modo-tag">DIFERENCIAS</span>
            <p class="modo-titulo">Outliers vs promedio</p>
            <p class="modo-desc">Desviaciones del pool · identificar outliers · fortalezas y debilidades</p>
        </div>
        """, unsafe_allow_html=True)

else:
    df = st.session_state['df']

    # Stats del dataset
    col1, col2, col3, col4 = st.columns(4)
    cols_excluir = ['jugador', 'posición', 'pos', 'nombre', 'equipo', 'club', 'edad', 'minutos']
    stats_num = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in cols_excluir]

    with col1:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(df)}</span><span class="stat-label">Jugadores</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(df.columns)}</span><span class="stat-label">Columnas</span></div>', unsafe_allow_html=True)
    with col3:
        pos = df['posición'].dropna().nunique() if 'posición' in df.columns else 0
        st.markdown(f'<div class="stat-box"><span class="stat-num">{pos}</span><span class="stat-label">Posiciones</span></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(stats_num)}</span><span class="stat-label">Stats</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🎯 ¿Qué querés hacer hoy?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">🔍</div>
            <span class="modo-tag">PRINCIPAL</span>
            <p class="modo-titulo">Similitud</p>
            <p class="modo-desc">
                Encontrá jugadores similares basándote en perfiles específicos.
                Usa 5 métricas para encontrar el reemplazo perfecto.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Similitud →", use_container_width=True, type="primary"):
            st.switch_page("pages/1_🔍_Similitud.py")

    with col2:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">⚖️</div>
            <span class="modo-tag">EXPLORACIÓN</span>
            <p class="modo-titulo">Comparación</p>
            <p class="modo-desc">
                Explorá el dataset, filtrá por posición y minutos,
                comparar hasta 4 jugadores con spider graphs.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Comparación →", use_container_width=True):
            st.switch_page("pages/2_⚖️_Comparacion.py")

    with col3:
        st.markdown("""
        <div class="modo-card">
            <div class="modo-icono">📊</div>
            <span class="modo-tag">ANÁLISIS</span>
            <p class="modo-titulo">Diferencias</p>
            <p class="modo-desc">
                Analizá qué tan lejos está cada jugador del promedio del pool.
                Identificá outliers y características únicas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Diferencias →", use_container_width=True):
            st.switch_page("pages/3_📊_Diferencias.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#7a9eab; padding:16px; font-family:'DM Sans',sans-serif; font-size:0.85rem;">
    <strong style="color:#4ecdc4;">FM DataLab v3</strong> · Streamlit Edition · Desarrollado para la comunidad de Football Manager
</div>
""", unsafe_allow_html=True)

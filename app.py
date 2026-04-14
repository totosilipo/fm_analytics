"""
FM Analytics - Home
====================
Página principal con selector de modos y carga centralizada.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils_common import inject_css, sidebar_carga_datos

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="FM Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# CSS adicional exclusivo del Home
st.markdown("""
<style>
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
.stat-box {
    background: var(--bg-mid);
    border-radius: 12px;
    padding: 22px 16px;
    text-align: center;
    border: 1px solid var(--border);
    transition: border-color 0.25s, box-shadow 0.25s;
}
.stat-box:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 20px var(--accent-glow);
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
    box-shadow: 0 4px 24px var(--accent-glow);
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

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    df = sidebar_carga_datos(pagina="home")

    if df is not None:
        st.markdown("### 📋 Resumen")
        if "jugador" in df.columns:
            st.metric("Jugadores", f"{len(df['jugador'].dropna().unique()):,}")
        if "posición" in df.columns:
            st.metric("Posiciones únicas", df["posición"].dropna().nunique())
        if "minutos" in df.columns:
            st.metric("Minutos totales", f"{int(df['minutos'].sum()):,}")

# ═══════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-wrap">
    <p class="hero-fm">FM</p>
    <p class="hero-datalab">Analytics</p>
    <p class="hero-sub">Análisis avanzado de jugadores · Football Manager</p>
    <div class="step-row">
        <div class="step-item"><div class="step-num">1</div> Cargar CSV</div>
        <div class="step-sep">›</div>
        <div class="step-item"><div class="step-num">2</div> Elegir Jugador</div>
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

# ═══════════════════════════════════════════════════════════════
# CONTENIDO
# ═══════════════════════════════════════════════════════════════

if df is None:
    st.markdown(
        '<div class="fm-info" style="text-align:center;font-size:1rem;">👈 <strong>Cargá tu archivo CSV desde el panel lateral para comenzar</strong></div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">🔍</div><span class="modo-tag">SIMILITUD</span>
            <p class="modo-titulo">Encontrar similares</p>
            <p class="modo-desc">16 perfiles · 5 métricas · filtros avanzados · ponderación personalizable</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">⚖️</div><span class="modo-tag">COMPARACIÓN</span>
            <p class="modo-titulo">Explorar dataset</p>
            <p class="modo-desc">Tabla completa · spider graphs · comparar hasta 4 jugadores · ranking</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">📊</div><span class="modo-tag">DIFERENCIAS</span>
            <p class="modo-titulo">Outliers vs promedio</p>
            <p class="modo-desc">Desviaciones del pool · identificar outliers · fortalezas y debilidades</p>
        </div>""", unsafe_allow_html=True)

else:
    # Stats del dataset
    xcl = {"jugador", "posición", "pos", "nombre", "equipo", "club", "edad", "minutos"}
    stats_num = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in xcl]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(df):,}</span><span class="stat-label">Jugadores</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(df.columns)}</span><span class="stat-label">Columnas</span></div>', unsafe_allow_html=True)
    with col3:
        # Calculamos el promedio de edad si la columna existe en el CSV
        edad_promedio = round(df["edad"].mean(), 1) if "edad" in df.columns else "N/A"
        st.markdown(f'<div class="stat-box"><span class="stat-num">{edad_promedio}</span><span class="stat-label">Edad Prom.</span></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><span class="stat-num">{len(stats_num)}</span><span class="stat-label">Stats numéricas</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🎯 ¿Qué querés hacer hoy?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">🔍</div><span class="modo-tag">PRINCIPAL</span>
            <p class="modo-titulo">Similitud</p>
            <p class="modo-desc">Encontrá jugadores similares con perfiles específicos y 5 métricas de similitud.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Ir a Similitud →", use_container_width=True, type="primary"):
            st.switch_page("pages/1_🔍_Similitud.py")

    with col2:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">⚖️</div><span class="modo-tag">EXPLORACIÓN</span>
            <p class="modo-titulo">Comparación</p>
            <p class="modo-desc">Explorá el dataset, filtrá y comparar hasta 4 jugadores con spider graphs.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Ir a Comparación →", use_container_width=True):
            st.switch_page("pages/2_⚖️_Comparacion.py")

    with col3:
        st.markdown("""<div class="modo-card">
            <div class="modo-icono">📊</div><span class="modo-tag">ANÁLISIS</span>
            <p class="modo-titulo">Diferencias</p>
            <p class="modo-desc">Analizá qué tan lejos está cada jugador del promedio del pool.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Ir a Diferencias →", use_container_width=True):
            st.switch_page("pages/3_📊_Diferencias.py")


# ═══════════════════════════════════════════════════════════════
# EJEMPLOS DE USO
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 💡 Ejemplos de uso")

st.markdown("""
<div class="modo-card" style="height: auto; padding: 24px; text-align: left;">
<h4 style="color: var(--text); font-family: var(--font-display); margin-top: 0; font-size: 1.2rem;">¿Cómo sacarle el máximo provecho a la herramienta?</h4>
<div style="color: var(--text-muted); font-family: var(--font-body); line-height: 1.6; font-size: 0.95rem;">
        
<p><strong style="color: var(--accent);">1. Encontrar al reemplazo perfecto (Similitud):</strong><br>
¿Vendiste a tu mediocampista estrella y estas luchando por encontrar el reemplazo perfecto?. Vas a <em>Similitud</em>, 
elegís el perfil "Todoterreno" (o el que mejor se adapte a tu táctica), filtrás por la posición exacta y el algoritmo te va a devolver 
los jugadores de tu base de datos que estadísticamente juegan más parecido a él. Eso no significa que sea el mejor. 
Por eso te recomiendo que analices más allá del top 10 que devuelve la tabla. Tomate el tiempo de ver jugador por jugador!</p>
        
<p><strong style="color: var(--accent);">2. Scouting cara a cara (Comparación):</strong><br>
¿Estás indeciso entre varios jugadores para fichar? ¿Querés evaluar que jugador de tu plantel rindió mejor?. Con la herramienta de <em>Comparación</em>, 
podés ver detalladamente todas sus estadisticas. También podes seleccionarlos para obtener una vista más personalizada o seleccionarlos para verlos en un
gráfico radial con todas sus estadisticas. </p>
        
<p><strong style="color: var(--accent);">3. Analisis respecto al promedio (Diferencias):</strong><br>
¿Querés saber que jugador de tu plantel da los mejores pases? ¿Querés ver que tan bien lo hace tu delantero respecto a los de su liga?. 
Vas a <em>Diferencias</em>, elegís las estadisticas que quieras y la tabla te mostrará qué jugador está rompiendo la métrica muy por encima del promedio general 
de la selección que hayas cargado. Descubrí que jugador está rindiendo con un nivel mejor que el promedio!.</p>

<p><strong style="color: var(--accent);"> Recordá descargar nuestra view para tener todas las estadisticas a la hora de exportar la base de datos.
</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
# (Tu código del footer sigue acá abajo...)
# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#7a9eab;padding:16px;font-family:'DM Sans',sans-serif;font-size:0.85rem;">
    <strong style="color:#4ecdc4;">FM Analytics v3</strong> · Streamlit Edition · Desarrollado para la comunidad de Football Manager
</div>
""", unsafe_allow_html=True)
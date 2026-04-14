"""
FM DataLab v3 - Diferencias
============================
View: solo renderiza UI y delega toda la lógica al ViewModel.
"""

import streamlit as st
import pandas as pd

from utils_common import inject_css, sidebar_carga_datos
from domain.diferencias_vm import DiferenciasViewModel
from data.stats_labels import label

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="FM DataLab v3 - Diferencias",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()
vm = DiferenciasViewModel()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 📊 Diferencias")
    if st.button("← Volver al Home", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("---")
    df = sidebar_carga_datos(pagina="diferencias")
    if df is not None:
        st.markdown("""
        <div class="fm-info" style="font-size:0.83rem;">
        📊 Desviaciones del promedio<br>
        🎯 Identificá outliers<br>
        📈 Fortalezas y debilidades
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# GUARD
# ═══════════════════════════════════════════════════════════════

st.markdown("# 📊 Diferencia vs Promedio")
st.markdown("### *Analizá qué tan lejos está cada jugador del promedio del pool*")
st.markdown("---")

if df is None:
    st.markdown(
        '<div class="fm-warning">⚠️ Cargá tu archivo CSV desde el panel lateral para comenzar.</div>',
        unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
# FILTROS
# ═══════════════════════════════════════════════════════════════

st.markdown("## ⚙️ Filtros")
c1, c2, c3, c4 = st.columns(4)

with c1:
    pos_opts        = vm.get_posiciones(df)
    posicion_filtro = st.selectbox("Posición", ["Todas"] + pos_opts)
with c2:
    min_min = st.number_input("Minutos mín.", min_value=0, value=0, step=100)
with c3:
    min_max = st.number_input(
        "Minutos máx.", min_value=0,
        value=vm.get_min_max_minutos(df),
        step=100)
with c4:
    limite = st.selectbox("Mostrar", [10, 25, 50, 100, "Todos"], index=2)

df_f = vm.aplicar_filtros(df, posicion_filtro, min_min, min_max)

st.markdown(
    f'<div class="fm-info">👥 {len(df_f):,} jugadores en el pool</div>',
    unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# SELECTOR DE STATS
# ═══════════════════════════════════════════════════════════════

st.markdown("## 📊 Estadísticas a Analizar")
stats_d  = vm.get_stats_numericas(df)
cols_sel = st.multiselect(
    "Seleccioná las estadísticas",
    options=stats_d,
    format_func=label,
    default=stats_d[:8] if len(stats_d) >= 8 else stats_d,
)

if not cols_sel:
    st.markdown(
        '<div class="fm-warning">⚠️ Seleccioná al menos una estadística.</div>',
        unsafe_allow_html=True)
    st.stop()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# PROMEDIOS
# ═══════════════════════════════════════════════════════════════

st.markdown("## 📈 Promedios del Pool")
promedios = vm.calcular_promedios(df_f, cols_sel)

for i in range(0, len(cols_sel), 4):
    row_cols = st.columns(4)
    for j, rc in enumerate(row_cols):
        if i + j < len(cols_sel):
            s = cols_sel[i + j]
            if s in promedios:
                with rc:
                    st.metric(label(s), f"{promedios[s]:.2f}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# TABLA DE DIFERENCIAS
# ═══════════════════════════════════════════════════════════════

df_dif = vm.calcular_diferencias(df_f, cols_sel, promedios, limite)

st.markdown("### 📋 Tabla de Diferencias")
st.markdown(
    '<span style="color:#4ecdc4;font-weight:700;">■</span> '
    '<span style="color:#e8f4f4;font-size:0.9rem;">Cyan = sobre el promedio &nbsp;&nbsp;</span>'
    '<span style="color:#ef4444;font-weight:700;">■</span> '
    '<span style="color:#e8f4f4;font-size:0.9rem;">Rojo = bajo el promedio</span>',
    unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if len(df_dif) == 0:
    st.markdown(
        '<div class="fm-warning">⚠️ No hay jugadores que cumplan los filtros.</div>',
        unsafe_allow_html=True)
else:
    df_display = vm.build_tabla_display(df_dif, cols_sel)
    df_display = df_display.rename(columns={s: label(s) for s in cols_sel if s in df_display.columns})
    cols_labeled = [label(s) for s in cols_sel if label(s) in df_display.columns]

    def color_diferencias(val):
        if isinstance(val, (int, float)) and not pd.isna(val):
            if val > 0: return 'color: #4ecdc4; font-weight: 700;'
            if val < 0: return 'color: #ef4444; font-weight: 700;'
        return ''

    def formato_texto(val):
        if pd.isna(val): return "—"
        return f"+{val:.2f}" if val > 0 else f"{val:.2f}"

    styled_df = (
        df_display.style
        .map(color_diferencias, subset=cols_labeled)
        .format({s: formato_texto for s in cols_labeled})
    )
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # ── Análisis rápido ────────────────────────────────────────────
    st.markdown("### 💡 Análisis Rápido")
    analisis = vm.get_analisis_rapido(df_dif, cols_sel)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("**🌟 Top 3 Más Destacados**")
        for jugador, valor in analisis["top_positivos"]:
            st.markdown(
                f'<div class="fm-success">🌟 <strong>{jugador}</strong>: +{valor:.2f}</div>',
                unsafe_allow_html=True)
    with a2:
        st.markdown("**📉 Top 3 Por Debajo**")
        for jugador, valor in analisis["top_negativos"]:
            st.markdown(
                f'<div class="fm-danger">📉 <strong>{jugador}</strong>: {valor:.2f}</div>',
                unsafe_allow_html=True)

    # ── Descarga ───────────────────────────────────────────────────
    st.markdown("---")
    csv = vm.build_csv_exportable(df_dif, cols_sel)
    st.download_button(
        "📥 Descargar Análisis (CSV)",
        data=csv,
        file_name="fm_diferencias.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#7a9eab;padding:16px;font-size:0.85rem;">'
    '<strong style="color:#4ecdc4;">FM DataLab v3</strong> · Diferencias</div>',
    unsafe_allow_html=True)

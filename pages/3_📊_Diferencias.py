"""
FM DataLab v3 - Diferencias
============================
Analiza diferencias vs el promedio del pool.
Filtro de posición avanzado (mismo parser que Similitud).
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils_common import (
    inject_css, sidebar_carga_datos,
    obtener_posiciones_unicas, filtrar_por_posicion,
)

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
# FILTROS — usa filtro avanzado (FIX 9)
# ═══════════════════════════════════════════════════════════════

st.markdown("## ⚙️ Filtros")
c1, c2, c3, c4 = st.columns(4)

with c1:
    # FIX 9: parser avanzado
    pos_opts = obtener_posiciones_unicas(df)
    posicion_filtro = st.selectbox("Posición", ["Todas"] + pos_opts)

with c2:
    min_min = st.number_input("Minutos mín.", min_value=0, value=0, step=100)
with c3:
    min_max = st.number_input(
        "Minutos máx.", min_value=0,
        value=int(df["minutos"].max()) if "minutos" in df.columns else 10000,
        step=100)
with c4:
    limite = st.selectbox("Mostrar", [10, 25, 50, 100, "Todos"], index=2)

df_f = df.copy()
if posicion_filtro != "Todas":
    df_f = filtrar_por_posicion(df_f, posicion_filtro)   # ← parser avanzado
if "minutos" in df_f.columns:
    df_f = df_f[(df_f["minutos"] >= min_min) & (df_f["minutos"] <= min_max)]

st.markdown(
    f'<div class="fm-info">👥 {len(df_f):,} jugadores en el pool</div>',
    unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# SELECTOR DE STATS
# ═══════════════════════════════════════════════════════════════

st.markdown("## 📊 Estadísticas a Analizar")
xcl = {"jugador","posición","pos","nombre","equipo","club","edad","minutos"}
stats_d = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in xcl]

cols_sel = st.multiselect("Seleccioná las estadísticas", options=stats_d,
    default=stats_d[:8] if len(stats_d)>=8 else stats_d)

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
promedios = {s: df_f[s].mean() for s in cols_sel if s in df_f.columns}

for i in range(0, len(cols_sel), 4):
    row_cols = st.columns(4)
    for j, rc in enumerate(row_cols):
        if i+j < len(cols_sel):
            s = cols_sel[i+j]
            if s in promedios:
                with rc:
                    st.metric(s, f"{promedios[s]:.2f}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# TABLA DE DIFERENCIAS
# ═══════════════════════════════════════════════════════════════


df_dif = df_f.copy()
for s in cols_sel:
    if s in df_dif.columns:
        df_dif[f"_dif_{s}"] = df_dif[s] - promedios.get(s, 0)

if limite != "Todos":
    df_dif = df_dif.head(int(limite))

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
    # 1. Preparar las columnas a mostrar
    base_cols = [c for c in ["jugador","posición","minutos"] if c in df_dif.columns]
    dif_cols = [f"_dif_{s}" for s in cols_sel if f"_dif_{s}" in df_dif.columns]
    
    # 2. Crear dataframe para display y limpiar los nombres de las columnas
    df_display = df_dif[base_cols + dif_cols].copy()
    df_display = df_display.rename(columns={f"_dif_{s}": s for s in cols_sel})
    
    # 3. Función para dar color a los valores
    def color_diferencias(val):
        if isinstance(val, (int, float)) and not pd.isna(val):
            if val > 0:
                return 'color: #4ecdc4; font-weight: 700;' # Cyan
            elif val < 0:
                return 'color: #ef4444; font-weight: 700;' # Rojo
        return ''

    # 4. Función para agregar el signo '+' a los positivos y manejar nulos
    def formato_texto(val):
        if pd.isna(val):
            return "—"
        if val > 0:
            return f"+{val:.2f}"
        return f"{val:.2f}"

    # 5. Aplicar estilos y formatos usando Pandas Styler
    styled_df = df_display.style.map(
        color_diferencias,
        subset=cols_sel
    ).format(
        {s: formato_texto for s in cols_sel}
    )

    # 6. Mostrar la tabla nativa (¡Esto habilita el ordenamiento al hacer clic en las columnas!)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


    # ── Análisis rápido ────────────────────────────────────────────
    st.markdown("### 💡 Análisis Rápido")
    dif_cols = [f"_dif_{s}" for s in cols_sel if f"_dif_{s}" in df_dif.columns]
    df_dif["_suma_pos"] = df_dif[dif_cols].apply(lambda x: x[x>0].sum(), axis=1)
    df_dif["_suma_neg"] = df_dif[dif_cols].apply(lambda x: x[x<0].sum(), axis=1)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("**🌟 Top 3 Más Destacados**")
        for _, r in df_dif.nlargest(3,"_suma_pos")[["jugador","_suma_pos"]].iterrows():
            st.markdown(
                f'<div class="fm-success">🌟 <strong>{r["jugador"]}</strong>: +{r["_suma_pos"]:.2f}</div>',
                unsafe_allow_html=True)
    with a2:
        st.markdown("**📉 Top 3 Por Debajo**")
        for _, r in df_dif.nsmallest(3,"_suma_neg")[["jugador","_suma_neg"]].iterrows():
            st.markdown(
                f'<div class="fm-danger">📉 <strong>{r["jugador"]}</strong>: {r["_suma_neg"]:.2f}</div>',
                unsafe_allow_html=True)

    # ── Descarga ───────────────────────────────────────────────────
    st.markdown("---")
    df_exp = df_dif[base_cols + [f"_dif_{s}" for s in cols_sel if f"_dif_{s}" in df_dif.columns]].copy()
    df_exp = df_exp.rename(columns={f"_dif_{s}": s for s in cols_sel})
    csv = df_exp.to_csv(index=False, encoding="utf-8-sig", sep=";")
    st.download_button("📥 Descargar Análisis (CSV)", data=csv,
        file_name="fm_diferencias.csv", mime="text/csv", use_container_width=True)

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#7a9eab;padding:16px;font-size:0.85rem;">'
    '<strong style="color:#4ecdc4;">FM DataLab v3</strong> · Diferencias</div>',
    unsafe_allow_html=True)
"""
FM DataLab v3 - Comparación
============================
Explora y compara jugadores con spider graphs.
Filtro de posición avanzado (mismo parser que Similitud).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

from utils_common import (
    inject_css, sidebar_carga_datos,
    obtener_posiciones_unicas, filtrar_por_posicion,
)

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="FM DataLab v3 - Comparación",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ═══════════════════════════════════════════════════════════════
# CATEGORÍAS DE SPIDER
# ═══════════════════════════════════════════════════════════════

CATEGORIAS = {
    "Ataque":         ["goles por 90 minutos","xg/90","tir/90","tirp/90","% conv",
                       "oc c/90","reg/90","asis/90","asie/90"],
    "Defensa":        ["rob/90","ent p","pcg %","desp/90","rechazos/90",
                       "cab g/90","cab p/90","pres c/90","pres i/90"],
    "Centrocampista": ["kp/90","pases prog/90","% de pases","oc c/90","dist/90",
                       "pos gan/90","pos perd/90","cen c/90","cen i/90"],
}

COLORES = [
    {"line":"#4ecdc4","fill":"rgba(78,205,196,0.15)"},
    {"line":"#ef4444","fill":"rgba(239,68,68,0.15)"},
    {"line":"#8b5cf6","fill":"rgba(139,92,246,0.15)"},
    {"line":"#fb923c","fill":"rgba(251,146,60,0.15)"},
]

# ═══════════════════════════════════════════════════════════════
# SPIDER GRAPH
# ═══════════════════════════════════════════════════════════════

def crear_spider(jugadores_data, stats, df_pool):
    N = len(stats)
    if N < 3: return None
    promedios = {s: float(df_pool[s].dropna().mean()) for s in stats if s in df_pool.columns}

    def pct(val, stat):
        col = df_pool[stat].dropna() if stat in df_pool.columns else pd.Series(dtype=float)
        if len(col) == 0 or col.max() == col.min(): return 0.5
        return float(np.clip((col < float(val or 0)).sum() / len(col), 0.05, 0.95))

    angles = [math.pi/2 - 2*math.pi*i/N for i in range(N)]
    fig = go.Figure()

    for nivel in [0.2,0.4,0.6,0.8,1.0]:
        xs = [nivel*math.cos(a) for a in angles] + [nivel*math.cos(angles[0])]
        ys = [nivel*math.sin(a) for a in angles] + [nivel*math.sin(angles[0])]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
            line=dict(color="rgba(78,205,196,0.15)", width=1),
            showlegend=False, hoverinfo="skip"))
    for a in angles:
        fig.add_trace(go.Scatter(x=[0,math.cos(a)], y=[0,math.sin(a)], mode="lines",
            line=dict(color="rgba(78,205,196,0.20)", width=1),
            showlegend=False, hoverinfo="skip"))
    for stat, angle in zip(stats, angles):
        lx, ly = 1.22*math.cos(angle), 1.22*math.sin(angle)
        xa = "left" if lx>0.15 else ("right" if lx<-0.15 else "center")
        fig.add_annotation(x=lx, y=ly, text=stat, showarrow=False,
            font=dict(color="#7a9eab", size=10), xanchor=xa, yanchor="middle")

    vp = [pct(promedios.get(s,0), s) for s in stats]
    fig.add_trace(go.Scatter(
        x=[v*math.cos(a) for v,a in zip(vp,angles)] + [vp[0]*math.cos(angles[0])],
        y=[v*math.sin(a) for v,a in zip(vp,angles)] + [vp[0]*math.sin(angles[0])],
        mode="lines+markers", name="Promedio lista",
        line=dict(color="#f5c518", width=2, dash="dot"),
        marker=dict(color="#f5c518", size=7),
        fill="toself", fillcolor="rgba(245,197,24,0.08)",
        text=[f"<b>{s}</b><br>Promedio: {promedios.get(s,0):.2f}" for s in stats]+[""],
        hovertemplate="%{text}<extra></extra>"))

    for idx, (nombre, row) in enumerate(jugadores_data):
        c = COLORES[idx % len(COLORES)]
        vals = [pct(float(row.get(s,0) or 0), s) for s in stats]
        fig.add_trace(go.Scatter(
            x=[v*math.cos(a) for v,a in zip(vals,angles)] + [vals[0]*math.cos(angles[0])],
            y=[v*math.sin(a) for v,a in zip(vals,angles)] + [vals[0]*math.sin(angles[0])],
            mode="lines+markers", name=nombre,
            line=dict(color=c["line"], width=2.5), marker=dict(color=c["line"], size=8),
            fill="toself", fillcolor=c["fill"],
            text=[f"<b>{s}</b><br>{nombre}: {float(row.get(s,0) or 0):.2f}<br>Prom: {promedios.get(s,0):.2f}"
                  for s in stats]+[""],
            hovertemplate="%{text}<extra></extra>"))

    fig.update_layout(
        paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
        font=dict(color="#e8f4f4", size=11), height=580,
        margin=dict(l=80,r=80,t=40,b=40), showlegend=True,
        legend=dict(bgcolor="#1a2332", bordercolor="rgba(78,205,196,0.3)",
                    borderwidth=1, font=dict(color="#e8f4f4", size=11), x=0.01, y=0.01),
        xaxis=dict(visible=False, range=[-1.5,1.5]),
        yaxis=dict(visible=False, range=[-1.5,1.5], scaleanchor="x", scaleratio=1))
    return fig

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## ⚖️ Comparación")
    if st.button("← Volver al Home", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("---")
    df = sidebar_carga_datos(pagina="comparacion")
    if df is not None:
        st.markdown("""
        <div class="fm-info" style="font-size:0.83rem;">
        📊 Explorá el dataset<br>
        🔍 Filtrá por posición y minutos<br>
        👥 Compará hasta 4 jugadores<br>
        📈 Spider graphs interactivos
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# GUARD
# ═══════════════════════════════════════════════════════════════

st.markdown("# ⚖️ Comparación de Jugadores")
st.markdown("### *Explorá y compará jugadores con spider graphs*")
st.markdown("---")

if df is None:
    st.markdown(
        '<div class="fm-warning">⚠️ Cargá tu archivo CSV desde el panel lateral para comenzar.</div>',
        unsafe_allow_html=True)
    st.stop()

if "jugadores_comparacion" not in st.session_state:
    st.session_state["jugadores_comparacion"] = []
if "categoria_activa" not in st.session_state:
    st.session_state["categoria_activa"] = "Defensa"

# ═══════════════════════════════════════════════════════════════
# FILTROS — usa filtro avanzado (FIX 9)
# ═══════════════════════════════════════════════════════════════

st.markdown("## ⚙️ Filtros")
c1, c2, c3, c4 = st.columns(4)

with c1:
    # FIX 9: posiciones con parser avanzado igual que Similitud
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
    limite = st.selectbox("Mostrar", [10, 25, 50, 100, 200, "Todos"], index=2)

# Aplicar filtros
df_f = df.copy()
if posicion_filtro != "Todas":
    df_f = filtrar_por_posicion(df_f, posicion_filtro)   # ← parser avanzado
if "minutos" in df_f.columns:
    df_f = df_f[(df_f["minutos"] >= min_min) & (df_f["minutos"] <= min_max)]
if limite != "Todos":
    df_f = df_f.head(int(limite))

st.markdown(
    f'<div class="fm-info">👥 {len(df_f):,} jugadores mostrados</div>',
    unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# TABLA DEL DATASET (AHORA ARRIBA)
# ═══════════════════════════════════════════════════════════════

st.markdown("## 📋 Dataset")
st.markdown("*Elegí un jugador de la lista para agregarlo al gráfico comparativo de abajo*")

# Sacamos el selector afuera del IF para que sus datos puedan ser usados por el gráfico después
xcl = {"jugador","posición","pos","nombre","equipo","club","edad","minutos"}
stats_d = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in xcl]

cols_sel = st.multiselect("Estadísticas a mostrar en la tabla (y en el gráfico 'Personalizado')", options=stats_d,
    default=stats_d[:8] if len(stats_d)>=8 else stats_d)

if len(df_f) == 0:
    st.markdown(
        '<div class="fm-warning">⚠️ No hay jugadores que cumplan los filtros.</div>',
        unsafe_allow_html=True)
else:
    base = [c for c in ["jugador","posición","minutos"] if c in df_f.columns]
    cols_show = [c for c in base+cols_sel if c in df_f.columns]
    df_disp = df_f[cols_show].copy()
    for c in cols_sel:
        if c in df_disp.columns:
            df_disp[c] = df_disp[c].round(2)

    # 1. Mostrar el dataframe de forma estática
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    # 2. Interfaz alternativa para seleccionar jugador
    st.markdown("### ➕ Agregar jugador a la comparación")
    c_sel, c_btn = st.columns([3, 1])

    with c_sel:
        # Menú desplegable con los jugadores filtrados
        sel = st.selectbox(
            "Seleccioná un jugador de la tabla:",
            options=df_disp["jugador"].tolist()
        )

    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True) # Espaciador para alinear el botón
        if st.button("Agregar al gráfico ⬇️", use_container_width=True, type="primary"):
            if sel:
                if sel not in st.session_state["jugadores_comparacion"]:
                    if len(st.session_state["jugadores_comparacion"]) < 4:
                        st.session_state["jugadores_comparacion"].append(sel)
                        st.rerun()
                    else:
                        st.markdown(
                            '<div class="fm-warning">⚠️ Máximo 4 jugadores. Eliminá uno abajo para agregar otro.</div>',
                            unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="fm-info">ℹ️ <strong>{sel}</strong> ya está en la comparación.</div>',
                        unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# PANEL DE COMPARACIÓN (AHORA ABAJO)
# ═══════════════════════════════════════════════════════════════

if st.session_state["jugadores_comparacion"]:
    st.markdown("## 📊 Comparación Visual")
    
    # Botones para eliminar jugadores seleccionados
    rm_cols = st.columns(len(st.session_state["jugadores_comparacion"]) + 1)
    for idx, nombre in enumerate(st.session_state["jugadores_comparacion"]):
        with rm_cols[idx]:
            if st.button(f"❌ Quitar {nombre}", key=f"rm_{idx}"):
                st.session_state["jugadores_comparacion"].remove(nombre)
                st.rerun()
    with rm_cols[-1]:
        if st.button("🗑️ Limpiar todo"):
            st.session_state["jugadores_comparacion"] = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Selector de categoría para el Spider Graph (AHORA CON 4 COLUMNAS)
    bc1, bc2, bc3, bc4 = st.columns(4)
    for col_b, cat, em in zip([bc1, bc2, bc3, bc4],
                               ["Ataque", "Defensa", "Centrocampista", "Personalizada"],
                               ["⚔️", "🛡️", "⚽", "🛠️"]):
        with col_b:
            active = st.session_state["categoria_activa"] == cat
            if st.button(f"{em} {cat}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state["categoria_activa"] = cat
                st.rerun()

    # LÓGICA PARA ELEGIR LAS ESTADÍSTICAS A GRAFICAR
    if st.session_state["categoria_activa"] == "Personalizada":
        stats_cat = [s for s in cols_sel if s in df.columns]
    else:
        stats_cat = [s for s in CATEGORIAS.get(st.session_state["categoria_activa"], [])
                     if s in df.columns]
                 
    if len(stats_cat) < 3:
        st.markdown(
            '<div class="fm-warning">⚠️ Necesitás al menos 3 estadísticas para armar el gráfico radial. Agregá más en el selector de arriba.</div>',
            unsafe_allow_html=True)
    else:
        jdata = [(n, df[df["jugador"]==n].iloc[0])
                 for n in st.session_state["jugadores_comparacion"]
                 if len(df[df["jugador"]==n]) > 0]
        if jdata:
            pool_ref = df_f if len(df_f) > 10 else df
            fig = crear_spider(jdata, stats_cat, pool_ref)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Valores Detallados del Gráfico")
        tdata = []
        for nombre in st.session_state["jugadores_comparacion"]:
            rw = df[df["jugador"]==nombre]
            if len(rw) > 0:
                j = rw.iloc[0]
                fila = {"Jugador": nombre}
                if "posición" in j: fila["Posición"] = j["posición"]
                if "minutos"  in j: fila["Minutos"]  = int(j["minutos"]) if not pd.isna(j["minutos"]) else 0
                for s in stats_cat:
                    v = j.get(s,0)
                    fila[s] = round(float(v),2) if not pd.isna(v) else 0
                tdata.append(fila)
        if tdata:
            st.dataframe(pd.DataFrame(tdata), use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#7a9eab;padding:16px;font-size:0.85rem;">'
    '<strong style="color:#4ecdc4;">FM DataLab v3</strong> · Comparación</div>',
    unsafe_allow_html=True)
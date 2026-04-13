"""
FM DataLab v3 - Comparación
============================
Explora y compara jugadores del dataset con spider graphs
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

st.set_page_config(
    page_title="FM DataLab v3 - Comparación",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

# =========================
# CATEGORÍAS
# =========================

CATEGORIAS = {
    "Ataque": ["goles por 90 minutos", "xg/90", "tir/90", "tirp/90", "% conv", "oc c/90", "reg/90", "asis/90", "asie/90"],
    "Defensa": ["rob/90", "ent p", "pcg %", "desp/90", "rechazos/90", "cab g/90", "cab p/90", "pres c/90", "pres i/90"],
    "Centrocampista": ["kp/90", "pases prog/90", "% de pases", "oc c/90", "dist/90", "pos gan/90", "pos perd/90", "cen c/90", "cen i/90"],
}

# Colores con rgba ya definidos correctamente — sin conversión dinámica
COLORES = [
    {"line": "#4ecdc4", "fill": "rgba(78,205,196,0.15)"},
    {"line": "#ef4444", "fill": "rgba(239,68,68,0.15)"},
    {"line": "#8b5cf6", "fill": "rgba(139,92,246,0.15)"},
    {"line": "#fb923c", "fill": "rgba(251,146,60,0.15)"},
]

# =========================
# SPIDER GRAPH
# =========================

def crear_spider(jugadores_data: list, stats: list, df_pool: pd.DataFrame) -> go.Figure:
    N = len(stats)
    if N < 3:
        return None

    promedios = {}
    for s in stats:
        promedios[s] = float(df_pool[s].dropna().mean()) if s in df_pool.columns else 0.0

    def pct(val: float, stat: str) -> float:
        col = df_pool[stat].dropna() if stat in df_pool.columns else pd.Series(dtype=float)
        if len(col) == 0 or col.max() == col.min():
            return 0.5
        return float(np.clip((col < val).sum() / len(col), 0.05, 0.95))

    angles = [math.pi / 2 - 2 * math.pi * i / N for i in range(N)]

    fig = go.Figure()

    # Grilla
    for nivel in [0.2, 0.4, 0.6, 0.8, 1.0]:
        xs = [nivel * math.cos(a) for a in angles] + [nivel * math.cos(angles[0])]
        ys = [nivel * math.sin(a) for a in angles] + [nivel * math.sin(angles[0])]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines',
            line=dict(color="rgba(78,205,196,0.15)", width=1),
            showlegend=False, hoverinfo='skip'))

    # Ejes
    for a in angles:
        fig.add_trace(go.Scatter(x=[0, math.cos(a)], y=[0, math.sin(a)], mode='lines',
            line=dict(color="rgba(78,205,196,0.20)", width=1),
            showlegend=False, hoverinfo='skip'))

    # Labels
    for stat, angle in zip(stats, angles):
        lx, ly = 1.22 * math.cos(angle), 1.22 * math.sin(angle)
        xanchor = 'left' if lx > 0.15 else ('right' if lx < -0.15 else 'center')
        fig.add_annotation(x=lx, y=ly, text=stat, showarrow=False,
            font=dict(color="#7a9eab", size=10, family="DM Sans, sans-serif"),
            xanchor=xanchor, yanchor='middle')

    # Promedio — amarillo punteado
    vp = [pct(promedios.get(s, 0.0), s) for s in stats]
    xp = [v * math.cos(a) for v, a in zip(vp, angles)] + [vp[0] * math.cos(angles[0])]
    yp = [v * math.sin(a) for v, a in zip(vp, angles)] + [vp[0] * math.sin(angles[0])]
    hp = [f"<b>{s}</b><br>Promedio: {promedios.get(s,0):.2f}" for s in stats] + \
         [f"<b>{stats[0]}</b><br>Promedio: {promedios.get(stats[0],0):.2f}"]
    fig.add_trace(go.Scatter(x=xp, y=yp, mode='lines+markers', name='Promedio lista',
        line=dict(color="#f5c518", width=2, dash='dot'),
        marker=dict(color="#f5c518", size=7),
        fill='toself', fillcolor="rgba(245,197,24,0.08)",
        text=hp, hovertemplate='%{text}<extra></extra>'))

    # Jugadores
    for idx, (nombre, row) in enumerate(jugadores_data):
        c = COLORES[idx % len(COLORES)]
        vals = [pct(float(row.get(s, 0) or 0), s) for s in stats]
        xs = [v * math.cos(a) for v, a in zip(vals, angles)] + [vals[0] * math.cos(angles[0])]
        ys = [v * math.sin(a) for v, a in zip(vals, angles)] + [vals[0] * math.sin(angles[0])]
        vals_r = [row.get(s, 0) for s in stats]
        hj = [f"<b>{s}</b><br>{nombre}: {float(v or 0):.2f}<br>Promedio: {promedios.get(s,0):.2f}"
              for s, v in zip(stats, vals_r)] + \
             [f"<b>{stats[0]}</b><br>{nombre}: {float(vals_r[0] or 0):.2f}"]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines+markers', name=nombre,
            line=dict(color=c["line"], width=2.5),
            marker=dict(color=c["line"], size=8),
            fill='toself',
            fillcolor=c["fill"],   # ← string rgba explícito, sin conversión
            text=hj, hovertemplate='%{text}<extra></extra>'))

    fig.update_layout(
        paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
        font=dict(color="#e8f4f4", family="DM Sans, sans-serif", size=11),
        height=580, margin=dict(l=80, r=80, t=40, b=40),
        showlegend=True,
        legend=dict(bgcolor="#1a2332", bordercolor="rgba(78,205,196,0.3)",
                    borderwidth=1, font=dict(color="#e8f4f4", size=11), x=0.01, y=0.01),
        xaxis=dict(visible=False, range=[-1.5, 1.5]),
        yaxis=dict(visible=False, range=[-1.5, 1.5], scaleanchor='x', scaleratio=1),
    )
    return fig

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.markdown("## ⚖️ Comparación")
    if st.button("← Volver al Home", use_container_width=True):
        st.switch_page("fm_datalab_home.py")
    st.markdown("---")
    st.info("""
    **Comparación** te permite:\n
    - 📊 Explorar el dataset\n- 🔍 Filtrar por posición y minutos\n
    - 📈 Click en fila para comparar\n- 👥 Hasta 4 jugadores a la vez
    """)

# =========================
# VERIFICAR DATOS
# =========================

if 'df' not in st.session_state or st.session_state['df'] is None:
    st.warning("⚠️ No hay datos cargados")
    if st.button("Ir al Home", type="primary"):
        st.switch_page("fm_datalab_home.py")
    st.stop()

df = st.session_state['df']
if 'jugadores_comparacion' not in st.session_state:
    st.session_state['jugadores_comparacion'] = []
if 'categoria_activa' not in st.session_state:
    st.session_state['categoria_activa'] = "Defensa"

# =========================
# HEADER + FILTROS
# =========================

st.markdown("# ⚖️ Comparación de Jugadores")
st.markdown("### *Explorá y compará jugadores con spider graphs*")
st.markdown("---")
st.markdown("## ⚙️ Filtros")

c1, c2, c3, c4 = st.columns(4)

with c1:
    pos_opts = []
    if 'posición' in df.columns:
        for ps in df['posición'].dropna().unique():
            for g in str(ps).split(','):
                g = g.strip()
                if '(' in g:
                    pos_opts.append(g.split('(')[0].strip())
                else:
                    pos_opts += [p.strip() for p in g.split('/')]
        pos_opts = sorted(set(pos_opts))
    posicion_filtro = st.selectbox("Posición", ["Todas"] + pos_opts)

with c2:
    min_min = st.number_input("Minutos mín.", min_value=0, value=0, step=100)
with c3:
    min_max = st.number_input("Minutos máx.", min_value=0,
        value=int(df['minutos'].max()) if 'minutos' in df.columns else 10000, step=100)
with c4:
    limite = st.selectbox("Mostrar", [10, 25, 50, 100, 200, "Todos"], index=2)

df_f = df.copy()
if posicion_filtro != "Todas" and 'posición' in df_f.columns:
    df_f = df_f[df_f['posición'].apply(
        lambda x: posicion_filtro.upper() in str(x).upper() if not pd.isna(x) else False)]
if 'minutos' in df_f.columns:
    df_f = df_f[(df_f['minutos'] >= min_min) & (df_f['minutos'] <= min_max)]
if limite != "Todos":
    df_f = df_f.head(int(limite))

st.markdown("---")

# =========================
# PANEL DE COMPARACIÓN
# =========================

if st.session_state['jugadores_comparacion']:
    st.markdown("## 👥 Jugadores Seleccionados")
    rm_cols = st.columns(len(st.session_state['jugadores_comparacion']) + 1)
    for idx, nombre in enumerate(st.session_state['jugadores_comparacion']):
        with rm_cols[idx]:
            if st.button(f"❌ {nombre}", key=f"rm_{idx}"):
                st.session_state['jugadores_comparacion'].remove(nombre)
                st.rerun()
    with rm_cols[-1]:
        if st.button("🗑️ Limpiar todo"):
            st.session_state['jugadores_comparacion'] = []
            st.rerun()

    st.markdown("---")
    st.markdown("## 📊 Comparación Visual")

    bc1, bc2, bc3 = st.columns(3)
    for col_b, cat, em in zip([bc1, bc2, bc3], ["Ataque", "Defensa", "Centrocampista"], ["⚔️", "🛡️", "⚽"]):
        with col_b:
            active = st.session_state['categoria_activa'] == cat
            if st.button(f"{em} {cat}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state['categoria_activa'] = cat
                st.rerun()

    stats_cat = [s for s in CATEGORIAS[st.session_state['categoria_activa']] if s in df.columns]

    if len(stats_cat) < 3:
        st.warning("⚠️ No hay suficientes estadísticas disponibles para esta categoría.")
    else:
        jdata = [(n, df[df['jugador'] == n].iloc[0]) for n in st.session_state['jugadores_comparacion']
                 if len(df[df['jugador'] == n]) > 0]
        if jdata:
            pool_ref = df_f if len(df_f) > 10 else df
            fig = crear_spider(jdata, stats_cat, pool_ref)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Valores Detallados")
        tdata = []
        for nombre in st.session_state['jugadores_comparacion']:
            rw = df[df['jugador'] == nombre]
            if len(rw) > 0:
                j = rw.iloc[0]
                fila = {'Jugador': nombre}
                if 'posición' in j: fila['Posición'] = j['posición']
                if 'minutos' in j: fila['Minutos'] = int(j['minutos']) if not pd.isna(j['minutos']) else 0
                for s in stats_cat:
                    v = j.get(s, 0)
                    fila[s] = round(float(v), 2) if not pd.isna(v) else 0
                tdata.append(fila)
        if tdata:
            st.dataframe(pd.DataFrame(tdata), use_container_width=True, hide_index=True)

    st.markdown("---")

# =========================
# TABLA DEL DATASET
# =========================

st.markdown("## 📋 Dataset Completo")
st.markdown("*Click en una fila para agregar el jugador a la comparación*")

if len(df_f) == 0:
    st.warning("⚠️ No hay jugadores que cumplan con los filtros")
else:
    xcl = ['jugador', 'posición', 'pos', 'nombre', 'equipo', 'club', 'edad', 'minutos']
    stats_d = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in xcl]
    cols_sel = st.multiselect("Estadísticas a mostrar", options=stats_d,
        default=stats_d[:8] if len(stats_d) >= 8 else stats_d)

    base = [c for c in ['jugador', 'posición', 'minutos'] if c in df_f.columns]
    cols_show = [c for c in base + cols_sel if c in df_f.columns]
    df_disp = df_f[cols_show].copy()
    for c in cols_sel:
        if c in df_disp.columns: df_disp[c] = df_disp[c].round(2)

    event = st.dataframe(df_disp, use_container_width=True, hide_index=True,
        on_select="rerun", selection_mode="single-row")

    if event.selection and event.selection.rows:
        sel = df_disp.iloc[event.selection.rows[0]]['jugador']
        if sel not in st.session_state['jugadores_comparacion']:
            if len(st.session_state['jugadores_comparacion']) < 4:
                st.session_state['jugadores_comparacion'].append(sel)
                st.rerun()
            else:
                st.warning("⚠️ Máximo 4 jugadores. Eliminá uno para agregar otro.")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#7a9eab;padding:16px;font-size:0.85rem;"><strong style="color:#4ecdc4;">FM DataLab v3</strong> · Comparación</div>', unsafe_allow_html=True)

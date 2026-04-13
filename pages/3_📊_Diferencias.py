"""
FM DataLab v3 - Diferencias
============================
Analiza diferencias vs el promedio del pool
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FM DataLab v3 - Diferencias",
    page_icon="📊",
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
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.markdown("## 📊 Diferencias")
    if st.button("← Volver al Home", use_container_width=True):
        st.switch_page("fm_datalab_home.py")
    st.markdown("---")
    st.info("""
    **Diferencias** te permite:\n
    - 📊 Ver desviaciones del promedio\n
    - 🎯 Identificar outliers\n
    - 📈 Analizar fortalezas/debilidades
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

# =========================
# HEADER
# =========================

st.markdown("# 📊 Diferencia vs Promedio")
st.markdown("### *Analizá qué tan lejos está cada jugador del promedio del pool*")
st.markdown("---")

# =========================
# FILTROS
# =========================

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
    limite = st.selectbox("Mostrar", [10, 25, 50, 100, "Todos"], index=2)

df_f = df.copy()
if posicion_filtro != "Todas" and 'posición' in df_f.columns:
    df_f = df_f[df_f['posición'].apply(
        lambda x: posicion_filtro.upper() in str(x).upper() if not pd.isna(x) else False)]
if 'minutos' in df_f.columns:
    df_f = df_f[(df_f['minutos'] >= min_min) & (df_f['minutos'] <= min_max)]

st.markdown("---")

# =========================
# SELECTOR DE STATS
# =========================

st.markdown("## 📊 Estadísticas a Analizar")

xcl = ['jugador', 'posición', 'pos', 'nombre', 'equipo', 'club', 'edad', 'minutos']
stats_d = [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in xcl]

cols_sel = st.multiselect(
    "Seleccioná las estadísticas", options=stats_d,
    default=stats_d[:8] if len(stats_d) >= 8 else stats_d,
    help="Verás la diferencia de cada jugador vs el promedio del pool"
)

if not cols_sel:
    st.warning("⚠️ Seleccioná al menos una estadística")
    st.stop()

st.markdown("---")

# =========================
# PROMEDIOS DEL POOL
# =========================

st.markdown("## 📈 Análisis de Diferencias")
st.markdown("### 📊 Promedios del Pool")

promedios = {s: df_f[s].mean() for s in cols_sel if s in df_f.columns}

cols_p = 4
for i in range(0, len(cols_sel), cols_p):
    row_cols = st.columns(cols_p)
    for j, rc in enumerate(row_cols):
        if i + j < len(cols_sel):
            s = cols_sel[i + j]
            if s in promedios:
                with rc:
                    st.metric(s, f"{promedios[s]:.2f}")

st.markdown("---")

# =========================
# TABLA CON COLORES HTML
# =========================

df_dif = df_f.copy()
for s in cols_sel:
    if s in df_dif.columns:
        df_dif[f'_dif_{s}'] = df_dif[s] - promedios.get(s, 0)

if limite != "Todos":
    df_dif = df_dif.head(int(limite))

st.markdown("### 📋 Tabla de Diferencias")
st.markdown(
    '<span style="color:#4ecdc4;font-weight:700;font-family:\'DM Mono\',monospace;">■</span> '
    '<span style="color:#e8f4f4;font-size:0.9rem;">Cyan = sobre el promedio &nbsp;&nbsp;</span>'
    '<span style="color:#ef4444;font-weight:700;">■</span> '
    '<span style="color:#e8f4f4;font-size:0.9rem;">Rojo = bajo el promedio</span>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

if len(df_dif) == 0:
    st.warning("⚠️ No hay jugadores que cumplan con los filtros")
else:
    base_cols = [c for c in ['jugador', 'posición', 'minutos'] if c in df_dif.columns]

    # Encabezado
    th_style = "background:#1e2d3d;color:#4ecdc4;padding:10px 14px;text-align:center;border-bottom:2px solid rgba(78,205,196,0.4);font-size:12px;white-space:nowrap;font-family:'DM Sans',sans-serif;font-weight:600;letter-spacing:0.5px;"
    thead = "".join(f'<th style="{th_style}">{c}</th>' for c in base_cols + cols_sel)

    td_base = "padding:9px 14px;text-align:center;border-bottom:1px solid rgba(78,205,196,0.08);font-size:13px;font-family:'DM Sans',sans-serif;"

    rows_html = []
    for i, (_, row) in enumerate(df_dif.iterrows()):
        bg = "#1a2332" if i % 2 == 0 else "#1c2838"
        cells = []

        for col in base_cols:
            val = row.get(col, "")
            if col == 'minutos' and not pd.isna(val):
                val = int(val)
            cells.append(f'<td style="{td_base}background:{bg};color:#e8f4f4;">{val}</td>')

        for s in cols_sel:
            dv = row.get(f'_dif_{s}', None)
            if dv is None or (isinstance(dv, float) and pd.isna(dv)):
                cells.append(f'<td style="{td_base}background:{bg};color:#7a9eab;">—</td>')
            elif dv > 0:
                cells.append(f'<td style="{td_base}background:{bg};color:#4ecdc4;font-weight:700;">+{dv:.2f}</td>')
            else:
                cells.append(f'<td style="{td_base}background:{bg};color:#ef4444;font-weight:700;">{dv:.2f}</td>')

        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    tabla_html = f"""
    <div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(78,205,196,0.2);margin-bottom:24px;">
    <table style="width:100%;border-collapse:collapse;background:#1a2332;">
        <thead><tr>{thead}</tr></thead>
        <tbody>{"".join(rows_html)}</tbody>
    </table>
    </div>
    """
    st.markdown(tabla_html, unsafe_allow_html=True)

    # =========================
    # ANÁLISIS RÁPIDO
    # =========================

    st.markdown("### 💡 Análisis Rápido")
    dif_cols = [f'_dif_{s}' for s in cols_sel if f'_dif_{s}' in df_dif.columns]
    df_dif['_suma_pos'] = df_dif[dif_cols].apply(lambda x: x[x > 0].sum(), axis=1)
    df_dif['_suma_neg'] = df_dif[dif_cols].apply(lambda x: x[x < 0].sum(), axis=1)

    acol1, acol2 = st.columns(2)
    with acol1:
        st.markdown("**🌟 Top 3 Más Destacados**")
        for _, r in df_dif.nlargest(3, '_suma_pos')[['jugador', '_suma_pos']].iterrows():
            st.success(f"🌟 {r['jugador']}: +{r['_suma_pos']:.2f}")

    with acol2:
        st.markdown("**📉 Top 3 Por Debajo**")
        for _, r in df_dif.nsmallest(3, '_suma_neg')[['jugador', '_suma_neg']].iterrows():
            st.error(f"📉 {r['jugador']}: {r['_suma_neg']:.2f}")

    # Descarga
    st.markdown("---")
    df_exp = df_dif[base_cols + [f'_dif_{s}' for s in cols_sel if f'_dif_{s}' in df_dif.columns]].copy()
    df_exp = df_exp.rename(columns={f'_dif_{s}': s for s in cols_sel})
    csv = df_exp.to_csv(index=False, encoding='utf-8-sig', sep=';')
    st.download_button("📥 Descargar Análisis (CSV)", data=csv,
        file_name="fm_diferencias.csv", mime="text/csv", use_container_width=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#7a9eab;padding:16px;font-size:0.85rem;"><strong style="color:#4ecdc4;">FM DataLab v3</strong> · Diferencias</div>', unsafe_allow_html=True)

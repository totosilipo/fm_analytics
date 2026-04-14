"""
FM DataLab v3 - Similitud
==========================
View: solo renderiza UI y delega toda la lógica al ViewModel.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math as _math

from utils_common import inject_css, sidebar_carga_datos
from domain.perfiles import PERFILES, PESOS_MAP, render_perfil_preview
from domain.similitud_vm import SimilitudViewModel
from data.stats_labels import label

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="FM DataLab v3 - Similitud",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()
vm = SimilitudViewModel()

# ═══════════════════════════════════════════════════════════════
# VISUALIZACIONES (render puro, sin lógica de negocio)
# ═══════════════════════════════════════════════════════════════

def render_barra_fm(jugadores_data: list, stats_perfil: list, df_ref: pd.DataFrame) -> str:
    COLORES = [
        {"barra": "#4ecdc4", "texto": "#4ecdc4"},
        {"barra": "#ef4444", "texto": "#ef4444"},
        {"barra": "#a78bfa", "texto": "#a78bfa"},
        {"barra": "#fb923c", "texto": "#fb923c"},
    ]
    maximos = {}
    for s in stats_perfil:
        if s in df_ref.columns:
            col = df_ref[s].dropna()
            mx = float(np.percentile(col, 95)) if len(col) > 0 else 1.0
            maximos[s] = mx if mx != 0 else 1.0

    th = ("background:#1e2d3d;color:#4ecdc4;padding:10px 16px;"
          "text-align:center;border-bottom:2px solid rgba(78,205,196,0.4);"
          "font-size:12px;white-space:nowrap;font-family:'DM Sans',sans-serif;"
          "font-weight:600;letter-spacing:0.5px;min-width:170px;")

    header = "".join(
        f'<th style="{th}border-bottom-color:{COLORES[i%len(COLORES)]["barra"]};">{n}</th>'
        for i, (n, _) in enumerate(jugadores_data)
    )

    td_base = ("padding:8px 14px;border-bottom:1px solid rgba(78,205,196,0.07);"
               "vertical-align:middle;")
    rows = ""
    for stat in stats_perfil:
        if stat not in df_ref.columns:
            continue
        row = (f'<td style="{td_base}color:#7a9eab;font-size:11px;'
               f'font-family:\'JetBrains Mono\',monospace;white-space:nowrap;'
               f'min-width:130px;">{label(stat)}</td>')
        for i, (_, jugador_row) in enumerate(jugadores_data):
            c   = COLORES[i % len(COLORES)]
            val = jugador_row.get(stat, None)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                v_num, v_str = 0.0, "—"
            else:
                v_num = float(val); v_str = f"{v_num:.2f}"
            pct = min(100, max(0, v_num / maximos.get(stat, 1.0) * 100))
            row += f"""<td style="{td_base}min-width:170px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;background:rgba(255,255,255,0.05);border-radius:3px;height:13px;overflow:hidden;">
                        <div style="width:{pct:.1f}%;height:100%;background:{c['barra']};border-radius:3px;"></div>
                    </div>
                    <span style="color:{c['texto']};font-family:'JetBrains Mono',monospace;
                                 font-size:11px;font-weight:700;min-width:36px;text-align:right;">{v_str}</span>
                </div>
            </td>"""
        rows += f"<tr>{row}</tr>"

    return f"""
    <div style="overflow-x:auto;border-radius:10px;border:1px solid rgba(78,205,196,0.2);
                margin:16px 0;background:#1a2332;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr>
            <th style="background:#1e2d3d;color:#4ecdc4;padding:10px 14px;text-align:left;
                       font-size:11px;font-family:'DM Sans',sans-serif;font-weight:600;
                       letter-spacing:1px;text-transform:uppercase;
                       border-bottom:2px solid rgba(78,205,196,0.3);">ESTADÍSTICA</th>
            {header}
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def crear_spider_perfil(jugadores_data, stats_perfil, df_ref):
    stats_ok = [s for s in stats_perfil if s in df_ref.columns]
    N = len(stats_ok)
    if N < 3:
        return None

    def pct(val, stat):
        col = df_ref[stat].dropna()
        if len(col) == 0 or col.max() == col.min(): return 0.5
        return float(np.clip((col < float(val or 0)).sum() / len(col), 0.05, 0.95))

    promedios = {s: float(df_ref[s].dropna().mean()) for s in stats_ok}
    angles    = [_math.pi/2 - 2*_math.pi*i/N for i in range(N)]

    fig = go.Figure()
    for nivel in [0.2, 0.4, 0.6, 0.8, 1.0]:
        xs = [nivel*_math.cos(a) for a in angles] + [nivel*_math.cos(angles[0])]
        ys = [nivel*_math.sin(a) for a in angles] + [nivel*_math.sin(angles[0])]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
            line=dict(color="rgba(78,205,196,0.15)", width=1),
            showlegend=False, hoverinfo="skip"))
    for a in angles:
        fig.add_trace(go.Scatter(x=[0, _math.cos(a)], y=[0, _math.sin(a)], mode="lines",
            line=dict(color="rgba(78,205,196,0.2)", width=1),
            showlegend=False, hoverinfo="skip"))
    for stat, angle in zip(stats_ok, angles):
        lx, ly = 1.2*_math.cos(angle), 1.2*_math.sin(angle)
        xa = "left" if lx > 0.1 else ("right" if lx < -0.1 else "center")
        fig.add_annotation(x=lx, y=ly, text=label(stat), showarrow=False,
            font=dict(color="#c8e6e4", size=10), xanchor=xa, yanchor="middle")

    vp = [pct(promedios.get(s, 0), s) for s in stats_ok]
    fig.add_trace(go.Scatter(
        x=[v*_math.cos(a) for v,a in zip(vp,angles)] + [vp[0]*_math.cos(angles[0])],
        y=[v*_math.sin(a) for v,a in zip(vp,angles)] + [vp[0]*_math.sin(angles[0])],
        mode="lines+markers", name="Promedio lista",
        line=dict(color="#f5c518", width=2, dash="dot"),
        marker=dict(color="#f5c518", size=7),
        fill="toself", fillcolor="rgba(245,197,24,0.08)",
        text=[f"<b>{label(s)}</b><br>Prom: {promedios.get(s,0):.2f}" for s in stats_ok] + [""],
        hovertemplate="%{text}<extra></extra>"))

    COLS = [
        ("#4ecdc4","rgba(78,205,196,0.15)"), ("#ef4444","rgba(239,68,68,0.15)"),
        ("#a78bfa","rgba(139,92,246,0.15)"), ("#fb923c","rgba(251,146,60,0.15)"),
    ]
    for idx, (nombre, row) in enumerate(jugadores_data):
        vals = [pct(float(row.get(s,0) or 0), s) for s in stats_ok]
        ln, fill = COLS[idx % len(COLS)]
        fig.add_trace(go.Scatter(
            x=[v*_math.cos(a) for v,a in zip(vals,angles)] + [vals[0]*_math.cos(angles[0])],
            y=[v*_math.sin(a) for v,a in zip(vals,angles)] + [vals[0]*_math.sin(angles[0])],
            mode="lines+markers", name=nombre,
            line=dict(color=ln, width=2.5), marker=dict(color=ln, size=8),
            fill="toself", fillcolor=fill,
            text=[f"<b>{label(s)}</b><br>{nombre}: {float(row.get(s,0) or 0):.2f}<br>Prom: {promedios.get(s,0):.2f}"
                  for s in stats_ok] + [""],
            hovertemplate="%{text}<extra></extra>"))

    fig.update_layout(
        paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
        font=dict(color="#c8e6e4", size=11), height=560,
        margin=dict(l=80, r=80, t=40, b=40), showlegend=True,
        legend=dict(bgcolor="#0d2a27", bordercolor="#4ecdc4", borderwidth=1,
                    font=dict(color="#c8e6e4"), x=0.01, y=0.01),
        xaxis=dict(visible=False, range=[-1.45,1.45]),
        yaxis=dict(visible=False, range=[-1.45,1.45], scaleanchor="x", scaleratio=1))
    return fig

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🔍 Similitud")
    if st.button("← Volver al Home", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("---")
    df = sidebar_carga_datos(pagina="similitud")

# ═══════════════════════════════════════════════════════════════
# GUARD
# ═══════════════════════════════════════════════════════════════

st.markdown("# 🔍 Análisis de Similitud")
st.markdown("### *Encontrá jugadores similares basándote en perfiles específicos*")
st.markdown("---")

if df is None:
    st.markdown(
        '<div class="fm-warning">⚠️ Cargá tu archivo CSV desde el panel lateral para comenzar.</div>',
        unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

st.markdown("## 🎯 Configuración del Análisis")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1️⃣ Jugador a Analizar")
    jugadores_lista = sorted(df["jugador"].dropna().unique())
    jugador_nombre  = st.selectbox("Seleccioná el jugador", jugadores_lista)

    info = vm.get_info_jugador(df, jugador_nombre)
    parts = [f"**{info['nombre']}**"]
    if "posicion" in info: parts.append(f"📍 {info['posicion']}")
    if "edad"    in info: parts.append(f"🎂 {info['edad']} años")
    if "minutos" in info: parts.append(f"⏱️ {info['minutos']} min")
    st.markdown("  ·  ".join(parts))

with col2:
    st.markdown("### 2️⃣ Perfil de Análisis")
    perfil_key = st.selectbox(
        "Seleccioná el perfil",
        list(PERFILES.keys()),
        format_func=lambda x: PERFILES[x]["nombre"]
    )
    stats = vm.get_stats_perfil(df, perfil_key)
    st.markdown(render_perfil_preview(PERFILES[perfil_key], stats), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FILTROS
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## ⚙️ Filtros")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎭 Posición")
    usar_posicion    = st.checkbox("Filtrar por posición específica", value=True)
    posicion_elegida = None
    if usar_posicion and "posición" in df.columns:
        posiciones_jugador = vm.get_posiciones_jugador(df, jugador_nombre)
        if posiciones_jugador:
            posicion_elegida = st.selectbox("Posición a filtrar", options=posiciones_jugador)
            st.markdown(
                f'<div class="fm-success">✅ Filtrando por <strong>{posicion_elegida}</strong></div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="fm-warning">⚠️ No se detectaron posiciones del jugador.</div>',
                        unsafe_allow_html=True)
            usar_posicion = False

with col2:
    st.markdown("### ⏱️ Minutos")
    usar_minutos       = st.checkbox("Filtrar por minutos jugados", value=True)
    porcentaje_minutos = 50
    if usar_minutos and "minutos" in df.columns:
        jugador_row = df[df["jugador"] == jugador_nombre].iloc[0]
        qmin = jugador_row.get("minutos", None)
        if qmin and not pd.isna(qmin):
            porcentaje_minutos = st.slider(
                "% mínimo de minutos del jugador referencia",
                min_value=0, max_value=100, value=50, step=5,
                help=f"Umbral: {int(float(qmin)*0.5):,} min (50% de {int(float(qmin)):,})")
        else:
            st.markdown('<div class="fm-warning">⚠️ El jugador no tiene datos de minutos.</div>',
                        unsafe_allow_html=True)
            usar_minutos = False

# ═══════════════════════════════════════════════════════════════
# PONDERACIÓN
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## ⚖️ Ponderación de Estadísticas")
usar_pesos = st.checkbox("Personalizar importancia de estadísticas", value=False)
pesos      = np.ones(len(stats))

if usar_pesos and stats:
    cols_pw    = st.columns(3)
    pesos_dict = {}
    for i, stat in enumerate(stats):
        with cols_pw[i % 3]:
            p = st.select_slider(label(stat), options=["Bajo","Medio","Alto"],
                                 value="Medio", key=f"pw_{stat}")
            pesos_dict[stat] = p
    pesos = vm.build_pesos(stats, pesos_dict)

# ═══════════════════════════════════════════════════════════════
# BOTÓN CALCULAR
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
col_top, col_btn = st.columns([1, 3])
with col_top:
    top_n = st.selectbox("Mostrar top", [5, 10, 15, 20, 30, 50, "Todos"], index=2)

current_hash = vm.build_hash(
    jugador_nombre, perfil_key, usar_posicion, posicion_elegida,
    usar_minutos, porcentaje_minutos, list(pesos)
)
ya_calculado = vm.ya_calculado(current_hash)

with col_btn:
    label_btn = "✅ Resultado actualizado — Recalcular" if ya_calculado else "🔍 CALCULAR SIMILITUDES"
    calcular  = st.button(label_btn, type="primary", use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# CÁLCULO
# ═══════════════════════════════════════════════════════════════

if calcular:
    with st.spinner("Calculando similitudes..."):
        info_calculo = vm.calcular(
            df, jugador_nombre, perfil_key, pesos,
            usar_posicion, posicion_elegida,
            usar_minutos, porcentaje_minutos,
            current_hash,
        )

    if not info_calculo["ok"]:
        st.markdown(
            f'<div class="fm-danger">❌ {info_calculo["error"]}</div>',
            unsafe_allow_html=True)
        st.stop()

    if info_calculo["pool_posicion"] is not None:
        st.markdown(
            f'<div class="fm-info">🎭 Pool por posición '
            f'<strong>{info_calculo["posicion_usada"]}</strong>: '
            f'{info_calculo["pool_posicion"]:,} jugadores</div>',
            unsafe_allow_html=True)

    finfo = info_calculo.get("filtro_minutos")
    if finfo:
        if "warning" in finfo:
            st.markdown(f'<div class="fm-warning">⚠️ {finfo["warning"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="fm-info">⏱️ Umbral: {finfo["porcentaje"]:.0f}% → '
                f'mín {finfo["min_minutos"]:.0f} min · '
                f'excluidos: {finfo["excluidos"]} · pool: {finfo["pool_final"]:,}</div>',
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# RESULTADOS
# ═══════════════════════════════════════════════════════════════

resultados   = vm.get_resultados()
stats_usadas = vm.get_stats_usadas()
df_pool_ref  = vm.get_pool_ref()
jugador_res  = vm.get_jugador_nombre()
perfil_res   = vm.get_perfil_nombre()

if resultados is None:
    st.stop()

st.markdown("---")
st.markdown(f"## 📊 Similares a **{jugador_res}** · perfil *{perfil_res}*")

top1 = resultados.iloc[0]
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🥇 Más Similar", top1["jugador"])
with c2: st.metric("Híbrida",        f"{top1['similitud']:.1f}%")
with c3: st.metric("MAE",            f"{top1['sim_mae']:.1f}%")
with c4: st.metric("Pearson",        f"{top1['sim_pearson']:.1f}%")

st.markdown("### 📋 Ranking")
top_n_val  = len(resultados) if top_n == "Todos" else int(top_n)
col_ord1, col_ord2, _ = st.columns([2, 1, 1])

with col_ord1:
    col_ordenar = st.selectbox(
        "Ordenar por",
        ["similitud", "sim_mae", "sim_pearson", "sim_euclidiana", "sim_ordinal"],
        format_func=lambda x: {
            "similitud":      "Híbrida %",
            "sim_mae":        "MAE %",
            "sim_pearson":    "Pearson %",
            "sim_euclidiana": "Euclidiana %",
            "sim_ordinal":    "Ordinal %",
        }[x]
    )
with col_ord2:
    orden_asc = st.selectbox("Orden", ["Mayor → Menor", "Menor → Mayor"], index=0)

ascendente = orden_asc == "Menor → Mayor"
res_sorted = resultados.sort_values(col_ordenar, ascending=ascendente).head(top_n_val)

cols_disp = ["jugador", "similitud", "sim_mae", "sim_pearson", "sim_euclidiana", "sim_ordinal"]
for c in ["posición", "edad", "minutos"]:
    if c in res_sorted.columns:
        cols_disp.insert(1, c)

df_disp = res_sorted[cols_disp].copy()
if "edad"    in df_disp.columns: df_disp["edad"]    = df_disp["edad"].apply(lambda x: str(int(x)) if not pd.isna(x) else "—")
if "minutos" in df_disp.columns: df_disp["minutos"] = df_disp["minutos"].apply(lambda x: str(int(x)) if not pd.isna(x) else "—")

df_disp = df_disp.rename(columns={
    "jugador":"Jugador","posición":"Posición","edad":"Edad","minutos":"Minutos",
    "similitud":"Híbrida %","sim_mae":"MAE %","sim_pearson":"Pearson %",
    "sim_euclidiana":"Euclidiana %","sim_ordinal":"Ordinal %",
})

st.dataframe(df_disp, use_container_width=True, hide_index=True,
    column_config={
        "Híbrida %":    st.column_config.ProgressColumn("Híbrida %",    format="%.1f%%", min_value=0, max_value=100),
        "MAE %":        st.column_config.NumberColumn("MAE %",          format="%.1f"),
        "Pearson %":    st.column_config.NumberColumn("Pearson %",      format="%.1f"),
        "Euclidiana %": st.column_config.NumberColumn("Euclidiana %",   format="%.1f"),
        "Ordinal %":    st.column_config.NumberColumn("Ordinal %",      format="%.1f"),
    })

st.markdown("""
<div class="fm-info" style="font-size:0.82rem;">
<strong>Métricas:</strong> Híbrida = 40% MAE + 25% Euclidiana + 20% Pearson + 15% Ordinal &nbsp;·&nbsp;
Todas en percentil normalizado contra el pool filtrado.
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# COMPARACIÓN VISUAL
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("## 📊 Comparación Visual")
st.markdown("*Seleccioná hasta 4 jugadores para comparar las stats del perfil*")

jugadores_opciones = [jugador_res] + res_sorted["jugador"].tolist()
sel_cols  = st.columns(4)
nueva_lista = []

for i in range(4):
    with sel_cols[i]:
        prev = vm.get_jugadores_comparar()
        default_idx = 0
        if i == 0:
            try: default_idx = (["Ninguno"] + jugadores_opciones).index(jugador_res)
            except: default_idx = 0
        elif i < len(prev) and prev[i] in jugadores_opciones:
            try: default_idx = (["Ninguno"] + jugadores_opciones).index(prev[i])
            except: default_idx = 0
        sel = st.selectbox(f"Jugador {i+1}", ["Ninguno"] + jugadores_opciones,
                           index=default_idx, key=f"comp_sel_{i}")
        if sel != "Ninguno":
            nueva_lista.append(sel)

vm.set_jugadores_comparar(nueva_lista)

jdata = [(n, df[df["jugador"] == n].iloc[0])
         for n in nueva_lista if len(df[df["jugador"] == n]) > 0]

if jdata:
    tab1, tab2 = st.tabs(["📊 Spider Graph", "📋 Barras estilo FM"])
    with tab1:
        fig = crear_spider_perfil(jdata, stats_usadas, df_pool_ref)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="fm-warning">⚠️ Necesitás al menos 3 stats del perfil disponibles.</div>',
                        unsafe_allow_html=True)
    with tab2:
        st.markdown(f"**Stats del perfil: {perfil_res}**")
        st.markdown(render_barra_fm(jdata, stats_usadas, df_pool_ref), unsafe_allow_html=True)
        st.markdown('<div class="fm-info" style="font-size:0.8rem;">Las barras representan el valor relativo al percentil 95 del pool.</div>',
                    unsafe_allow_html=True)
else:
    st.markdown('<div class="fm-info">Seleccioná al menos un jugador en los selectores de arriba para ver la comparación.</div>',
                unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DESCARGA
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
csv = res_sorted.to_csv(index=False, encoding="utf-8-sig", sep=";")
st.download_button(
    "📥 Descargar Resultados (CSV)",
    data=csv,
    file_name=f"fm_similares_{jugador_res.replace(' ','_')}.csv",
    mime="text/csv",
    use_container_width=True,
)

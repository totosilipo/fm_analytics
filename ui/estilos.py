"""
FM DataLab v3 - Estilos
========================
CSS global y función de inyección. Sin lógica de negocio.
"""

import streamlit as st

COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --bg-dark: #1a2332;
    --bg-mid: #1e2d3d;
    --bg-card: #223044;
    --teal-glow: #2a6b6b;
    --accent: #4ecdc4;
    --accent-dim: #3aada5;
    --accent-glow:rgba(78,205,196,0.18);
    --text: #e8f4f4;
    --text-muted: #7a9eab;
    --border: rgba(78,205,196,0.15);
    --border-mid: rgba(78,205,196,0.30);
    --danger: #ef4444;
    --warn: #f5c518;
    --font-display:'DM Serif Display', Georgia, serif;
    --font-body: 'DM Sans', 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Courier New', monospace;
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
h2, h3 { color: var(--accent); font-family: var(--font-display); }
p, label, .stMarkdown p { color: var(--text); font-family: var(--font-body); }
code, .stCode { font-family: var(--font-mono) !important; }

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
[data-testid="stMetricLabel"] { color: var(--text-muted); font-family: var(--font-body); }

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

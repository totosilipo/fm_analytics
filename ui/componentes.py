"""
FM DataLab v3 - Componentes UI
================================
Componentes Streamlit reutilizables entre páginas.
Única capa que puede importar streamlit directamente.
"""

import streamlit as st
import pandas as pd

from data.loader import cargar_csv


def sidebar_carga_datos(pagina: str = "") -> pd.DataFrame | None:
    """
    Componente de sidebar unificado para carga de datos.
    Muestra el estado actual del archivo y permite reemplazarlo.
    Retorna el DataFrame activo o None.
    """
    st.markdown("## 📁 Datos")

    df_actual       = st.session_state.get("df", None)
    nombre_archivo  = st.session_state.get("nombre_archivo", None)

    if df_actual is not None and nombre_archivo:
        st.markdown(
            f'<div class="archivo-pill"><span class="dot"></span>{nombre_archivo}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="fm-success">✅ {len(df_actual):,} jugadores · '
            f'{len(df_actual.columns)} columnas</div>',
            unsafe_allow_html=True,
        )
        reemplazar = st.checkbox("Cargar otro archivo", value=False, key=f"reemplazar_{pagina}")
    else:
        reemplazar = True

    if reemplazar:
        uploaded_file = st.file_uploader(
            "Seleccioná tu CSV de Football Manager",
            type=["csv"],
            help="CSV exportado desde FM. Se detecta automáticamente el separador (';' o ',')",
            key=f"uploader_{pagina}",
        )

        if uploaded_file is not None:
            df_nuevo, sep, error = cargar_csv(uploaded_file)

            if error:
                st.markdown(
                    f'<div class="fm-danger">❌ Error al cargar: {error}</div>',
                    unsafe_allow_html=True,
                )
                return df_actual  # devolver el anterior si hay error

            st.session_state["df"]             = df_nuevo
            st.session_state["nombre_archivo"] = uploaded_file.name
            st.session_state["sep_usado"]      = sep

            # limpiar resultados anteriores al cargar nuevo archivo
            for key in ["resultados", "jugadores_similitud_comparar",
                        "ultima_busqueda_hash", "df_pool_ref"]:
                st.session_state.pop(key, None)

            st.markdown(
                f'<div class="fm-success">✅ Cargado con separador "{sep}"</div>',
                unsafe_allow_html=True,
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

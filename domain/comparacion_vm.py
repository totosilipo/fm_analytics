"""
FM DataLab v3 - ComparacionViewModel
======================================
Orquesta la lógica de negocio de la página de Comparación.
- Sin ningún st.* de rendering (solo session_state para persistencia)
- La página solo lee estado y llama a métodos públicos
"""

import pandas as pd
import numpy as np
import streamlit as st

from data.filtros import filtrar_por_posicion, obtener_posiciones_unicas


# Categorías predefinidas para los spider graphs
CATEGORIAS = {
    "Ataque": [
        "goles por 90 minutos", "xg/90", "tir/90", "tirp/90", "% conv",
        "oc c/90", "reg/90", "asis/90", "asie/90",
    ],
    "Defensa": [
        "rob/90", "ent p", "pcg %", "desp/90", "rechazos/90",
        "cab g/90", "cab p/90", "pres c/90", "pres i/90",
    ],
    "Centrocampista": [
        "kp/90", "pases prog/90", "% de pases", "oc c/90", "dist/90",
        "pos gan/90", "pos perd/90", "cen c/90", "cen i/90",
    ],
}


class ComparacionViewModel:

    # ── Claves de session_state ──────────────────────────────────────────────

    _KEY_JUGADORES  = "jugadores_comparacion"
    _KEY_CATEGORIA  = "categoria_activa"

    # ── Inicialización ───────────────────────────────────────────────────────

    def init_estado(self):
        """Inicializa las claves de estado si no existen. Llamar al inicio de la página."""
        if self._KEY_JUGADORES not in st.session_state:
            st.session_state[self._KEY_JUGADORES] = []
        if self._KEY_CATEGORIA not in st.session_state:
            st.session_state[self._KEY_CATEGORIA] = "Defensa"

    # ── Lectura de estado ────────────────────────────────────────────────────

    def get_jugadores(self) -> list:
        return st.session_state.get(self._KEY_JUGADORES, [])

    def get_categoria_activa(self) -> str:
        return st.session_state.get(self._KEY_CATEGORIA, "Defensa")

    def get_categorias(self) -> dict:
        return CATEGORIAS

    # ── Filtrado del dataset ─────────────────────────────────────────────────

    def aplicar_filtros(
        self,
        df: pd.DataFrame,
        posicion: str,
        min_min: int,
        min_max: int,
        limite: int | str,
    ) -> pd.DataFrame:
        """Aplica filtros de posición, minutos y límite de filas."""
        df_f = df.copy()

        if posicion != "Todas":
            df_f = filtrar_por_posicion(df_f, posicion)

        if "minutos" in df_f.columns:
            df_f = df_f[(df_f["minutos"] >= min_min) & (df_f["minutos"] <= min_max)]

        if limite != "Todos":
            df_f = df_f.head(int(limite))

        return df_f

    def get_posiciones(self, df: pd.DataFrame) -> list:
        return obtener_posiciones_unicas(df)

    def get_stats_numericas(self, df: pd.DataFrame) -> list:
        excluir = {"jugador", "posición", "pos", "nombre", "equipo", "club", "edad", "minutos"}
        return [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in excluir]

    # ── Manejo de jugadores en comparación ──────────────────────────────────

    def agregar_jugador(self, nombre: str) -> str | None:
        """
        Intenta agregar un jugador a la comparación.
        Retorna un mensaje de error/info, o None si se agregó correctamente.
        """
        jugadores = self.get_jugadores()

        if nombre in jugadores:
            return f"{nombre} ya está en la comparación."
        if len(jugadores) >= 4:
            return "Máximo 4 jugadores. Eliminá uno para agregar otro."

        st.session_state[self._KEY_JUGADORES] = jugadores + [nombre]
        return None

    def quitar_jugador(self, nombre: str):
        jugadores = self.get_jugadores()
        st.session_state[self._KEY_JUGADORES] = [j for j in jugadores if j != nombre]

    def limpiar_jugadores(self):
        st.session_state[self._KEY_JUGADORES] = []

    def set_categoria(self, categoria: str):
        st.session_state[self._KEY_CATEGORIA] = categoria

    # ── Stats para el spider ─────────────────────────────────────────────────

    def get_stats_spider(self, categoria: str, cols_personalizadas: list, df: pd.DataFrame) -> list:
        """
        Retorna las stats disponibles para el spider según la categoría activa.
        Para 'Personalizada' usa las columnas seleccionadas por el usuario.
        """
        if categoria == "Personalizada":
            return [s for s in cols_personalizadas if s in df.columns]
        return [s for s in CATEGORIAS.get(categoria, []) if s in df.columns]

    def get_datos_jugadores(self, nombres: list, df: pd.DataFrame) -> list:
        """Retorna lista de (nombre, row) para los jugadores seleccionados."""
        return [
            (n, df[df["jugador"] == n].iloc[0])
            for n in nombres
            if len(df[df["jugador"] == n]) > 0
        ]

    def get_tabla_comparacion(
        self, nombres: list, stats: list, df: pd.DataFrame
    ) -> pd.DataFrame:
        """Construye el DataFrame de valores detallados para la tabla de comparación."""
        filas = []
        for nombre in nombres:
            rw = df[df["jugador"] == nombre]
            if len(rw) == 0:
                continue
            j = rw.iloc[0]
            fila = {"Jugador": nombre}
            if "posición" in j:
                fila["Posición"] = j["posición"]
            if "minutos" in j:
                fila["Minutos"] = int(j["minutos"]) if not pd.isna(j["minutos"]) else 0
            for s in stats:
                v = j.get(s, 0)
                fila[s] = round(float(v), 2) if not pd.isna(v) else 0
            filas.append(fila)
        return pd.DataFrame(filas)

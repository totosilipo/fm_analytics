"""
FM DataLab v3 - SimilitudViewModel
====================================
Orquesta la lógica de negocio de la página de Similitud.
- Sin ningún st.* de rendering (solo session_state para persistencia)
- La página solo lee resultados y llama a métodos públicos
"""

import hashlib
import json

import numpy as np
import pandas as pd
import streamlit as st

from data.filtros import filtrar_por_posicion, filtrar_minutos, extraer_posiciones_jugador
from domain.perfiles import PERFILES, PESOS_MAP, validar_stats_perfil
from domain.similitud import (
    SimilitudComparatorV3,
    compute_similarity_v3,
    ranking_jugadores,
)


class SimilitudViewModel:

    # ── Claves de session_state ──────────────────────────────────────────────

    _KEY_RESULTADOS    = "resultados"
    _KEY_JUGADOR       = "jugador_nombre_res"
    _KEY_PERFIL        = "perfil_nombre_res"
    _KEY_STATS         = "stats_usadas"
    _KEY_POOL_REF      = "df_pool_ref"
    _KEY_HASH          = "ultima_busqueda_hash"
    _KEY_COMPARAR      = "jugadores_similitud_comparar"

    # ── Hash de parámetros ───────────────────────────────────────────────────

    def build_hash(
        self,
        jugador_nombre: str,
        perfil_key: str,
        usar_posicion: bool,
        posicion_elegida: str | None,
        usar_minutos: bool,
        porcentaje_minutos: float,
        pesos: list,
    ) -> str:
        """Hash determinista de los parámetros del cálculo."""
        payload = {
            "j":   jugador_nombre,
            "p":   perfil_key,
            "up":  usar_posicion,
            "pos": posicion_elegida,
            "um":  usar_minutos,
            "pct": porcentaje_minutos,
            "w":   list(pesos),
        }
        return hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def ya_calculado(self, current_hash: str) -> bool:
        return st.session_state.get(self._KEY_HASH) == current_hash

    # ── Lectura de estado ────────────────────────────────────────────────────

    def get_resultados(self) -> pd.DataFrame | None:
        return st.session_state.get(self._KEY_RESULTADOS)

    def get_jugador_nombre(self) -> str | None:
        return st.session_state.get(self._KEY_JUGADOR)

    def get_perfil_nombre(self) -> str | None:
        return st.session_state.get(self._KEY_PERFIL)

    def get_stats_usadas(self) -> list:
        return st.session_state.get(self._KEY_STATS, [])

    def get_pool_ref(self) -> pd.DataFrame | None:
        return st.session_state.get(self._KEY_POOL_REF)

    def get_jugadores_comparar(self) -> list:
        return st.session_state.get(self._KEY_COMPARAR, [])

    def set_jugadores_comparar(self, jugadores: list):
        st.session_state[self._KEY_COMPARAR] = jugadores

    # ── Helpers de UI (sin st.* de render) ──────────────────────────────────

    def get_posiciones_jugador(self, df: pd.DataFrame, jugador_nombre: str) -> list:
        jugador_row = df[df["jugador"] == jugador_nombre].iloc[0]
        return extraer_posiciones_jugador(jugador_row.get("posición", ""))

    def get_stats_perfil(self, df: pd.DataFrame, perfil_key: str) -> list:
        return validar_stats_perfil(df, PERFILES[perfil_key])

    def build_pesos(self, stats: list, pesos_dict: dict) -> np.ndarray:
        """Construye el array de pesos a partir del dict {stat: nivel_str}."""
        return np.array([PESOS_MAP.get(pesos_dict.get(s, "Medio"), 1.0) for s in stats])

    def get_info_jugador(self, df: pd.DataFrame, jugador_nombre: str) -> dict:
        """Retorna dict con campos opcionales del jugador para mostrar en UI."""
        row = df[df["jugador"] == jugador_nombre].iloc[0]
        info = {"nombre": jugador_nombre}
        if "posición" in df.columns and not pd.isna(row.get("posición")):
            info["posicion"] = row["posición"]
        if "edad" in df.columns and not pd.isna(row.get("edad")):
            info["edad"] = int(row["edad"])
        if "minutos" in df.columns and not pd.isna(row.get("minutos")):
            info["minutos"] = int(row["minutos"])
        return info

    # ── Cálculo principal ────────────────────────────────────────────────────

    def calcular(
        self,
        df: pd.DataFrame,
        jugador_nombre: str,
        perfil_key: str,
        pesos: np.ndarray,
        usar_posicion: bool,
        posicion_elegida: str | None,
        usar_minutos: bool,
        porcentaje_minutos: float,
        current_hash: str,
    ) -> dict:
        """
        Ejecuta el pipeline completo de similitud.
        Persiste resultados en session_state.
        Retorna un dict con info del proceso para que la página
        pueda mostrar mensajes informativos (sin lógica de negocio).

        Retorna:
            {
                "ok": bool,
                "error": str | None,
                "pool_posicion": int | None,
                "posicion_usada": str | None,
                "filtro_minutos": dict | None,
            }
        """
        resultado_info = {
            "ok": False,
            "error": None,
            "pool_posicion": None,
            "posicion_usada": None,
            "filtro_minutos": None,
        }

        jugador_row = df[df["jugador"] == jugador_nombre].iloc[0]
        perfil      = PERFILES[perfil_key]
        stats       = validar_stats_perfil(df, perfil)

        if not stats:
            resultado_info["error"] = "Ninguna stat del perfil existe en el dataset."
            return resultado_info

        df_pool = df.copy()

        # Filtro de posición
        if usar_posicion and posicion_elegida:
            df_pool = filtrar_por_posicion(df_pool, posicion_elegida)
            resultado_info["pool_posicion"] = len(df_pool)
            resultado_info["posicion_usada"] = posicion_elegida

        # Filtro de minutos
        if usar_minutos:
            df_pool, finfo = filtrar_minutos(df_pool, jugador_row, porcentaje_minutos)
            resultado_info["filtro_minutos"] = finfo

        # Cálculo de similitud
        comp      = SimilitudComparatorV3()
        comp.fit(df_pool, stats)

        cat_pool  = comp.categorize_dataframe(df_pool[stats]) * pesos
        norm_pool = comp.normalize_dataframe(df_pool[stats])  * pesos

        q_stats   = {s: jugador_row.get(s, np.nan) for s in stats}
        cat_q     = comp.categorize_player(q_stats).astype(float) * pesos
        norm_q    = comp.normalize_player(q_stats) * pesos

        mae_s, euc_s, pear_s, ord_s, hyb_s = compute_similarity_v3(
            comp, cat_pool, cat_q, norm_pool, norm_q
        )

        resultados = ranking_jugadores(
            df_pool, mae_s, euc_s, pear_s, ord_s, hyb_s, jugador_row["jugador"]
        )

        # Persistir en session_state
        st.session_state[self._KEY_RESULTADOS] = resultados
        st.session_state[self._KEY_JUGADOR]    = jugador_nombre
        st.session_state[self._KEY_PERFIL]     = perfil["nombre"]
        st.session_state[self._KEY_STATS]      = stats
        st.session_state[self._KEY_POOL_REF]   = df_pool
        st.session_state[self._KEY_HASH]       = current_hash
        st.session_state.pop(self._KEY_COMPARAR, None)

        resultado_info["ok"] = True
        return resultado_info

    # ── Limpieza ─────────────────────────────────────────────────────────────

    def limpiar_comparacion(self):
        st.session_state.pop(self._KEY_COMPARAR, None)

    def limpiar_todo(self):
        for key in [self._KEY_RESULTADOS, self._KEY_JUGADOR, self._KEY_PERFIL,
                    self._KEY_STATS, self._KEY_POOL_REF, self._KEY_HASH,
                    self._KEY_COMPARAR]:
            st.session_state.pop(key, None)

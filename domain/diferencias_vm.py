"""
FM DataLab v3 - DiferenciasViewModel
======================================
Orquesta la lógica de negocio de la página de Diferencias.
- Sin ningún st.* de rendering (solo session_state para persistencia)
- La página solo lee resultados y llama a métodos públicos
"""

import pandas as pd
import numpy as np
import streamlit as st

from data.filtros import filtrar_por_posicion, obtener_posiciones_unicas


class DiferenciasViewModel:

    # ── Filtrado ─────────────────────────────────────────────────────────────

    def aplicar_filtros(
        self,
        df: pd.DataFrame,
        posicion: str,
        min_min: int,
        min_max: int,
    ) -> pd.DataFrame:
        """Aplica filtros de posición y rango de minutos."""
        df_f = df.copy()

        if posicion != "Todas":
            df_f = filtrar_por_posicion(df_f, posicion)

        if "minutos" in df_f.columns:
            df_f = df_f[(df_f["minutos"] >= min_min) & (df_f["minutos"] <= min_max)]

        return df_f

    def get_posiciones(self, df: pd.DataFrame) -> list:
        return obtener_posiciones_unicas(df)

    def get_stats_numericas(self, df: pd.DataFrame) -> list:
        excluir = {"jugador", "posición", "pos", "nombre", "equipo", "club", "edad", "minutos"}
        return [c for c in df.columns if df[c].dtype in [np.float64, np.int64] and c not in excluir]

    def get_min_max_minutos(self, df: pd.DataFrame) -> int:
        if "minutos" in df.columns:
            return int(df["minutos"].max())
        return 10000

    # ── Cálculo de diferencias ───────────────────────────────────────────────

    def calcular_promedios(self, df_f: pd.DataFrame, cols: list) -> dict:
        """Calcula el promedio del pool para cada stat seleccionada."""
        return {s: df_f[s].mean() for s in cols if s in df_f.columns}

    def calcular_diferencias(
        self,
        df_f: pd.DataFrame,
        cols: list,
        promedios: dict,
        limite: int | str,
    ) -> pd.DataFrame:
        """
        Agrega columnas de diferencia vs promedio al DataFrame filtrado.
        Aplica el límite de filas si corresponde.
        Retorna el DataFrame con columnas _dif_{stat}.
        """
        df_dif = df_f.copy()

        for s in cols:
            if s in df_dif.columns:
                df_dif[f"_dif_{s}"] = df_dif[s] - promedios.get(s, 0)

        if limite != "Todos":
            df_dif = df_dif.head(int(limite))

        return df_dif

    def build_tabla_display(
        self, df_dif: pd.DataFrame, cols: list
    ) -> pd.DataFrame:
        """
        Construye el DataFrame listo para mostrar en st.dataframe.
        Renombra las columnas _dif_{stat} → {stat} para display.
        """
        base_cols = [c for c in ["jugador", "posición", "minutos"] if c in df_dif.columns]
        dif_cols  = [f"_dif_{s}" for s in cols if f"_dif_{s}" in df_dif.columns]

        df_display = df_dif[base_cols + dif_cols].copy()
        df_display = df_display.rename(columns={f"_dif_{s}": s for s in cols})
        return df_display

    def get_analisis_rapido(self, df_dif: pd.DataFrame, cols: list) -> dict:
        """
        Calcula el análisis rápido: top 3 más destacados y top 3 por debajo.
        Retorna dict con listas de (jugador, valor).
        """
        dif_cols = [f"_dif_{s}" for s in cols if f"_dif_{s}" in df_dif.columns]
        if not dif_cols:
            return {"top_positivos": [], "top_negativos": []}

        df_calc = df_dif.copy()
        df_calc["_suma_pos"] = df_calc[dif_cols].apply(lambda x: x[x > 0].sum(), axis=1)
        df_calc["_suma_neg"] = df_calc[dif_cols].apply(lambda x: x[x < 0].sum(), axis=1)

        top_pos = [
            (r["jugador"], r["_suma_pos"])
            for _, r in df_calc.nlargest(3, "_suma_pos")[["jugador", "_suma_pos"]].iterrows()
        ]
        top_neg = [
            (r["jugador"], r["_suma_neg"])
            for _, r in df_calc.nsmallest(3, "_suma_neg")[["jugador", "_suma_neg"]].iterrows()
        ]

        return {"top_positivos": top_pos, "top_negativos": top_neg}

    def build_csv_exportable(self, df_dif: pd.DataFrame, cols: list) -> str:
        """Construye el CSV listo para descargar."""
        base_cols = [c for c in ["jugador", "posición", "minutos"] if c in df_dif.columns]
        dif_cols  = [f"_dif_{s}" for s in cols if f"_dif_{s}" in df_dif.columns]

        df_exp = df_dif[base_cols + dif_cols].copy()
        df_exp = df_exp.rename(columns={f"_dif_{s}": s for s in cols})
        return df_exp.to_csv(index=False, encoding="utf-8-sig", sep=";")

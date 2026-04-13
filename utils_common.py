"""
FM DataLab v3 - Módulo Común
=============================
Funciones compartidas entre todas las páginas
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine, euclidean
from dataclasses import dataclass
from typing import Optional
import re

# =========================
# CONFIG INICIAL
# =========================

STATS = [
    "xg/90", "goles por 90 minutos", "kp/90", "pases prog/90", "% de pases",
    "reg/90", "cen.c/i", "rob/90", "ent p", "pcg %", "cen c/90", "pos perd/90",
    "pres c/90", "cab g/90", "tir/90", "% conv", "asis/90", "oc c/90",
    "asie/90", "entr/90", "cab clv/90", "gleq/90", "dist/90", "min/par",
    "eneq/90", "xg -sp/90", "cen i/90", "desp/90", "dsr/90", "pres i/90",
    "pos gan/90", "rechazos/90", "% de disparos", "tirp/90", "ps i/90", "cab p/90"
]

PERFILES = {
    "lateral": {
        "nombre": "Lateral",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "cen.c/i", "rob/90", "ent p", "dist/90", "pcg %"],
    },
    "carrilero": {
        "nombre": "Carrilero",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "cen.c/i", "ent p", "dist/90", "tir/90", "asis/90", "cen i/90"],
    },
    "carrilero_org": {
        "nombre": "Carrilero Organizador",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90",
                  "ent p", "pos perd/90", "asis/90"],
    },
    "central": {
        "nombre": "Central",
        "stats": ["rob/90", "ent p", "pcg %", "pres c/90",
                  "cab g/90", "entr/90", "desp/90", "rechazos/90"],
    },
    "central_salida": {
        "nombre": "Central con Salida",
        "stats": ["rob/90", "ent p", "pcg %", "pres c/90", "cab g/90",
                  "desp/90", "rechazos/90", "pases prog/90", "% de pases"],
    },
    "central_avanzado": {
        "nombre": "Central Avanzado",
        "stats": ["kp/90", "pases prog/90", "% de pases", "reg/90", "rob/90",
                  "ent p", "pcg %", "cab g/90", "entr/90", "desp/90",
                  "rechazos/90", "ps i/90"],
    },
    "mc_defensivo": {
        "nombre": "Mediocampista Defensivo",
        "stats": ["rob/90", "ent p", "pcg %", "pases prog/90",
                  "% de pases", "ps i/90", "pos perd/90", "pos gan/90"],
    },
    "organizador_def": {
        "nombre": "Organizador Defensivo",
        "stats": ["reg/90", "kp/90", "pases prog/90", "% de pases",
                  "ps i/90", "pos perd/90", "ent p", "pcg %", "pos gan/90"],
    },
    "todoterreno": {
        "nombre": "Todoterreno",
        "stats": ["ent p", "pres c/90", "reg/90", "% de pases", "tir/90",
                  "asis/90", "dist/90", "pos gan/90"],
    },
    "extremo": {
        "nombre": "Extremo",
        "stats": ["goles por 90 minutos", "kp/90", "reg/90", "cen.c/i",
                  "pos perd/90", "pres c/90", "tir/90", "asis/90", "cen i/90"],
    },
    "delantero_interior": {
        "nombre": "Delantero Interior",
        "stats": ["goles por 90 minutos", "reg/90", "cen.c/i", "pos perd/90",
                  "pres c/90", "tir/90", "xg/90", "asis/90", "cen i/90"],
    },
    "mediapunta": {
        "nombre": "Mediapunta",
        "stats": ["goles por 90 minutos", "kp/90", "reg/90", "pos perd/90",
                  "tir/90", "asis/90", "% de pases", "ps i/90"],
    },
    "organizador_adel": {
        "nombre": "Organizador Adelantado",
        "stats": ["kp/90", "reg/90", "pos perd/90", "tir/90", "asis/90",
                  "% de pases", "ps i/90", "oc c/90"],
    },
    "delantero_apoyo": {
        "nombre": "Delantero de Apoyo",
        "stats": ["kp/90", "reg/90", "tir/90", "% conv", "asis/90",
                  "ps i/90", "oc c/90"],
    },
    "delantero_centro": {
        "nombre": "Delantero Centro",
        "stats": ["reg/90", "tir/90", "% conv", "oc c/90",
                  "xg/90", "goles por 90 minutos", "cab g/90", "tirp/90"],
    },
    "delantero_torre": {
        "nombre": "Delantero Torre",
        "stats": ["tir/90", "% conv", "oc c/90", "xg/90",
                  "goles por 90 minutos", "cab g/90", "tirp/90",
                  "cab p/90", "% de pases"],
    },
}

PESOS_MAP = {
    "Bajo": 0.5,
    "Medio": 1.0,
    "Alto": 2.0
}

# =========================
# COMPARADOR V3
# =========================

@dataclass
class PercentileThresholds:
    """Almacena los umbrales de percentiles para una estadística"""
    p10: float
    p25: float
    p40: float
    p50: float
    p60: float
    p75: float
    p90: float
    min: float
    max: float
    mean: float
    std: float


class SimilitudComparatorV3:
    """Comparador v3 optimizado para detectar valores muy similares."""

    def __init__(self):
        self.percentile_thresholds: dict[str, PercentileThresholds] = {}
        self.fitted = False

    def fit(self, df_pool: pd.DataFrame, stats: list[str]):
        """Ajusta el comparador calculando percentiles y normalizaciones."""
        self.stats = stats
        self.percentile_thresholds = {}

        for stat in stats:
            if stat not in df_pool.columns:
                continue

            col = df_pool[stat].dropna()

            if len(col) == 0:
                continue

            self.percentile_thresholds[stat] = PercentileThresholds(
                p10=np.percentile(col, 10),
                p25=np.percentile(col, 25),
                p40=np.percentile(col, 40),
                p50=np.percentile(col, 50),
                p60=np.percentile(col, 60),
                p75=np.percentile(col, 75),
                p90=np.percentile(col, 90),
                min=np.min(col),
                max=np.max(col),
                mean=np.mean(col),
                std=np.std(col)
            )

        self.fitted = True

    def _categorize_value_fine(self, value: float, stat_name: str) -> int:
        """Categorización fina: 7 niveles"""
        if pd.isna(value):
            return 0

        if stat_name not in self.percentile_thresholds:
            return 0

        t = self.percentile_thresholds[stat_name]

        if value <= t.p10:
            return -3
        elif value <= t.p25:
            return -2
        elif value <= t.p40:
            return -1
        elif value <= t.p60:
            return 0
        elif value <= t.p75:
            return 1
        elif value <= t.p90:
            return 2
        else:
            return 3

    def categorize_player(self, player_stats: dict[str, float]) -> np.ndarray:
        """Categoriza las estadísticas de un jugador."""
        return np.array([
            self._categorize_value_fine(player_stats.get(stat, np.nan), stat)
            for stat in self.stats
        ])

    def categorize_dataframe(self, df_stats: pd.DataFrame) -> np.ndarray:
        """Categoriza las estadísticas de todos los jugadores."""
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat in df_stats.columns:
                result[:, i] = df_stats[stat].apply(
                    lambda x: self._categorize_value_fine(x, stat)
                )
        return result

    def normalize_player(self, player_stats: dict[str, float]) -> np.ndarray:
        """Normaliza las estadísticas de un jugador usando z-score."""
        normalized = []
        for stat in self.stats:
            value = player_stats.get(stat, np.nan)
            
            if pd.isna(value) or stat not in self.percentile_thresholds:
                normalized.append(0.0)
                continue
            
            t = self.percentile_thresholds[stat]
            if t.std == 0:
                normalized.append(0.0)
            else:
                z = (value - t.mean) / t.std
                normalized.append(np.clip(z, -3, 3))
        
        return np.array(normalized)

    def normalize_dataframe(self, df_stats: pd.DataFrame) -> np.ndarray:
        """Normaliza las estadísticas de todos los jugadores."""
        result = np.zeros((len(df_stats), len(self.stats)))
        for i, stat in enumerate(self.stats):
            if stat not in df_stats.columns or stat not in self.percentile_thresholds:
                continue
            
            t = self.percentile_thresholds[stat]
            if t.std == 0:
                continue
            
            col = df_stats[stat].fillna(t.mean)
            z_scores = (col - t.mean) / t.std
            result[:, i] = np.clip(z_scores, -3, 3)
        
        return result

    def mae_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Similitud basada en MAE (menor diferencia = mayor similitud)."""
        mae = np.mean(np.abs(vec1 - vec2))
        return 1 - (mae / 3)

    def euclidean_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Similitud euclidiana normalizada."""
        dist = euclidean(vec1, vec2)
        max_dist = np.sqrt(len(vec1) * 36)
        return 1 - (dist / max_dist)

    def pearson_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Similitud de correlación de Pearson."""
        if np.std(vec1) == 0 or np.std(vec2) == 0:
            return 0.5
        try:
            corr, _ = pearsonr(vec1, vec2)
            return (corr + 1) / 2
        except:
            return 0.5

    def ordinal_similarity(self, cat1: np.ndarray, cat2: np.ndarray) -> float:
        """Similitud ordinal basada en categorías."""
        diff = np.abs(cat1 - cat2)
        max_diff = 6
        return 1 - (np.mean(diff) / max_diff)

    def hybrid_similarity_score(
        self,
        cat1: np.ndarray,
        cat2: np.ndarray,
        norm1: np.ndarray,
        norm2: np.ndarray
    ) -> float:
        """Score híbrido optimizado."""
        mae_sim = self.mae_similarity(norm1, norm2)
        euc_sim = self.euclidean_similarity(norm1, norm2)
        pear_sim = self.pearson_similarity(norm1, norm2)
        ord_sim = self.ordinal_similarity(cat1, cat2)
        
        return 0.40 * mae_sim + 0.25 * euc_sim + 0.20 * pear_sim + 0.15 * ord_sim


# =========================
# FUNCIONES DE UTILIDAD
# =========================

def limpiar_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y normaliza el DataFrame."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (
                df[col].astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = df[col].replace(["-", "nan", ""], np.nan)
            df[col] = pd.to_numeric(df[col], errors="ignore")
    
    return df


def extraer_posiciones_jugador(posicion_str: str) -> list[str]:
    """
    Extrae posiciones asegurando que los roles solo sean D, C o I.
    Soporta posiciones separadas por comas, puntos o puntos y comas.
    Ej: 'MP (DI). DL (C)' -> ['MP(D)', 'MP(I)', 'DL(C)']
    """
    if not posicion_str or pd.isna(posicion_str):
        return []
        
    posiciones_limpias = []
    
    # MAGIA AQUÍ: Reemplazamos puntos y puntos y comas por comas.
    # Así "MP(DI). DL(C)" se convierte en "MP(DI), DL(C)" y el split funciona.
    texto_normalizado = str(posicion_str).upper().replace('.', ',').replace(';', ',')
    grupos = texto_normalizado.split(',')
    
    for grupo in grupos:
        grupo = grupo.strip()
        if not grupo: 
            continue
            
        if '(' in grupo:
            base, roles_str = grupo.split('(', 1)
            bases = [b.strip() for b in base.split('/') if b.strip()]
            
            roles_validos = re.findall(r'[DCI]', roles_str)
            roles_validos = list(dict.fromkeys(roles_validos))
            
            for b in bases:
                if roles_validos:
                    for r in roles_validos:
                        posiciones_limpias.append(f"{b}({r})")
                else:
                    posiciones_limpias.append(b)
                    
        else:
            bases = [b.strip() for b in grupo.split('/') if b.strip()]
            posiciones_limpias.extend(bases)
            
    return list(dict.fromkeys(posiciones_limpias))


def filtrar_posicion(df: pd.DataFrame, posicion: str) -> pd.DataFrame:
    """
    Filtra el DataFrame por posición específica.
    Soporta formato completo con roles: ej 'MD(A)' o solo base 'MD'
    """
    def tiene_posicion(pos_str):
        if not pos_str or pd.isna(pos_str): 
            return False
        
        buscar = posicion.upper().strip()
        
        # Caso 1: Búsqueda con rol específico (ej: "MD(A)")
        if '(' in buscar:
            base_buscar = buscar.split('(')[0].strip()
            rol_buscar = buscar.split('(')[1].replace(')', '').strip()
            
            for grupo in str(pos_str).split(','):
                grupo = grupo.strip()
                parte_base = grupo.split('(')[0].strip()
                roles = list(grupo.split('(')[1].replace(')', '').strip()) if '(' in grupo else []
                
                # Revisar si la base coincide con alguna de las partes separadas por /
                for token in parte_base.split('/'):
                    if token.strip().upper() == base_buscar and rol_buscar in roles:
                        return True
            return False
        
        # Caso 2: Búsqueda solo por base (ej: "MD")
        else:
            bases = [t.split('(')[0].strip().upper()
                     for grupo in str(pos_str).split(',')
                     for t in grupo.split('/')]
            return buscar in bases
    
    # Encontrar columna de posición
    col_pos = next((c for c in df.columns if c in ['posición','posicion','pos','position']), None)
    if col_pos:
        df = df[df[col_pos].apply(tiene_posicion)]
    
    return df


def filtrar_minutos(
    df: pd.DataFrame,
    query_jugador: pd.Series,
    porcentaje: float,
    min_col: str = "minutos"
) -> tuple[pd.DataFrame, dict]:
    """Filtra por minutos y retorna stats del filtrado."""
    stats = {}
    
    if min_col not in df.columns:
        stats['warning'] = f"Columna '{min_col}' no encontrada"
        return df, stats
    
    query_minutos = query_jugador.get(min_col, None)
    if query_minutos is None or pd.isna(query_minutos):
        stats['warning'] = "El jugador no tiene datos de minutos"
        return df, stats
    
    query_minutos = float(query_minutos)
    min_minutos = query_minutos * (porcentaje / 100)
    
    len_anterior = len(df)
    filtrado = df[df[min_col] >= min_minutos].reset_index(drop=True)
    excluidos = len_anterior - len(filtrado)
    
    stats['query_minutos'] = query_minutos
    stats['porcentaje'] = porcentaje
    stats['min_minutos'] = min_minutos
    stats['excluidos'] = excluidos
    stats['pool_final'] = len(filtrado)
    
    if len(filtrado) < 30:
        stats['warning'] = f"Pool con menos de 30 jugadores ({len(filtrado)}). Resultados menos precisos."
    
    return filtrado, stats


def validar_stats_perfil(df: pd.DataFrame, perfil: dict) -> list[str]:
    """Valida que las stats del perfil existan en el DataFrame."""
    return [stat for stat in perfil["stats"] if stat in df.columns]


def compute_similarity_v3(
    comparator: SimilitudComparatorV3,
    cat_pool: np.ndarray,
    cat_query: np.ndarray,
    norm_pool: np.ndarray,
    norm_query: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calcula todas las métricas de similitud."""
    n_jugadores = cat_pool.shape[0]
    
    mae_sim = np.zeros(n_jugadores)
    euclidean_sim = np.zeros(n_jugadores)
    pearson_sim = np.zeros(n_jugadores)
    ordinal_sim = np.zeros(n_jugadores)
    hybrid_sim = np.zeros(n_jugadores)
    
    for i in range(n_jugadores):
        mae_sim[i] = comparator.mae_similarity(norm_pool[i], norm_query)
        euclidean_sim[i] = comparator.euclidean_similarity(norm_pool[i], norm_query)
        pearson_sim[i] = comparator.pearson_similarity(norm_pool[i], norm_query)
        ordinal_sim[i] = comparator.ordinal_similarity(cat_pool[i], cat_query)
        hybrid_sim[i] = comparator.hybrid_similarity_score(
            cat_pool[i], cat_query, norm_pool[i], norm_query
        )
    
    return mae_sim, euclidean_sim, pearson_sim, ordinal_sim, hybrid_sim


def ranking_jugadores(
    df_pool: pd.DataFrame,
    mae_sim: np.ndarray,
    euclidean_sim: np.ndarray,
    pearson_sim: np.ndarray,
    ordinal_sim: np.ndarray,
    hybrid_sim: np.ndarray,
    query_nombre: str,
) -> pd.DataFrame:
    """Genera el ranking de jugadores similares."""
    result = df_pool.copy()
    result["sim_mae"] = (mae_sim * 100).round(1)
    result["sim_euclidiana"] = (euclidean_sim * 100).round(1)
    result["sim_pearson"] = (pearson_sim * 100).round(1)
    result["sim_ordinal"] = (ordinal_sim * 100).round(1)
    result["similitud"] = (hybrid_sim * 100).round(1)
    
    result = result[result["jugador"].str.lower() != query_nombre.lower()]
    
    return result.sort_values(by="similitud", ascending=False).reset_index(drop=True)


# =========================
# ESTILOS CSS COMPARTIDOS
# =========================

COMMON_CSS = """
<style>
    .stApp {
        background-color: #0e1117;
    }
    
    h1 {
        color: #00ff88;
        font-family: 'Courier New', monospace;
        border-bottom: 2px solid #00ff88;
        padding-bottom: 10px;
    }
    
    h2, h3 {
        color: #00ccff;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #00ff88;
    }
    
    .dataframe {
        font-size: 14px;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1a1d24;
    }
    
    .stButton > button {
        background-color: #00ff88;
        color: #0e1117;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #00ccff;
        transform: scale(1.05);
    }
</style>
"""

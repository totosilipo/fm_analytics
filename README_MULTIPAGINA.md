# FM DataLab v3 - Sistema Multi-Página

## 📋 Descripción

Aplicación web completa para analizar jugadores de Football Manager con múltiples herramientas de análisis.

**Réplica exacta** del script `prueba_sim.py` con interfaz web moderna y funcionalidades expandidas.

## ✨ Páginas Disponibles

### 🏠 Home
Página principal con selector de modos y carga de datos.

### 🔍 Similitud
Encuentra jugadores similares basándote en perfiles específicos:
- **16 perfiles diferentes** (Lateral, Carrilero, Central, Extremo, etc.)
- **5 métricas de similitud** (MAE, Euclidiana, Pearson, Ordinal, Híbrida)
- **Filtro mejorado de posición** - Elegí entre todas las posiciones del jugador (ej: MD(A), MD(D))
- **Filtro por minutos** con % configurable
- **Ponderación personalizable** de estadísticas
- **Top 15 resultados** con métricas detalladas

### ⚖️ Comparación
Explora y compara jugadores del dataset:
- **Vista de tabla completa** con filtros
- **Filtros por posición y minutos**
- **Ordenar por cualquier estadística**
- **Selección flexible de columnas**
- **Exportación a CSV**

### 📊 Diferencias
Analiza diferencias vs el promedio del pool:
- **Comparación con promedios** del pool filtrado
- **Identificación de outliers**
- **Análisis de fortalezas/debilidades**
- **Top jugadores destacados**

## 🚀 Instalación

### Opción 1: Instalación Local (Más Fácil)

1. **Instalar Python 3.8+**
   - Descargá Python desde: https://www.python.org/downloads/
   - Durante la instalación, marcá "Add Python to PATH"

2. **Descargar y extraer el proyecto**
   - Descomprimí el archivo ZIP en una carpeta

3. **Instalar dependencias**
   ```bash
   cd ruta/a/la/carpeta
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   streamlit run fm_datalab_home.py
   ```

5. **Abrir en el navegador**
   - Se abrirá automáticamente en `http://localhost:8501`

### Opción 2: Con Virtual Environment (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run fm_datalab_home.py
```

## 📖 Cómo Usar

### 1. Preparar tu CSV

Exportá tu vista desde Football Manager con:
- **Separador:** `;` (punto y coma)
- **Encoding:** UTF-8
- **Columnas mínimas:**
  - `jugador` (nombre del jugador)
  - `posición` (posición del jugador - formato FM: ej "DF(C), MD(D/A)")
  - `minutos` (minutos jugados)
  - Las estadísticas según el análisis que quieras hacer

### 2. Cargar el archivo

1. Ejecutá `streamlit run fm_datalab_home.py`
2. En el sidebar, click en "Browse files"
3. Seleccioná tu CSV
4. Esperá la confirmación de carga

### 3. Elegir modo de análisis

Desde el **Home**, elegí qué querés hacer:

#### 🔍 **Para encontrar reemplazos directos**
→ Click en "Ir a Similitud"
- Seleccioná el jugador
- Elegí el perfil (ej: "Delantero Centro")
- Configurá filtros:
  - ✅ Filtrar por posición (nuevo: elegí la posición específica)
  - ✅ Filtrar por minutos
- (Opcional) Personalizar pesos de stats
- Click en "CALCULAR SIMILITUDES"

#### ⚖️ **Para explorar el dataset**
→ Click en "Ir a Comparación"
- Aplicá filtros (posición, minutos)
- Seleccioná columnas a mostrar
- Ordenar por estadísticas
- Descargar tabla filtrada

#### 📊 **Para encontrar outliers**
→ Click en "Ir a Diferencias"
- Aplicá filtros
- Seleccioná stats a analizar
- Ver quién está arriba/abajo del promedio
- Identificar jugadores únicos

## 🎯 Perfiles Disponibles (Similitud)

| Perfil | Estadísticas Clave |
|--------|-------------------|
| **Lateral** | Pases progresivos, centros, robos, entradas |
| **Carrilero** | KP, centros, asistencias, disparos |
| **Carrilero Organizador** | KP, pases prog, % pases, posesiones |
| **Central** | Robos, entradas, % duelos, despejes |
| **Central con Salida** | Central + pases progresivos |
| **Central Avanzado** | Central + KP + regates |
| **MC Defensivo** | Robos, recuperaciones, % duelos |
| **Organizador Defensivo** | Regates, KP, pases prog, recuperaciones |
| **Todoterreno** | Entradas, presiones, regates, distancia |
| **Extremo** | Goles, KP, regates, centros, disparos |
| **Delantero Interior** | Goles, regates, presiones, xG |
| **Mediapunta** | Goles, KP, asistencias, % pases |
| **Organizador Adelantado** | KP, asistencias, ocasiones creadas |
| **Delantero de Apoyo** | KP, ocasiones creadas, % conversión |
| **Delantero Centro** | Disparos, goles, xG, remates al arco |
| **Delantero Torre** | Cabezazos, goles, remates al arco |

## 🆕 Mejoras en esta Versión

### Filtro de Posición Mejorado
**Antes:** Solo filtraba por posición base (ej: todos los MD)

**Ahora:** Elegís la posición específica con rol:
- Si un jugador puede jugar `MD(D)` y `MD(A)`
- El selector te muestra ambas opciones
- Podés filtrar específicamente por `MD(A)` para encontrar solo mediocampistas de apoyo

Soporta formatos complejos de FM:
- `DF(C), MD(D/A)` → Se puede filtrar por DF(C), MD(D) o MD(A)
- `MC/MD(A)` → Se puede filtrar por MC(A) o MD(A)
- `DL(A)` → Filtrado exacto por lateral de apoyo

### Sistema Multi-Página
- Navegación fluida entre modos
- Datos compartidos entre páginas
- Cada página enfocada en un tipo de análisis

### Interfaz Mejorada
- Diseño moderno con tema oscuro
- Métricas visuales
- Feedback en tiempo real
- Exportación directa a CSV

## 📊 Métricas Explicadas (Similitud)

### Similitud Híbrida (Score Final)
Combina 4 métricas con pesos optimizados:
- **40% MAE:** Diferencia promedio absoluta
- **25% Euclidiana:** Distancia en espacio normalizado
- **20% Pearson:** Correlación lineal
- **15% Ordinal:** Similitud categórica por percentiles

### MAE (Mean Absolute Error)
Mide la diferencia promedio entre los valores. Menor diferencia = mayor similitud.

### Pearson
Mide si los perfiles tienen la misma "forma" o tendencia.

### Euclidiana
Distancia geométrica en espacio multidimensional normalizado.

### Ordinal
Compara en qué percentil está cada jugador (p10, p25, p40, p50, p60, p75, p90).

## 🔧 Solución de Problemas

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Error al cargar el archivo"
- Verificá que el separador sea `;`
- Verificá que tenga las columnas: `jugador`, `posición`, `minutos`
- Guardá el CSV con encoding UTF-8

### "Pool con menos de 30 jugadores"
- Reducí el % de minutos requerido
- Desactivá el filtro de posición
- Usá un CSV con más jugadores

### La app no se abre
```bash
# Verificar instalación
streamlit --version

# Si no está instalado
pip install streamlit

# Ejecutar en puerto específico
streamlit run fm_datalab_home.py --server.port 8502
```

### No aparecen las páginas en el sidebar
- Verificá que la carpeta `pages/` esté en el mismo directorio que `fm_datalab_home.py`
- Los archivos en `pages/` deben terminar en `.py`

## 📁 Estructura del Proyecto

```
fm_datalab_v3/
├── fm_datalab_home.py           # Página principal (ejecutar este)
├── utils_common.py              # Funciones compartidas
├── requirements.txt             # Dependencias
├── README.md                    # Este archivo
└── pages/                       # Páginas de la app
    ├── 1_🔍_Similitud.py       # Análisis de similitud
    ├── 2_⚖️_Comparacion.py     # Comparación de jugadores
    └── 3_📊_Diferencias.py     # Diferencias vs promedio
```

## 💡 Consejos de Uso

1. **Cargá el CSV una sola vez** - Los datos se comparten entre todas las páginas
2. **Navegá libremente** - Usá el sidebar para cambiar de página
3. **Exportá resultados** - Cada página tiene botón de descarga
4. **Combiná análisis:**
   - Similitud → Encontrar candidatos
   - Comparación → Ver stats específicas
   - Diferencias → Validar que sean outliers en lo que necesitás

## 🆘 Soporte

Si tenés problemas:
1. Verificá que Python 3.8+ esté instalado
2. Verificá que todas las dependencias estén instaladas
3. Revisá que tu CSV tenga el formato correcto
4. Probá con un dataset más pequeño primero

## 📄 Licencia

Uso personal y educativo.

---

**Desarrollado para la comunidad de Football Manager** ⚽

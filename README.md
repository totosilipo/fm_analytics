---
title: FM Analytics
emoji: ⚽
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: false
license: mit
---

# ⚽ FM Analytics

Análisis avanzado de jugadores de Football Manager.

## Páginas

- 🔍 **Similitud** — Encontrá jugadores similares por perfil y métricas
- ⚖️ **Comparación** — Explorá el dataset con spider graphs interactivos
- 📊 **Diferencias** — Analizá desviaciones respecto al promedio del pool

## Uso

1. Cargá tu CSV exportado desde Football Manager (separador `;`, encoding UTF-8)
2. Elegí el modo de análisis desde el Home
3. Aplicá filtros, configurá pesos y calculá

## Formato del CSV

El archivo debe tener al menos las columnas: `jugador`, `posición`, `minutos`.
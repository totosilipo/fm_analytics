#!/bin/bash

echo "===================================="
echo "FM DATALAB v3 - Sistema Multi-Página"
echo "===================================="
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo ""
    echo "Instala Python desde:"
    echo "  - Mac: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    exit 1
fi

echo "Python encontrado: $(python3 --version)"
echo ""

# Verificar si Streamlit está instalado
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Streamlit no encontrado. Instalando dependencias..."
    echo ""
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
fi

echo ""
echo "===================================="
echo "Iniciando FM DataLab v3..."
echo "===================================="
echo ""
echo "La aplicación se abrirá en tu navegador automáticamente."
echo ""
echo "PÁGINAS DISPONIBLES:"
echo "  - Home (página principal)"
echo "  - Similitud (encontrar jugadores similares)"
echo "  - Comparación (explorar dataset)"
echo "  - Diferencias (análisis vs promedio)"
echo ""
echo "Si no se abre automáticamente, copia: http://localhost:8501"
echo ""
echo "Para cerrar la aplicación, presiona Ctrl+C"
echo "===================================="
echo ""

streamlit run fm_datalab_home.py

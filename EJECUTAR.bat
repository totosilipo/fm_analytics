@echo off
echo ====================================
echo FM DATALAB v3 - Sistema Multi-Pagina
echo ====================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Durante la instalacion, marca "Add Python to PATH"
    pause
    exit /b 1
)

echo Python encontrado
echo.

REM Verificar dependencias clave (Streamlit y Plotly)
python -c "import streamlit; import plotly" >nul 2>&1
if errorlevel 1 (
    echo Instalando/Actualizando dependencias necesarias...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo.
echo ====================================
echo Iniciando FM DataLab v3...
echo ====================================
echo.
echo La aplicacion se abrira en tu navegador automaticamente.
echo.
echo PAGINAS DISPONIBLES:
echo   - Home (pagina principal)
echo   - Similitud (encontrar jugadores similares)
echo   - Comparacion (explorar dataset)
echo   - Diferencias (analisis vs promedio)
echo.
echo Si no se abre automaticamente, copia: http://localhost:8501
echo.
echo Para cerrar la aplicacion, presiona Ctrl+C en esta ventana
echo ====================================
echo.

streamlit run fm_datalab_home.py

pause

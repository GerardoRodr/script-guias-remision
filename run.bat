@echo off
if not exist "venv" (
    echo El entorno virtual no existe. Por favor ejecuta setup_env.bat primero.
    pause
    exit /b
)

call venv\Scripts\activate.bat

:: Si hay argumentos, usamos la version CLI
if not "%~1"=="" (
    python main.py %*
) else (
    :: Si no hay argumentos, lanzamos la interfaz grafica
    echo Iniciando interfaz grafica...
    python gui_main.py
)


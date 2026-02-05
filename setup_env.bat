@echo off
echo Configurando el entorno...

:: Crear venv si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar venv e instalar dependencias
echo Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Configuracion completa! Ahora puedes ejecutar el script usando run.bat
pause

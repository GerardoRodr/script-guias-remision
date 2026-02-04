@echo off
echo Setting up environment...

:: Create venv if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv and install requirements
echo Installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Setup complete! You can now run the script using run.bat
pause

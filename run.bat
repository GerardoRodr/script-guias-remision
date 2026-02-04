@echo off
if not exist "venv" (
    echo Virtual environment not found. Please run setup_env.bat first.
    pause
    exit /b
)

call venv\Scripts\activate.bat
python main.py %*

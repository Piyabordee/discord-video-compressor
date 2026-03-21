@echo off
REM Run Discord Video Compressor with Python 3.12

cd /d "%~dp0"

REM Check if .venv312 exists
if not exist ".venv312\Scripts\python.exe" (
    echo ERROR: Python 3.12 virtual environment not found!
    echo Please run the migration script first.
    pause
    exit /b 1
)

REM Run with Python 3.12
echo Starting Discord Video Compressor (Python 3.12 + PySide6)...
.venv312\Scripts\python.exe main.pyw

pause

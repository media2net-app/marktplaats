@echo off
REM ========================================
REM Marktplaats - Dependencies Installeren
REM ========================================
REM Dit script installeert alle benodigde dependencies
REM ========================================

setlocal

echo ========================================
echo Marktplaats - Dependencies Installeren
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is niet geinstalleerd!
    echo.
    echo Installeer Python 3.9 of hoger van: https://www.python.org/downloads/
    echo Zorg dat je "Add Python to PATH" aanvinkt tijdens installatie.
    echo.
    pause
    exit /b 1
)

echo [OK] Python gevonden
python --version
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Installeren van Python packages...
echo.

REM Install required packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Fout bij installeren van Python packages
    pause
    exit /b 1
)

echo.
echo [OK] Python packages geinstalleerd
echo.

echo [INFO] Installeren van Playwright browsers...
echo Dit kan even duren...
echo.

python -m playwright install chromium

if errorlevel 1 (
    echo [WARNING] Fout bij installeren van Playwright browsers
    echo Dit kan betekenen dat Chromium al geinstalleerd is.
)

echo.
echo ========================================
echo Installatie voltooid!
echo ========================================
echo.
echo Je kunt nu start_marktplaats.bat gebruiken om te starten.
echo.
pause

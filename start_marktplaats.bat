@echo off
REM ========================================
REM Marktplaats Product Poster - Start Script
REM ========================================
REM Dit script start het Marktplaats poster script
REM ========================================

setlocal

echo ========================================
echo Marktplaats Product Poster
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

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

REM Check if main script exists
if not exist "marktplaats_poster.py" (
    echo [ERROR] Script niet gevonden: marktplaats_poster.py
    echo Zorg dat dit bestand in de rootmap van het project staat.
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env bestand niet gevonden!
    echo.
    echo Maak een .env bestand met:
    echo   API_BASE_URL=https://jouw-api-url.vercel.app
    echo   INTERNAL_API_KEY=je-api-key
    echo.
    echo Of gebruik env.example als voorbeeld.
    echo.
    pause
)

echo [INFO] Starten van Marktplaats Product Poster...
echo.

REM Run the script
python marktplaats_poster.py

if errorlevel 1 (
    echo.
    echo [ERROR] Script is gestopt met een fout
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Klaar!
echo ========================================
pause

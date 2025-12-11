@echo off
REM ========================================
REM Marktplaats Automator - Standalone Installer
REM ========================================
REM Dit script installeert alle benodigde dependencies en voert het script uit
REM ========================================

setlocal enabledelayedexpansion

echo ========================================
echo Marktplaats Automator - Installatie
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

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if scripts directory exists
if not exist "scripts" (
    echo [ERROR] Scripts directory niet gevonden!
    echo Zorg dat dit bestand in de rootmap van het project staat.
    pause
    exit /b 1
)

echo.
echo [INFO] Installeren van Python dependencies...
echo.

REM Install required packages
python -m pip install --upgrade pip >nul 2>&1
python -m pip install playwright requests python-dotenv >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Fout bij installeren van dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies geinstalleerd

REM Install Playwright browsers
echo.
echo [INFO] Installeren van Playwright browsers (dit kan even duren)...
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
echo Starten van Marktplaats Automator...
echo.

REM Run the standalone script
python scripts\post_marktplaats_standalone.py

if errorlevel 1 (
    echo.
    echo [ERROR] Script is gestopt met een fout
    pause
    exit /b 1
)

echo.
echo ========================================
echo Klaar!
echo ========================================
pause




















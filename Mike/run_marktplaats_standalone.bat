@echo off
REM ========================================
REM Marktplaats Automator - Standalone Runner
REM ========================================
REM Dit script voert het Marktplaats automator script uit
REM ========================================

setlocal

echo ========================================
echo Marktplaats Automator - Runner
echo ========================================
echo.

REM Get script directory (where this .bat file is located)
set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

REM Verify we're in the right directory
if not "%CD%"=="%SCRIPT_DIR%" (
    echo [WARNING] Kon niet naar script directory navigeren
    echo Probeer opnieuw...
    cd /d "%~dp0"
)

echo [INFO] Script directory: %SCRIPT_DIR%
echo [INFO] Huidige directory: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is niet geinstalleerd!
    echo.
    echo Voer eerst install_and_run_marktplaats.bat uit om alles te installeren.
    echo.
    pause
    exit /b 1
)

echo [OK] Python gevonden
python --version
echo.

REM Check if scripts directory exists (use both forward and backslash for compatibility)
if not exist "scripts" (
    if not exist "scripts\" (
        echo [ERROR] Scripts directory niet gevonden!
        echo.
        echo Huidige directory: %CD%
        echo Verwacht pad: %CD%\scripts
        echo.
        echo Zorg dat dit bestand in de rootmap van het project staat.
        echo.
        echo Bestanden in huidige directory:
        dir /b
        echo.
        pause
        exit /b 1
    )
)

REM Check if the actual script file exists (try both path separators)
if not exist "scripts\post_marktplaats_standalone.py" (
    if not exist "scripts/post_marktplaats_standalone.py" (
        echo [ERROR] Script bestand niet gevonden!
        echo.
        echo Huidige directory: %CD%
        echo Verwacht: %CD%\scripts\post_marktplaats_standalone.py
        echo.
        echo Bestanden in scripts directory:
        if exist "scripts" (
            dir /b scripts
        ) else (
            echo (scripts directory bestaat niet)
        )
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Scripts directory gevonden
echo [OK] Script bestand gevonden: scripts\post_marktplaats_standalone.py

REM Run the standalone script (ensure we're in the right directory)
cd /d "%SCRIPT_DIR%"
python "scripts\post_marktplaats_standalone.py"

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


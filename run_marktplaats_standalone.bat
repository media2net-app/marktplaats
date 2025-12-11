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

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

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

REM Check if scripts directory exists
if not exist "scripts\post_marktplaats_standalone.py" (
    echo [ERROR] Script niet gevonden!
    echo Zorg dat dit bestand in de rootmap van het project staat.
    pause
    exit /b 1
)

REM Run the standalone script with logging
set "LOGDIR=%SCRIPT_DIR%logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "LOGFILE=%LOGDIR%\standalone_%DATE:~-4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.log"

echo Logging naar: %LOGFILE%
echo.

REM Use PowerShell to capture stdout+stderr with live console + log
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$host.UI.RawUI.WindowTitle = 'Marktplaats Standalone Runner';" ^
  "; python -u scripts\\post_marktplaats_standalone.py 2>&1 | Tee-Object -FilePath '%LOGFILE%'"

if errorlevel 1 (
    echo.
    echo [ERROR] Script is gestopt met een fout. Zie log: %LOGFILE%
    pause
    exit /b 1
)

echo.
echo ========================================
echo Klaar! Log: %LOGFILE%
echo ========================================
pause




















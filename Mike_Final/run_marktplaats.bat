@echo off
cd /d %~dp0

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir "logs"

echo ========================================
echo Marktplaats Automator - Batch Mode
echo ========================================
echo.
echo Dit script plaatst alle pending producten uit de database.
echo.

:: Check if requests module is installed, if not, install it
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing required Python packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

:: Run the Python script to post all pending products from the database
echo Running Marktplaats Automator for all pending products...
echo Output will be logged to logs\last_run.log
powershell -NoProfile -ExecutionPolicy Bypass -Command "python scripts\post_all_pending.py 2>&1 | Tee-Object -FilePath 'logs\\last_run.log'"

echo.
echo Log opgeslagen in logs\last_run.log
pause
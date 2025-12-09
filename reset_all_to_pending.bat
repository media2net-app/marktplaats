@echo off
cd /d %~dp0

echo ========================================
echo Reset ALLE Producten naar Pending
echo ========================================
echo.

:: Check if requests module is installed
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing required Python packages...
    pip install requests python-dotenv
)

:: Run the reset script
python scripts\reset_all_products.py

echo.
pause


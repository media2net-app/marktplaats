@echo off
cd /d %~dp0

echo ========================================
echo Reset Failed Products naar Pending
echo ========================================
echo.

:: Check if requests module is installed
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing required Python packages...
    pip install requests
)

:: Run the reset script
python scripts\reset_failed_products.py

echo.
pause


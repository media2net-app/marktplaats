@echo off
echo ========================================
echo Foto Upload Test - Marktplaats
echo ========================================
echo.
echo Dit script test de foto upload functionaliteit.
echo.
echo INSTRUCTIES:
echo 1. Sluit alle Chrome vensters
echo 2. Start Chrome met remote debugging:
echo    chrome.exe --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"
echo.
echo OF gebruik dit script dat Chrome start:
echo.
pause

REM Start Chrome with remote debugging
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

REM Wait a bit for Chrome to start
timeout /t 3 /nobreak >nul

REM Run the test script
python scripts\test_photo_upload.py

pause


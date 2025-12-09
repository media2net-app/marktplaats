@echo off
echo ========================================
echo Start Chrome met Remote Debugging
echo ========================================
echo.
echo Dit start Chrome met remote debugging zodat
echo het test script kan verbinden.
echo.
echo SLUIT EERST ALLE CHROME VENSTERS!
echo.
pause

REM Find Chrome executable
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo [ERROR] Chrome niet gevonden!
    echo Zoek handmatig naar chrome.exe en start met:
    echo chrome.exe --remote-debugging-port=9222
    pause
    exit /b 1
)

echo Chrome starten met remote debugging...
echo Path: %CHROME_PATH%
echo.

REM Start Chrome with remote debugging and user data
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

echo.
echo Chrome is gestart met remote debugging op poort 9222
echo Je kunt nu test_photo_upload.py draaien
echo.
pause


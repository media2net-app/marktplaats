@echo off
cd /d %~dp0

echo ========================================
echo Vercel Deployment Script
echo ========================================
echo.

echo Stap 1: Controleren of Vercel CLI geinstalleerd is...
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI niet gevonden. Installeren...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo Fout bij installeren van Vercel CLI
        pause
        exit /b 1
    )
)

echo.
echo Stap 2: Inloggen op Vercel (als je nog niet ingelogd bent)...
vercel login

echo.
echo Stap 3: Project aanmaken en deployen...
echo Project naam: marktplaats
echo.

vercel --name marktplaats --yes

echo.
echo ========================================
echo Deployment voltooid!
echo ========================================
echo.
echo Let op: Je moet nog environment variables instellen in Vercel dashboard:
echo   - DATABASE_URL
echo   - NEXTAUTH_SECRET
echo   - NEXTAUTH_URL
echo   - INTERNAL_API_KEY
echo.
pause


#!/bin/bash
# Script om pending producten naar Marktplaats te plaatsen (Lokale API)
# Dubbelklik dit bestand om het uit te voeren

# Ga naar de directory waar dit script staat
cd "$(dirname "$0")"

# Check of .env bestaat
if [ ! -f .env ]; then
    echo "⚠️  .env bestand niet gevonden!"
    echo "Kopieer env.example naar .env en pas aan:"
    echo "  cp env.example .env"
    echo ""
    echo "Druk op een toets om te sluiten..."
    read -n 1
    exit 1
fi

# Check of Python dependencies zijn geïnstalleerd
if ! python3 -c "import playwright, requests, dotenv" 2>/dev/null; then
    echo "⚠️  Dependencies missen!"
    echo "Installeer met:"
    echo "  pip install playwright requests python-dotenv"
    echo "  python -m playwright install chromium"
    echo ""
    echo "Druk op een toets om te sluiten..."
    read -n 1
    exit 1
fi

echo "=========================================="
echo "🖥️  Marktplaats Local Worker"
echo "=========================================="
echo "Gebruikt: Lokale API (localhost:3000)"
echo ""
echo "⚠️  Zorg dat je lokale server draait!"
echo "   Start in een andere terminal: npm run dev"
echo ""

# Check of server draait
if ! lsof -ti:3000 > /dev/null 2>&1; then
    echo "❌ Geen server gevonden op poort 3000"
    echo ""
    echo "Start eerst je lokale server:"
    echo "  cd .."
    echo "  npm run dev"
    echo ""
    echo "Druk op een toets om te sluiten..."
    read -n 1
    exit 1
fi

echo "✅ Server gevonden op poort 3000"
echo ""

# Voer het script uit met lokale API
export API_BASE_URL="http://localhost:3000"
python3 post_pending_local.py

# Wacht op gebruiker input voordat terminal sluit
echo ""
echo "=========================================="
echo "Klaar! Druk op een toets om te sluiten..."
echo "=========================================="
read -n 1

#!/bin/bash
# Script om pending producten naar Marktplaats te plaatsen
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

# Vraag welke API URL te gebruiken
echo "=========================================="
echo "🖥️  Marktplaats Local Worker"
echo "=========================================="
echo ""
echo "Kies API server:"
echo "  1) Productie (marktplaats-eight.vercel.app)"
echo "  2) Lokaal (localhost:3000)"
echo ""
read -p "Kies optie (1 of 2): " choice

if [ "$choice" == "1" ]; then
    API_BASE_URL="https://marktplaats-eight.vercel.app"
    echo "✅ Gebruikt productie API"
elif [ "$choice" == "2" ]; then
    API_BASE_URL="http://localhost:3000"
    echo "✅ Gebruikt lokale API"
    echo ""
    echo "⚠️  Zorg dat je lokale server draait (npm run dev)"
else
    echo "❌ Ongeldige keuze, gebruik productie API"
    API_BASE_URL="https://marktplaats-eight.vercel.app"
fi

echo ""
echo "=========================================="
echo "Starten..."
echo "=========================================="
echo ""

# Voer het script uit
export API_BASE_URL
python3 post_pending_local.py

# Wacht op gebruiker input voordat terminal sluit
echo ""
echo "=========================================="
echo "Klaar! Druk op een toets om te sluiten..."
echo "=========================================="
read -n 1

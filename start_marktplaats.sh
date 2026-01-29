#!/bin/bash
# ========================================
# Marktplaats Product Poster - Start Script (Mac/Linux)
# ========================================
# Dit script start het Marktplaats poster script
# ========================================

set -e

echo "========================================"
echo "Marktplaats Product Poster"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is niet geinstalleerd!"
    echo ""
    echo "Installeer Python 3.9 of hoger:"
    echo "  brew install python3"
    echo "  Of download van: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "[OK] Python gevonden"
python3 --version
echo ""

# Check if main script exists
if [ ! -f "marktplaats_poster.py" ]; then
    echo "[ERROR] Script niet gevonden: marktplaats_poster.py"
    echo "Zorg dat dit bestand in de rootmap van het project staat."
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env bestand niet gevonden!"
    echo ""
    echo "Maak een .env bestand met:"
    echo "  API_BASE_URL=https://jouw-api-url.vercel.app"
    echo "  INTERNAL_API_KEY=je-api-key"
    echo ""
    echo "Of gebruik env.example als voorbeeld."
    echo ""
    read -p "Druk op ENTER om door te gaan (of Ctrl+C om te stoppen)..."
fi

echo "[INFO] Starten van Marktplaats Product Poster..."
echo ""

# Run the script
python3 marktplaats_poster.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Script is gestopt met een fout"
    echo ""
    exit 1
fi

echo ""
echo "========================================"
echo "Klaar!"
echo "========================================"

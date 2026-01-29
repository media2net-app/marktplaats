#!/bin/bash
# ========================================
# Marktplaats - Dependencies Installeren (Mac/Linux)
# ========================================
# Dit script installeert alle benodigde dependencies
# ========================================

set -e

echo "========================================"
echo "Marktplaats - Dependencies Installeren"
echo "========================================"
echo ""

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

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[INFO] Installeren van Python packages..."
echo ""

# Install required packages
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Fout bij installeren van Python packages"
    exit 1
fi

echo ""
echo "[OK] Python packages geinstalleerd"
echo ""

echo "[INFO] Installeren van Playwright browsers..."
echo "Dit kan even duren..."
echo ""

python3 -m playwright install chromium

if [ $? -ne 0 ]; then
    echo "[WARNING] Fout bij installeren van Playwright browsers"
    echo "Dit kan betekenen dat Chromium al geinstalleerd is."
fi

echo ""
echo "========================================"
echo "Installatie voltooid!"
echo "========================================"
echo ""
echo "Je kunt nu start_marktplaats.sh gebruiken om te starten."
echo ""

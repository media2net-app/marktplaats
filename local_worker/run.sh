#!/bin/bash
# Convenience script om het lokale worker script te draaien

cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env bestand niet gevonden!"
    echo "Kopieer .env.example naar .env en pas aan:"
    echo "  cp .env.example .env"
    exit 1
fi

# Run the script
python3 post_pending_local.py

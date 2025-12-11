#!/bin/bash

# Get the directory where the script is located
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

echo "========================================"
echo "Marktplaats Automator - Batch Mode"
echo "========================================"
echo ""
echo "Dit script plaatst alle pending producten uit de database."
echo ""

# Check if requests module is installed, if not, install it
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing required Python packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install required packages"
        exit 1
    fi
fi

# Run the Python script to post all pending products from the database
echo "Running Marktplaats Automator for all pending products..."
echo "Output will be logged to logs/last_run.log"
echo ""

python3 scripts/post_all_pending.py 2>&1 | tee logs/last_run.log

echo ""
echo "Log opgeslagen in logs/last_run.log"
echo ""
echo "Druk op Enter om af te sluiten..."
read

















#!/bin/bash

# Get the directory where the script is located
cd "$(dirname "$0")"

echo "========================================"
echo "Reset Failed Products naar Pending"
echo "========================================"
echo ""

# Check if requests module is installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing required Python packages..."
    pip3 install requests
fi

# Run the reset script
python3 scripts/reset_failed_products.py

echo ""
echo "Druk op Enter om af te sluiten..."
read

















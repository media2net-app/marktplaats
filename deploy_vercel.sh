#!/bin/bash

# Get the directory where the script is located
cd "$(dirname "$0")"

echo "========================================"
echo "Vercel Deployment Script"
echo "========================================"
echo ""

echo "Stap 1: Controleren of Vercel CLI geïnstalleerd is..."
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI niet gevonden. Installeren..."
    npm install -g vercel
    if [ $? -ne 0 ]; then
        echo "Fout bij installeren van Vercel CLI"
        exit 1
    fi
fi

echo ""
echo "Stap 2: Inloggen op Vercel (als je nog niet ingelogd bent)..."
vercel login

echo ""
echo "Stap 3: Project aanmaken en deployen..."
echo "Project naam: marktplaats"
echo ""

vercel --name marktplaats --yes

echo ""
echo "========================================"
echo "Deployment voltooid!"
echo "========================================"
echo ""
echo "Let op: Je moet nog environment variables instellen in Vercel dashboard:"
echo "  - DATABASE_URL"
echo "  - NEXTAUTH_SECRET"
echo "  - NEXTAUTH_URL"
echo "  - INTERNAL_API_KEY"
echo ""
echo "Druk op Enter om af te sluiten..."
read




















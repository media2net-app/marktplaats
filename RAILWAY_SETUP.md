# Railway Setup voor Marktplaats Automator

Railway is ideaal voor het draaien van het Python script omdat het:
- Persistent storage ondersteunt (user_data_dir blijft behouden)
- Headless browsers ondersteunt
- Continue processen kan draaien
- Environment variables kan beheren

## Stap 1: Railway Project Aanmaken

1. Ga naar https://railway.app
2. Klik op "New Project"
3. Kies "Deploy from GitHub repo"
4. Selecteer je marktplaats repository

## Stap 2: Service Configureren

### Service Type
- **Type**: Web Service (of Background Worker)
- **Start Command**: `python scripts/post_all_pending.py` (of je monitor script)

### Environment Variables

Voeg de volgende environment variables toe in Railway:

```env
# Marktplaats API
NEXTAUTH_URL=https://jouw-vercel-app.vercel.app
API_BASE_URL=https://jouw-vercel-app.vercel.app
INTERNAL_API_KEY=je-api-key-hier

# Playwright Configuratie
USER_DATA_DIR=/app/user_data
MEDIA_ROOT=/app/public/media
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl
HEADLESS=true

# Optioneel
ACTION_DELAY_MS=200
MP_VERBOSE=true
MP_FAST=true
```

### Belangrijke Notities:

1. **USER_DATA_DIR**: Gebruik `/app/user_data` voor persistent storage
   - Railway heeft persistent volumes, dus de login sessie blijft behouden
   - De eerste keer moet je handmatig inloggen (zie Stap 3)

2. **HEADLESS**: Zet op `true` voor Railway (geen display beschikbaar)

3. **INTERNAL_API_KEY**: Moet hetzelfde zijn als in je Vercel deployment

## Stap 3: Eerste Login Setup

Voor de eerste keer moet je handmatig inloggen:

1. Zet tijdelijk `HEADLESS=false` (als Railway dit ondersteunt via browser)
2. Of gebruik lokaal:
   ```bash
   python scripts/post_ads.py --login
   ```
   Dit opent een browser waar je handmatig inlogt
3. Kopieer de `user_data` folder naar Railway (via persistent volume)

**Alternatief**: Gebruik Railway's browser preview (als beschikbaar) om in te loggen.

## Stap 4: Persistent Volume Configureren

Railway heeft automatisch persistent storage voor `/app`, maar zorg dat:

1. De `user_data` folder wordt behouden tussen deployments
2. Railway's persistent volume is gekoppeld aan `/app/user_data`

## Stap 5: Dependencies Installeren

Railway detecteert automatisch Python projecten, maar zorg dat:

1. `requirements.txt` bestaat in de root
2. Playwright browsers worden geïnstalleerd:
   ```bash
   python -m playwright install chromium
   ```

Voeg dit toe aan je start script of gebruik een build command.

## Stap 6: Monitoring Script (Optioneel)

Voor continue monitoring van pending producten, gebruik:

```bash
python scripts/monitor_categories.py
```

Of maak een eigen loop script dat `post_all_pending.py` periodiek aanroept.

## Troubleshooting

### Login Sessie Verloren
- Controleer of `USER_DATA_DIR` correct is ingesteld
- Zorg dat Railway's persistent volume is gekoppeld
- Herhaal Stap 3 om opnieuw in te loggen

### Browser Start Fouten
- Zorg dat `HEADLESS=true` is ingesteld
- Controleer of Playwright browsers zijn geïnstalleerd
- Check Railway logs voor specifieke errors

### API Connectie Problemen
- Controleer of `NEXTAUTH_URL` en `API_BASE_URL` correct zijn
- Verifieer dat `INTERNAL_API_KEY` overeenkomt met Vercel
- Test de API endpoints handmatig

### Foto Upload Problemen
- Controleer of `MEDIA_ROOT` correct is ingesteld
- Zorg dat de folder bestaat en schrijfbaar is
- Voor blob storage, gebruik Vercel Blob Storage (zie VERCEL_BLOB_SETUP.md)

## Railway vs Vercel

- **Vercel**: Host de Next.js web app (frontend + API)
- **Railway**: Draait de Python scripts (Playwright automatisering)

Deze scheiding is ideaal omdat:
- Vercel is geoptimaliseerd voor Next.js
- Railway is beter voor lange-running processen met persistent storage
- Playwright werkt beter op Railway (niet serverless)

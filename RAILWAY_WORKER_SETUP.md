# Railway Worker Setup

Deze gids legt uit hoe je de Railway worker correct configureert om automatisch pending producten te verwerken.

## Probleem

Als je in de Railway logs ziet:
- `Response status: 401`
- `Error checking status: 401 - {"error":"Unauthorized"}`
- `Checking pending products at: .../api/products/batch-post`

Dan zijn er twee problemen:
1. **Verkeerd endpoint**: Het gebruikt `/api/products/batch-post` in plaats van `/api/products/pending`
2. **API key mismatch**: De `INTERNAL_API_KEY` komt niet overeen tussen Vercel en Railway

## Oplossing

### Stap 1: Gebruik het juiste worker script

Er zijn twee opties:

#### Optie A: Gebruik `railway_worker.py` (Aanbevolen)
Dit is een nieuw script speciaal gemaakt voor Railway:

```bash
python scripts/railway_worker.py
```

Dit script:
- ✅ Gebruikt het juiste endpoint: `/api/products/pending`
- ✅ Stuurt API key correct mee (header + query parameter)
- ✅ Verwerkt alle pending producten automatisch
- ✅ Update producten via batch-update endpoint
- ✅ Draait continu en checkt elke 5 minuten (configureerbaar)

#### Optie B: Gebruik `post_all_pending.py` (Bestaand)
Dit script werkt ook, maar draait één keer en stopt:

```bash
python scripts/post_all_pending.py
```

Voor continu draaien, gebruik een cron job of loop in Railway.

### Stap 2: Configureer Railway Service

1. **Start Command**:
   ```
   python scripts/railway_worker.py
   ```

2. **Environment Variables** in Railway:
   ```env
   # API Configuration (VERPLICHT - moet overeenkomen met Vercel!)
   NEXTAUTH_URL=https://marktplaats-eight.vercel.app
   API_BASE_URL=https://marktplaats-eight.vercel.app
   INTERNAL_API_KEY=je-api-key-hier
   
   # Check Interval (optioneel, default 300 seconden = 5 minuten)
   CHECK_INTERVAL=300
   
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

### Stap 3: Zorg dat API Keys overeenkomen

**BELANGRIJK**: De `INTERNAL_API_KEY` moet **exact hetzelfde** zijn in:
- ✅ Vercel Environment Variables
- ✅ Railway Environment Variables

**Hoe te controleren:**

1. **Vercel**:
   - Ga naar je Vercel project → Settings → Environment Variables
   - Zoek `INTERNAL_API_KEY`
   - Kopieer de waarde

2. **Railway**:
   - Ga naar je Railway service → Variables
   - Zet `INTERNAL_API_KEY` op dezelfde waarde
   - Of voeg het toe als het nog niet bestaat

3. **Redeploy beide**:
   - Vercel: Redeploy de laatste deployment
   - Railway: Restart de service

### Stap 4: Test de configuratie

1. **Check Railway logs**:
   ```
   Railway Dashboard → Your Service → Logs
   ```

2. **Je zou moeten zien**:
   ```
   ✅ Successfully imported post_ads module
   Checking pending products at: https://marktplaats-eight.vercel.app/api/products/pending
   Response status: 200
   ```

3. **Als je nog steeds 401 ziet**:
   - Controleer of `INTERNAL_API_KEY` exact hetzelfde is in beide platforms
   - Controleer of er geen extra spaties zijn
   - Controleer of de API key niet is veranderd

## Troubleshooting

### "Response status: 401"
**Oorzaak**: API key mismatch of niet meegestuurd

**Oplossing**:
1. Controleer of `INTERNAL_API_KEY` in Railway exact overeenkomt met Vercel
2. Zorg dat er geen extra spaties zijn
3. Redeploy beide services

### "Checking pending products at: .../batch-post"
**Oorzaak**: Oud worker script gebruikt verkeerd endpoint

**Oplossing**:
1. Gebruik `railway_worker.py` in plaats van het oude script
2. Update de start command in Railway naar: `python scripts/railway_worker.py`

### "No pending products" (maar je hebt wel pending producten)
**Oorzaak**: Verkeerde user ID of API key geeft toegang tot verkeerde user

**Oplossing**:
1. Controleer of de API key toegang heeft tot de juiste user
2. Check of producten daadwerkelijk status "pending" hebben in de database

### Worker stopt na één run
**Oorzaak**: Je gebruikt `post_all_pending.py` in plaats van `railway_worker.py`

**Oplossing**:
- Gebruik `railway_worker.py` voor continu draaien
- Of zet een cron job op in Railway die `post_all_pending.py` periodiek uitvoert

## Best Practices

1. **Gebruik `railway_worker.py`** voor continu draaien
2. **Check interval**: 300 seconden (5 minuten) is een goede balans
3. **Monitor logs**: Check regelmatig Railway logs voor errors
4. **API key security**: Gebruik een sterke, unieke API key
5. **Error handling**: De worker herstelt automatisch van tijdelijke errors

## Verificatie

Na correcte setup zou je in Railway logs moeten zien:

```
🚂 Railway Marktplaats Worker
======================================================================
API Base URL: https://marktplaats-eight.vercel.app
Check Interval: 300 seconds (5 minutes)
INTERNAL_API_KEY: ✅ Set
======================================================================

✅ Successfully imported post_ads module
Checking pending products at: https://marktplaats-eight.vercel.app/api/products/pending
Response status: 200
No pending products. Waiting...
```

Als je dit ziet, werkt alles correct! 🎉

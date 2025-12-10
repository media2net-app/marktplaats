# Railway Auto Posting - Status Check

## ✅ Hoe het werkt:

1. **Railway Worker** draait continu op Railway
2. **Elke 5 minuten** checkt het of er pending producten zijn
3. **Als er pending producten zijn**, roept het de batch-post API aan
4. **De API** roept voor elk product de posting endpoint aan
5. **De posting endpoint** gebruikt Playwright/Chromium om op Marktplaats te posten

## 🔍 Check of Railway Worker draait:

### 1. Ga naar Railway Dashboard
- Ga naar je Railway project
- Klik op je service (marktplaats worker)
- Ga naar **"Logs"** tab

### 2. Check de logs voor:
```
🚂 Railway Marktplaats Worker
API Base URL: https://jouw-app.vercel.app
Check Interval: 300 seconds (5 minutes)
INTERNAL_API_KEY: ✅ Set
```

### 3. Check of het pending producten vindt:
```
[2024-XX-XX XX:XX:XX] Found 1 pending product(s)
Starting batch post...
```

## ⚙️ Vereiste Environment Variables in Railway:

Zorg dat deze zijn ingesteld in Railway:

```bash
# Verplicht:
API_BASE_URL=https://jouw-app.vercel.app
NEXTAUTH_URL=https://jouw-app.vercel.app
INTERNAL_API_KEY=jouw-api-key-hier

# Optioneel:
CHECK_INTERVAL=300  # Check elke 5 minuten
PLAYWRIGHT_HEADLESS=true
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl
```

## 🚨 Mogelijke Problemen:

### 1. Railway Worker draait niet
- **Check**: Railway dashboard → Service → Logs
- **Oplossing**: Herstart de service of check deployment status

### 2. INTERNAL_API_KEY niet ingesteld
- **Check**: Railway dashboard → Service → Variables
- **Oplossing**: Voeg `INTERNAL_API_KEY` toe (moet overeenkomen met Vercel)

### 3. API_BASE_URL verkeerd
- **Check**: Railway logs voor connection errors
- **Oplossing**: Zet `API_BASE_URL` naar je Vercel production URL

### 4. Geen pending producten gevonden
- **Check**: App → Products → Status filter
- **Oplossing**: Zorg dat producten op "pending" staan

## ⏱️ Timing:

- **Check interval**: Standaard elke 5 minuten (300 seconden)
- **Eerste check**: Direct na start van worker
- **Max wachttijd**: 5 minuten na het toevoegen van een pending product

## 📊 Status Tracking:

Je kunt de status volgen via:
1. **App Dashboard**: Zie hoeveel pending/processing/completed producten er zijn
2. **Railway Logs**: Zie real-time wat de worker doet
3. **Product Status**: Elke product toont zijn status (pending → processing → completed/failed)

## ✅ Testen:

1. **Voeg een product toe** met status "pending"
2. **Wacht maximaal 5 minuten**
3. **Check Railway logs** om te zien of het wordt opgepikt
4. **Check product status** in de app (zou moeten veranderen naar "processing" dan "completed")

## 🔧 Handmatig Triggeren (voor testen):

Je kunt ook handmatig triggeren via de app:
- Ga naar Dashboard
- Klik op "Batch Post Pending Products" knop
- Dit roept direct de batch-post API aan (zonder te wachten op Railway)


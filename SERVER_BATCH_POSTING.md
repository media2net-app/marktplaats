# Server-Side Batch Posting

Het Marktplaats posting script gebruikt Playwright (browser automation), wat **niet werkt op Vercel serverless**. Je hebt een externe server nodig om dit uit te voeren.

## Opties

### Optie 1: Eigen Server/PC met Cron Job (Aanbevolen)

1. **Zet een server/PC op** die altijd aan staat (of gebruik een VPS)
2. **Installeer Python en dependencies**:
   ```bash
   pip install playwright requests python-dotenv
   playwright install chromium
   ```
3. **Maak een cron job** die regelmatig het batch endpoint aanroept:
   ```bash
   # Elke 5 minuten
   */5 * * * * curl -X POST "https://jouw-app.vercel.app/api/products/batch-post?api_key=JOUW_API_KEY"
   ```

### Optie 2: Vercel Cron Job + Externe Service

1. **Zet een externe service op** (bijv. Railway, Render, of je eigen server)
2. **Maak een Vercel Cron Job** die deze service aanroept
3. **De externe service** voert het Python script uit

### Optie 3: Handmatig via UI

1. **Gebruik de UI** om individuele producten te posten
2. **Of maak een knop** die het batch endpoint aanroept

## API Endpoints

### POST `/api/products/batch-post`

Post alle pending producten in batch.

**Authenticatie:**
- Session (voor frontend)
- API key via header: `x-api-key: JOUW_API_KEY`
- API key via query: `?api_key=JOUW_API_KEY`

**Response:**
```json
{
  "success": true,
  "message": "Batch posting voltooid: 3 succesvol, 0 gefaald",
  "processed": 3,
  "results": [
    {
      "productId": "...",
      "title": "...",
      "success": true,
      "message": "Product succesvol geplaatst"
    }
  ],
  "errors": []
}
```

### GET `/api/products/batch-post`

Check de status van pending producten.

**Response:**
```json
{
  "pending": 5,
  "processing": 1,
  "completed": 10,
  "failed": 2
}
```

## Voorbeeld: Cron Job op Linux/Mac

```bash
# Maak een script: ~/marktplaats-batch-post.sh
#!/bin/bash
curl -X POST "https://jouw-app.vercel.app/api/products/batch-post?api_key=JOUW_API_KEY" \
  -H "Content-Type: application/json"
```

```bash
# Maak het uitvoerbaar
chmod +x ~/marktplaats-batch-post.sh

# Voeg toe aan crontab
crontab -e

# Voeg deze regel toe (elke 5 minuten):
*/5 * * * * /home/gebruiker/marktplaats-batch-post.sh >> /tmp/marktplaats-cron.log 2>&1
```

## Voorbeeld: Windows Task Scheduler

1. Maak een `.bat` bestand:
   ```batch
   @echo off
   curl -X POST "https://jouw-app.vercel.app/api/products/batch-post?api_key=JOUW_API_KEY"
   ```

2. Open Task Scheduler
3. Maak een nieuwe taak die dit script elke 5 minuten uitvoert

## Belangrijk

⚠️ **Het Python script heeft een browser nodig** (Playwright), dus:
- ❌ Werkt NIET op Vercel serverless
- ❌ Werkt NIET op serverless platforms zonder browser support
- ✅ Werkt WEL op een eigen server/PC met Python en Playwright
- ✅ Werkt WEL op VPS/dedicated servers

## Alternatief: Externe Worker Service

Als je geen eigen server hebt, kun je een externe service gebruiken zoals:
- **Railway** (railway.app) - gratis tier beschikbaar
- **Render** (render.com) - gratis tier beschikbaar
- **DigitalOcean App Platform** - betaald
- **AWS EC2** - betaald
- **Google Cloud Run** - met container (complexer)

Deze services kunnen een Python script draaien met Playwright.


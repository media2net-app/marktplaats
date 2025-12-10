# Railway Deployment - Marktplaats Posting Worker

Deze gids helpt je om de Marktplaats posting worker op Railway te deployen.

## 📋 Vereisten

1. **Railway account** (gratis op [railway.app](https://railway.app))
2. **GitHub repository** (of Railway CLI)
3. **Vercel app** met API endpoints (al gedeployed)

## 🚀 Stap 1: Railway Project Aanmaken

1. Ga naar [railway.app](https://railway.app) en log in
2. Klik op **"New Project"**
3. Kies **"Deploy from GitHub repo"**
4. Selecteer je `marktplaats` repository
5. Railway detecteert automatisch de configuratie

## ⚙️ Stap 2: Environment Variables Instellen

In Railway dashboard, ga naar je service → **Variables** tab en voeg toe:

### Verplichte Variables:

```bash
# API Configuration
API_BASE_URL=https://jouw-app.vercel.app
NEXTAUTH_URL=https://jouw-app.vercel.app
INTERNAL_API_KEY=jouw-api-key-hier

# Playwright Configuration
PLAYWRIGHT_HEADLESS=true

# Marktplaats Configuration
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl

# Worker Configuration (optioneel)
CHECK_INTERVAL=300  # Check elke 5 minuten (in seconden)
```

### Waar vind je INTERNAL_API_KEY?

1. Ga naar je Vercel dashboard
2. Selecteer je project
3. Ga naar **Settings** → **Environment Variables**
4. Zoek `INTERNAL_API_KEY`
5. Kopieer de waarde en plak in Railway

## 📦 Stap 3: Build & Deploy Configuratie

Railway gebruikt automatisch `railway.json` voor configuratie. De configuratie:

- **Build**: Installeert Python dependencies en Playwright Chromium
- **Deploy**: Start de worker script die continu draait

### Handmatige Configuratie (als railway.json niet werkt):

1. Ga naar je service → **Settings**
2. **Build Command**:
   ```bash
   pip install -r requirements.txt && playwright install chromium
   ```
3. **Start Command**:
   ```bash
   python scripts/railway_worker.py
   ```

## 💾 Stap 4: Persistent Storage (Belangrijk!)

De worker moet de Marktplaats login sessie bewaren. Railway heeft persistent storage nodig:

1. Ga naar je service → **Settings**
2. Scroll naar **"Volumes"**
3. Klik **"Add Volume"**
4. Mount path: `/app/user_data`
5. Dit bewaart de login sessie tussen restarts

### Of via Environment Variable:

```bash
USER_DATA_DIR=/app/user_data
```

## 🔄 Stap 5: Eerste Login Setup

De eerste keer moet je handmatig inloggen op Marktplaats:

### Optie A: Via Railway Logs (Aanbevolen)

1. Deploy de worker
2. Wacht tot de worker draait
3. De worker probeert automatisch in te loggen
4. Check de logs voor login instructies

### Optie B: Via Login Script

Maak een tijdelijk login script:

```python
# scripts/railway_login.py
import asyncio
from post_ads import run

async def login():
    await run(
        csv_path=None,
        api_url=None,
        product_id=None,
        login_only=True,  # Alleen inloggen
        keep_open=False
    )

if __name__ == '__main__':
    asyncio.run(login())
```

Run dit eenmalig via Railway CLI of via een tijdelijke service.

## 📊 Stap 6: Monitoring

### Railway Dashboard:

1. Ga naar je service
2. **Metrics** tab: Zie CPU, Memory, Network usage
3. **Logs** tab: Zie real-time logs van de worker

### Logs Controleren:

```bash
# Via Railway CLI
railway logs

# Of via dashboard
# Ga naar service → Logs tab
```

## 🔧 Troubleshooting

### Worker start niet:

1. Check **Logs** voor error messages
2. Verify alle environment variables zijn ingesteld
3. Check of `requirements.txt` alle dependencies bevat

### "Playwright browser not found":

```bash
# Voeg toe aan build command:
playwright install chromium
playwright install-deps chromium
```

### "401 Unauthorized":

- Check of `INTERNAL_API_KEY` correct is ingesteld
- Check of de key in Vercel hetzelfde is als in Railway
- Verify `API_BASE_URL` wijst naar je Vercel app

### Login sessie verloren:

- Check of volume is gemount op `/app/user_data`
- Verify `USER_DATA_DIR` environment variable
- Mogelijk moet je opnieuw inloggen

### Worker draait maar post niets:

1. Check logs voor "No pending products"
2. Verify er zijn daadwerkelijk pending products in database
3. Test het batch endpoint handmatig:
   ```bash
   curl -X POST "https://jouw-app.vercel.app/api/products/batch-post" \
     -H "x-api-key: jouw-api-key"
   ```

## 📈 Optimalisatie

### Check Interval Aanpassen:

```bash
# Elke 1 minuut (60 seconden)
CHECK_INTERVAL=60

# Elke 10 minuten (600 seconden)
CHECK_INTERVAL=600
```

### Resource Limits:

Railway gratis tier heeft:
- 512MB RAM
- 1GB Storage
- 100GB Bandwidth/maand

Voor productie, overweeg:
- **Hobby Plan** ($5/maand): Meer resources
- **Pro Plan** ($20/maand): Nog meer resources + support

## 🎯 Testen

### Test de Worker Lokaal:

```bash
# Set environment variables
export API_BASE_URL=https://jouw-app.vercel.app
export INTERNAL_API_KEY=jouw-api-key
export PLAYWRIGHT_HEADLESS=true

# Run worker
python scripts/railway_worker.py
```

### Test Batch Endpoint:

```bash
curl -X POST "https://jouw-app.vercel.app/api/products/batch-post" \
  -H "x-api-key: jouw-api-key" \
  -H "Content-Type: application/json"
```

## 📝 Checklist

- [ ] Railway account aangemaakt
- [ ] Project gedeployed van GitHub
- [ ] Alle environment variables ingesteld
- [ ] Persistent volume toegevoegd voor user_data
- [ ] Build command werkt (Playwright geïnstalleerd)
- [ ] Worker start succesvol
- [ ] Eerste login voltooid
- [ ] Worker detecteert pending products
- [ ] Batch posting werkt
- [ ] Logs worden correct getoond

## 🆘 Hulp Nodig?

1. Check Railway logs voor errors
2. Verify alle environment variables
3. Test endpoints handmatig met curl
4. Check Vercel logs voor API errors
5. Railway docs: [docs.railway.app](https://docs.railway.app)

## 🔄 Updates Deployen

Railway deployt automatisch bij elke push naar GitHub:

```bash
git add .
git commit -m "Update worker"
git push
```

Railway detecteert de push en deployt automatisch!


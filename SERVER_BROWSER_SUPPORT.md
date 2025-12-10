# Browser Support voor Marktplaats Posting

## ❌ Werkt NIET (Serverless/Geen Browser)

Deze platforms kunnen **GEEN** browser draaien:
- **Vercel** (serverless) - ❌ Geen browser support
- **AWS Lambda** (serverless) - ❌ Geen browser support  
- **Netlify Functions** (serverless) - ❌ Geen browser support
- **Cloudflare Workers** (serverless) - ❌ Geen browser support

## ✅ Werkt WEL (Met Browser Support)

Deze platforms **KUNNEN** een browser draaien (met aanpassingen):

### 1. **Railway** (railway.app) ⭐ Aanbevolen
- ✅ Gratis tier beschikbaar
- ✅ Kan Playwright/Chromium draaien
- ✅ Eenvoudige deployment
- ⚠️ Moet headless mode gebruiken
- ⚠️ Moet dependencies installeren: `playwright install chromium`

### 2. **Render** (render.com)
- ✅ Gratis tier beschikbaar
- ✅ Kan Playwright/Chromium draaien
- ⚠️ Langzamer dan Railway
- ⚠️ Moet headless mode gebruiken

### 3. **DigitalOcean App Platform**
- ✅ Kan containers draaien met browser
- ⚠️ Betaald (vanaf $5/maand)
- ✅ Betrouwbaar en snel

### 4. **AWS EC2 / Lightsail**
- ✅ Volledige controle
- ✅ Kan alles draaien
- ⚠️ Betaald (vanaf ~$5/maand)
- ⚠️ Moet zelf beheren

### 5. **Google Cloud Run** (met container)
- ✅ Kan containers draaien
- ⚠️ Complexer opzetten
- ⚠️ Moet Docker image maken

### 6. **Eigen PC/Server**
- ✅ Volledige controle
- ✅ Gratis (als je PC aan staat)
- ✅ Kan headless of zichtbaar draaien
- ⚠️ Moet altijd aan staan

## 🔧 Aanpassingen Nodig voor Server Deployment

Het script gebruikt nu `headless=False`. Voor servers moet je dit aanpassen:

### Optie 1: Environment Variable (Aanbevolen)

Voeg toe aan `.env`:
```bash
PLAYWRIGHT_HEADLESS=true
```

En pas het script aan om dit te lezen:
```python
headless = os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true'
browser = await p.chromium.launch_persistent_context(
    user_data_dir=user_data_dir,
    headless=headless,  # Gebruik environment variable
    ...
)
```

### Optie 2: Command Line Argument

Voeg `--headless` flag toe aan het script.

### Optie 3: Automatisch Detecteren

Detecteer of we op een server zitten:
```python
import os
# Detecteer of we op een server zitten (geen DISPLAY)
is_server = not os.getenv('DISPLAY') and os.getenv('CI') or os.getenv('RAILWAY_ENVIRONMENT')
headless = is_server or os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true'
```

## 📋 Vereisten voor Server Deployment

1. **Playwright installeren**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

3. **Environment Variables**:
   ```bash
   NEXTAUTH_URL=https://jouw-app.vercel.app
   API_BASE_URL=https://jouw-app.vercel.app
   INTERNAL_API_KEY=jouw-api-key
   PLAYWRIGHT_HEADLESS=true
   MARKTPLAATS_BASE_URL=https://www.marktplaats.nl
   ```

4. **User Data Directory**:
   - Moet persistent zijn (voor login sessie)
   - Op servers: gebruik een volume/persistent storage
   - Op Railway: gebruik Railway volumes
   - Op Render: gebruik persistent disk

## 🚀 Railway Deployment (Stap-voor-stap)

1. **Maak account** op railway.app
2. **Nieuwe project** → "Deploy from GitHub repo"
3. **Voeg environment variables toe**:
   - `NEXTAUTH_URL`
   - `API_BASE_URL`
   - `INTERNAL_API_KEY`
   - `PLAYWRIGHT_HEADLESS=true`
4. **Voeg build command toe**:
   ```bash
   pip install -r requirements.txt && playwright install chromium
   ```
5. **Start command**:
   ```bash
   python scripts/post_all_pending.py
   ```
6. **Of gebruik een cron job** die het batch endpoint aanroept

## ⚠️ Belangrijke Opmerkingen

1. **Login Sessie**: 
   - Marktplaats login moet persistent zijn
   - Gebruik `launch_persistent_context` met een volume
   - Eerste keer: login handmatig, daarna blijft sessie bewaard

2. **Headless Mode**:
   - Werkt meestal goed
   - Soms detecteert Marktplaats automation
   - Gebruik `--disable-blink-features=AutomationControlled`

3. **Timeouts**:
   - Servers kunnen langzamer zijn
   - Verhoog timeouts indien nodig

4. **Resources**:
   - Chromium gebruikt veel RAM (~200-500MB)
   - Zorg voor voldoende memory op server

## 🎯 Aanbevolen Setup

**Voor productie:**
- **Railway** of **Render** (gratis tier)
- Headless mode
- Cron job die elke 5-10 minuten het batch endpoint aanroept
- Persistent volume voor user data

**Voor ontwikkeling:**
- Eigen PC
- Zichtbare browser (`headless=False`)
- Handmatig uitvoeren of via cron job


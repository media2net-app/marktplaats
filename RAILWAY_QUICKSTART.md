# Railway Quick Start 🚂

Snelle setup voor Railway deployment in 5 minuten!

## ⚡ Snelle Stappen

### 1. Railway Account
- Ga naar [railway.app](https://railway.app)
- Log in met GitHub

### 2. Nieuw Project
- Klik **"New Project"**
- Kies **"Deploy from GitHub repo"**
- Selecteer je `marktplaats` repository

### 3. Environment Variables
In Railway dashboard → je service → **Variables**:

```bash
API_BASE_URL=https://jouw-app.vercel.app
NEXTAUTH_URL=https://jouw-app.vercel.app
INTERNAL_API_KEY=jouw-api-key
PLAYWRIGHT_HEADLESS=true
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl
```

**Waar vind je INTERNAL_API_KEY?**
- Vercel dashboard → Project → Settings → Environment Variables
- Zoek `INTERNAL_API_KEY` en kopieer de waarde

### 4. Persistent Storage
- Service → Settings → Volumes
- Klik **"Add Volume"**
- Mount path: `/app/user_data`

### 5. Deploy!
Railway deployt automatisch. Check de **Logs** tab om te zien of het werkt.

## ✅ Testen

Na deployment, check de logs:
```bash
# In Railway dashboard → Logs tab
# Je zou moeten zien:
🚂 Railway Marktplaats Worker
API Base URL: https://...
Check Interval: 300 seconds
```

## 🔧 Eerste Login

De eerste keer moet je inloggen op Marktplaats. De worker probeert dit automatisch, maar als het faalt:

1. Check logs voor login instructies
2. Of maak een tijdelijke login service (zie RAILWAY_SETUP.md)

## 📊 Monitoring

- **Logs**: Service → Logs tab (real-time)
- **Metrics**: Service → Metrics tab (CPU, Memory)
- **Deployments**: Service → Deployments tab (geschiedenis)

## 🆘 Problemen?

1. **Worker start niet**: Check logs voor errors
2. **401 Unauthorized**: Verify INTERNAL_API_KEY is correct
3. **No browser**: Check of `playwright install chromium` in build command staat
4. **Login lost**: Check of volume is gemount op `/app/user_data`

## 📖 Volledige Documentatie

Zie `RAILWAY_SETUP.md` voor uitgebreide instructies.


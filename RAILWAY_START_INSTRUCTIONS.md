# Railway Start Instructies

## ✅ Wat ik heb gedaan

Ik heb de volgende configuratiebestanden aangemaakt zodat Railway automatisch het juiste script start:

1. **`railway.toml`** - Railway configuratie met start command
2. **`Procfile`** - Process definitie voor worker
3. **`nixpacks.toml`** - Build configuratie voor Python en Playwright

## 🚀 Railway Setup Stappen

### Stap 1: Push naar GitHub (als je Railway via GitHub verbindt)

Als je Railway via GitHub verbindt:
```bash
git add railway.toml Procfile nixpacks.toml scripts/railway_worker.py
git commit -m "Add Railway worker configuration"
git push
```

Railway zal automatisch detecteren dat er een nieuwe deployment is.

### Stap 2: Configureer Railway Service

1. **Ga naar Railway Dashboard** → Je Project → Je Service
2. **Settings** → **Deploy**
3. **Start Command**: Zorg dat dit is: `python scripts/railway_worker.py`
   - Als het leeg is, wordt `railway.toml` gebruikt
   - Als het anders is, pas het aan naar: `python scripts/railway_worker.py`

### Stap 3: Verifieer Environment Variables

Zorg dat deze zijn ingesteld in Railway (Shared Variables of Service Variables):

```env
NEXTAUTH_URL=https://marktplaats-eight.vercel.app
API_BASE_URL=https://marktplaats-eight.vercel.app
INTERNAL_API_KEY=LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl
DATABASE_URL=prisma+postgres://...
HEADLESS=true
USER_DATA_DIR=/app/user_data
MEDIA_ROOT=/app/public/media
CHECK_INTERVAL=300
```

### Stap 4: Deploy/Redeploy

1. **Automatisch**: Als je via GitHub verbindt, deployt Railway automatisch na push
2. **Handmatig**: Klik op **Deploy** of **Redeploy** in Railway dashboard

### Stap 5: Check Logs

Na deployment, check Railway logs. Je zou moeten zien:

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
No pending products. Waiting 300 seconds...
```

## 🔍 Troubleshooting

### "Module not found" errors
- Zorg dat `requirements.txt` alle dependencies bevat
- Railway installeert automatisch via `pip install -r requirements.txt`

### "Playwright browser not found"
- Railway installeert automatisch via `nixpacks.toml`
- Als het niet werkt, check of `python -m playwright install chromium` wordt uitgevoerd

### "401 Unauthorized"
- Controleer of `INTERNAL_API_KEY` exact hetzelfde is in Railway en Vercel
- Check of de API key correct wordt meegestuurd in logs

### Service stopt direct
- Check Railway logs voor error messages
- Zorg dat `railway_worker.py` executable is (al gedaan: `chmod +x`)
- Check of alle dependencies geïnstalleerd zijn

## 📋 Verificatie Checklist

- [ ] `railway.toml` bestaat en heeft correcte start command
- [ ] `Procfile` bestaat met worker definitie
- [ ] `nixpacks.toml` bestaat met build configuratie
- [ ] `scripts/railway_worker.py` bestaat en is executable
- [ ] Environment variables zijn ingesteld in Railway
- [ ] Start Command in Railway is: `python scripts/railway_worker.py`
- [ ] Service is gedeployed
- [ ] Logs tonen geen errors
- [ ] Logs tonen: `Checking pending products at: .../api/products/pending`
- [ ] Logs tonen: `Response status: 200`

## 🎯 Als het werkt

Je zou nu moeten zien dat:
- ✅ Railway worker draait continu
- ✅ Elke 5 minuten checkt voor pending producten
- ✅ Automatisch producten plaatst op Marktplaats wanneer er pending zijn
- ✅ Geen 401 errors meer
- ✅ Logs tonen correct endpoint: `/api/products/pending`

## 💡 Tips

1. **Monitor logs regelmatig** om te zien of alles werkt
2. **Test met één pending product** eerst voordat je bulk processing doet
3. **Check Railway dashboard** voor resource usage (CPU, memory)
4. **Zet CHECK_INTERVAL hoger** (bijv. 600) als je minder vaak wilt checken

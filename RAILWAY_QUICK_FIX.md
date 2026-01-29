# Railway Quick Fix

## ✅ Wat je al goed hebt gedaan

Je hebt alle environment variables correct ingesteld in Railway:
- ✅ `API_BASE_URL`: `https://marktplaats-eight.vercel.app/`
- ✅ `INTERNAL_API_KEY`: `LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=`
- ✅ `NEXTAUTH_URL`: `https://marktplaats-eight.vercel.app/`
- ✅ `MARKTPLAATS_BASE_URL`: `https://www.marktplaats.nl`
- ✅ `DATABASE_URL`: Prisma Accelerate URL

**De API key werkt!** (getest en geeft geen 401 error meer)

## ❌ Wat nog moet worden aangepast

Het probleem is dat je Railway worker waarschijnlijk nog het **oude script** gebruikt dat:
- ❌ Het verkeerde endpoint gebruikt: `/api/products/batch-post`
- ❌ Alleen status counts teruggeeft, geen producten

## 🔧 Oplossing

### Stap 1: Check je Railway Start Command

Ga naar je Railway service → **Settings** → **Deploy** en check de **Start Command**.

**Verkeerd (oud):**
```
python scripts/[oud_script].py
```

**Goed (nieuw):**
```
python scripts/railway_worker.py
```

### Stap 2: Update Start Command

Als je nog het oude script gebruikt:
1. Ga naar Railway → Je Service → Settings → Deploy
2. Verander **Start Command** naar: `python scripts/railway_worker.py`
3. Klik op **Save**
4. Railway zal automatisch redeployen

### Stap 3: Verifieer in Logs

Na de redeploy, check je Railway logs. Je zou moeten zien:

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

**Belangrijk**: Je moet zien:
- ✅ `Checking pending products at: .../api/products/pending` (NIET batch-post!)
- ✅ `Response status: 200` (NIET 401!)

## 📋 Checklist

- [ ] Start Command in Railway is: `python scripts/railway_worker.py`
- [ ] Railway service is gereployed na aanpassing
- [ ] Logs tonen: `Checking pending products at: .../api/products/pending`
- [ ] Logs tonen: `Response status: 200`
- [ ] Geen 401 errors meer

## 🎯 Als het nog niet werkt

1. **Check of `railway_worker.py` bestaat** in je Railway repository
2. **Check Railway logs** voor import errors
3. **Verifieer dat `INTERNAL_API_KEY` in Vercel exact hetzelfde is** als in Railway
4. **Restart Railway service** na aanpassingen

## 💡 Alternatief

Als je het oude script wilt blijven gebruiken, moet je het aanpassen om:
- `/api/products/pending` te gebruiken in plaats van `/api/products/batch-post`
- De API key correct mee te sturen

Maar het is makkelijker om gewoon `railway_worker.py` te gebruiken! 🚀

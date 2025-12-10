# Railway Worker Troubleshooting

## 🔍 Probleem: Alleen "Starting Container" en "Stopping Container" logs

Als je alleen container start/stop logs ziet, betekent dit dat de worker script crasht direct na start.

## ✅ Stap 1: Check Environment Variables

Ga naar Railway → Service → Variables en check of deze zijn ingesteld:

### Verplicht:
- `INTERNAL_API_KEY` - Moet overeenkomen met Vercel INTERNAL_API_KEY
- `API_BASE_URL` - Je Vercel production URL (bijv. `https://marktplaats-xxx.vercel.app`)
- `NEXTAUTH_URL` - Zelfde als API_BASE_URL

### Optioneel:
- `CHECK_INTERVAL` - Standaard 300 (5 minuten)
- `PLAYWRIGHT_HEADLESS` - Standaard `true`
- `MARKTPLAATS_BASE_URL` - Standaard `https://www.marktplaats.nl`

## ✅ Stap 2: Check Logs voor Errors

1. Ga naar Railway → Service → Logs
2. Scroll naar beneden
3. Zoek naar:
   - `❌ ERROR` - Foutmeldingen
   - `Failed to import` - Import errors
   - `INTERNAL_API_KEY not set` - Missing API key

## ✅ Stap 3: Test Import

De worker moet deze modules kunnen importeren:
- `post_ads` - Het hoofdscript
- `playwright` - Browser automation
- `requests` - HTTP requests

Als er import errors zijn, check of alle dependencies zijn geïnstalleerd.

## ✅ Stap 4: Check Service Status

1. Ga naar Railway → Service → Settings
2. Check "Status" - Moet "Active" zijn
3. Check "Restart Policy" - Moet "ON_FAILURE" zijn met max retries

## ✅ Stap 5: Handmatig Testen

Je kunt de worker handmatig testen door:

1. **Redeploy** de service
2. **Watch logs** in real-time
3. **Check** of je deze logs ziet:
   ```
   ======================================================================
   🚂 Railway Marktplaats Worker
   ======================================================================
   API Base URL: https://...
   Check Interval: 300 seconds (5 minutes)
   INTERNAL_API_KEY: ✅ Set
   ======================================================================
   ```

## 🚨 Veelvoorkomende Problemen

### 1. INTERNAL_API_KEY niet ingesteld
**Symptoom**: Service crasht direct, geen logs
**Oplossing**: Voeg `INTERNAL_API_KEY` toe in Railway Variables

### 2. API_BASE_URL verkeerd
**Symptoom**: Connection errors in logs
**Oplossing**: Zet naar je Vercel production URL (niet localhost!)

### 3. Import errors
**Symptoom**: `Failed to import post_ads` in logs
**Oplossing**: Check of alle dependencies in `requirements.txt` staan

### 4. Playwright niet geïnstalleerd
**Symptoom**: `playwright` import error
**Oplossing**: Check Dockerfile - `playwright install chromium` moet uitgevoerd zijn

### 5. Service restart loop
**Symptoom**: Service start en stopt continu
**Oplossing**: Check logs voor de exacte error, meestal missing env var

## 📊 Verwachte Logs

Na een succesvolle start zou je moeten zien:

```
======================================================================
🚂 Railway Marktplaats Worker
======================================================================
API Base URL: https://marktplaats-xxx.vercel.app
Check Interval: 300 seconds (5 minutes)
INTERNAL_API_KEY: ✅ Set
======================================================================

✅ Successfully imported post_ads module
[2024-XX-XX XX:XX:XX] No pending products. Waiting 300 seconds...
```

## 🔧 Debug Commands

Als je toegang hebt tot Railway CLI:

```bash
railway logs --service marktplaats
railway variables --service marktplaats
railway status
```

## 💡 Tips

1. **Wacht even**: Na deploy kan het 1-2 minuten duren voordat logs verschijnen
2. **Refresh logs**: Klik op refresh in Railway logs viewer
3. **Check alle tabs**: Soms staan errors in "Attributes" of "Raw Data" tab
4. **Redeploy**: Soms helpt een fresh deploy

## 🆘 Nog steeds problemen?

1. **Check Railway status page**: https://status.railway.app
2. **Check Vercel status**: Zorg dat je API endpoints werken
3. **Test API handmatig**: 
   ```bash
   curl -X GET "https://jouw-app.vercel.app/api/products/batch-post" \
     -H "x-api-key: jouw-api-key"
   ```


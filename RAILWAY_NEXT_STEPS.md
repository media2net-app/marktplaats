# Railway Next Steps - Marktplaats Posting Activeren

Railway is nu online! Volg deze stappen om producten naar Marktplaats te kunnen posten:

## ✅ Stap 1: Environment Variables Instellen

Ga naar Railway dashboard → je service → **Variables** tab en voeg toe:

### Verplichte Variables:

```bash
# API Configuration (Vervang met jouw echte waarden!)
API_BASE_URL=https://jouw-app.vercel.app
NEXTAUTH_URL=https://jouw-app.vercel.app
INTERNAL_API_KEY=jouw-api-key-hier

# Playwright Configuration
PLAYWRIGHT_HEADLESS=true

# Marktplaats Configuration
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl

# Worker Configuration (optioneel)
CHECK_INTERVAL=300  # Check elke 5 minuten (300 seconden)
USER_DATA_DIR=/app/user_data
```

### Waar vind je deze waarden?

1. **API_BASE_URL / NEXTAUTH_URL**: 
   - Je Vercel app URL (bijv. `https://marktplaats-eight.vercel.app`)

2. **INTERNAL_API_KEY**:
   - Ga naar Vercel dashboard → je project
   - Settings → Environment Variables
   - Zoek `INTERNAL_API_KEY` en kopieer de waarde

## ✅ Stap 2: Persistent Volume Toevoegen

Voor de Marktplaats login sessie (belangrijk!):

1. Railway dashboard → je service
2. Ga naar **Settings** tab
3. Scroll naar **"Volumes"** sectie
4. Klik **"Add Volume"**
5. **Mount Path**: `/app/user_data`
6. **Size**: 1GB is genoeg
7. Klik **"Add"**

Dit bewaart je login sessie tussen restarts!

## ✅ Stap 3: Service Herstarten

Na het instellen van environment variables:

1. Ga naar **Deployments** tab
2. Klik op de meest recente deployment
3. Klik **"Redeploy"** (of wacht tot Railway automatisch redeployt)

## ✅ Stap 4: Eerste Login Opzetten

De eerste keer moet je inloggen op Marktplaats. Er zijn 2 opties:

### Optie A: Automatisch (Aanbevolen)

De worker probeert automatisch in te loggen. Check de logs:

1. Railway dashboard → je service → **Logs** tab
2. Zoek naar login gerelateerde berichten
3. Als er een login prompt is, volg de instructies

### Optie B: Handmatig via Login Script

Als automatisch niet werkt, maak een tijdelijke login service:

1. Maak een nieuwe service in Railway
2. **Start Command**: `python scripts/post_ads.py --login`
3. Run deze service eenmalig
4. Login handmatig in de browser (als headless=False)
5. Stop de service na login

## ✅ Stap 5: Testen

### Test 1: Check Worker Status

In Railway Logs, je zou moeten zien:
```
🚂 Railway Marktplaats Worker
API Base URL: https://...
Check Interval: 300 seconds
INTERNAL_API_KEY: ✅ Set
```

### Test 2: Check Pending Products

1. Maak een test product in je Vercel app (status: pending)
2. Wacht 5 minuten (of pas CHECK_INTERVAL aan naar 60 seconden voor testen)
3. Check Railway Logs voor:
   ```
   Found X pending product(s)
   Starting batch post...
   ```

### Test 3: Test Batch Endpoint Handmatig

```bash
curl -X POST "https://jouw-app.vercel.app/api/products/batch-post" \
  -H "x-api-key: jouw-api-key"
```

## ✅ Stap 6: Monitoring

### Railway Logs

- **Real-time logs**: Service → Logs tab
- **Filter**: Zoek naar "pending", "posting", "error"
- **Success**: Zoek naar "✅ Batch posting completed"

### Vercel Dashboard

- Check of producten status veranderen van `pending` → `processing` → `completed`
- Check `marktplaatsUrl` en `marktplaatsAdId` velden

## 🔧 Troubleshooting

### Worker start niet:

1. Check **Logs** voor error messages
2. Verify alle environment variables zijn ingesteld
3. Check of `INTERNAL_API_KEY` correct is

### "401 Unauthorized":

- Check of `INTERNAL_API_KEY` in Railway hetzelfde is als in Vercel
- Verify `API_BASE_URL` wijst naar je Vercel app
- Check Vercel logs voor API errors

### "No pending products":

- Maak een test product in Vercel app
- Check of status `pending` is
- Verify product heeft alle verplichte velden

### Login sessie verloren:

- Check of volume is gemount op `/app/user_data`
- Verify `USER_DATA_DIR` environment variable
- Mogelijk moet je opnieuw inloggen

### Browser errors:

- Check logs voor Playwright errors
- Verify alle dependencies zijn geïnstalleerd
- Check of `PLAYWRIGHT_HEADLESS=true` is ingesteld

## 📊 Optimalisatie

### Check Interval Aanpassen:

Voor snellere tests:
```bash
CHECK_INTERVAL=60  # Elke minuut
```

Voor productie:
```bash
CHECK_INTERVAL=300  # Elke 5 minuten (standaard)
```

### Resource Monitoring:

- Railway dashboard → **Metrics** tab
- Monitor CPU, Memory, Network usage
- Upgrade plan als nodig (Hobby $5/maand)

## ✅ Checklist

- [ ] Environment variables ingesteld (API_BASE_URL, INTERNAL_API_KEY, etc.)
- [ ] Persistent volume toegevoegd (`/app/user_data`)
- [ ] Service geredeployed
- [ ] Worker start succesvol (check logs)
- [ ] Eerste login voltooid
- [ ] Test product gemaakt (status: pending)
- [ ] Worker detecteert pending products
- [ ] Batch posting werkt
- [ ] Product succesvol geplaatst op Marktplaats

## 🎯 Snelle Test

1. **Maak een test product** in Vercel app:
   - Titel: "Test Product"
   - Status: pending
   - Alle verplichte velden ingevuld

2. **Wacht 5 minuten** (of pas CHECK_INTERVAL aan)

3. **Check Railway Logs**:
   - Zoek naar "Found 1 pending product(s)"
   - Zoek naar "Starting batch post..."
   - Zoek naar "✅ Batch posting completed"

4. **Check Vercel Dashboard**:
   - Product status moet `completed` zijn
   - `marktplaatsUrl` moet gevuld zijn

## 🆘 Hulp Nodig?

1. Check Railway logs voor specifieke errors
2. Check Vercel logs voor API errors
3. Verify alle environment variables
4. Test endpoints handmatig met curl
5. Check `RAILWAY_SETUP.md` voor uitgebreide documentatie

## 🚀 Je bent klaar!

Als alles werkt, post de worker automatisch alle pending producten elke 5 minuten (of zoals ingesteld in CHECK_INTERVAL).


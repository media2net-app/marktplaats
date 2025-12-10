# Railway Logs in App - Setup Guide

De app kan nu Railway logs tonen! Volg deze stappen om het in te stellen:

## 📋 Stap 1: Railway API Token Aanmaken

1. Ga naar [railway.app](https://railway.app)
2. Klik op je **profiel** (rechtsboven)
3. Ga naar **"Settings"** → **"Tokens"**
4. Klik **"New Token"**
5. Geef een naam (bijv. "Marktplaats App")
6. Klik **"Create"**
7. **Kopieer de token** (je ziet hem maar 1x!)

## 📋 Stap 2: Project ID en Service ID Vinden

### Project ID:

1. Ga naar je Railway project
2. Klik op **"Settings"** (project settings, niet service settings)
3. Scroll naar **"General"**
4. **Project ID** staat daar (bijv. `abc123-def456-...`)

### Service ID:

1. Ga naar je service (de worker service)
2. Klik op **"Settings"** (service settings)
3. Scroll naar **"General"**
4. **Service ID** staat daar (bijv. `xyz789-uvw012-...`)

**Of via URL:**
- Project ID: `https://railway.app/project/{PROJECT_ID}`
- Service ID: `https://railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`

## 📋 Stap 3: Environment Variables Instellen in Vercel

1. Ga naar **Vercel dashboard**
2. Selecteer je project
3. Ga naar **Settings** → **Environment Variables**
4. Voeg toe:

```bash
RAILWAY_API_TOKEN=je-token-hier
RAILWAY_PROJECT_ID=je-project-id-hier
RAILWAY_SERVICE_ID=je-service-id-hier
```

5. Klik **"Save"**
6. **Redeploy** je app (of wacht tot automatische deploy)

## ✅ Stap 4: Testen

1. Ga naar je app
2. Klik op **"Railway Logs"** in de sidebar
3. Je zou nu de logs moeten zien!

## 🔧 Troubleshooting

### "Railway API not configured"

- Check of alle 3 environment variables zijn ingesteld
- Verify de waarden zijn correct gekopieerd (geen extra spaties)
- Redeploy de app na het toevoegen van variables

### "Failed to fetch logs from Railway"

- Check of `RAILWAY_API_TOKEN` correct is
- Verify `RAILWAY_PROJECT_ID` en `RAILWAY_SERVICE_ID` kloppen
- Check Railway dashboard of de service draait

### "Unauthorized"

- Check of je ingelogd bent in de app
- Verify je session is geldig

### Geen logs zichtbaar

- Check of de Railway service draait
- Verify er zijn daadwerkelijk logs (check Railway dashboard)
- Wacht even en klik "Verversen"

## 📊 Features

- **Real-time logs**: Auto-refresh elke 5 seconden
- **Kleurcodering**: Errors (rood), warnings (geel), info (blauw)
- **Timestamps**: Nederlandse datum/tijd format
- **Scroll naar beneden**: Automatisch scroll naar nieuwste logs
- **Handmatig verversen**: Klik op "Verversen" knop

## 🔒 Security

- Railway API token is **gevoelige informatie**
- Bewaar het veilig
- Deel het niet publiekelijk
- Als token gelekt is, maak een nieuwe aan en verwijder de oude

## 💡 Tips

- **Auto-refresh uitzetten**: Als je logs niet nodig hebt, zet auto-refresh uit om resources te besparen
- **Filter logs**: Gebruik browser search (Ctrl+F / Cmd+F) om te zoeken in logs
- **Logs exporteren**: Gebruik Railway dashboard voor volledige log export

## 🆘 Hulp Nodig?

1. Check Railway dashboard → Logs tab (werkt het daar?)
2. Verify environment variables in Vercel
3. Check browser console voor errors
4. Test de API endpoint handmatig:
   ```bash
   curl -X GET "https://jouw-app.vercel.app/api/railway/logs" \
     -H "Cookie: next-auth.session-token=..."
   ```


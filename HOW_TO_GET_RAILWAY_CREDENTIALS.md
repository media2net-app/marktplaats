# Hoe Railway API Credentials Krijgen - Stap voor Stap

## 🔑 Stap 1: Railway API Token Aanmaken

1. **Ga naar Railway**: [railway.app](https://railway.app) en log in
2. **Klik op je profiel** (rechtsboven, je avatar/naam)
3. **Ga naar "Settings"** in het dropdown menu
4. **Klik op "Tokens"** tab (links in het menu)
5. **Klik "New Token"** knop
6. **Geef een naam** (bijv. "Marktplaats App Logs")
7. **Klik "Create"**
8. **⚠️ BELANGRIJK: Kopieer de token NU** - je ziet hem maar 1x!
   - De token ziet eruit als: `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 📋 Stap 2: Project ID Vinden

### Methode A: Via Project Settings

1. **Ga naar je Railway project** (de "marktplaats" project)
2. **Klik op "Settings"** (project settings, niet service settings)
   - Dit is de settings van het hele project, niet van een individuele service
3. **Scroll naar "General"** sectie
4. **Zoek "Project ID"**
   - Ziet eruit als: `abc123-def456-ghi789` of een UUID

### Methode B: Via URL

1. **Ga naar je project** in Railway
2. **Kijk naar de URL** in je browser
3. De URL ziet eruit als: `https://railway.app/project/{PROJECT_ID}`
4. **Kopieer het PROJECT_ID** deel uit de URL

## 🔧 Stap 3: Service ID Vinden

### Methode A: Via Service Settings

1. **Ga naar je service** (de worker service die je hebt gemaakt)
2. **Klik op "Settings"** (service settings, niet project settings)
3. **Scroll naar "General"** sectie
4. **Zoek "Service ID"**
   - Ziet eruit als: `xyz789-uvw012-rst345` of een UUID

### Methode B: Via URL

1. **Ga naar je service** in Railway
2. **Kijk naar de URL** in je browser
3. De URL ziet eruit als: `https://railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`
4. **Kopieer het SERVICE_ID** deel uit de URL

### Methode C: Via Service List

1. **Ga naar je project** in Railway
2. **Klik op je service** (de worker service)
3. **In de URL** zie je: `/service/{SERVICE_ID}`
4. **Kopieer de SERVICE_ID**

## ⚙️ Stap 4: Environment Variables Instellen in Vercel

1. **Ga naar Vercel Dashboard**: [vercel.com](https://vercel.com)
2. **Selecteer je project** (marktplaats)
3. **Klik op "Settings"** (bovenaan)
4. **Klik op "Environment Variables"** (links in het menu)
5. **Voeg 3 nieuwe variables toe**:

### Variable 1: RAILWAY_API_TOKEN
- **Name**: `RAILWAY_API_TOKEN`
- **Value**: Plak de token die je in Stap 1 hebt gekopieerd
- **Environment**: Selecteer alle (Production, Preview, Development)
- **Klik "Save"**

### Variable 2: RAILWAY_PROJECT_ID
- **Name**: `RAILWAY_PROJECT_ID`
- **Value**: Plak het Project ID dat je in Stap 2 hebt gevonden
- **Environment**: Selecteer alle (Production, Preview, Development)
- **Klik "Save"**

### Variable 3: RAILWAY_SERVICE_ID
- **Name**: `RAILWAY_SERVICE_ID`
- **Value**: Plak het Service ID dat je in Stap 3 hebt gevonden
- **Environment**: Selecteer alle (Production, Preview, Development)
- **Klik "Save"**

## 🔄 Stap 5: Redeploy

Na het toevoegen van de environment variables:

1. **Ga naar "Deployments"** tab in Vercel
2. **Klik op de meest recente deployment**
3. **Klik op "Redeploy"** (of wacht tot automatische redeploy)
4. **Wacht tot deployment klaar is**

## ✅ Stap 6: Testen

1. **Ga naar je app**: `https://jouw-app.vercel.app`
2. **Log in**
3. **Klik op "Railway Logs"** in de sidebar
4. **Je zou nu de logs moeten zien!**

## 🔍 Troubleshooting

### "Railway API not configured" error blijft

1. **Check of alle 3 variables zijn ingesteld**:
   - RAILWAY_API_TOKEN
   - RAILWAY_PROJECT_ID
   - RAILWAY_SERVICE_ID

2. **Check of je de juiste environment hebt geselecteerd**:
   - Voor production: selecteer "Production"
   - Of selecteer "All" om overal te gebruiken

3. **Redeploy na het toevoegen**:
   - Environment variables worden alleen geladen bij build time
   - Je moet redeployen na het toevoegen

4. **Check of de waarden correct zijn**:
   - Geen extra spaties voor/na de waarden
   - Geen quotes nodig (Vercel voegt die automatisch toe)
   - Token begint met `railway_`

### "Failed to fetch logs" error

1. **Check of Railway API token geldig is**:
   - Ga naar Railway → Settings → Tokens
   - Check of de token nog bestaat
   - Maak een nieuwe aan als nodig

2. **Check of Project ID en Service ID kloppen**:
   - Verify in Railway dashboard
   - Check of de service nog bestaat

3. **Check Railway logs**:
   - Ga naar Railway dashboard
   - Check of de service draait
   - Check of er logs zijn

### Geen logs zichtbaar

1. **Check of de Railway service draait**
2. **Check of er daadwerkelijk logs zijn** (in Railway dashboard)
3. **Wacht even en klik "Verversen"**
4. **Check browser console** voor errors

## 📸 Screenshot Locaties

### Railway API Token:
- Railway Dashboard → Profiel (rechtsboven) → Settings → Tokens

### Project ID:
- Railway Dashboard → Project → Settings → General → Project ID
- Of in URL: `/project/{PROJECT_ID}`

### Service ID:
- Railway Dashboard → Project → Service → Settings → General → Service ID
- Of in URL: `/project/{PROJECT_ID}/service/{SERVICE_ID}`

## 💡 Tips

- **Bewaar de credentials veilig**: De API token geeft toegang tot je Railway project
- **Gebruik verschillende tokens**: Maak een aparte token voor de app (niet je persoonlijke token)
- **Test eerst lokaal**: Voeg de variables toe aan `.env.local` voor lokale testing
- **Check permissions**: Zorg dat de token de juiste permissions heeft

## 🆘 Nog steeds problemen?

1. **Check Vercel logs**: Ga naar Vercel → Project → Deployments → Klik op deployment → Logs
2. **Check browser console**: Open Developer Tools (F12) → Console tab
3. **Test API endpoint handmatig**: 
   ```bash
   curl -X GET "https://jouw-app.vercel.app/api/railway/logs" \
     -H "Cookie: next-auth.session-token=..."
   ```


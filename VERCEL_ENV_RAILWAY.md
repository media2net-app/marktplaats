# Vercel Environment Variables - Railway Logs

## ✅ Credentials die je hebt:

- **RAILWAY_API_TOKEN**: `195af680-b076-4c50-81e7-4938ae49139d`
- **RAILWAY_PROJECT_ID**: `d7cf2713-0d81-4820-b62f-cd732285675c`
- **RAILWAY_SERVICE_ID**: ⚠️ **Nog nodig!** (zie hieronder)

## 📋 Stap 1: Service ID Vinden

Je hebt nog een **Service ID** nodig. Dit is de ID van je worker service in Railway:

1. **Ga naar Railway**: [railway.app](https://railway.app)
2. **Ga naar je project** (marktplaats)
3. **Klik op je service** (de worker service die je hebt gemaakt)
4. **Klik op "Settings"** (service settings, niet project settings)
5. **Scroll naar "General"**
6. **Zoek "Service ID"** en kopieer het

**Of via URL:**
- Ga naar je service in Railway
- Kijk naar de URL: `https://railway.app/project/d7cf2713-0d81-4820-b62f-cd732285675c/service/{SERVICE_ID}`
- Het SERVICE_ID deel is wat je nodig hebt

## 📋 Stap 2: Environment Variables Toevoegen in Vercel

1. **Ga naar Vercel Dashboard**: [vercel.com](https://vercel.com)
2. **Selecteer je project** (marktplaats)
3. **Klik "Settings"** (bovenaan)
4. **Klik "Environment Variables"** (links in menu)

### Variable 1: RAILWAY_API_TOKEN
- **Name**: `RAILWAY_API_TOKEN`
- **Value**: `195af680-b076-4c50-81e7-4938ae49139d`
- **Environment**: ✅ Production, ✅ Preview, ✅ Development
- **Klik "Save"**

### Variable 2: RAILWAY_PROJECT_ID
- **Name**: `RAILWAY_PROJECT_ID`
- **Value**: `d7cf2713-0d81-4820-b62f-cd732285675c`
- **Environment**: ✅ Production, ✅ Preview, ✅ Development
- **Klik "Save"**

### Variable 3: RAILWAY_SERVICE_ID
- **Name**: `RAILWAY_SERVICE_ID`
- **Value**: `{PLAK_HIER_JOUW_SERVICE_ID}`
- **Environment**: ✅ Production, ✅ Preview, ✅ Development
- **Klik "Save"**

## 🔄 Stap 3: Redeploy

Na het toevoegen van alle 3 variables:

1. **Ga naar "Deployments"** tab
2. **Klik op de meest recente deployment**
3. **Klik "Redeploy"**
4. **Wacht tot deployment klaar is**

## ✅ Stap 4: Testen

1. **Ga naar je app**: `https://jouw-app.vercel.app`
2. **Log in**
3. **Klik "Railway Logs"** in de sidebar
4. **Je zou nu de logs moeten zien!**

## 🔍 Service ID Snel Vinden

Als je niet zeker weet welke service:

1. **Ga naar Railway project**
2. **Kijk naar alle services** in je project
3. **Zoek de service** die de worker draait (meestal de enige Python service)
4. **Klik erop** → Settings → General → Service ID

## 💡 Tip

Als je meerdere services hebt, de Service ID is meestal de service die:
- Python gebruikt
- Het `railway_worker.py` script draait
- "Worker" of "Marktplaats" in de naam heeft


# Vercel Environment Variables - Complete Setup

## ✅ Alle Credentials:

- **RAILWAY_API_TOKEN**: `195af680-b076-4c50-81e7-4938ae49139d`
- **RAILWAY_PROJECT_ID**: `d7cf2713-0d81-4820-b62f-cd732285675c`
- **RAILWAY_SERVICE_ID**: `784bc95a-e824-4d0c-b69e-7eddb39143d9` ✅

## 📋 Stap-voor-Stap: Environment Variables Toevoegen in Vercel

1. **Ga naar Vercel Dashboard**: [vercel.com](https://vercel.com)
2. **Selecteer je project** (marktplaats)
3. **Klik "Settings"** (bovenaan de pagina)
4. **Klik "Environment Variables"** (links in het menu)

### Variable 1: RAILWAY_API_TOKEN

- **Name**: `RAILWAY_API_TOKEN`
- **Value**: `195af680-b076-4c50-81e7-4938ae49139d`
- **Environment**: 
  - ✅ Production
  - ✅ Preview  
  - ✅ Development
- **Klik "Save"**

### Variable 2: RAILWAY_PROJECT_ID

- **Name**: `RAILWAY_PROJECT_ID`
- **Value**: `d7cf2713-0d81-4820-b62f-cd732285675c`
- **Environment**: 
  - ✅ Production
  - ✅ Preview
  - ✅ Development
- **Klik "Save"**

### Variable 3: RAILWAY_SERVICE_ID

- **Name**: `RAILWAY_SERVICE_ID`
- **Value**: `784bc95a-e824-4d0c-b69e-7eddb39143d9`
- **Environment**: 
  - ✅ Production
  - ✅ Preview
  - ✅ Development
- **Klik "Save"**

## 🔄 Stap 2: Redeploy

Na het toevoegen van alle 3 variables:

1. **Ga naar "Deployments"** tab (bovenaan)
2. **Klik op de meest recente deployment**
3. **Klik "Redeploy"** (of wacht tot automatische redeploy)
4. **Wacht tot deployment klaar is** (ongeveer 1-2 minuten)

## ✅ Stap 3: Testen

1. **Ga naar je app**: `https://jouw-app.vercel.app`
2. **Log in**
3. **Klik "Railway Logs"** in de sidebar
4. **Je zou nu de logs moeten zien!** 🎉

## 🔍 Verificatie

Na redeploy, check:

1. **Railway Logs pagina** toont logs (geen error meer)
2. **Auto-refresh** werkt (elke 5 seconden)
3. **Logs worden getoond** met timestamps en kleuren

## 🆘 Als het nog niet werkt:

1. **Check Vercel Environment Variables**:
   - Ga naar Settings → Environment Variables
   - Verify alle 3 variables zijn ingesteld
   - Check of ze voor alle environments zijn ingesteld

2. **Check Deployment**:
   - Ga naar Deployments tab
   - Check of de laatste deployment succesvol was
   - Check deployment logs voor errors

3. **Test API endpoint**:
   ```bash
   curl -X GET "https://jouw-app.vercel.app/api/railway/logs" \
     -H "Cookie: next-auth.session-token=..."
   ```

4. **Check Browser Console**:
   - Open Developer Tools (F12)
   - Ga naar Console tab
   - Kijk voor errors

## ✅ Checklist

- [ ] RAILWAY_API_TOKEN toegevoegd in Vercel
- [ ] RAILWAY_PROJECT_ID toegevoegd in Vercel
- [ ] RAILWAY_SERVICE_ID toegevoegd in Vercel
- [ ] Alle variables ingesteld voor Production, Preview, Development
- [ ] App geredeployed
- [ ] Railway Logs pagina getest
- [ ] Logs worden getoond

## 🎯 Je bent klaar!

Na het instellen van deze 3 variables en redeploy, zou de Railway Logs pagina moeten werken!


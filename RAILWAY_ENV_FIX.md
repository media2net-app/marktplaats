# Railway Environment Variables Fix

## Probleem
De logs pagina geeft een 404 error: "Railway project or service not found"

Dit betekent dat de `RAILWAY_PROJECT_ID` of `RAILWAY_SERVICE_ID` niet correct zijn ingesteld in Vercel.

## Oplossing

### Stap 1: Check Vercel Environment Variables

1. Ga naar Vercel Dashboard: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats**
3. Ga naar **Settings** → **Environment Variables**
4. Check of deze 3 variabelen zijn ingesteld:
   - `RAILWAY_API_TOKEN`
   - `RAILWAY_PROJECT_ID`
   - `RAILWAY_SERVICE_ID`

### Stap 2: Verifieer de Waarden

#### RAILWAY_API_TOKEN
- Ga naar Railway → Account Settings → Tokens
- Maak een nieuwe "Account Token" als je er geen hebt
- Kopieer de token en plak in Vercel

#### RAILWAY_PROJECT_ID
- Ga naar Railway → Je Project
- De Project ID staat in de URL: `https://railway.app/project/{PROJECT_ID}`
- Of ga naar Project Settings → General → Project ID
- Kopieer de volledige UUID (bijv. `d7cf2713-0d81-4820-b62f-cd732285675c`)

#### RAILWAY_SERVICE_ID
- Ga naar Railway → Je Project → Je Service (de worker)
- De Service ID staat in de URL: `https://railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`
- Of ga naar Service Settings → General → Service ID
- Kopieer de volledige UUID (bijv. `784bc95a-e824-4d0c-b69e-7eddb39143d9`)

### Stap 3: Update Vercel Environment Variables

1. In Vercel → Settings → Environment Variables
2. Voor elke variabele:
   - Check of de waarde correct is (volledige UUID, geen extra spaties)
   - Als de waarde verkeerd is, klik op de variabele → Edit → Update
   - Zorg dat "Production" is aangevinkt
3. **BELANGRIJK**: Na het updaten van environment variables:
   - Ga naar **Deployments**
   - Klik op de 3 dots (⋯) van de laatste deployment
   - Kies **Redeploy**
   - Dit zorgt dat de nieuwe environment variables worden geladen

### Stap 4: Test

1. Wacht tot de redeploy klaar is (1-2 minuten)
2. Ga naar https://marktplaats-eight.vercel.app/logs
3. Check of de logs nu worden getoond

## Veelvoorkomende Fouten

### Fout 1: Verkeerde Project ID
- **Symptoom**: 404 error
- **Oplossing**: Check of de Project ID exact overeenkomt met Railway

### Fout 2: Verkeerde Service ID
- **Symptoom**: 404 error
- **Oplossing**: Check of de Service ID exact overeenkomt met je Railway service

### Fout 3: Verlopen API Token
- **Symptoom**: 401 error
- **Oplossing**: Genereer een nieuwe Account Token in Railway

### Fout 4: Environment Variables niet geladen
- **Symptoom**: "Railway API not configured"
- **Oplossing**: Redeploy de applicatie na het toevoegen/updaten van environment variables

## Debug Tips

1. **Check Vercel Logs**:
   - Ga naar Vercel → Je Project → Logs
   - Zoek naar "[RAILWAY LOGS]" logs
   - Deze tonen welke environment variables zijn gevonden

2. **Check Browser Console**:
   - Open Developer Tools (F12)
   - Ga naar Console tab
   - Zoek naar "Railway API Debug Info"
   - Deze toont welke IDs worden gebruikt

3. **Test API Direct**:
   - Je kunt de `/api/railway/services` endpoint gebruiken om services te lijsten
   - Dit helpt om de juiste Service ID te vinden

## Snelle Check

Run dit commando om te checken welke environment variables zijn ingesteld (lokaal):
```bash
echo "RAILWAY_API_TOKEN: ${RAILWAY_API_TOKEN:0:10}..."
echo "RAILWAY_PROJECT_ID: $RAILWAY_PROJECT_ID"
echo "RAILWAY_SERVICE_ID: $RAILWAY_SERVICE_ID"
```

Voor Vercel, check de logs in de Vercel dashboard.


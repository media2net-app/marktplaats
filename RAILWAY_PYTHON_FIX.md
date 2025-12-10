# Railway Python Build Fix

## Probleem
Railway detecteert je project als Node.js (vanwege `package.json`), maar we hebben Python nodig. Error: `pip: command not found`

## ✅ Oplossing 1: Dockerfile (Aanbevolen)

Ik heb een `Dockerfile` aangemaakt die Railway automatisch gebruikt. Dit werkt het beste.

**Wat te doen:**
1. Push de nieuwe bestanden naar GitHub
2. Railway detecteert automatisch de `Dockerfile`
3. Railway buildt met Docker in plaats van Nixpacks

## ✅ Oplossing 2: Nixpacks Configuratie

Als Dockerfile niet werkt, gebruik `nixpacks.toml`:

Railway gebruikt dan Nixpacks met Python 3.11.

## ✅ Oplossing 3: Handmatig in Railway Settings

1. Ga naar Railway dashboard
2. Service → **Settings**
3. **Build Command**:
   ```bash
   pip install -r requirements.txt && playwright install chromium
   ```
4. **Start Command**:
   ```bash
   python scripts/railway_worker.py
   ```
5. **Python Version**: Zet op `3.11` (in Settings)

## 🔧 Railway Settings Aanpassen

Als Railway nog steeds Node.js detecteert:

1. Service → **Settings**
2. Zoek **"Build Settings"**
3. **Builder**: Kies `Dockerfile` of `Nixpacks`
4. Als Nixpacks: Zorg dat `nixpacks.toml` bestaat
5. Als Dockerfile: Zorg dat `Dockerfile` bestaat

## 📋 Verificatie

Na fix, check build logs. Je zou moeten zien:
```
Step 1/10 : FROM python:3.11-slim
...
Step 5/10 : RUN pip install -r requirements.txt
...
Step 6/10 : RUN playwright install chromium
...
```

## 🆘 Nog steeds problemen?

1. **Delete en recreate service** in Railway
2. **Check Railway logs** voor specifieke errors
3. **Verify Dockerfile syntax**: `docker build .` lokaal testen (optioneel)
4. **Check Python version**: Railway moet Python 3.11+ gebruiken

## 💡 Tip

De **Dockerfile oplossing** is het meest betrouwbaar omdat het expliciet is wat Railway moet doen.


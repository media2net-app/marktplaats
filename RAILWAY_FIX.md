# Railway Build Error Fix

Als je de error ziet: **"✖ No start command was found"**, gebruik een van deze oplossingen:

## ✅ Oplossing 1: Handmatig Start Command Instellen (Snelste)

1. Ga naar Railway dashboard
2. Selecteer je service
3. Ga naar **Settings** tab
4. Scroll naar **"Start Command"**
5. Voer in:
   ```bash
   python scripts/railway_worker.py
   ```
6. Klik **Save**
7. Railway redeployt automatisch

## ✅ Oplossing 2: Via Railway UI (Service Settings)

1. Service → **Settings**
2. Zoek **"Deploy"** sectie
3. **Start Command**: `python scripts/railway_worker.py`
4. **Build Command**: `pip install -r requirements.txt && playwright install chromium`
5. Save en redeploy

## ✅ Oplossing 3: Gebruik main.py (Automatisch)

Railway zoekt automatisch naar `main.py` in de root. Ik heb deze al aangemaakt, dus:

1. Push naar GitHub:
   ```bash
   git add main.py Procfile railway.toml
   git commit -m "Add Railway entry points"
   git push
   ```
2. Railway detecteert automatisch `main.py` en start het

## ✅ Oplossing 4: Procfile

Railway ondersteunt ook `Procfile`. Deze is al aangemaakt:

```
worker: python scripts/railway_worker.py
```

Railway detecteert dit automatisch.

## 🔍 Verificatie

Na fix, check de logs:
```bash
# In Railway dashboard → Logs
# Je zou moeten zien:
🚂 Railway Marktplaats Worker
API Base URL: ...
```

## 📋 Checklist

- [ ] Start command ingesteld in Railway Settings
- [ ] Build command ingesteld: `pip install -r requirements.txt && playwright install chromium`
- [ ] Environment variables ingesteld (INTERNAL_API_KEY, etc.)
- [ ] Service geredeployed
- [ ] Logs tonen worker start

## 🆘 Nog steeds problemen?

1. **Check Railway Logs** voor specifieke errors
2. **Verify Python version**: Railway gebruikt Python 3.11+ standaard
3. **Check requirements.txt**: Alle dependencies aanwezig?
4. **Verify file paths**: `scripts/railway_worker.py` bestaat?

## 💡 Tip

De **snelste oplossing** is Oplossing 1: handmatig het start command instellen in Railway Settings. Dit werkt altijd!


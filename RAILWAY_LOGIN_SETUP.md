# Railway Marktplaats Login Setup

## 🔐 Login Methode

Het script gebruikt een **persistent browser context** om ingelogd te blijven. Dit betekent:

1. **Eerste keer**: Je moet handmatig inloggen (of via script)
2. **Daarna**: De login session wordt opgeslagen en hergebruikt

## ⚠️ Probleem op Railway

Op Railway draait alles **headless** (zonder browser venster), dus je kunt niet handmatig inloggen.

## ✅ Oplossing: Login Credentials Toevoegen

**BELANGRIJK**: Het script gebruikt momenteel een persistent browser context. De eerste keer moet je handmatig inloggen, daarna wordt de sessie opgeslagen.

Voeg deze environment variables toe in Railway voor toekomstige automatische login:

### In Railway Dashboard → Service → Variables:

```bash
MARKTPLAATS_EMAIL=gert-d-g@outlook.com
MARKTPLAATS_PASSWORD=Gert1990
```

**Huidige credentials:**
- Email: `gert-d-g@outlook.com`
- Password: `Gert1990`

## 📋 Stap-voor-Stap:

1. **Ga naar Railway Dashboard**
2. **Selecteer je service** (marktplaats worker)
3. **Klik "Variables"** tab
4. **Voeg toe**:
   - `MARKTPLAATS_EMAIL` = `gert-d-g@outlook.com`
   - `MARKTPLAATS_PASSWORD` = `Gert1990`
5. **Klik "Save"**
6. **Redeploy** de service

## 🔧 Automatische Login (Toekomstige Verbetering)

Momenteel gebruikt het script alleen de persistent context. Als er geen login session is, moet je handmatig inloggen.

**Optie 1: Eerste keer lokaal inloggen**
- Run het script lokaal één keer met `--login` flag
- De `user_data` folder wordt dan gekopieerd naar Railway

**Optie 2: Automatische login toevoegen**
- Het script kan worden aangepast om automatisch in te loggen met de credentials
- Dit vereist code aanpassingen

## 📍 Huidige Status

Het script checkt momenteel alleen of je al ingelogd bent via de persistent context. Als er geen session is, moet je handmatig inloggen.

## 🚀 Voor Nu: Voeg Credentials Toe

Voeg de credentials toe aan Railway Variables, ook al gebruikt het script ze nog niet automatisch. Dit maakt het makkelijker om later automatische login toe te voegen.

## ✅ Checklist

- [ ] `MARKTPLAATS_EMAIL` toegevoegd in Railway
- [ ] `MARKTPLAATS_PASSWORD` toegevoegd in Railway  
- [ ] Service geredeployed
- [ ] Check logs om te zien of login werkt


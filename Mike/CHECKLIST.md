# ✅ Checklist: Is alles compleet voor Mike?

## 📦 Bestanden in de map Mike

- ✅ `install_and_run_marktplaats.bat` - Eerste installatie
- ✅ `run_marktplaats_standalone.bat` - Normale uitvoering
- ✅ `scripts/post_marktplaats_standalone.py` - Hoofdscript
- ✅ `scripts/post_ads.py` - Marktplaats automatisering
- ✅ `README_STANDALONE.md` - Documentatie
- ✅ `LEES_DIT_EERST.txt` - Snelle start
- ✅ `requirements.txt` - Python dependencies

## ✅ Wat het script doet

1. **Verbindt met live API** - Haalt producten op via de productie API
2. **Downloadt foto's** - Haalt foto's op van blob storage via de API
3. **Opent Chrome** - Gebruikt je bestaande Chrome sessie
4. **Plaatst op Marktplaats** - Automatisch plaatsen van alle pending producten
5. **Update database** - Werkt status en statistieken bij

## ⚠️ Belangrijk: API URL Controleren

Het script gebruikt deze API URL:
```
https://marktplaats-eight.vercel.app
```

**Controleer of dit de juiste URL is!**

Als je Vercel deployment een andere URL heeft, pas dan aan in:
- `scripts/post_marktplaats_standalone.py` (regel 18)

## ⚠️ Belangrijk: API Key

Het script gebruikt momenteel:
```
internal-key-change-in-production
```

**Zorg dat deze overeenkomt met de `INTERNAL_API_KEY` in Vercel!**

## ✅ Vereisten voor Mike

1. **Windows 10 of hoger**
2. **Python 3.9+** geïnstalleerd met "Add Python to PATH"
3. **Chrome browser** geïnstalleerd
4. **Ingelogd op Marktplaats** in Chrome (voordat je het script start)

## ✅ Testen

1. Dubbelklik op `install_and_run_marktplaats.bat`
2. Script installeert alles automatisch
3. Script haalt pending producten op
4. Script plaatst producten op Marktplaats
5. Database wordt automatisch bijgewerkt

## ✅ Conclusie

**JA, de map Mike bevat alles wat nodig is!**

Het script is volledig standalone en heeft geen toegang nodig tot:
- ❌ Lokale database
- ❌ Lokale bestanden
- ❌ Lokale code

Alles wordt via de API opgehaald van de productie server.


# Marktplaats Automator - Standalone Versie

Deze map bevat alle benodigde bestanden om de Marktplaats Automator te gebruiken zonder het volledige project.

## 📋 Vereisten

- Python 3.8 of hoger
- Windows (voor `.bat` bestanden)
- Internetverbinding

## 🚀 Installatie

1. **Python installeren** (als je dat nog niet hebt):
   - Download van: https://www.python.org/downloads/
   - Zorg dat je "Add Python to PATH" aanvinkt tijdens installatie

2. **Bestanden uitpakken**:
   - Pak alle bestanden uit naar een map (bijv. `C:\MarktplaatsAutomator`)

3. **Environment variabelen instellen (BELANGRIJK!)**:
   - Kopieer `.env.example` naar `.env`
   - Open `.env` in een teksteditor (bijv. Kladblok)
   - Pas de volgende waarden aan met je ECHTE gegevens:
     ```
     NEXTAUTH_URL=https://jouw-domein.vercel.app
     API_BASE_URL=https://jouw-domein.vercel.app
     INTERNAL_API_KEY=jouw-api-key
     MARKTPLAATS_EMAIL=jouw-email@voorbeeld.nl
     MARKTPLAATS_PASSWORD=jouw-wachtwoord
     ```
   
   ⚠️ **LET OP**: 
   - Vervang `jouw-domein.vercel.app` door je ECHTE Vercel URL (bijv. `https://marktplaats-eight.vercel.app`)
   - Vervang `jouw-api-key` door je ECHTE INTERNAL_API_KEY (deze staat in je Vercel dashboard onder Settings > Environment Variables)
   - Gebruik NOOIT `localhost` of `127.0.0.1` - dit werkt alleen lokaal!

## ▶️ Gebruik

**Dubbelklik op `run_marktplaats.bat`**

Het script zal:
- Automatisch Python packages installeren als nodig
- Alle pending producten uit de database ophalen
- Deze producten op Marktplaats plaatsen
- Een logbestand maken in `logs\last_run.log`

## 📁 Bestandsstructuur

```
Mike_Final/
├── run_marktplaats.bat      # Hoofdscript (dubbelklik om te starten)
├── requirements.txt         # Python dependencies
├── .env.example            # Voorbeeld configuratie
├── README.md               # Deze handleiding
└── scripts/
    ├── post_all_pending.py # Script dat pending producten ophaalt
    └── post_ads.py         # Script dat advertenties plaatst
```

## ⚙️ Configuratie

### API Instellingen

In `.env` moet je de volgende waarden instellen:

- **NEXTAUTH_URL**: De LIVE URL van je webapp (bijv. `https://marktplaats-eight.vercel.app`)
  - ⚠️ **GEEN localhost!** Dit moet je echte Vercel URL zijn
- **API_BASE_URL**: Zelfde als NEXTAUTH_URL (ook de LIVE URL)
- **INTERNAL_API_KEY**: De API key die je hebt ingesteld in je Vercel dashboard
  - Deze vind je in: Vercel Dashboard > Je Project > Settings > Environment Variables
  - Moet exact overeenkomen met de `INTERNAL_API_KEY` in je Vercel environment variables

### Marktplaats Login

- **MARKTPLAATS_EMAIL**: Je Marktplaats email adres
- **MARKTPLAATS_PASSWORD**: Je Marktplaats wachtwoord

⚠️ **BELANGRIJK**: De `.env` file bevat gevoelige informatie. Deel deze niet publiekelijk!

## 📝 Logs

Na elke run wordt een logbestand gemaakt in:
- `logs\last_run.log`

Hierin zie je:
- Welke producten zijn geplaatst
- Eventuele fouten
- Status updates

## ❓ Problemen oplossen

### "Python is niet herkend"
- Installeer Python en zorg dat je "Add Python to PATH" aanvinkt
- Herstart je computer na installatie

### "Failed to install required packages"
- Controleer je internetverbinding
- Probeer handmatig: `pip install -r requirements.txt`

### "API connection failed" of "WAARSCHUWING: Je gebruikt nog localhost!"
- ⚠️ **Dit betekent dat je nog localhost gebruikt!**
- Open je `.env` bestand en controleer:
  - `NEXTAUTH_URL` moet beginnen met `https://` (niet `http://localhost`)
  - `API_BASE_URL` moet beginnen met `https://` (niet `http://localhost`)
  - Beide moeten je ECHTE Vercel URL zijn (bijv. `https://marktplaats-eight.vercel.app`)
- Controleer of `INTERNAL_API_KEY` exact overeenkomt met je Vercel environment variables
- Controleer of je webapp online is door de URL in je browser te openen

### "No pending products found"
- Dit is normaal als er geen producten met status "pending" in de database staan
- Controleer je webapp om producten toe te voegen of status te wijzigen

## 🔒 Veiligheid

- Deel je `.env` bestand NOOIT publiekelijk
- Gebruik een sterke `INTERNAL_API_KEY`
- Bewaar je Marktplaats credentials veilig

## 📞 Support

Voor vragen of problemen, neem contact op met de ontwikkelaar.


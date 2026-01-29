# Marktplaats Product Poster - Nieuwe Versie

## Overzicht

Dit is de nieuwe, vereenvoudigde versie van het Marktplaats automatisering systeem. Het systeem is volledig herschreven om betrouwbaarder en eenvoudiger te gebruiken.

## Wat is er veranderd?

### ✅ Verbeteringen:
- **Eén duidelijk script**: `marktplaats_poster.py` - geen verwarring meer
- **Betere login detectie**: Script detecteert of je ingelogd bent en helpt je inloggen
- **Duidelijke foutmeldingen**: Je ziet precies wat er mis gaat
- **Eenvoudigere structuur**: Minder bestanden, duidelijker wat wat doet

### ❌ Verwijderd:
- Oude standalone scripts (vervangen door marktplaats_poster.py)
- Duplicate code in Mike/ en Mike_Final/ folders
- Verwarrende meerdere entry points

## Installatie

### Eerste keer:

1. **Installeer Python 3.9+**
   - Download van: https://www.python.org/downloads/
   - **Belangrijk**: Vink "Add Python to PATH" aan tijdens installatie!

2. **Installeer dependencies**
   - Dubbelklik op `install_dependencies.bat`
   - Of handmatig:
     ```bash
     pip install -r requirements.txt
     python -m playwright install chromium
     ```

3. **Maak .env bestand**
   - Kopieer `env.example` naar `.env`
   - Vul in:
     ```
     API_BASE_URL=https://jouw-api-url.vercel.app
     INTERNAL_API_KEY=je-api-key
     ```

## Gebruik

### Normaal gebruik:

1. **Start het script**
   - Dubbelklik op `start_marktplaats.bat`
   - Of handmatig: `python marktplaats_poster.py`

2. **Eerste keer: Inloggen**
   - Script opent browser
   - Als je niet ingelogd bent, krijg je duidelijke instructies
   - Log in op Marktplaats in de browser
   - Druk op ENTER in het terminal venster
   - Je login wordt opgeslagen voor volgende keren

3. **Producten plaatsen**
   - Script haalt automatisch pending producten op
   - Downloadt foto's
   - Plaatst producten één voor één
   - Update database met resultaten

## Hoe het werkt

1. **Haalt producten op** van de API (`/api/products/pending`)
2. **Downloadt foto's** naar tijdelijke map
3. **Opent browser** (Chrome via Playwright)
4. **Controleert login** - helpt je inloggen als nodig
5. **Plaatst producten** automatisch:
   - Kiest categorie
   - Vult titel, beschrijving, prijs
   - Uploadt foto's
   - Publiceert advertentie
6. **Update database** met resultaten (URL, views, saves, etc.)
7. **Ruimt op** tijdelijke bestanden

## Configuratie

### Environment Variables (.env):

```env
# API Configuratie
API_BASE_URL=https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app
INTERNAL_API_KEY=je-api-key-hier

# Marktplaats (optioneel)
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl

# Browser (optioneel)
USER_DATA_DIR=~/.marktplaats_browser
MEDIA_ROOT=./public/media

# Performance (optioneel)
HEADLESS=false  # true voor headless mode (geen browser venster)
MP_FAST=true    # true voor snellere mode (kortere wachttijden)
```

## Troubleshooting

### "Python is niet geinstalleerd"
- Installeer Python van https://www.python.org/downloads/
- Zorg dat je "Add Python to PATH" aanvinkt

### "Authenticatie fout"
- Controleer je `.env` bestand
- Zorg dat `INTERNAL_API_KEY` correct is
- Zorg dat `API_BASE_URL` correct is

### "Browser opent niet"
- Sluit alle Chrome vensters
- Probeer opnieuw
- Als het blijft falen, installeer Chrome handmatig

### "Niet ingelogd"
- Volg de instructies in het script
- Log in handmatig in de browser
- Druk op ENTER als je klaar bent
- Je login wordt opgeslagen voor volgende keren

### "Producten worden niet geplaatst"
- Controleer of je echt bent ingelogd
- Kijk in de browser wat er gebeurt
- Check de console output voor foutmeldingen
- Zorg dat producten "pending" status hebben in database

## Bestandsstructuur

```
marktplaats/
├── marktplaats_poster.py      # Hoofdscript (START HIER)
├── start_marktplaats.bat      # Windows start script
├── install_dependencies.bat   # Installatie script
├── .env                       # Configuratie (maak zelf aan)
├── env.example                # Voorbeeld configuratie
├── requirements.txt           # Python dependencies
├── scripts/
│   └── post_ads.py           # Browser automatisering
└── README_NIEUW_SYSTEEM.md   # Deze documentatie
```

## Oude Bestanden

De volgende bestanden zijn vervangen en kunnen worden verwijderd:
- `scripts/post_marktplaats_standalone.py` (vervangen door marktplaats_poster.py)
- `local_worker/post_pending_local.py` (vervangen door marktplaats_poster.py)
- `run_marktplaats_standalone.bat` (vervangen door start_marktplaats.bat)
- `install_and_run_marktplaats.bat` (vervangen door install_dependencies.bat + start_marktplaats.bat)

## Support

Als je problemen hebt:
1. Check deze README eerst
2. Kijk naar de console output voor foutmeldingen
3. Check of je .env bestand correct is
4. Zorg dat je de nieuwste versie van Python hebt

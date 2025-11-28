# Marktplaats Advertentie Automator

Automatiseer het plaatsen van advertenties op Marktplaats op basis van een productlijst.

## Benodigdheden
- Python 3.10+
- Google Chrome of Chromium (voor Playwright)

## Installatie
1. Installeer dependencies:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

2. Maak een `.env` (zie `env.example`) en pas aan waar nodig.

3. Vul `products.csv` met jouw producten.

## Inloggen
Log éénmalig in met een persistent profiel zodat de sessie bewaard blijft:
```bash
python scripts/post_ads.py --login
```
Dit opent een browser. Log in op Marktplaats en sluit het venster. De sessie wordt opgeslagen in de `user_data/` map.

## Uitvoeren (advertenties plaatsen)
```bash
python scripts/post_ads.py --csv products.csv
```

## CSV-formaat
Kolommen:
- title
- description
- price
- category_path (niet nodig; script gebruikt standaard "Vind categorie")
- location (optioneel)
- photos (optioneel; paden gescheiden door `;`)
- article_number (optioneel; als ingevuld, zoekt script foto’s in `MEDIA_ROOT/[article_number]`)

Voorbeeld in `products.csv` bevat een rij met `isolatieplaat` en `article_number`.

## Foto’s mappenstructuur
- Zet je beelden hier: `public/media/[artikelnummer]/*.jpg|.jpeg|.png|.heic`
- Stel `MEDIA_ROOT` in `.env` indien je een andere map gebruikt.

## Config (env)
Zie `env.example` en kopieer naar `.env`:
- USER_DATA_DIR: persistent profiel
- MARKTPLAATS_BASE_URL: basis URL
- MEDIA_ROOT: root map voor foto’s (default `./public/media`)
- ACTION_DELAY_MS: kleine vertraging tussen acties

## Werking
- Script opent de plaats-ad pagina, vult titel, klikt "Vind categorie", kiest eerste suggestie en klikt "Verder".
- Vult beschrijving/prijs/locatie indien aanwezig.
- Uploadt foto’s uit `photos` of, als leeg, automatisch uit `MEDIA_ROOT/[article_number]`.
- Probeert de advertentie te publiceren.

UI kan wijzigen; geef door welke stap/selector faalt, dan pas ik het aan.

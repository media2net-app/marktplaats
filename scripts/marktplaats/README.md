# Marktplaats Automatisering Module

Modulaire implementatie voor het plaatsen van advertenties op Marktplaats via Playwright.

## Structuur

```
scripts/marktplaats/
├── __init__.py          # Module initialisatie
├── utils.py             # Utility functies (logging, Product dataclass, etc.)
├── browser.py            # Browser management en login
├── form_filler.py        # Formulier invullen (categorie, velden)
├── photo_upload.py       # Foto upload functionaliteit
├── publisher.py          # Advertentie plaatsen en URL ophalen
└── main.py              # Hoofd orchestrator
```

## Modules

### `browser.py` - Browser Management
- Start browser met persistent context
- Automatisch inloggen
- Sessie beheer
- Cookie handling

### `form_filler.py` - Formulier Invullen
- Navigeren naar plaats advertentie pagina
- Categorie selectie (auto-suggest of pad)
- Alle velden invullen (titel, beschrijving, prijs, etc.)
- Categorie-specifieke velden
- Gratis bundle selectie

### `photo_upload.py` - Foto Upload
- Foto's ophalen (van product.photos of artikelnummer)
- File input vinden
- Foto's uploaden
- Upload verificatie

### `publisher.py` - Advertentie Plaatsen
- Publiceer knop vinden en klikken
- Error checking
- Ad URL ophalen (van huidige pagina of "Mijn advertenties")

### `main.py` - Orchestrator
- Coördineert alle modules
- Leest producten (van API of CSV)
- Plaatst producten
- Retourneert resultaten

## Gebruik

### Via Python script

```python
from marktplaats.main import run

# Van API
results = await run(api_url="http://localhost:3000/api/products/pending")

# Van CSV
results = await run(csv_path="products.csv")
```

### Via command line

```bash
# Login alleen
python scripts/post_ads_new.py --login

# Van CSV
python scripts/post_ads_new.py --csv products.csv

# Van API
python scripts/post_ads_new.py --api http://localhost:3000/api/products/pending
```

### Via post_pending_local_new.py

```bash
# Gebruik lokale API
python local_worker/post_pending_local_new.py

# Met custom API URL
API_BASE_URL=https://marktplaats-eight.vercel.app python local_worker/post_pending_local_new.py
```

## Environment Variables

- `MARKTPLAATS_BASE_URL`: Base URL voor Marktplaats (default: https://www.marktplaats.nl)
- `USER_DATA_DIR`: Directory voor browser user data (default: ./user_data)
- `MEDIA_ROOT`: Root directory voor foto's (default: ./public/media)
- `MARKTPLAATS_EMAIL`: Email voor automatisch inloggen
- `MARKTPLAATS_PASSWORD`: Wachtwoord voor automatisch inloggen
- `INTERNAL_API_KEY`: API key voor authenticatie
- `MP_VERBOSE`: Verbose logging (default: true)
- `MP_FAST`: Fast mode (kortere wait times, default: true)
- `MP_DEBUG_SCREENSHOTS`: Maak screenshots bij errors (default: false)
- `HEADLESS`: Run browser in headless mode (default: false)

## Voordelen van Nieuwe Structuur

1. **Modulair**: Elke module heeft een duidelijke verantwoordelijkheid
2. **Onderhoudbaar**: Makkelijker om aanpassingen te maken
3. **Testbaar**: Modules kunnen individueel getest worden
4. **Herbruikbaar**: Modules kunnen in andere contexten gebruikt worden
5. **Leesbaar**: Duidelijkere code structuur

## Migratie van Oude Scripts

De oude `post_ads.py` (2200+ regels) is vervangen door deze modulaire structuur. 
De functionaliteit blijft hetzelfde, maar de code is nu veel beter georganiseerd.

### Oude vs Nieuwe

**Oud:**
- `scripts/post_ads.py` - Alles in één bestand
- `local_worker/post_pending_local.py` - Gebruikt oude post_ads.py

**Nieuw:**
- `scripts/marktplaats/` - Modulaire structuur
- `scripts/post_ads_new.py` - Entry point (vervangt oude post_ads.py)
- `local_worker/post_pending_local_new.py` - Gebruikt nieuwe modules

## Testing

Test de nieuwe implementatie met:

```bash
# Test login
python scripts/post_ads_new.py --login

# Test met één product (via API)
python scripts/post_ads_new.py --api http://localhost:3000/api/products/pending
```

## Troubleshooting

### Browser start niet
- Check of Playwright geïnstalleerd is: `python -m playwright install chromium`
- Check of USER_DATA_DIR schrijfrechten heeft

### Login mislukt
- Check MARKTPLAATS_EMAIL en MARKTPLAATS_PASSWORD in .env
- Probeer handmatig in te loggen met `--login` flag

### Foto's worden niet gevonden
- Check MEDIA_ROOT in .env
- Check of foto's in `MEDIA_ROOT/[article_number]/` staan
- Check of foto extensies .jpg, .jpeg, .png, of .heic zijn

### Categorie niet gevonden
- Check of category_path correct is (bijv. "Huis en Inrichting > Banken")
- Check of categorie bestaat in Marktplaats

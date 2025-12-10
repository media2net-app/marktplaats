# Marktplaats Categorie Scraper & Importer

Dit document beschrijft hoe je alle categorieën en subcategorieën van Marktplaats kunt scrapen en importeren in de database.

## Scripts

### 1. `scrape_categories_from_homepage.py`
Scrapet alle categorieën en subcategorieën van de Marktplaats hoofdpagina.

**Gebruik:**
```bash
python3 scripts/scrape_categories_from_homepage.py
```

Dit script:
- Opent de Marktplaats hoofdpagina
- Vindt alle hoofdcategorieën in de sidebar
- Klikt op elke categorie om subcategorieën te krijgen
- Slaat alles op in `categories_scraped.json`

### 2. `import_categories_to_db.py`
Importeert gescrapete categorieën naar de database via de API.

**Gebruik:**
```bash
python3 scripts/import_categories_to_db.py [categories_file] [api_url] [api_key]
```

**Parameters:**
- `categories_file` (optioneel): Pad naar JSON bestand met categorieën (default: `categories_scraped.json`)
- `api_url` (optioneel): Base URL van de API (default: uit `.env`)
- `api_key` (optioneel): API key voor authenticatie (default: uit `.env`)

**Voorbeeld:**
```bash
# Gebruik defaults uit .env
python3 scripts/import_categories_to_db.py

# Specificeer bestand en URL
python3 scripts/import_categories_to_db.py categories_scraped.json https://jouw-domein.vercel.app
```

### 3. `scrape_and_import_categories.py`
Complete workflow: Scrapet categorieën en importeert ze direct naar de database.

**Gebruik:**
```bash
python3 scripts/scrape_and_import_categories.py
```

Dit script combineert beide stappen in één commando.

## Workflow

### Stap 1: Scrape categorieën
```bash
python3 scripts/scrape_categories_from_homepage.py
```

Dit duurt enkele minuten omdat het door alle categorieën navigeert. Het resultaat wordt opgeslagen in `categories_scraped.json`.

### Stap 2: Import naar database
```bash
python3 scripts/import_categories_to_db.py
```

Dit verstuurt alle categorieën naar de database via de API endpoint `/api/categories`.

### Of alles in één keer:
```bash
python3 scripts/scrape_and_import_categories.py
```

## API Endpoint

### POST `/api/categories`

Voegt categorieën toe aan de database.

**Authenticatie:**
- Session (ingelogde gebruiker) OF
- API key via header `x-api-key` of query parameter `api_key`

**Request Body:**
```json
{
  "categories": [
    {
      "id": "auto",
      "name": "Auto's",
      "level": 1,
      "parentId": null,
      "path": "Auto's",
      "marktplaatsId": null
    },
    {
      "id": "auto-onderdelen",
      "name": "Auto-onderdelen",
      "level": 2,
      "parentId": "auto",
      "path": "Auto's > Auto-onderdelen",
      "marktplaatsId": null
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "created": 150,
  "updated": 10,
  "skipped": 5,
  "errors": []
}
```

## Categorie Structuur

Elke categorie heeft:
- `id`: Unieke identifier (wordt gegenereerd als niet opgegeven)
- `name`: Naam van de categorie
- `level`: Niveau (1 = hoofdcategorie, 2 = subcategorie, 3 = sub-subcategorie)
- `parentId`: ID van de parent categorie (null voor hoofdcategorieën)
- `path`: Volledige pad zoals "Auto's > Auto-onderdelen > Motoren"
- `marktplaatsId`: Marktplaats interne ID (optioneel)

## Troubleshooting

### Geen categorieën gevonden
- Controleer of je internet verbinding hebt
- Zorg dat Marktplaats bereikbaar is
- Probeer de scraper opnieuw (soms zijn er tijdelijke problemen)

### API fouten
- Controleer of `NEXTAUTH_URL` en `INTERNAL_API_KEY` correct zijn ingesteld in `.env`
- Controleer of de API server draait (localhost:3000 of Vercel)
- Controleer of je API key correct is

### Duplicate categorieën
- De import functie update automatisch bestaande categorieën
- Categorieën worden gematcht op `id` of `path`

## Opmerkingen

- De scraper gebruikt Chrome/Chromium met Playwright
- Het script opent een browser venster (headless=False) zodat je kunt zien wat er gebeurt
- Het proces kan 10-30 minuten duren afhankelijk van het aantal categorieën
- Zorg dat je Chrome/Chromium geïnstalleerd hebt

















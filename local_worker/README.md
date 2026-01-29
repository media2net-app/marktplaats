# Lokaal Marktplaats Worker

Dit script draait lokaal op je Mac en plaatst pending producten naar Marktplaats.

## Installatie

1. **Zorg dat je dependencies hebt geïnstalleerd:**
   ```bash
   pip install playwright requests python-dotenv
   python -m playwright install chromium
   ```

2. **Kopieer `.env.example` naar `.env`:**
   ```bash
   cp .env.example .env
   ```

3. **Pas `.env` aan met je instellingen:**
   - `API_BASE_URL`: Je lokale server (`http://localhost:3000`) of productie URL
   - `INTERNAL_API_KEY`: Moet overeenkomen met de key in je `.env.local`
   - `USER_DATA_DIR`: Waar de browser session wordt opgeslagen (optioneel)
   - `MEDIA_ROOT`: Waar je product foto's staan (optioneel)

## Gebruik

### Basis gebruik:
```bash
python post_pending_local.py
```

### Met custom API URL:
```bash
API_BASE_URL=https://marktplaats-eight.vercel.app python post_pending_local.py
```

### Met headless mode (geen browser venster):
```bash
HEADLESS=true python post_pending_local.py
```

## Eerste keer gebruik

De eerste keer dat je het script draait, moet je inloggen op Marktplaats:

1. Het script opent een browser venster
2. Log in op Marktplaats (handmatig)
3. De login wordt opgeslagen in `USER_DATA_DIR`
4. Volgende keren hoef je niet meer in te loggen

## Hoe het werkt

1. **Haalt pending producten op** van de API (`/api/products/pending`)
2. **Plaatst ze op Marktplaats** via Playwright browser automation
3. **Update de database** met de resultaten (URL, ad ID, statistieken)

## Troubleshooting

### "Unauthorized" fout
- Controleer of `INTERNAL_API_KEY` overeenkomt met je `.env.local`
- Controleer of de API server draait

### "Connection refused"
- Start je lokale server: `npm run dev`
- Of gebruik productie URL: `API_BASE_URL=https://marktplaats-eight.vercel.app`

### Browser opent niet
- Installeer Playwright: `python -m playwright install chromium`
- Controleer of je DISPLAY variabele is ingesteld (voor headless)

### Foto's worden niet gevonden
- Controleer `MEDIA_ROOT` pad
- Foto's moeten in `MEDIA_ROOT/{article_number}/` staan

## Environment Variables

| Variabele | Beschrijving | Standaard |
|-----------|--------------|-----------|
| `API_BASE_URL` | API server URL | `http://localhost:3000` |
| `INTERNAL_API_KEY` | API authenticatie key | `internal-key-change-in-production` |
| `MARKTPLAATS_BASE_URL` | Marktplaats URL | `https://www.marktplaats.nl` |
| `USER_DATA_DIR` | Browser session directory | `~/.marktplaats_browser` |
| `MEDIA_ROOT` | Foto's directory | `../public/media` |
| `ACTION_DELAY_MS` | Vertraging tussen acties | `200` |
| `HEADLESS` | Headless mode | `false` |

## Verschil met Railway Worker

- **Railway Worker**: Draait continu op Railway, checkt elke 5 minuten
- **Lokaal Script**: Draait handmatig, verwerkt alle pending producten en stopt

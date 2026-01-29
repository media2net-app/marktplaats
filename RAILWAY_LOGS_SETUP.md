# Railway Logs Setup

Deze gids legt uit hoe je Railway logs kunt bekijken in de web applicatie.

## Probleem

Als je de foutmelding ziet: **"Failed to fetch logs from Railway"**, betekent dit dat de Railway API credentials niet zijn geconfigureerd in Vercel.

## Oplossing

Je moet twee environment variables instellen in Vercel:

1. `RAILWAY_API_TOKEN` - Je Railway API token
2. `RAILWAY_SERVICE_ID` - Je Railway Service ID

## Stap 1: Railway API Token ophalen

1. Ga naar [Railway Dashboard](https://railway.app)
2. Klik op je profiel (rechtsboven)
3. Ga naar "Settings" → "Tokens"
4. Klik op "New Token"
5. Geef het token een naam (bijv. "Marktplaats Logs")
6. Kopieer het token (je ziet het maar één keer!)

## Stap 2: Railway Service ID vinden

1. Ga naar je Railway project
2. Klik op de service waar je Python worker draait
3. In de URL zie je: `https://railway.app/project/[PROJECT_ID]/service/[SERVICE_ID]`
4. De `SERVICE_ID` is het deel na `/service/`
5. Of ga naar "Settings" → "General" en scroll naar beneden voor de Service ID

## Stap 3: Environment Variables instellen in Vercel

1. Ga naar je [Vercel Dashboard](https://vercel.com)
2. Selecteer je project
3. Ga naar **Settings** → **Environment Variables**
4. Voeg de volgende variables toe:

### RAILWAY_API_TOKEN
- **Name**: `RAILWAY_API_TOKEN`
- **Value**: Je Railway API token (uit Stap 1)
- **Environment**: Alle environments (Production, Preview, Development)

### RAILWAY_SERVICE_ID
- **Name**: `RAILWAY_SERVICE_ID`
- **Value**: Je Railway Service ID (uit Stap 2)
- **Environment**: Alle environments (Production, Preview, Development)

## Stap 4: Redeploy

Na het toevoegen van de environment variables:

1. Ga naar **Deployments** in Vercel
2. Klik op de drie puntjes (⋯) van de laatste deployment
3. Kies **Redeploy**
4. Wacht tot de deployment klaar is

## Stap 5: Testen

1. Ga naar je applicatie → **Logs** pagina
2. Je zou nu Railway logs moeten zien
3. Als je nog steeds een fout ziet, controleer:
   - Of de environment variables correct zijn ingevuld
   - Of je de juiste Service ID hebt (van de service waar je Python worker draait)
   - Of je API token nog geldig is

## Troubleshooting

### "Railway API authentication failed"
- Controleer of `RAILWAY_API_TOKEN` correct is
- Genereer een nieuw token als het oude verlopen is

### "Railway service not found"
- Controleer of `RAILWAY_SERVICE_ID` correct is
- Zorg dat je de Service ID gebruikt, niet de Project ID

### "Railway API access forbidden"
- Controleer of je API token de juiste permissions heeft
- Zorg dat je token toegang heeft tot het project en de service

### Geen logs zichtbaar
- Zorg dat je Railway service daadwerkelijk draait
- Controleer of er logs worden gegenereerd in Railway dashboard
- Wacht even en klik op "Ververs"

## Alternatief: Logs direct in Railway bekijken

Als je de logs niet in de web app kunt zien, kun je ze ook direct in Railway bekijken:

1. Ga naar je Railway project
2. Klik op je service
3. Ga naar het **Logs** tabblad
4. Hier zie je alle logs in real-time

## Opmerking

De Railway logs functionaliteit is optioneel. Als je Railway niet gebruikt of de logs niet nodig hebt, kun je deze stap overslaan. De applicatie werkt ook zonder Railway logs configuratie.

# Railway Logs Error Debugging

## 🔍 Error: "Failed to fetch logs from Railway"

### Stap 1: Check Server Logs

Open de terminal waar `npm run dev` draait en kijk naar de logs. Je zou moeten zien:

```
[RAILWAY LOGS] Making request to: https://backboard.railway.app/graphql/v1
[RAILWAY LOGS] Variables: { projectId: 'd7cf2713...', serviceId: '784bc95a...', ... }
[RAILWAY LOGS] Response status: XXX XXX
```

### Stap 2: Check Browser Console

Open Developer Tools (F12) → Console tab en kijk naar de error details.

### Stap 3: Veelvoorkomende Errors

#### Error 401: Unauthorized
- **Oorzaak**: Railway API token is ongeldig
- **Oplossing**: Maak nieuwe token aan in Railway → Settings → Tokens

#### Error 404: Not Found
- **Oorzaak**: Project ID of Service ID is incorrect
- **Oplossing**: Check of IDs correct zijn in `.env.local`

#### Error 500: Server Error
- **Oorzaak**: Railway API heeft een probleem
- **Oplossing**: Check Railway status page

### Stap 4: Test Railway API Token

Test of de token werkt:

```bash
curl -X POST "https://backboard.railway.app/graphql/v1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JOUW_TOKEN_HIER" \
  -d '{"query": "query { me { id } }"}'
```

Als dit "Not Found" geeft, is de token ongeldig.

### Stap 5: Check Environment Variables

Zorg dat deze in `.env.local` staan:

```bash
RAILWAY_API_TOKEN=...
RAILWAY_PROJECT_ID=...
RAILWAY_SERVICE_ID=...
```

### Stap 6: Herstart Dev Server

Na het aanpassen van environment variables:

1. Stop de server (Ctrl+C)
2. Start opnieuw: `npm run dev`
3. Test opnieuw

## ✅ Na Fix

Na het fixen zou je moeten zien:
- Geen errors in browser console
- Logs worden getoond op `/logs` pagina
- Auto-refresh werkt


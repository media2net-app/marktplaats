# Logs Page Error - Oplossing

## 🔍 Probleem

`http://localhost:3000/logs` geeft een error.

## ✅ Oplossingen

### 1. Herstart de Dev Server

De environment variables worden alleen geladen bij start. Herstart de server:

1. **Stop de server**: Druk `Ctrl+C` in de terminal waar de server draait
2. **Start opnieuw**: `npm run dev` of `PORT=3000 npm run dev`

### 2. Check of je ingelogd bent

De logs pagina vereist authenticatie:

1. Ga naar `http://localhost:3000/login`
2. Log in met je credentials
3. Ga dan naar `http://localhost:3000/logs`

### 3. Check Environment Variables

Zorg dat deze in `.env.local` staan:

```bash
RAILWAY_API_TOKEN=195af680-b076-4c50-81e7-4938ae49139d
RAILWAY_PROJECT_ID=d7cf2713-0d81-4820-b62f-cd732285675c
RAILWAY_SERVICE_ID=784bc95a-e824-4d0c-b69e-7eddb39143d9
```

### 4. Check Browser Console

Open Developer Tools (F12) → Console tab en kijk voor errors.

## 🔧 Veelvoorkomende Errors

### "Unauthorized"
- **Oorzaak**: Niet ingelogd
- **Oplossing**: Log in via `/login`

### "Railway API not configured"
- **Oorzaak**: Environment variables niet geladen
- **Oplossing**: Herstart dev server

### "Failed to fetch logs"
- **Oorzaak**: Railway API credentials incorrect
- **Oplossing**: Check of credentials correct zijn in `.env.local`

## ✅ Test

Na herstart van de server:

1. Log in op `http://localhost:3000/login`
2. Ga naar `http://localhost:3000/logs`
3. Je zou nu de Railway logs moeten zien!


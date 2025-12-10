# Railway API Token Fix

## ⚠️ Probleem: "Not Found" van Railway API

De Railway API geeft "Not Found" terug, wat meestal betekent dat:
1. **De token is ongeldig** (verwijderd of verlopen)
2. **Verkeerde token type** (project token vs account token)

## ✅ Oplossing: Nieuwe Token Aanmaken

### Stap 1: Ga naar Railway Tokens

1. Ga naar [railway.app](https://railway.app)
2. Klik op je **profiel** (rechtsboven)
3. Ga naar **Settings** → **Tokens**
4. **Verwijder de oude token** (als die er nog is)
5. Klik **"New Token"**

### Stap 2: Maak Account Token

Voor de GraphQL API heb je een **Account Token** nodig (niet Project Token):

1. Geef een naam (bijv. "Marktplaats App Logs")
2. **BELANGRIJK**: Selecteer **"Account Token"** (niet Project Token)
3. Klik **"Create"**
4. **Kopieer de token** (je ziet hem maar 1x!)

### Stap 3: Update Environment Variables

**Lokaal (.env.local):**
```bash
RAILWAY_API_TOKEN=nieuwe-token-hier
```

**Vercel (Production):**
1. Ga naar Vercel Dashboard → Project → Settings → Environment Variables
2. Update `RAILWAY_API_TOKEN` met de nieuwe token
3. Redeploy

## 🔍 Token Types

- **Account Token**: Voor GraphQL API (wat we nodig hebben)
- **Project Token**: Voor project-specifieke acties (niet voor GraphQL)

## ✅ Test Nieuwe Token

Na het updaten, test of het werkt:

1. Herstart dev server
2. Ga naar `/logs` pagina
3. Check of logs nu worden getoond

## 📝 Huidige Token (mogelijk ongeldig)

De huidige token die je gebruikt:
- `195af680-b076-4c50-81e7-4938ae49139d`

Als deze "Not Found" geeft, is hij waarschijnlijk ongeldig of verwijderd.


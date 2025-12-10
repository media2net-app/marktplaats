# Railway Logs Error - Troubleshooting

## 🔍 Error: "Failed to fetch logs from Railway"

### Stap 1: Check Browser Console

1. Open Developer Tools (F12)
2. Ga naar **Console** tab
3. Kijk naar de exacte error message
4. Check of er meer details zijn

### Stap 2: Check Server Logs

De server logs (in terminal waar `npm run dev` draait) zouden nu meer details moeten tonen:
- HTTP status code
- Railway API response
- Token status

### Stap 3: Verify Railway API Token

De token die je hebt gebruikt is: `195af680-b076-4c50-81e7-4938ae49139d`

**Check of deze token nog geldig is:**

1. Ga naar Railway → Profiel → Settings → Tokens
2. Check of de token nog bestaat
3. Als de token verwijderd is, maak een nieuwe aan

### Stap 4: Test Railway API Direct

Test of de token werkt:

```bash
curl -X POST "https://backboard.railway.app/graphql/v1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 195af680-b076-4c50-81e7-4938ae49139d" \
  -d '{
    "query": "query { me { id } }"
  }'
```

Als dit een error geeft, is de token ongeldig.

### Stap 5: Check Project ID en Service ID

Verify dat deze correct zijn:
- **Project ID**: `d7cf2713-0d81-4820-b62f-cd732285675c`
- **Service ID**: `784bc95a-e824-4d0c-b69e-7eddb39143d9`

### Stap 6: Check Railway Service Status

1. Ga naar Railway dashboard
2. Check of je service draait
3. Check of er logs zijn in Railway zelf

## 🔧 Veelvoorkomende Oorzaken

### 1. Token Ongeldig
- **Symptoom**: 401 Unauthorized
- **Oplossing**: Maak nieuwe token aan in Railway

### 2. Verkeerde Project/Service ID
- **Symptoom**: GraphQL error "Project not found"
- **Oplossing**: Verify IDs in Railway dashboard

### 3. Service Heeft Geen Logs
- **Symptoom**: Empty logs array
- **Oplossing**: Check of service draait en logs produceert

### 4. Network Issue
- **Symptoom**: Connection timeout
- **Oplossing**: Check internet verbinding

## ✅ Test Na Fix

1. Herstart dev server (als je credentials hebt aangepast)
2. Refresh de logs pagina
3. Check browser console voor nieuwe error details
4. Check server terminal voor backend errors

## 📊 Verbeterde Error Messages

Na de update zou je nu meer details moeten zien:
- HTTP status code
- Railway API error message
- Token status (zonder token zelf te tonen)


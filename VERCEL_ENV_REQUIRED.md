# ⚠️ VERPLICHTE ENVIRONMENT VARIABLES VOOR VERCEL

De app werkt NIET zonder deze environment variables! Zorg dat ze allemaal zijn ingesteld.

## Stap 1: Ga naar Vercel Dashboard

1. Ga naar: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats** of **marktplaats-eight**
3. Ga naar: **Settings** → **Environment Variables**

## Stap 2: Voeg deze VERPLICHTE variables toe

### 1. DATABASE_URL (VERPLICHT!)
```
Type: Production, Preview, Development
Value: Je PostgreSQL connection string
Voorbeeld: prisma+postgres://... (Prisma Accelerate)
Of: postgresql://user:password@host:port/database
```

**Zonder dit werkt de app NIET!**

### 2. NEXTAUTH_SECRET (VERPLICHT!)
```
Type: Production, Preview, Development
Value: Een willekeurige geheime string (minimaal 32 karakters)
Genereer met: openssl rand -base64 32
```

**Zonder dit werkt authenticatie NIET!**

### 3. NEXTAUTH_URL (VERPLICHT!)
```
Type: Production, Preview, Development
Value: https://marktplaats-eight.vercel.app
(Of je custom domain als je die hebt)
```

**Zonder dit werkt authenticatie NIET!**

### 4. INTERNAL_API_KEY (Aanbevolen)
```
Type: Production, Preview, Development
Value: LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=
(Of genereer je eigen veilige key)
```

## Stap 3: Optionele Variables (voor Railway logs)

### 5. RAILWAY_API_TOKEN (Optioneel - voor logs)
```
Type: Production, Preview, Development
Value: Je Railway API token
```

### 6. RAILWAY_SERVICE_ID (Optioneel - voor logs)
```
Type: Production, Preview, Development
Value: Je Railway Service ID
```

## Stap 4: Redeploy

Na het instellen van alle variables:

1. Ga naar **Deployments** tab
2. Klik op de drie puntjes (⋯) naast de laatste deployment
3. Kies **Redeploy**
4. Of push een nieuwe commit naar GitHub

## Troubleshooting

### "Database not configured" error
- ✅ Controleer of `DATABASE_URL` is ingesteld
- ✅ Controleer of de waarde correct is (begint met `prisma+postgres://` of `postgresql://`)
- ✅ Controleer of je database toegankelijk is vanaf Vercel

### "NextAuth" errors
- ✅ Controleer of `NEXTAUTH_SECRET` is ingesteld
- ✅ Controleer of `NEXTAUTH_URL` is ingesteld en correct is
- ✅ Genereer een nieuwe secret als nodig: `openssl rand -base64 32`

### App toont alleen login pagina
- ✅ Controleer Vercel logs voor errors
- ✅ Controleer of alle environment variables zijn ingesteld
- ✅ Controleer of de database connectie werkt

### Hoe check je Vercel logs?
1. Ga naar **Deployments** tab
2. Klik op de laatste deployment
3. Klik op **View Function Logs** of **Runtime Logs**

## Quick Check Script

Je kunt deze command runnen om te checken of alles werkt:

```bash
curl https://marktplaats-eight.vercel.app/api/auth/providers
```

Als dit werkt, is NextAuth geconfigureerd. Als dit faalt, check de environment variables.

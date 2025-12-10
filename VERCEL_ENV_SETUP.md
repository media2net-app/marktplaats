# Vercel Environment Variables Setup

## ⚠️ BELANGRIJK: Deze environment variables MOETEN worden ingesteld in Vercel!

Ga naar: https://vercel.com/media2net-apps-projects/marktplaats/settings/environment-variables

## Vereiste Environment Variables:

### 1. NEXTAUTH_SECRET (VERPLICHT)
Genereer een veilige secret:
```bash
openssl rand -base64 32
```

Of gebruik deze (vervang deze door je eigen):
```
[GEGENEREERDE_SECRET_HIER]
```

**Zet dit in Vercel als:** `NEXTAUTH_SECRET`

### 2. DATABASE_URL (VERPLICHT)
Je PostgreSQL connection string. Bijvoorbeeld:
- Prisma Accelerate: `prisma+postgres://...`
- Standaard PostgreSQL: `postgresql://user:password@host:port/database`

**Zet dit in Vercel als:** `DATABASE_URL`

### 3. NEXTAUTH_URL (VERPLICHT)
Je Vercel deployment URL:
```
https://marktplaats-9298xsau7-media2net-apps-projects.vercel.app
```

Of je custom domain als je die hebt ingesteld.

**Zet dit in Vercel als:** `NEXTAUTH_URL`

### 4. INTERNAL_API_KEY (Aanbevolen)
Een veilige API key voor interne communicatie. Gebruik dezelfde als in je `.env` bestand.

**Zet dit in Vercel als:** `INTERNAL_API_KEY`

## Stappen om in te stellen:

1. Ga naar: https://vercel.com/media2net-apps-projects/marktplaats/settings/environment-variables
2. Klik op "Add New"
3. Voeg elke variable toe voor **Production**, **Preview**, en **Development**
4. Klik op "Save"
5. Ga naar **Deployments** tab
6. Klik op de drie puntjes (⋯) naast de laatste deployment
7. Kies **Redeploy**

## Na het instellen:

Na het instellen van de environment variables, moet je opnieuw deployen:
```bash
vercel --prod
```

Of via het Vercel dashboard: klik op "Redeploy" bij de laatste deployment.


















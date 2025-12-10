# PostgreSQL Database Setup voor Vercel

Je hebt een PostgreSQL database nodig voor productie. Hier zijn de beste opties:

## Optie 1: Vercel Postgres (Aanbevolen - Eenvoudigst)

Vercel heeft een ingebouwde PostgreSQL service:

1. Ga naar: https://vercel.com/dashboard
2. Klik op je project: **marktplaats**
3. Ga naar **Storage** tab
4. Klik op **Create Database**
5. Kies **Postgres**
6. Kies een naam (bijv. `marktplaats-db`)
7. Kies een regio (bijv. `Frankfurt` voor Europa)
8. Klik op **Create**

Vercel maakt automatisch de `DATABASE_URL` environment variable aan!

## Optie 2: Prisma Accelerate (Aanbevolen voor Performance)

1. Ga naar: https://console.prisma.io/
2. Maak een account aan (gratis tier beschikbaar)
3. Maak een nieuw project
4. Koppel je database (of maak een nieuwe via Prisma)
5. Kopieer de Accelerate URL (begint met `prisma+postgres://`)

**Format:**
```
prisma+postgres://user:password@host:port/database?schema=public&pgbouncer=true
```

## Optie 3: Supabase (Gratis Tier)

1. Ga naar: https://supabase.com/
2. Maak een gratis account
3. Maak een nieuw project
4. Ga naar **Settings** → **Database**
5. Kopieer de **Connection string** (URI)

**Format:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## Optie 4: Neon (Serverless PostgreSQL - Gratis Tier)

1. Ga naar: https://neon.tech/
2. Maak een gratis account
3. Maak een nieuw project
4. Kopieer de connection string

**Format:**
```
postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

## Optie 5: Railway (Gratis Credits)

1. Ga naar: https://railway.app/
2. Maak een account
3. Maak een nieuw project
4. Voeg een PostgreSQL service toe
5. Kopieer de connection string

## Connection String Format

### Standaard PostgreSQL:
```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
```

### Prisma Accelerate:
```
prisma+postgres://[user]:[password]@[host]:[port]/[database]?schema=public&pgbouncer=true
```

## Na het krijgen van je Connection String:

### Via Vercel CLI:
```bash
vercel env add DATABASE_URL production
# Plak je connection string wanneer gevraagd
```

### Via Vercel Dashboard:
1. Ga naar: https://vercel.com/media2net-apps-projects/marktplaats/settings/environment-variables
2. Klik op **Add New**
3. Naam: `DATABASE_URL`
4. Waarde: plak je connection string
5. Selecteer: **Production**, **Preview**, **Development**
6. Klik op **Save**

## Database Migratie

Na het instellen van `DATABASE_URL`, moet je de database schema aanmaken:

### Optie A: Via Vercel (aanbevolen)
1. Ga naar je Vercel deployment
2. Open de terminal/console
3. Run: `npx prisma db push`

### Optie B: Lokaal (met production DATABASE_URL)
```bash
# Haal environment variables op
vercel env pull .env.production

# Push schema naar database
npx prisma db push
```

## Test je Database Connectie

```bash
# Test lokaal (met .env.production)
npx prisma studio
```

Of test via een database client zoals:
- TablePlus
- DBeaver
- pgAdmin

## Belangrijk:

- **Gebruik SSL**: Zorg dat je connection string `?sslmode=require` bevat
- **Beveilig je credentials**: Deel je connection string NOOIT publiekelijk
- **Backup**: Zorg voor regelmatige backups van je productie database


















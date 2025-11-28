# Vercel Setup Instructies

## Probleem: 404 NOT_FOUND Error

Als je een 404 error krijgt op https://marktplaats-eight.vercel.app/, is dit meestal omdat Vercel de verkeerde root directory gebruikt.

## Oplossing: Root Directory Instellen

### Optie 1: Via Vercel Dashboard (Aanbevolen)

1. Ga naar https://vercel.com/dashboard
2. Selecteer je project: **marktplaats** of **marktplaats-eight**
3. Ga naar **Settings** → **General**
4. Scroll naar **Root Directory**
5. Klik op **Edit**
6. Stel in op: `webapp`
7. Klik op **Save**

### Optie 2: Via Vercel CLI

```bash
cd webapp
vercel link
# Selecteer je bestaande project
# Wanneer gevraagd naar root directory, geef op: . (punt, omdat je al in webapp bent)
```

### Optie 3: Herdeploy vanuit webapp directory

```bash
cd webapp
vercel --prod
```

## Environment Variables Controleren

Zorg dat de volgende environment variables zijn ingesteld in Vercel:

1. **DATABASE_URL** - Je PostgreSQL connection string (Prisma Accelerate URL)
   - Format: `prisma+postgres://...` of `postgresql://...`
   
2. **NEXTAUTH_SECRET** - Een willekeurige geheime string
   - Genereer met: `openssl rand -base64 32`
   
3. **NEXTAUTH_URL** - Je Vercel deployment URL
   - Bijvoorbeeld: `https://marktplaats-eight.vercel.app`
   
4. **INTERNAL_API_KEY** (optioneel) - Voor interne API communicatie

### Environment Variables Instellen:

1. Ga naar Vercel Dashboard → Je Project → **Settings** → **Environment Variables**
2. Voeg elke variable toe voor **Production**, **Preview**, en **Development**
3. Klik op **Save**

## Na het Instellen

Na het instellen van de root directory en environment variables:

1. Ga naar **Deployments** tab
2. Klik op de drie puntjes (⋯) naast de laatste deployment
3. Kies **Redeploy**
4. Of push een nieuwe commit naar GitHub

## Build Logs Controleren

Als het nog steeds niet werkt:

1. Ga naar **Deployments** tab
2. Klik op de laatste deployment
3. Bekijk de **Build Logs** voor errors
4. Controleer of:
   - `npm install` succesvol is
   - `prisma generate` succesvol is
   - `next build` succesvol is
   - Er geen missing dependencies zijn

## Veelvoorkomende Problemen

### 1. Database Connectie Fout
- Controleer of `DATABASE_URL` correct is
- Zorg dat je database toegankelijk is vanaf Vercel's servers
- Voor Prisma Accelerate: gebruik `prisma+postgres://` URL

### 2. Prisma Generate Fout
- Zorg dat `postinstall` script in package.json staat: `"postinstall": "prisma generate"`
- Controleer of Prisma schema correct is

### 3. Missing Dependencies
- Controleer of alle dependencies in `package.json` staan
- Run `npm install` lokaal om te testen

### 4. Python Scripts (Niet Beschikbaar op Vercel)
- Python scripts kunnen **niet** direct op Vercel draaien
- API routes die Python scripts aanroepen zullen falen op Vercel
- Overweeg om Python scripts te hosten op een andere service (bijv. Railway, Render, of een VPS)

## Test Lokaal

Test eerst lokaal of alles werkt:

```bash
cd webapp
npm install
npm run build
npm start
```

Als dit lokaal werkt, zou het ook op Vercel moeten werken (mits root directory en environment variables correct zijn ingesteld).


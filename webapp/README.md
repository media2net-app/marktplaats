# Marktplaats Automator Webapp

Next.js webapplicatie voor het beheren en automatisch plaatsen van advertenties op Marktplaats.

## Installatie

1. Installeer dependencies:
```bash
npm install
```

2. Kopieer `.env.local.example` naar `.env.local` en vul de waarden in:
```bash
cp .env.local.example .env.local
```

3. Initialiseer de database:
```bash
npx prisma generate
npx prisma db push
```

4. Maak een eerste gebruiker aan (via Prisma Studio of handmatig):
```bash
npx prisma studio
```

Of gebruik een seed script om een test gebruiker aan te maken.

## Development

Start de development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in je browser.

## Structuur

- `/app` - Next.js App Router pages en API routes
- `/components` - React components
- `/lib` - Utility functies (auth, database)
- `/prisma` - Database schema

## Features

- ✅ Gebruikers authenticatie met NextAuth
- ✅ Product beheer (CRUD)
- ✅ Automatisch plaatsen op Marktplaats via Python script
- ✅ Status tracking van geplaatste advertenties


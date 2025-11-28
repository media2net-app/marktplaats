# Vercel Deployment Instructies

## Stap 1: Installeer Vercel CLI (als nog niet geïnstalleerd)

```bash
npm install -g vercel
```

## Stap 2: Login op Vercel

```bash
vercel login
```

## Stap 3: Deploy naar Vercel

Navigeer naar de `webapp` directory en run:

```bash
cd webapp
vercel --name marktplaats --yes
```

Of gebruik het batch script:
```bash
deploy_vercel.bat
```

## Stap 4: Environment Variables instellen

Na de eerste deployment, ga naar het Vercel dashboard en voeg de volgende environment variables toe:

1. **DATABASE_URL** - Je PostgreSQL connection string (Prisma Accelerate URL)
2. **NEXTAUTH_SECRET** - Een willekeurige geheime string (genereer met: `openssl rand -base64 32`)
3. **NEXTAUTH_URL** - Je Vercel deployment URL (bijv. `https://marktplaats.vercel.app`)
4. **INTERNAL_API_KEY** - Een geheime API key voor interne communicatie tussen Next.js en Python scripts

## Stap 5: Production Database migratie

Na het instellen van environment variables, run een nieuwe deployment zodat Prisma de database kan migreren:

```bash
cd webapp
vercel --prod
```

## Belangrijke Notities

- **Database**: Zorg dat je PostgreSQL database (Prisma Accelerate) al is ingesteld en toegankelijk is
- **Media Files**: De `public/media` folder wordt niet automatisch geüpload. Overweeg om media files op te slaan in een cloud storage service (bijv. AWS S3, Cloudinary)
- **Python Scripts**: De Python scripts draaien lokaal en kunnen niet direct op Vercel draaien. Overweeg om deze te hosten op een andere service of als serverless functions

## Troubleshooting

### Build fouten
- Controleer of alle environment variables correct zijn ingesteld
- Zorg dat `DATABASE_URL` correct is en toegankelijk is vanaf Vercel's servers
- Check de build logs in Vercel dashboard voor specifieke foutmeldingen

### Database connectie problemen
- Zorg dat je Prisma Accelerate URL correct is
- Controleer of je database firewall/whitelist Vercel's IP adressen toestaat
- Test de database connectie lokaal eerst


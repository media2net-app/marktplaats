# Deployment Guide

## Environment Variables

Voor live deployment moet je de volgende environment variabelen instellen:

### Next.js Web App (`.env.local` of hosting platform environment variables)

```env
# Database
DATABASE_URL="prisma+postgres://..." # Je Prisma Accelerate URL

# NextAuth
NEXTAUTH_URL="https://jouw-domein.nl"
NEXTAUTH_SECRET="een-veilige-random-string-minimaal-32-karakters"

# Internal API Key (voor Python scripts)
INTERNAL_API_KEY="een-veilige-random-string-voor-api-authenticatie"

# Optioneel: API Base URL (als anders dan NEXTAUTH_URL)
API_BASE_URL="https://jouw-domein.nl"
```

### Python Scripts (`.env` in project root)

```env
# Playwright persistent context directory
USER_DATA_DIR=./user_data

# Base URL for Marktplaats
MARKTPLAATS_BASE_URL=https://www.marktplaats.nl

# Root folder for product photos
MEDIA_ROOT=./public/media

# Optional: slow down actions for stability (in ms)
ACTION_DELAY_MS=200

# API Configuration (voor batch processing)
NEXTAUTH_URL=https://jouw-domein.nl
API_BASE_URL=https://jouw-domein.nl
INTERNAL_API_KEY=zelfde-als-in-nextjs-env
```

## Belangrijke Notities voor Live Deployment

### 1. API Key Security
- **Wijzig de default API key** (`internal-key-change-in-production`) naar een veilige random string
- Gebruik dezelfde `INTERNAL_API_KEY` in zowel Next.js als Python `.env`
- Deel deze key NOOIT publiekelijk

### 2. Database
- Gebruik Prisma Accelerate of een andere PostgreSQL database
- Zorg dat de `DATABASE_URL` correct is ingesteld
- Run `npx prisma db push` of `npx prisma migrate deploy` na deployment

### 3. File Storage
- Zorg dat de `MEDIA_ROOT` directory bestaat en schrijfbaar is
- Voor cloud deployment, overweeg cloud storage (S3, etc.) en pas de upload code aan

### 4. Python Scripts
- Installeer dependencies: `pip install -r requirements.txt`
- Installeer Playwright browsers: `python -m playwright install chromium`
- Zorg dat de scripts toegang hebben tot de media directory

### 5. Next.js Deployment
- Build command: `npm run build`
- Start command: `npm start` (of gebruik hosting platform defaults)
- Zorg dat Node.js versie 18+ wordt gebruikt

### 6. API Endpoints
De volgende endpoints zijn beschikbaar voor de Python scripts:
- `GET /api/products/pending?api_key=YOUR_KEY` - Haal pending producten op
- `POST /api/products/batch-update` (met `x-api-key` header) - Update meerdere producten
- `GET /api/products/export/[id]?api_key=YOUR_KEY` - Export één product

## Testing

Na deployment, test de API authenticatie:

```bash
# Test pending products endpoint
curl "https://jouw-domein.nl/api/products/pending?api_key=YOUR_KEY"

# Test met header
curl -H "x-api-key: YOUR_KEY" "https://jouw-domein.nl/api/products/pending"
```

## Troubleshooting

### 401 Unauthorized
- Controleer of `INTERNAL_API_KEY` correct is ingesteld in beide environments
- Controleer of de API key exact overeenkomt (geen extra spaties)
- Controleer of de Next.js server draait en bereikbaar is

### Database Errors
- Controleer `DATABASE_URL` format
- Zorg dat Prisma migrations zijn uitgevoerd
- Controleer database connectiviteit

### File Upload Errors
- Controleer `MEDIA_ROOT` pad en schrijfrechten
- Voor cloud deployment, overweeg cloud storage


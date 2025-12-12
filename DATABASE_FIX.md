# Database Configuratie Fix

## Probleem
De fout toont dat Prisma Accelerate verwacht een `file:` protocol (SQLite), maar de DATABASE_URL is ingesteld op PostgreSQL (Prisma Accelerate).

## Oplossing

Het schema is aangepast van SQLite naar PostgreSQL om compatibel te zijn met Prisma Accelerate.

### Voor Lokaal Gebruik

Als je lokaal SQLite wilt gebruiken, zet dan in `.env.local`:
```env
DATABASE_URL="file:./dev.db"
```

### Voor Productie (Vercel)

Zet in Vercel environment variables:
```env
DATABASE_URL="prisma+postgres://..."  # Je Prisma Accelerate URL
```

## Na de Wijziging

1. **Lokaal**: 
   - Als je SQLite gebruikt: `DATABASE_URL="file:./dev.db"` in `.env.local`
   - Als je PostgreSQL gebruikt: `DATABASE_URL="postgresql://..."` of `prisma+postgres://...`

2. **Regenerate Prisma Client**:
   ```bash
   npx prisma generate
   ```

3. **Database Migratie** (als je van SQLite naar PostgreSQL switcht):
   ```bash
   npx prisma migrate dev --name switch_to_postgresql
   ```
   Of voor productie:
   ```bash
   npx prisma migrate deploy
   ```

## Belangrijk

- **Lokaal**: Kan SQLite gebruiken (`file:./dev.db`)
- **Productie**: Moet PostgreSQL gebruiken (Prisma Accelerate of direct PostgreSQL)
- Het schema is nu ingesteld op PostgreSQL om compatibel te zijn met beide

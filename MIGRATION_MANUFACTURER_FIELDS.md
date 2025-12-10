# Database Migratie - Fabrikant Velden

## ✅ Wat is toegevoegd:

3 nieuwe standaard velden voor producten:
1. **Handelsnaam fabrikant** (max 255 tekens)
2. **Postadres fabrikant** (max 255 tekens)
3. **E-mailadres fabrikant** (max 255 tekens)

## 📋 Database Migratie Uitvoeren:

De database migratie moet worden uitgevoerd om de nieuwe velden toe te voegen aan de database.

### Optie 1: Lokaal (Aanbevolen)

```bash
npx prisma migrate dev --name add_manufacturer_fields
```

Dit zal:
- Een nieuwe migratie aanmaken
- De migratie toepassen op je lokale database
- Prisma Client regenereren

### Optie 2: Via Prisma Studio

Als je Prisma Accelerate gebruikt, kan je de migratie handmatig uitvoeren via Prisma Studio of direct via SQL:

```sql
ALTER TABLE "Product" 
ADD COLUMN "manufacturerName" TEXT,
ADD COLUMN "manufacturerAddress" TEXT,
ADD COLUMN "manufacturerEmail" TEXT;
```

### Optie 3: Via Vercel/Production

Voor productie, gebruik:

```bash
npx prisma migrate deploy
```

## ✅ Wat is al gedaan:

1. ✅ Prisma schema bijgewerkt (`prisma/schema.prisma`)
2. ✅ ProductForm component bijgewerkt met nieuwe velden
3. ✅ API routes bijgewerkt (POST en PUT)
4. ✅ Interface bijgewerkt
5. ✅ Form reset bijgewerkt
6. ✅ Prisma Client geregenereerd

## 📍 Locatie van velden in formulier:

De fabrikant velden worden getoond **na de categorie-specifieke velden** en **voor de beschrijving** in het product formulier.

Ze zijn altijd zichtbaar (niet afhankelijk van categorie selectie).

## 🔍 Features:

- **Max lengte**: 255 tekens per veld
- **Character counter**: Toont aantal tekens (bijv. "0/255")
- **Email validatie**: E-mailadres veld heeft email type
- **Help tekst**: Link naar Marktplaats informatie over EU fabrikanten
- **Optioneel**: Alle velden zijn optioneel (niet verplicht)

## 🚀 Na migratie:

1. Test het formulier lokaal
2. Maak een nieuw product aan
3. Check of de fabrikant velden worden opgeslagen
4. Deploy naar productie


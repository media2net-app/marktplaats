# Vercel Blob Storage Setup

Om foto uploads te laten werken op Vercel (productie), moet je Vercel Blob Storage configureren.

## Stap 1: Vercel Blob Storage Token Ophalen

1. Ga naar je Vercel Dashboard: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats**
3. Ga naar **Settings** → **Storage**
4. Klik op **Create Database** of **Add Storage**
5. Selecteer **Blob Storage**
6. Maak een nieuwe Blob Storage aan (of gebruik bestaande)
7. Kopieer de **BLOB_READ_WRITE_TOKEN**

## Stap 2: Environment Variable Toevoegen

1. Ga naar **Settings** → **Environment Variables**
2. Klik op **Add New**
3. Voeg toe:
   - **Key**: `BLOB_READ_WRITE_TOKEN`
   - **Value**: De token die je hebt gekopieerd
   - **Environments**: Selecteer **Production**, **Preview**, en **Development**
4. Klik op **Save**

## Stap 3: Redeploy

Na het toevoegen van de environment variable:

1. Ga naar **Deployments** tab
2. Klik op de drie puntjes (⋯) naast de laatste deployment
3. Kies **Redeploy**

Of push een nieuwe commit naar GitHub.

## Alternatief: Zonder Blob Storage (Niet Aanbevolen)

Als je geen Vercel Blob Storage wilt gebruiken, zal de applicatie automatisch terugvallen op lokale opslag. **Dit werkt NIET op Vercel serverless**, omdat het bestandssysteem read-only is.

Voor productie is Vercel Blob Storage **verplicht** voor foto uploads.

## Kosten

Vercel Blob Storage heeft een gratis tier:
- **Gratis**: 1 GB opslag, 100 GB bandwidth per maand
- **Pro**: $0.15 per GB opslag, $0.40 per GB bandwidth

Voor de meeste gebruikers is de gratis tier voldoende.

## Troubleshooting

### "BLOB_READ_WRITE_TOKEN not configured"
- Zorg dat je de environment variable hebt toegevoegd in Vercel
- Zorg dat je hebt gere-deployed na het toevoegen

### Foto's worden niet getoond
- Controleer of de blob storage token correct is
- Check de browser console voor errors
- Controleer de Vercel logs voor upload errors

### Upload werkt lokaal maar niet op productie
- Dit is normaal - lokaal gebruikt het filesystem, productie gebruikt blob storage
- Zorg dat `BLOB_READ_WRITE_TOKEN` is ingesteld in Vercel
















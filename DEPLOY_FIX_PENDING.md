# Fix: Pending Producten API

## Probleem
Het script vond geen pending producten terwijl er wel 2 producten op wachten stonden.

## Oorzaak
De API gebruikte bij API-key authenticatie alleen de eerste gebruiker, terwijl de producten van een andere gebruiker waren.

## Oplossing
De API is aangepast om bij API-key authenticatie **alle pending producten** op te halen (van alle gebruikers).

## Bestanden aangepast
1. `app/api/products/pending/route.ts` - Haalt nu alle pending producten op
2. `app/api/products/batch-post/route.ts` - Telt nu alle producten (niet alleen eerste gebruiker)

## Deploy naar Vercel

Voer dit uit om te deployen:

```bash
cd /Users/gebruiker/Desktop/marktplaats
git add app/api/products/pending/route.ts app/api/products/batch-post/route.ts
git commit -m "Fix: API haalt nu alle pending producten op bij API key authenticatie"
git push
```

Of gebruik het deploy script:

```bash
./deploy_vercel.sh
```

Na deployment zou het script de pending producten moeten vinden!

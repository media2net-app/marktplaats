# ⚠️ BELANGRIJK: Zet INTERNAL_API_KEY in Vercel!

## Probleem
Je krijgt een "401 Unauthorized" fout omdat de `INTERNAL_API_KEY` niet in Vercel staat.

## Oplossing

### Stap 1: Ga naar Vercel Dashboard

1. Open: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats**
3. Ga naar: **Settings** > **Environment Variables**

### Stap 2: Voeg INTERNAL_API_KEY toe

1. Klik op **"Add New"**
2. Vul in:
   - **Name**: `INTERNAL_API_KEY`
   - **Value**: `LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=`
   - **Environment**: Selecteer ALLE drie:
     - ✅ Production
     - ✅ Preview  
     - ✅ Development
3. Klik op **"Save"**

### Stap 3: Redeploy je app (BELANGRIJK!)

Na het toevoegen van de environment variable MOET je de app opnieuw deployen:

**Optie A: Via Vercel Dashboard**
1. Ga naar **Deployments** tab
2. Klik op de drie puntjes (⋯) naast de laatste deployment
3. Kies **"Redeploy"**
4. Wacht tot de deployment klaar is (ongeveer 1-2 minuten)

**Optie B: Via Terminal (als je Vercel CLI hebt)**
```bash
vercel --prod
```

### Stap 4: Test opnieuw

Na de redeploy, run `run_marktplaats.bat` opnieuw. Het zou nu moeten werken!

## Controleer of het werkt

Als je nog steeds "401 Unauthorized" krijgt:

1. ✅ Controleer of `INTERNAL_API_KEY` in Vercel staat
2. ✅ Controleer of de waarde EXACT hetzelfde is (geen extra spaties!)
3. ✅ Controleer of je ALLE environments hebt geselecteerd (Production, Preview, Development)
4. ✅ Controleer of je de app hebt geredeployed NA het toevoegen van de key
5. ✅ Wacht 1-2 minuten na redeploy voordat je test

## Debug informatie

Als je de debug output ziet:
```
[DEBUG] INTERNAL_API_KEY aanwezig: Ja
```

Dan wordt de key goed gelezen uit je `.env` bestand. Het probleem is dat Vercel de key niet heeft, of de app is niet geredeployed.

## Nog steeds problemen?

Als het na deze stappen nog steeds niet werkt:

1. Controleer in Vercel of de key er echt staat:
   - Ga naar Settings > Environment Variables
   - Zoek naar `INTERNAL_API_KEY`
   - Controleer of de waarde correct is

2. Controleer of de deployment is voltooid:
   - Ga naar Deployments tab
   - De laatste deployment moet status "Ready" hebben

3. Test de API handmatig:
   - Open in browser: `https://marktplaats-eight.vercel.app/api/products/pending?api_key=LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=`
   - Als je "Unauthorized" krijgt, staat de key niet goed in Vercel
   - Als je JSON data krijgt, werkt het!



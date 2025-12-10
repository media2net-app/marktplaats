# Hoe vind ik mijn INTERNAL_API_KEY?

## Optie 1: Check Vercel Environment Variables (als je het al hebt ingesteld)

1. Ga naar: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats**
3. Ga naar **Settings** > **Environment Variables**
4. Zoek naar `INTERNAL_API_KEY`
5. Als je het ziet, kopieer de waarde en gebruik die in je `.env` bestand

## Optie 2: Maak een nieuwe INTERNAL_API_KEY aan

Als je nog geen `INTERNAL_API_KEY` hebt ingesteld, maak er dan een aan:

### Stap 1: Genereer een veilige key

**Op Mac/Linux:**
```bash
openssl rand -base64 32
```

**Op Windows (PowerShell):**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Of gebruik een online generator:**
- Ga naar: https://randomkeygen.com/
- Kies "CodeIgniter Encryption Keys" of "Fort Knox Password"
- Kopieer een van de gegenereerde keys

**Of gebruik deze (vervang door je eigen unieke key):**
```
mkp-internal-2024-secure-key-change-this-to-something-random
```

### Stap 2: Zet het in Vercel

1. Ga naar: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats**
3. Ga naar **Settings** > **Environment Variables**
4. Klik op **Add New**
5. Vul in:
   - **Name**: `INTERNAL_API_KEY`
   - **Value**: (plak de key die je hebt gegenereerd)
   - **Environment**: Selecteer alle (Production, Preview, Development)
6. Klik op **Save**

### Stap 3: Redeploy je app

Na het toevoegen van de environment variable:

1. Ga naar **Deployments** tab
2. Klik op de drie puntjes (⋯) naast de laatste deployment
3. Kies **Redeploy**

Of via terminal:
```bash
vercel --prod
```

### Stap 4: Gebruik dezelfde key in je .env

In je `.env` bestand (lokaal of in Mike_Final):
```
INTERNAL_API_KEY=dezelfde-key-als-in-vercel
```

⚠️ **BELANGRIJK**: De key in je `.env` moet EXACT hetzelfde zijn als in Vercel!

## Optie 3: Gebruik de default (alleen voor testen)

Als je snel wilt testen zonder Vercel in te stellen, kun je tijdelijk de default gebruiken:

```
INTERNAL_API_KEY=internal-key-change-in-production
```

⚠️ **WAARSCHUWING**: Dit is niet veilig voor productie! Gebruik dit alleen voor lokale tests.

## Controleer of het werkt

Na het instellen, test of het werkt:

1. Open je `.env` bestand
2. Zorg dat `INTERNAL_API_KEY` dezelfde waarde heeft als in Vercel
3. Run `run_marktplaats.bat` (of `run_marktplaats.sh` op Mac)
4. Als je geen "Unauthorized" fout krijgt, werkt het!

## Troubleshooting

**"Unauthorized: Invalid API key"**
- Controleer of de key in `.env` EXACT hetzelfde is als in Vercel (geen extra spaties!)
- Controleer of je de key hebt toegevoegd aan Vercel
- Controleer of je app opnieuw hebt gedeployed na het toevoegen van de key

**"INTERNAL_API_KEY not found"**
- Zorg dat je `.env` bestand in dezelfde map staat als `run_marktplaats.bat`
- Controleer of de regel begint met `INTERNAL_API_KEY=` (geen spaties rond de `=`)
- Controleer of er geen `#` voor de regel staat (dat maakt het een commentaar)



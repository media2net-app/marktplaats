# Troubleshooting: "Je gebruikt nog localhost!"

## Probleem
Het script zegt dat je nog localhost gebruikt, terwijl je `.env` bestand de juiste URL heeft.

## Oplossing

### Stap 1: Controleer waar je .env bestand staat

Het `.env` bestand MOET in dezelfde map staan als `run_marktplaats.bat`:

```
Mike_Final/
├── .env                    ← HIER moet het staan!
├── run_marktplaats.bat
├── requirements.txt
└── scripts/
    └── post_all_pending.py
```

### Stap 2: Controleer de inhoud van je .env

Open je `.env` bestand en controleer:

1. **Geen spaties rond de `=`**
   ```
   ✅ GOED: NEXTAUTH_URL=https://marktplaats-eight.vercel.app
   ❌ FOUT: NEXTAUTH_URL = https://marktplaats-eight.vercel.app
   ```

2. **Geen quotes nodig**
   ```
   ✅ GOED: NEXTAUTH_URL=https://marktplaats-eight.vercel.app
   ❌ FOUT: NEXTAUTH_URL="https://marktplaats-eight.vercel.app"
   ```

3. **Geen commentaar op dezelfde regel**
   ```
   ✅ GOED: NEXTAUTH_URL=https://marktplaats-eight.vercel.app
   ❌ FOUT: NEXTAUTH_URL=https://marktplaats-eight.vercel.app  # mijn URL
   ```

4. **Geen lege regels met alleen spaties**
   - Verwijder lege regels of regels met alleen spaties

### Stap 3: Controleer de bestandsnaam

- Het bestand moet heten: `.env` (met de punt vooraan!)
- NIET: `env`, `.env.txt`, `env.example`, etc.

### Stap 4: Test het script

Run het script opnieuw. Je zou nu debug output moeten zien:

```
[DEBUG] .env geladen van: D:\Users\Highscreen\Desktop\Mike_Final\.env
[DEBUG] NEXTAUTH_URL uit .env: https://marktplaats-eight.vercel.app
[DEBUG] API_BASE_URL uit .env: https://marktplaats-eight.vercel.app
[DEBUG] base_url (gebruikt): https://marktplaats-eight.vercel.app
```

Als je ziet dat `base_url (gebruikt)` nog steeds `localhost` is, dan wordt de `.env` niet goed gelezen.

### Stap 5: Handmatig testen

Open PowerShell in de `Mike_Final` map en test:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('NEXTAUTH_URL:', os.getenv('NEXTAUTH_URL'))"
```

Als dit `None` of `localhost` toont, dan wordt de `.env` niet gelezen.

## Veelvoorkomende fouten

### Fout 1: .env staat in verkeerde map
```
Mike_Final/
├── .env                    ← FOUT: staat hier
└── scripts/
    └── .env                ← FOUT: of hier
```

**Oplossing**: Verplaats `.env` naar de root van `Mike_Final` (waar `run_marktplaats.bat` staat)

### Fout 2: Bestand heet niet .env
```
Mike_Final/
├── env                     ← FOUT
├── .env.txt                ← FOUT
└── .env.example            ← FOUT (dit is alleen een voorbeeld!)
```

**Oplossing**: Hernoem naar `.env` (met de punt!)

### Fout 3: Verkeerde encoding
Windows kan soms problemen hebben met de encoding.

**Oplossing**: 
1. Open `.env` in Kladblok
2. Kies "Opslaan als"
3. Encoding: "UTF-8"
4. Sla op als `.env` (zonder .txt extensie)

### Fout 4: Verborgen bestand
Windows verbergt soms bestanden die beginnen met een punt.

**Oplossing**:
1. Open File Explorer
2. Ga naar "View" tab
3. Vink "Hidden items" aan
4. Controleer of `.env` zichtbaar is

## Nog steeds problemen?

Als het nog steeds niet werkt:

1. Kopieer de volledige debug output
2. Controleer of `.env` in de juiste map staat
3. Controleer of de waarden correct zijn (geen spaties, geen quotes)
4. Probeer het script opnieuw


# Check API Key in Vercel

## Probleem
Het script vindt geen pending producten, en de debug endpoints geven 401 errors.

## Mogelijke Oorzaak
De `INTERNAL_API_KEY` in Vercel komt mogelijk niet overeen met de key in je `.env.local`.

## Oplossing

### Stap 1: Check je lokale API key
```bash
cd /Users/gebruiker/Desktop/marktplaats
grep INTERNAL_API_KEY .env.local
```

Of check het bestand:
```bash
cat INTERNAL_API_KEY.txt
```

### Stap 2: Check Vercel Environment Variables

1. Ga naar: https://vercel.com/dashboard
2. Selecteer je project: **marktplaats** of **marktplaats-eight**
3. Ga naar: **Settings** → **Environment Variables**
4. Zoek: `INTERNAL_API_KEY`
5. Check of de waarde EXACT hetzelfde is als in je `.env.local`

### Stap 3: Update als nodig

Als de key niet overeenkomt of ontbreekt:

1. Kopieer de key uit `INTERNAL_API_KEY.txt`:
   ```
   LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=
   ```

2. Zet deze in Vercel:
   - Name: `INTERNAL_API_KEY`
   - Value: `LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=`
   - Environment: Alle (Production, Preview, Development)
   - Klik "Save"

3. **Redeploy**:
   - Ga naar **Deployments** tab
   - Klik op ⋯ naast laatste deployment
   - Kies "Redeploy"

### Stap 4: Test opnieuw

Na redeploy, wacht 1-2 minuten en test:
```bash
cd local_worker
./Post\ Pending\ \(Productie\).command
```

## Belangrijk
- De API key moet EXACT hetzelfde zijn (geen extra spaties!)
- Zorg dat je redeploy doet na het aanpassen van environment variables

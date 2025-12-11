# Vercel Environment Variable - BLOB_READ_WRITE_TOKEN

## ⚠️ BELANGRIJK: Voeg deze environment variable toe in Vercel!

Ga naar: https://vercel.com/media2net-apps-projects/marktplaats/settings/environment-variables

## Environment Variable:

**Key:** `BLOB_READ_WRITE_TOKEN`

**Value:** 
```
vercel_blob_rw_uAvAROUzbMYRyRq4_UsFiWw0TazSzsrRL4hsIv5IkhFLses
```

**Environments:** Selecteer **Production**, **Preview**, en **Development**

## Stappen:

1. Ga naar: https://vercel.com/media2net-apps-projects/marktplaats/settings/environment-variables
2. Klik op **Add New**
3. Voeg de variable toe zoals hierboven
4. Klik op **Save**
5. Ga naar **Deployments** tab
6. Klik op de drie puntjes (⋯) naast de laatste deployment
7. Kies **Redeploy**

## Na het instellen:

Na het toevoegen van de environment variable, moet je opnieuw deployen:
```bash
vercel --prod
```

Of via het Vercel dashboard: klik op "Redeploy" bij de laatste deployment.

## Testen:

Na de redeploy, test foto upload:
1. Ga naar je live site
2. Probeer een product toe te voegen met foto's
3. Controleer of de foto's worden geüpload en getoond



















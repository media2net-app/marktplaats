# Hoe Service ID Vinden - Stap voor Stap

Je bent nu op **Project Settings**. Je moet naar **Service Settings** gaan!

## 🔍 Methode 1: Via Service Settings (Aanbevolen)

1. **Ga terug naar je project** (klik op "humble-acceptance" linksboven of ga naar je project)
2. **Klik op je SERVICE** (niet op het project, maar op de service binnen het project)
   - Dit is meestal de service die je worker draait
   - De naam kan zijn: "marktplaats", "worker", of iets anders
3. **Klik op "Settings"** (service settings, niet project settings)
   - Dit is de settings van de SERVICE, niet van het PROJECT
4. **Scroll naar "General"** sectie
5. **Zoek "Service ID"** - dit is wat je nodig hebt!

## 🔍 Methode 2: Via URL

1. **Ga naar je service** in Railway
2. **Klik op je service** (de worker service)
3. **Kijk naar de URL** in je browser
4. De URL ziet eruit als:
   ```
   https://railway.app/project/d7cf2713-0d81-4820-b62f-cd732285675c/service/{SERVICE_ID}
   ```
5. **Het SERVICE_ID deel** (na `/service/`) is wat je nodig hebt!

## 🔍 Methode 3: Via Service List

1. **Ga naar je project** in Railway
2. **Je ziet een lijst van services** (meestal 1 of meer)
3. **Klik op de service** die je worker draait
   - Dit is meestal de Python service
   - Of de service met "worker" in de naam
4. **In de URL** zie je: `/service/{SERVICE_ID}`
5. **Kopieer de SERVICE_ID**

## 🔍 Methode 4: Via Railway CLI (Als je CLI hebt)

```bash
railway service
```

Dit toont alle services met hun IDs.

## 🔍 Methode 5: Via API (Als je de token hebt)

Je kunt de Service ID ook via de API ophalen, maar dat is complexer.

## ⚠️ Belangrijk Verschil

- **Project Settings**: Dit is wat je nu ziet - hier vind je **Project ID**
- **Service Settings**: Dit is wat je nodig hebt - hier vind je **Service ID**

## 📸 Visuele Gids

1. **Project pagina** → Zie je alle services
2. **Klik op een service** → Ga je naar die service
3. **Klik "Settings"** → Service Settings (niet Project Settings!)
4. **Scroll naar "General"** → Zie je Service ID

## 💡 Tips

- Als je maar **1 service** hebt, klik daarop
- Als je **meerdere services** hebt, zoek de service die:
  - Python gebruikt
  - `railway_worker.py` draait
  - "Worker" of "Marktplaats" in de naam heeft
- De Service ID is een **UUID** (zoals: `abc123-def456-...`)

## 🆘 Nog steeds niet gevonden?

1. **Maak een screenshot** van je Railway project pagina (waar je alle services ziet)
2. Of **vertel me hoeveel services** je hebt en wat hun namen zijn
3. Dan kan ik je precies vertellen welke je nodig hebt!


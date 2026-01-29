# Systeem Analyse - Marktplaats Automator

## Huidige Situatie

### Structuur
Het systeem bestaat uit:
1. **Next.js Web App** - Frontend/backend voor productbeheer
2. **Python Scripts** - Browser automatisering met Playwright
3. **Meerdere Entry Points** - Verwarrende structuur

### Entry Points (Probleem: Te Veel!)
- `scripts/post_marktplaats_standalone.py` - Standalone versie die API gebruikt
- `local_worker/post_pending_local.py` - Lokale worker versie
- `scripts/post_ads.py` - Core browser automatisering
- `scripts/post_all_pending.py` - Nog een variant

### Hoe het NU werkt:
1. Script haalt pending producten op via API
2. Downloadt foto's van API naar tijdelijke map
3. Opent browser met Playwright (persistent context)
4. **Verwacht dat gebruiker al ingelogd is** (geen automatische login!)
5. Plaatst producten automatisch
6. Update database met resultaten

### Problemen:
1. **Geen automatische login** - Systeem verwacht dat je al ingelogd bent
2. **Complexe code** - Veel fallbacks en strategieën maken het moeilijk te debuggen
3. **Meerdere entry points** - Verwarrend welke te gebruiken
4. **Oude code** - Mike/ en Mike_Final/ folders met duplicate code
5. **Login check werkt niet goed** - `ensure_logged_in()` checkt alleen, logt niet in

## Gewenste Situatie

### Wat moet werken:
1. **Eén simpel script** dat je start op je PC
2. **Opent browser** automatisch
3. **Helpt met inloggen** (of automatisch als mogelijk)
4. **Plaatst producten** automatisch op Marktplaats
5. **Werkt betrouwbaar** zonder complexe configuratie

## Plan van Aanpak

### Stap 1: Nieuwe Eenvoudige Entry Point
- Maak `marktplaats_poster.py` - één duidelijk script
- Combineert functionaliteit van standalone + local worker
- Duidelijke foutmeldingen en logging

### Stap 2: Verbeter Login
- Betere detectie of gebruiker ingelogd is
- Duidelijke instructies als niet ingelogd
- Optioneel: Automatische login flow (als credentials beschikbaar zijn)

### Stap 3: Vereenvoudig Code
- Schoon op `post_ads.py`
- Verwijder onnodige complexiteit
- Betere error handling

### Stap 4: Opruimen
- Verwijder oude code (Mike/, Mike_Final/)
- Update batch files
- Documentatie updaten

### Stap 5: Testen
- Test volledige flow
- Zorg dat het werkt op Windows PC

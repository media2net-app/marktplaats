# Marktplaats Automator - Standalone Versie

Dit is een standalone versie van de Marktplaats Automator die werkt zonder toegang tot lokale bestanden. Alles wordt via de API opgehaald.

## Vereisten

- Windows 10 of hoger
- Python 3.9 of hoger ([Download hier](https://www.python.org/downloads/))
  - **Belangrijk:** Vink "Add Python to PATH" aan tijdens installatie!

## Installatie (Eerste keer)

1. Dubbelklik op `install_and_run_marktplaats.bat`
2. Het script installeert automatisch alle benodigde dependencies
3. Dit kan enkele minuten duren (vooral het downloaden van Chromium)

## Gebruik

### Eerste keer
- Dubbelklik op `install_and_run_marktplaats.bat`
- Dit installeert alles en voert het script direct uit

### Volgende keren
- Dubbelklik op `run_marktplaats_standalone.bat`
- Het script haalt automatisch alle pending producten op en plaatst ze op Marktplaats

## Wat doet het script?

1. **Verbindt met de productie database** via de API
2. **Haalt alle pending producten op** die geplaatst moeten worden
3. **Downloadt foto's** van de productie server naar een tijdelijke map
4. **Opent Chrome** op je computer
5. **Logt in op Marktplaats** (gebruikt je bestaande Chrome sessie)
6. **Plaatst elk product** automatisch op Marktplaats
7. **Update de database** met de resultaten (status, URL, views, etc.)
8. **Ruimt tijdelijke bestanden op**

## Configuratie

De API URL en key staan in `scripts/post_marktplaats_standalone.py`:

```python
API_BASE_URL = 'https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app'
API_KEY = 'internal-key-change-in-production'
```

Als de API URL verandert, pas deze aan in het script.

## Troubleshooting

### "Python is niet geinstalleerd"
- Installeer Python van https://www.python.org/downloads/
- Zorg dat je "Add Python to PATH" aanvinkt

### "Script niet gevonden"
- Zorg dat alle bestanden in dezelfde map staan
- De mapstructuur moet zijn:
  ```
  marktplaats/
  ├── install_and_run_marktplaats.bat
  ├── run_marktplaats_standalone.bat
  └── scripts/
      ├── post_marktplaats_standalone.py
      ├── post_ads.py
      └── ... (andere script bestanden)
  ```

### "Fout bij ophalen producten"
- Controleer je internetverbinding
- Controleer of de API URL correct is
- Neem contact op als het probleem aanhoudt

### Chrome opent niet / Script werkt niet
- Zorg dat Chrome geinstalleerd is
- Sluit andere Chrome vensters
- Probeer het opnieuw

## Opmerkingen

- Het script gebruikt je bestaande Chrome sessie, dus je moet al ingelogd zijn op Marktplaats
- Foto's worden tijdelijk gedownload en automatisch opgeruimd na gebruik
- Het script werkt volledig standalone - geen lokale database of bestanden nodig
















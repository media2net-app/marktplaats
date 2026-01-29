# eBay Integratie Setup

Deze applicatie ondersteunt nu het plaatsen van producten op eBay via de eBay Inventory API.

## Vereisten

1. **eBay Developer Account**
   - Maak een account aan op: https://developer.ebay.com/
   - Maak een nieuwe applicatie aan in de Developer Portal
   - Noteer je credentials (App ID, Cert ID, Dev ID)

2. **Business Policies**
   - Je moet Business Policies hebben ingesteld in je eBay account
   - Dit zijn: Payment Policy, Return Policy, en Fulfillment Policy
   - Je hebt de Policy IDs nodig voor de configuratie

## Environment Variables

Voeg de volgende environment variables toe aan je `.env` bestand of Vercel environment variables:

### Verplicht

```bash
# eBay API Credentials (Sandbox)
EBAY_APP_ID=your-ebay-app-id-here
EBAY_CERT_ID=your-ebay-cert-id-here
EBAY_DEV_ID=your-ebay-dev-id-here

# eBay Environment (true voor sandbox, false voor production)
EBAY_SANDBOX=true

# eBay Business Policies (vereist voor listings)
EBAY_PAYMENT_POLICY_ID=je-payment-policy-id
EBAY_RETURN_POLICY_ID=je-return-policy-id
EBAY_FULFILLMENT_POLICY_ID=je-fulfillment-policy-id

# eBay Merchant Location Key (standaard locatie voor inventory)
EBAY_MERCHANT_LOCATION_KEY=default_location
```

### Optioneel

```bash
# eBay User Token (OAuth token - optioneel, anders gebruikt de app client credentials)
EBAY_USER_TOKEN=je-user-token-hier
```

## Sandbox vs Production

### Sandbox (Testomgeving)
- Gebruik sandbox credentials van eBay Developer Portal
- Set `EBAY_SANDBOX=true`
- Test listings verschijnen op: https://sandbox.ebay.nl

### Production (Live)
- Gebruik production credentials van eBay Developer Portal
- Set `EBAY_SANDBOX=false`
- Listings verschijnen op: https://www.ebay.nl

## Business Policies Setup

1. Log in op je eBay account (of sandbox account)
2. Ga naar **Account** → **Site Preferences** → **Business Policies**
3. Maak de volgende policies aan:
   - **Payment Policy**: Definieer betaalmethoden
   - **Return Policy**: Definieer retourvoorwaarden
   - **Fulfillment Policy**: Definieer verzendopties
4. Noteer de Policy IDs en voeg ze toe aan je environment variables

## OAuth Token (Optioneel)

Voor productie gebruik is het aanbevolen om een OAuth User Token te gebruiken:

1. Ga naar eBay Developer Portal
2. Ga naar je applicatie
3. Klik op "Get a User Token"
4. Volg de OAuth flow
5. Kopieer de token en voeg toe als `EBAY_USER_TOKEN`

Zonder user token gebruikt de app client credentials, wat beperkte rechten heeft.

## Gebruik

### Product plaatsen op eBay

1. Ga naar de productenlijst
2. Klik op **"Plaats op eBay"** bij een pending product
3. Het product wordt automatisch:
   - Geconverteerd naar een eBay inventory item
   - Een offer (listing) aangemaakt
   - Gepubliceerd op eBay

### Product informatie

Na plaatsing wordt de volgende informatie opgeslagen:
- `ebayUrl`: Link naar de eBay listing
- `ebayItemId`: eBay item ID
- `ebaySku`: SKU gebruikt voor inventory (gelijk aan artikelnummer)
- `postedToEbayAt`: Datum van plaatsing

## API Endpoints

### POST `/api/products/[id]/post-ebay`

Plaatst een product op eBay.

**Response:**
```json
{
  "success": true,
  "message": "Product succesvol geplaatst op eBay",
  "ebayUrl": "https://sandbox.ebay.nl/itm/123456789",
  "ebayItemId": "123456789",
  "offerId": "offer-123"
}
```

## Troubleshooting

### "eBay credentials not configured"
- Controleer of `EBAY_APP_ID`, `EBAY_CERT_ID`, en `EBAY_DEV_ID` zijn ingesteld

### "eBay business policies not configured"
- Controleer of alle drie de policy IDs zijn ingesteld
- Zorg dat de policies bestaan in je eBay account

### "Failed to get eBay access token"
- Controleer of je credentials correct zijn
- Voor sandbox, gebruik sandbox credentials
- Voor production, gebruik production credentials

### "Failed to create inventory location"
- De locatie bestaat mogelijk al - dit is normaal
- Controleer of `EBAY_MERCHANT_LOCATION_KEY` is ingesteld

### "Failed to create offer"
- Controleer of alle verplichte velden zijn ingevuld (titel, beschrijving, prijs)
- Zorg dat er minimaal één foto is geüpload
- Controleer of de business policies correct zijn ingesteld

## Categorie Mapping

Momenteel wordt er geen specifieke categorie mapping gedaan. eBay zal automatisch een categorie voorstellen of je kunt handmatig een categorie ID toevoegen in de code.

Voor productie gebruik, overweeg:
- Een categorie mapping tabel te maken
- eBay categorieën op te halen via de Taxonomy API
- Categorieën automatisch te matchen op basis van product eigenschappen

## Limitaties

- **Sandbox**: Test listings zijn alleen zichtbaar in sandbox omgeving
- **Categorieën**: Automatische categorie mapping is nog niet geïmplementeerd
- **Afbeeldingen**: Afbeeldingen moeten publiekelijk toegankelijk zijn (via URL)
- **Voorraad**: Momenteel wordt quantity altijd op 1 gezet

## Volgende Stappen

1. ✅ Basis integratie geïmplementeerd
2. ⏳ Categorie mapping toevoegen
3. ⏳ Bulk posting functionaliteit
4. ⏳ Listing updates/edits
5. ⏳ Order management integratie

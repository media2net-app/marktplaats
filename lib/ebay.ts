/**
 * eBay API Integration Service
 * 
 * This service handles communication with eBay's Inventory API
 * to create and manage listings.
 * 
 * Documentation: https://developer.ebay.com/api-docs/sell/inventory/overview.html
 */

interface EbayConfig {
  appId: string // Client ID
  certId: string // Client Secret
  devId: string // Developer ID
  userToken?: string // User Access Token (OAuth token)
  sandbox: boolean // Use sandbox environment
}

interface EbayInventoryItem {
  sku: string
  product?: {
    title: string
    description: string
    imageUrls: string[]
    aspects?: Record<string, string[]>
    condition?: string
    conditionDescription?: string
  }
  availability: {
    shipToLocationAvailability: {
      quantity: number
    }
  }
}

interface EbayOffer {
  sku: string
  marketplaceId: string // 'EBAY_NL' for Netherlands
  format: 'FIXED_PRICE' | 'AUCTION'
  listingDescription: string
  pricingSummary: {
    price: {
      value: string
      currency: string
    }
  }
  quantity: number
  categoryId?: string
  merchantLocationKey: string
  listingPolicies: {
    paymentPolicyId: string
    returnPolicyId: string
    fulfillmentPolicyId: string
  }
}

interface EbayLocation {
  location: {
    address: {
      addressLine1: string
      city: string
      postalCode: string
      countryCode: string
    }
  }
  name: string
  phone?: string
}

export class EbayApi {
  private config: EbayConfig
  private baseUrl: string
  private accessToken: string | null = null

  constructor(config: EbayConfig) {
    this.config = config
    this.baseUrl = config.sandbox
      ? 'https://api.sandbox.ebay.com'
      : 'https://api.ebay.com'
  }

  /**
   * Get OAuth access token using client credentials
   * For sandbox, we can use user token directly or get OAuth token
   */
  async getAccessToken(): Promise<string> {
    if (this.accessToken) {
      return this.accessToken
    }

    // If user token is provided, use it directly
    if (this.config.userToken) {
      this.accessToken = this.config.userToken
      return this.accessToken
    }

    // Otherwise, get OAuth token using client credentials
    const oauthUrl = this.config.sandbox
      ? 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
      : 'https://api.ebay.com/identity/v1/oauth2/token'

    const credentials = Buffer.from(
      `${this.config.appId}:${this.config.certId}`
    ).toString('base64')

    const response = await fetch(oauthUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: `Basic ${credentials}`,
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        scope: 'https://api.ebay.com/oauth/api_scope/sell.inventory',
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to get eBay access token: ${response.status} ${errorText}`)
    }

    const data = await response.json()
    this.accessToken = data.access_token
    if (!this.accessToken) {
      throw new Error('Failed to get access token')
    }
    return this.accessToken
  }

  /**
   * Create or update an inventory location
   */
  async createInventoryLocation(
    merchantLocationKey: string,
    location: EbayLocation
  ): Promise<void> {
    const token = await this.getAccessToken()
    const url = `${this.baseUrl}/sell/inventory/v1/location/${merchantLocationKey}`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_NL',
      },
      body: JSON.stringify(location),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(
        `Failed to create inventory location: ${response.status} ${errorText}`
      )
    }
  }

  /**
   * Create or replace an inventory item
   */
  async createOrReplaceInventoryItem(
    sku: string,
    item: EbayInventoryItem
  ): Promise<void> {
    const token = await this.getAccessToken()
    const url = `${this.baseUrl}/sell/inventory/v1/inventory_item/${sku}`

    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_NL',
      },
      body: JSON.stringify(item),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(
        `Failed to create inventory item: ${response.status} ${errorText}`
      )
    }
  }

  /**
   * Create an offer (listing) from an inventory item
   */
  async createOffer(offer: EbayOffer): Promise<{ offerId: string }> {
    const token = await this.getAccessToken()
    const url = `${this.baseUrl}/sell/inventory/v1/offer`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_NL',
      },
      body: JSON.stringify(offer),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to create offer: ${response.status} ${errorText}`)
    }

    const data = await response.json()
    return { offerId: data.offerId }
  }

  /**
   * Publish an offer to make it live on eBay
   */
  async publishOffer(offerId: string): Promise<{ listingId: string }> {
    const token = await this.getAccessToken()
    const url = `${this.baseUrl}/sell/inventory/v1/offer/${offerId}/publish`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_NL',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to publish offer: ${response.status} ${errorText}`)
    }

    const data = await response.json()
    return { listingId: data.listingId }
  }

  /**
   * Get offer details
   */
  async getOffer(offerId: string): Promise<any> {
    const token = await this.getAccessToken()
    const url = `${this.baseUrl}/sell/inventory/v1/offer/${offerId}`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_NL',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to get offer: ${response.status} ${errorText}`)
    }

    return await response.json()
  }

  /**
   * Map Marktplaats condition to eBay condition
   */
  static mapCondition(marktplaatsCondition: string | null): string {
    const conditionMap: Record<string, string> = {
      Nieuw: 'NEW',
      'Zo goed als nieuw': 'NEW_OTHER',
      Gebruikt: 'USED',
    }
    return conditionMap[marktplaatsCondition || 'Gebruikt'] || 'USED'
  }

  /**
   * Get eBay category ID from Marktplaats category
   * This is a simplified mapping - in production, you'd want a proper category mapping
   */
  static getCategoryId(marktplaatsCategory?: string | null): string | undefined {
    // Default category for testing - should be mapped properly
    // Common categories:
    // 11700 - Antiques & Art
    // 11700 - Books, Comics & Magazines
    // 1281 - Business & Industrial
    // 1281 - Cameras & Photo
    // 1281 - Cars, Motorcycles & Vehicles
    // 1281 - Clothing, Shoes & Accessories
    // 1281 - Collectibles
    // 1281 - Computers/Tablets & Networking
    // 1281 - Consumer Electronics
    // 1281 - Crafts
    // 1281 - Dolls & Bears
    // 1281 - DVDs & Movies
    // 1281 - Entertainment Memorabilia
    // 1281 - Gift Cards & Coupons
    // 1281 - Health & Beauty
    // 1281 - Home & Garden
    // 1281 - Jewelry & Watches
    // 1281 - Music
    // 1281 - Musical Instruments & Gear
    // 1281 - Pet Supplies
    // 1281 - Pottery & Glass
    // 1281 - Real Estate
    // 1281 - Specialty Services
    // 1281 - Sporting Goods
    // 1281 - Sports Mem, Cards & Fan Shop
    // 1281 - Stamps
    // 1281 - Tickets & Experiences
    // 1281 - Toys & Hobbies
    // 1281 - Travel
    // 1281 - Video Games & Consoles
    // 1281 - Everything Else

    // For now, return undefined to let eBay auto-categorize
    // In production, create a proper mapping table
    return undefined
  }
}

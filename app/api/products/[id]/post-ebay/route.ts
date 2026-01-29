import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { EbayApi } from '@/lib/ebay'
import { listFiles } from '@/lib/storage'

/**
 * POST /api/products/[id]/post-ebay
 * 
 * Posts a product to eBay using the Inventory API
 */
export async function POST(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const params = await context.params
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
      include: {
        category: true,
      },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Update status to processing
    await prisma.product.update({
      where: { id: params.id },
      data: { status: 'processing' },
    })

    // Get eBay credentials from environment
    const ebayAppId = process.env.EBAY_APP_ID
    const ebayCertId = process.env.EBAY_CERT_ID
    const ebayDevId = process.env.EBAY_DEV_ID
    const ebayUserToken = process.env.EBAY_USER_TOKEN // Optional: OAuth user token
    const ebaySandbox = process.env.EBAY_SANDBOX !== 'false' // Default to true for safety
    const ebayMerchantLocationKey = process.env.EBAY_MERCHANT_LOCATION_KEY || 'default_location'
    const ebayPaymentPolicyId = process.env.EBAY_PAYMENT_POLICY_ID
    const ebayReturnPolicyId = process.env.EBAY_RETURN_POLICY_ID
    const ebayFulfillmentPolicyId = process.env.EBAY_FULFILLMENT_POLICY_ID

    if (!ebayAppId || !ebayCertId || !ebayDevId) {
      return NextResponse.json(
        { error: 'eBay credentials not configured. Please set EBAY_APP_ID, EBAY_CERT_ID, and EBAY_DEV_ID.' },
        { status: 500 }
      )
    }

    if (!ebayPaymentPolicyId || !ebayReturnPolicyId || !ebayFulfillmentPolicyId) {
      return NextResponse.json(
        { error: 'eBay business policies not configured. Please set EBAY_PAYMENT_POLICY_ID, EBAY_RETURN_POLICY_ID, and EBAY_FULFILLMENT_POLICY_ID.' },
        { status: 500 }
      )
    }

    // Initialize eBay API
    const ebayApi = new EbayApi({
      appId: ebayAppId,
      certId: ebayCertId,
      devId: ebayDevId,
      userToken: ebayUserToken,
      sandbox: ebaySandbox,
    })

    try {
      // Get product images
      const imageUrls = await listFiles(product.articleNumber)
      
      // Convert relative paths to absolute URLs if needed
      const baseUrl = process.env.NEXTAUTH_URL 
        || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null)
        || 'http://localhost:3000'
      
      const fullImageUrls = imageUrls.map(url => {
        if (url.startsWith('http')) {
          return url
        }
        return `${baseUrl}${url}`
      })

      // Use article number as SKU (must be unique per seller)
      const sku = product.articleNumber

      // Step 1: Create or update inventory location (if not exists)
      // For simplicity, we'll try to create it, but it might already exist
      try {
        await ebayApi.createInventoryLocation(ebayMerchantLocationKey, {
          location: {
            address: {
              addressLine1: product.location || 'Amsterdam',
              city: product.location?.split(',')[0] || 'Amsterdam',
              postalCode: '1000AA',
              countryCode: 'NL',
            },
          },
          name: 'Default Location',
        })
      } catch (error: any) {
        // Location might already exist, that's okay
        if (!error.message?.includes('already exists')) {
          console.warn('Warning creating inventory location:', error)
        }
      }

      // Step 2: Create or replace inventory item
      await ebayApi.createOrReplaceInventoryItem(sku, {
        sku,
        product: {
          title: product.title,
          description: product.description,
          imageUrls: fullImageUrls.length > 0 ? fullImageUrls : [],
          condition: EbayApi.mapCondition(product.condition),
          conditionDescription: product.condition || undefined,
        },
        availability: {
          shipToLocationAvailability: {
            quantity: 1, // Single item listing
          },
        },
      })

      // Step 3: Create offer
      const offerResult = await ebayApi.createOffer({
        sku,
        marketplaceId: 'EBAY_NL',
        format: 'FIXED_PRICE',
        listingDescription: product.description,
        pricingSummary: {
          price: {
            value: product.price.toFixed(2),
            currency: 'EUR',
          },
        },
        quantity: 1,
        categoryId: EbayApi.getCategoryId(product.category?.path),
        merchantLocationKey: ebayMerchantLocationKey,
        listingPolicies: {
          paymentPolicyId: ebayPaymentPolicyId!,
          returnPolicyId: ebayReturnPolicyId!,
          fulfillmentPolicyId: ebayFulfillmentPolicyId!,
        },
      })

      // Step 4: Publish offer
      const publishResult = await ebayApi.publishOffer(offerResult.offerId)

      // Get the final listing details
      const offerDetails = await ebayApi.getOffer(offerResult.offerId)
      
      // Construct eBay URL
      const ebayItemId = publishResult.listingId
      const ebayUrl = ebaySandbox
        ? `https://sandbox.ebay.nl/itm/${ebayItemId}`
        : `https://www.ebay.nl/itm/${ebayItemId}`

      // Update product with eBay information
      await prisma.product.update({
        where: { id: params.id },
        data: {
          status: 'completed',
          ebayUrl,
          ebayItemId,
          ebaySku: sku,
          postedToEbayAt: new Date(),
        },
      })

      return NextResponse.json({
        success: true,
        message: 'Product succesvol geplaatst op eBay',
        ebayUrl,
        ebayItemId,
        offerId: offerResult.offerId,
      })
    } catch (ebayError: any) {
      console.error('[POST-EBAY] eBay API error:', ebayError)

      // Update product status
      await prisma.product.update({
        where: { id: params.id },
        data: { status: 'failed' },
      })

      return NextResponse.json(
        {
          success: false,
          error: 'Fout bij plaatsen op eBay',
          details: ebayError.message || 'Unknown error',
        },
        { status: 500 }
      )
    }
  } catch (error: any) {
    console.error('Error posting product to eBay:', error)
    
    // Update product status
    try {
      await prisma.product.update({
        where: { id: params.id },
        data: { status: 'failed' },
      })
    } catch {
      // Ignore update errors
    }

    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    )
  }
}

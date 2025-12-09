import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Get all pending products for batch processing
 * This endpoint returns all products with status 'pending' for the authenticated user
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    
    // Allow authentication via session or API key (for Python script)
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Try session first, then API key
    let session_user = null
    try {
      session_user = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    // Validate API key if no session (trim whitespace for comparison)
    const isApiKeyValid = apiKey && (apiKey.trim() === validApiKey.trim())
    
    if (!session_user && !isApiKeyValid) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user ID from session or use a default (for API key mode, get first user or all)
    let userId: string | null = null
    if (session_user) {
      userId = session_user.user.id
    } else if (isApiKeyValid) {
      // For API key mode: allow user_id parameter, or return all pending products
      const requestedUserId = request.nextUrl.searchParams.get('user_id')
      if (requestedUserId) {
        userId = requestedUserId
      } else {
        // No user_id specified with API key: return ALL pending products (for batch processing)
        userId = null // null means no user filter
      }
    } else {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const products = await prisma.product.findMany({
      where: { 
        ...(userId ? { userId: userId } : {}), // Only filter by userId if specified
        status: 'pending',
      },
      include: {
        category: true,
      },
      orderBy: { createdAt: 'asc' },
    })

    // Format products for Python script compatibility
    // Include photo URLs for remote access
    const baseUrl = process.env.NEXTAUTH_URL 
      || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null)
      || 'http://localhost:3000'
    
    // Use the valid API key for photo_api_url (not the one from request, which might be different)
    const photoApiKey = validApiKey
    
    const exportData = products.map(product => {
      // Get photo URLs from API
      const photoUrls: string[] = []
      // Photos will be downloaded from /api/products/[id]/images endpoint
      // For now, we'll include the product ID so the script can fetch images
      
      // Get category path - use the category that is set for the product
      let categoryPath: string | null = null
      if (product.category) {
        categoryPath = product.category.path
        console.log(`Product ${product.id} (${product.title}) has category: ${categoryPath}`)
      } else {
        console.log(`Product ${product.id} (${product.title}) has NO category set`)
      }
      
      return {
        id: product.id,
        title: product.title,
        description: product.description,
        price: product.price.toString(),
        location: product.location || '',
        photos: photoUrls, // Will be populated by script via API
        photo_api_url: `${baseUrl}/api/products/${product.id}/images?api_key=${photoApiKey}`, // API endpoint to get photo URLs
        article_number: product.articleNumber,
        condition: product.condition || 'Gebruikt',
        delivery_methods: [],
        delivery_option: product.deliveryOption || 'Ophalen of Verzenden',
        category_path: categoryPath, // Use the category that was set for the product
        category_fields: product.categoryFields || {}, // Include category-specific fields
      }
    })

    return NextResponse.json(exportData)
  } catch (error) {
    console.error('Error fetching pending products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


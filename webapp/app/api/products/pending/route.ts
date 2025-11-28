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
    
    // Validate API key if no session
    const isApiKeyValid = apiKey && (apiKey === validApiKey)
    
    if (!session_user && !isApiKeyValid) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user ID from session or use a default (for API key mode, get first user or all)
    let userId: string | null = null
    if (session_user) {
      userId = session_user.user.id
    } else if (isApiKeyValid) {
      // For API key mode, get the first user's products (or you could pass user_id as param)
      // In a multi-user system, you'd want to pass user_id as a parameter
      const firstUser = await prisma.user.findFirst()
      if (firstUser) {
        userId = firstUser.id
      } else {
        return NextResponse.json({ error: 'No users found' }, { status: 404 })
      }
    } else {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const products = await prisma.product.findMany({
      where: { 
        userId: userId,
        status: 'pending',
      },
      include: {
        category: true,
      },
      orderBy: { createdAt: 'asc' },
    })

    // Format products for Python script compatibility
    const exportData = products.map(product => ({
      id: product.id,
      title: product.title,
      description: product.description,
      price: product.price.toString(),
      location: product.location || '',
      photos: [], // Photos are found via article_number in media folder
      article_number: product.articleNumber,
      condition: product.condition || 'Gebruikt',
      delivery_methods: [],
      material: product.material || '',
      thickness: product.thickness || '',
      total_surface: product.totalSurface || '',
      delivery_option: product.deliveryOption || 'Ophalen of Verzenden',
      category_path: product.category?.path || null,
    }))

    return NextResponse.json(exportData)
  } catch (error) {
    console.error('Error fetching pending products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


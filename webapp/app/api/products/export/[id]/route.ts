import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Export product data for Python script
 * This endpoint returns product data in a format compatible with the Python script
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    
    // Allow authentication via session or API key (for Python script)
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY
    
    // Try session first, then API key
    let session = null
    try {
      session = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    if (!session && (!apiKey || apiKey !== validApiKey)) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
      include: {
        category: true,
      },
    })

    // If using API key, skip user check (internal use only)
    // If using session, verify ownership
    if (session && product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Format product data for Python script compatibility
    const exportData = {
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
    }

    return NextResponse.json(exportData)
  } catch (error) {
    console.error('Error exporting product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


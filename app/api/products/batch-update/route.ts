import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Batch update products after posting
 * This endpoint allows the Python script to update multiple products at once
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    
    // Allow authentication via session or API key
    const apiKeyHeader = request.headers.get('x-api-key')
    const apiKeyQuery = request.nextUrl.searchParams.get('api_key')
    const apiKey = apiKeyHeader || apiKeyQuery
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Trim and compare API keys
    const trimmedApiKey = apiKey?.trim()
    const trimmedValidKey = validApiKey.trim()
    const keysMatch = trimmedApiKey === trimmedValidKey
    
    let session_user = null
    try {
      session_user = await getServerSession()
    } catch {
      // Session check failed
    }
    
    // Validate API key if no session
    const isApiKeyValid = trimmedApiKey && keysMatch
    
    if (!session_user && !isApiKeyValid) {
      console.error('[BATCH-UPDATE] Unauthorized:', {
        hasSession: !!session_user,
        hasApiKey: !!apiKey,
        keysMatch: keysMatch
      })
      return NextResponse.json({ 
        error: 'Unauthorized',
        hint: !apiKey ? 'No API key provided.' : 'Invalid API key.'
      }, { status: 401 })
    }

    const body = await request.json()
    const updates = body.updates as Array<{
      productId: string
      status?: string
      ad_url?: string
      ad_id?: string
      views?: number
      saves?: number
      posted_at?: string
    }>

    if (!Array.isArray(updates)) {
      return NextResponse.json({ error: 'Invalid request format' }, { status: 400 })
    }

    const results = []
    for (const update of updates) {
      try {
        const product = await prisma.product.findUnique({
          where: { id: update.productId },
        })

        if (!product) {
          results.push({ productId: update.productId, success: false, error: 'Product not found' })
          continue
        }

        // Check ownership if using session
        if (session_user && product.userId !== session_user.user.id) {
          results.push({ productId: update.productId, success: false, error: 'Unauthorized' })
          continue
        }

        // Parse posted_at date
        let postedAtDate: Date | null = null
        if (update.posted_at) {
          // Try to parse date, fallback to current date
          postedAtDate = new Date()
        }

        await prisma.product.update({
          where: { id: update.productId },
          data: {
            status: update.status || 'completed',
            marktplaatsUrl: update.ad_url || null,
            marktplaatsAdId: update.ad_id || null,
            views: update.views || 0,
            saves: update.saves || 0,
            postedAt: postedAtDate,
          },
        })

        results.push({ productId: update.productId, success: true })
      } catch (error: any) {
        results.push({ productId: update.productId, success: false, error: error.message })
      }
    }

    return NextResponse.json({ results })
  } catch (error) {
    console.error('Error batch updating products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


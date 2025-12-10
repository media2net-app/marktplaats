import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Batch post all pending products
 * This endpoint can be called from:
 * 1. Frontend (with session auth)
 * 2. Cron job (with API key)
 * 3. External service (with API key)
 */
export async function POST(request: NextRequest) {
  try {
    // Allow authentication via session or API key
    const session = await getServerSession()
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Validate authentication
    const isApiKeyValid = apiKey && (apiKey.trim() === validApiKey.trim())
    
    if (!session && !isApiKeyValid) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user ID from session if available
    let userId: string | null = null
    if (session?.user) {
      userId = session.user.id
    }

    // Get all pending products
    // When called with API key (no session), get ALL pending products regardless of user
    // When called with session, only get products for that user
    const whereClause: any = {
      status: 'pending',
    }
    
    // Only filter by userId if we have a session (not for API key calls)
    if (session?.user) {
      whereClause.userId = userId
    }
    // If API key is used without session, don't filter by userId (get all pending)
    
    console.log(`[BATCH-POST] Fetching pending products: userId=${userId || 'ALL (API key)'}, where=${JSON.stringify(whereClause)}`)
    
    const pendingProducts = await prisma.product.findMany({
      where: whereClause,
      orderBy: { createdAt: 'asc' },
      take: 50, // Limit to 50 products per batch to avoid timeouts
    })
    
    console.log(`[BATCH-POST] Found ${pendingProducts.length} pending products`)

    if (pendingProducts.length === 0) {
      return NextResponse.json({
        success: true,
        message: 'Geen pending producten gevonden',
        processed: 0,
      })
    }

    // Get base URL for posting individual products
    const baseUrl = process.env.NEXTAUTH_URL 
      || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null)
      || 'http://localhost:3000'

    const results = []
    const errors = []

    // Process each product
    for (const product of pendingProducts) {
      try {
        // Update status to processing
        await prisma.product.update({
          where: { id: product.id },
          data: { status: 'processing' },
        })

        // Call the individual post endpoint
        const postUrl = `${baseUrl}/api/products/${product.id}/post`
        const response = await fetch(postUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': validApiKey,
          },
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
          throw new Error(errorData.error || `HTTP ${response.status}`)
        }

        const result = await response.json()
        results.push({
          productId: product.id,
          title: product.title,
          success: result.success,
          message: result.message,
        })

        // Small delay to avoid overwhelming the system
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error: any) {
        errors.push({
          productId: product.id,
          title: product.title,
          error: error.message || 'Unknown error',
        })

        // Update status to failed
        await prisma.product.update({
          where: { id: product.id },
          data: { status: 'failed' },
        }).catch(() => {}) // Ignore errors updating status
      }
    }

    return NextResponse.json({
      success: true,
      message: `Batch posting voltooid: ${results.length} succesvol, ${errors.length} gefaald`,
      processed: pendingProducts.length,
      results,
      errors,
    })
  } catch (error: any) {
    console.error('Error in batch post:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    )
  }
}

/**
 * GET endpoint to check batch posting status
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    const isApiKeyValid = apiKey && (apiKey.trim() === validApiKey.trim())
    
    if (!session && !isApiKeyValid) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get counts by status
    // When called with API key (no session), count ALL products
    // When called with session, only count products for that user
    const whereClause: any = {}
    if (session?.user) {
      whereClause.userId = session.user.id
    }
    // If API key is used without session, don't filter by userId (count all)
    
    const counts = await prisma.product.groupBy({
      by: ['status'],
      where: Object.keys(whereClause).length > 0 ? whereClause : undefined,
      _count: true,
    })

    const statusCounts = counts.reduce((acc, item) => {
      acc[item.status] = item._count
      return acc
    }, {} as Record<string, number>)

    console.log(`[BATCH-POST GET] Status counts: ${JSON.stringify(statusCounts)}, userId=${session?.user?.id || 'ALL (API key)'}`)

    return NextResponse.json({
      pending: statusCounts.pending || 0,
      processing: statusCounts.processing || 0,
      completed: statusCounts.completed || 0,
      failed: statusCounts.failed || 0,
    })
  } catch (error: any) {
    console.error('Error getting batch status:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}


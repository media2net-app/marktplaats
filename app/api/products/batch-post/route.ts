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
    const pendingProducts = await prisma.product.findMany({
      where: {
        ...(userId ? { userId } : {}), // Filter by user if session exists
        status: 'pending',
      },
      orderBy: { createdAt: 'asc' },
      take: 50, // Limit to 50 products per batch to avoid timeouts
    })

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
    const counts = await prisma.product.groupBy({
      by: ['status'],
      _count: true,
    })

    const statusCounts = counts.reduce((acc, item) => {
      acc[item.status] = item._count
      return acc
    }, {} as Record<string, number>)

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


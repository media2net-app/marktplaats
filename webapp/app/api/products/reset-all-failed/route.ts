import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Reset all failed products to pending status
 * This allows the batch script to pick them up again
 */
export async function POST(request: NextRequest) {
  try {
    // Allow authentication via session or API key
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    let session = null
    try {
      session = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    // Validate API key if no session
    const isApiKeyValid = apiKey && (apiKey === validApiKey)
    
    if (!session && !isApiKeyValid) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    // Get user ID from session or use first user for API key mode
    let userId: string | null = null
    if (session) {
      userId = session.user.id
    } else if (isApiKeyValid) {
      const firstUser = await prisma.user.findFirst()
      if (firstUser) {
        userId = firstUser.id
      } else {
        return NextResponse.json({ error: 'No users found' }, { status: 404 })
      }
    }

    // First, get count of failed products before update
    const failedProducts = await prisma.product.findMany({
      where: {
        userId: userId!,
        status: {
          in: ['failed', 'Failed', 'FAILED', 'mislukt', 'Mislukt', 'MISLUKT']
        },
      },
      select: { id: true },
    })
    
    const failedCount = failedProducts.length
    
    if (failedCount === 0) {
      return NextResponse.json({
        success: true,
        message: 'Geen mislukte producten gevonden',
        updated: 0,
      })
    }

    // Update all failed products to pending status
    // Try multiple status values to catch all variations
    const result = await prisma.product.updateMany({
      where: {
        userId: userId!,
        status: {
          in: ['failed', 'Failed', 'FAILED', 'mislukt', 'Mislukt', 'MISLUKT']
        },
      },
      data: {
        status: 'pending',
        marktplaatsUrl: null,
        marktplaatsAdId: null,
        views: 0,
        saves: 0,
        postedAt: null,
      },
    })

    return NextResponse.json({
      success: true,
      message: `${result.count} product(en) gereset naar pending`,
      updated: result.count,
    })
  } catch (error) {
    console.error('Error resetting failed products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

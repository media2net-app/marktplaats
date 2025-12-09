import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Reset ALL products to pending status
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
    if (session && session.user) {
      userId = session.user.id
    } else if (isApiKeyValid) {
      const firstUser = await prisma.user.findFirst()
      if (firstUser) {
        userId = firstUser.id
      } else {
        return NextResponse.json({ error: 'No users found' }, { status: 404 })
      }
    }

    // First, get count of all products before update
    const allProducts = await prisma.product.findMany({
      where: {
        userId: userId!,
      },
      select: { id: true, status: true },
    })
    
    const totalCount = allProducts.length
    
    if (totalCount === 0) {
      return NextResponse.json({
        success: true,
        message: 'Geen producten gevonden',
        updated: 0,
      })
    }

    // Update ALL products to pending status
    const result = await prisma.product.updateMany({
      where: {
        userId: userId!,
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
      total: totalCount,
    })
  } catch (error) {
    console.error('Error resetting all products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


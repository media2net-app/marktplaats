import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Reset status of failed products back to pending
 * This allows users to retry posting failed products
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const productIds = body.productIds as string[]

    if (!Array.isArray(productIds) || productIds.length === 0) {
      return NextResponse.json({ error: 'Product IDs array is required' }, { status: 400 })
    }

    // Update all specified products to pending status
    const result = await prisma.product.updateMany({
      where: {
        id: { in: productIds },
        userId: session.user.id, // Only update user's own products
        status: 'failed', // Only reset failed products
      },
      data: {
        status: 'pending',
        // Clear previous failed attempt data
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
    console.error('Error resetting product status:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


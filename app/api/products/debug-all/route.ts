import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * Debug endpoint to get ALL products (regardless of status or user)
 * Only accessible with API key for debugging
 */
export async function GET(request: NextRequest) {
  try {
    // Only allow API key authentication for this debug endpoint
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    if (!apiKey || apiKey.trim() !== validApiKey.trim()) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get ALL products with their status
    const allProducts = await prisma.product.findMany({
      select: {
        id: true,
        title: true,
        status: true,
        userId: true,
        articleNumber: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    })

    // Group by status
    const byStatus = {
      pending: allProducts.filter(p => p.status === 'pending'),
      processing: allProducts.filter(p => p.status === 'processing'),
      completed: allProducts.filter(p => p.status === 'completed'),
      failed: allProducts.filter(p => p.status === 'failed'),
    }

    // Get unique user IDs
    const userIds = [...new Set(allProducts.map(p => p.userId))]

    return NextResponse.json({
      total: allProducts.length,
      byStatus: {
        pending: byStatus.pending.length,
        processing: byStatus.processing.length,
        completed: byStatus.completed.length,
        failed: byStatus.failed.length,
      },
      userIds: userIds,
      products: allProducts.map(p => ({
        id: p.id,
        title: p.title,
        status: p.status,
        userId: p.userId,
        articleNumber: p.articleNumber,
      })),
      pendingProducts: byStatus.pending.map(p => ({
        id: p.id,
        title: p.title,
        userId: p.userId,
        articleNumber: p.articleNumber,
      })),
    })
  } catch (error) {
    console.error('Error in debug-all:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

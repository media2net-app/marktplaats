import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { listFiles } from '@/lib/storage'

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
    })

    if (!product) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }
    
    // If using session, verify ownership
    // If using API key, allow access (internal use only)
    if (session && session.user && product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Find all images using storage utility (handles both blob and local)
    const { listFiles } = await import('@/lib/storage')
    const files = await listFiles(product.articleNumber)

    return NextResponse.json({ images: files })
  } catch (error) {
    console.error('Error getting product images:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


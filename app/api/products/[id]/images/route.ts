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
    const apiKeyHeader = request.headers.get('x-api-key')
    const apiKeyQuery = request.nextUrl.searchParams.get('api_key')
    const apiKey = apiKeyHeader || apiKeyQuery
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Log for debugging (only in development)
    if (process.env.NODE_ENV !== 'production') {
      console.log('[IMAGES API] API Key check:', {
        hasHeader: !!apiKeyHeader,
        hasQuery: !!apiKeyQuery,
        keyLength: apiKey?.length,
        validKeyLength: validApiKey.length,
        keysMatch: apiKey === validApiKey
      })
    }
    
    // Try session first, then API key
    let session = null
    try {
      session = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    // If no session, require valid API key
    if (!session) {
      if (!apiKey) {
        console.log('[IMAGES API] No API key provided')
        return NextResponse.json({ error: 'Unauthorized: No API key provided' }, { status: 401 })
      }
      
      // Trim whitespace and compare
      const trimmedApiKey = apiKey.trim()
      const trimmedValidKey = validApiKey.trim()
      
      if (trimmedApiKey !== trimmedValidKey) {
        console.log('[IMAGES API] Invalid API key:', {
          provided: trimmedApiKey.substring(0, 10) + '...',
          expected: trimmedValidKey.substring(0, 10) + '...'
        })
        return NextResponse.json({ error: 'Unauthorized: Invalid API key' }, { status: 401 })
      }
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


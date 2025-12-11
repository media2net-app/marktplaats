import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Batch post status check endpoint
 * Returns status of pending/processing/completed/failed products
 * Used by Railway worker to check if there are products to process
 */
export async function GET(request: NextRequest) {
  try {
    // Allow authentication via session or API key
    const apiKeyHeader = request.headers.get('x-api-key')
    const apiKeyQuery = request.nextUrl.searchParams.get('api_key')
    const apiKey = apiKeyHeader || apiKeyQuery
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Trim and compare API keys
    const trimmedApiKey = apiKey?.trim()
    const trimmedValidKey = validApiKey.trim()
    const keysMatch = trimmedApiKey === trimmedValidKey
    
    // Try session first
    let session_user = null
    try {
      session_user = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    // Validate API key if no session
    const isApiKeyValid = trimmedApiKey && keysMatch
    
    if (!session_user && !isApiKeyValid) {
      console.error('[BATCH-POST] Unauthorized:', {
        hasSession: !!session_user,
        hasApiKey: !!apiKey,
        keysMatch: keysMatch,
        keyPrefix: apiKey?.substring(0, 10) + '...',
        validPrefix: validApiKey.substring(0, 10) + '...'
      })
      return NextResponse.json({ 
        error: 'Unauthorized',
        hint: !apiKey ? 'No API key provided. Include x-api-key header or api_key query parameter.' : 'Invalid API key.'
      }, { status: 401 })
    }

    // Get user ID from session or use first user (for API key mode)
    let userId: string
    if (session_user) {
      userId = session_user.user.id
    } else if (isApiKeyValid) {
      // For API key mode, get the first user's products
      const firstUser = await prisma.user.findFirst()
      if (firstUser) {
        userId = firstUser.id
      } else {
        return NextResponse.json({ error: 'No users found' }, { status: 404 })
      }
    } else {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Count products by status
    const [pending, processing, completed, failed] = await Promise.all([
      prisma.product.count({ where: { userId, status: 'pending' } }),
      prisma.product.count({ where: { userId, status: 'processing' } }),
      prisma.product.count({ where: { userId, status: 'completed' } }),
      prisma.product.count({ where: { userId, status: 'failed' } }),
    ])

    return NextResponse.json({
      pending,
      processing,
      completed,
      failed,
      total: pending + processing + completed + failed,
    })
  } catch (error) {
    console.error('Error in batch-post route:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

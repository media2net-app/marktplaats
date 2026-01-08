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
      // Log more details for debugging
      console.error('[BATCH-POST] Unauthorized:', {
        hasSession: !!session_user,
        hasApiKey: !!apiKey,
        hasHeader: !!apiKeyHeader,
        hasQuery: !!apiKeyQuery,
        keysMatch: keysMatch,
        keyLength: apiKey?.length,
        validKeyLength: validApiKey.length,
        keyPrefix: apiKey?.substring(0, 10) + '...',
        validPrefix: validApiKey.substring(0, 10) + '...'
      })
      return NextResponse.json({ 
        error: 'Unauthorized',
        message: 'Failed to authenticate. Check your API key.',
        hint: !apiKey ? 'No API key provided. Include x-api-key header or api_key query parameter.' : 'Invalid API key. Make sure INTERNAL_API_KEY matches in both Vercel and Railway.'
      }, { status: 401 })
    }

    // Get user ID from session or use all users (for API key mode)
    let userId: string | null = null
    if (session_user) {
      userId = session_user.user.id
    } else if (isApiKeyValid) {
      // For API key mode, count ALL products from ALL users
      userId = null
    } else {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Build where clauses - if userId is null, count all products
    const wherePending = userId ? { userId, status: 'pending' } : { status: 'pending' }
    const whereProcessing = userId ? { userId, status: 'processing' } : { status: 'processing' }
    const whereCompleted = userId ? { userId, status: 'completed' } : { status: 'completed' }
    const whereFailed = userId ? { userId, status: 'failed' } : { status: 'failed' }

    // Count products by status
    const [pending, processing, completed, failed] = await Promise.all([
      prisma.product.count({ where: wherePending }),
      prisma.product.count({ where: whereProcessing }),
      prisma.product.count({ where: whereCompleted }),
      prisma.product.count({ where: whereFailed }),
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


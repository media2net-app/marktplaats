import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'

/**
 * Fetch logs from Railway service
 * Requires Railway API token and Service ID
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const railwayToken = process.env.RAILWAY_API_TOKEN
    const serviceId = process.env.RAILWAY_SERVICE_ID

    if (!railwayToken) {
      console.error('[RAILWAY LOGS] RAILWAY_API_TOKEN not configured')
      return NextResponse.json({ 
        error: 'Railway API token not configured',
        message: 'Failed to fetch logs from Railway',
        hint: 'Set RAILWAY_API_TOKEN environment variable in Vercel',
        configured: false
      }, { status: 500 })
    }

    if (!serviceId) {
      console.error('[RAILWAY LOGS] RAILWAY_SERVICE_ID not configured')
      return NextResponse.json({ 
        error: 'Railway Service ID not configured',
        message: 'Failed to fetch logs from Railway',
        hint: 'Set RAILWAY_SERVICE_ID environment variable in Vercel',
        configured: false
      }, { status: 500 })
    }

    // Get limit from query params (default 100)
    const limit = parseInt(request.nextUrl.searchParams.get('limit') || '100')
    const before = request.nextUrl.searchParams.get('before') || null

    // Railway GraphQL API endpoint
    const graphqlEndpoint = 'https://backboard.railway.app/graphql/v2'

    // GraphQL query to fetch logs
    const query = `
      query GetServiceLogs($serviceId: ID!, $limit: Int, $before: String) {
        service(id: $serviceId) {
          logs(limit: $limit, before: $before) {
            edges {
              node {
                id
                message
                timestamp
                level
              }
            }
            pageInfo {
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }
          }
        }
      }
    `

    const variables = {
      serviceId,
      limit,
      ...(before && { before })
    }

    // Fetch logs from Railway
    const response = await fetch(graphqlEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${railwayToken}`,
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('[RAILWAY LOGS] Railway API error:', response.status, errorText)
      let errorMessage = 'Failed to fetch logs from Railway'
      
      // Provide more specific error messages
      if (response.status === 401) {
        errorMessage = 'Railway API authentication failed. Check your RAILWAY_API_TOKEN.'
      } else if (response.status === 404) {
        errorMessage = 'Railway service not found. Check your RAILWAY_SERVICE_ID.'
      } else if (response.status === 403) {
        errorMessage = 'Railway API access forbidden. Check your API token permissions.'
      }
      
      return NextResponse.json({ 
        error: errorMessage,
        message: errorMessage,
        details: errorText,
        status: response.status,
        configured: true
      }, { status: response.status })
    }

    const data = await response.json()

    if (data.errors) {
      console.error('[RAILWAY LOGS] Railway GraphQL errors:', data.errors)
      const firstError = data.errors[0]?.message || 'Unknown error'
      return NextResponse.json({ 
        error: 'Railway API returned errors',
        message: `Failed to fetch logs from Railway: ${firstError}`,
        details: data.errors,
        configured: true
      }, { status: 500 })
    }

    const logs = data.data?.service?.logs?.edges || []
    const pageInfo = data.data?.service?.logs?.pageInfo || {}

    return NextResponse.json({
      logs: logs.map((edge: any) => ({
        id: edge.node.id,
        message: edge.node.message,
        timestamp: edge.node.timestamp,
        level: edge.node.level,
      })),
      pageInfo,
    })
  } catch (error: any) {
    console.error('[RAILWAY LOGS] Error fetching Railway logs:', error)
    return NextResponse.json({ 
      error: 'Internal server error',
      message: `Failed to fetch logs from Railway: ${error.message || 'Unknown error'}`,
      details: error.message,
      configured: !!process.env.RAILWAY_API_TOKEN && !!process.env.RAILWAY_SERVICE_ID
    }, { status: 500 })
  }
}


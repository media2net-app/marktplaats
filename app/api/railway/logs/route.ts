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
      return NextResponse.json({ 
        error: 'Railway API token not configured',
        hint: 'Set RAILWAY_API_TOKEN environment variable'
      }, { status: 500 })
    }

    if (!serviceId) {
      return NextResponse.json({ 
        error: 'Railway Service ID not configured',
        hint: 'Set RAILWAY_SERVICE_ID environment variable'
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
      console.error('Railway API error:', response.status, errorText)
      return NextResponse.json({ 
        error: 'Failed to fetch logs from Railway',
        details: errorText,
        status: response.status
      }, { status: response.status })
    }

    const data = await response.json()

    if (data.errors) {
      console.error('Railway GraphQL errors:', data.errors)
      return NextResponse.json({ 
        error: 'Railway API returned errors',
        details: data.errors
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
    console.error('Error fetching Railway logs:', error)
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error.message 
    }, { status: 500 })
  }
}

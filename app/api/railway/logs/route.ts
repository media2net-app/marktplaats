import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'

/**
 * Get Railway logs via Railway API
 * Requires RAILWAY_API_TOKEN, RAILWAY_PROJECT_ID, and RAILWAY_SERVICE_ID
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const railwayApiToken = process.env.RAILWAY_API_TOKEN
    const railwayProjectId = process.env.RAILWAY_PROJECT_ID
    const railwayServiceId = process.env.RAILWAY_SERVICE_ID

    // If service ID not set, try to find it automatically
    if (!railwayServiceId && railwayApiToken && railwayProjectId) {
      try {
        // Try to get the first service from the project
        const listQuery = `
          query GetServices($projectId: String!) {
            project(id: $projectId) {
              services {
                id
                name
              }
            }
          }
        `
        
        const listResponse = await fetch('https://backboard.railway.app/graphql/v1', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${railwayApiToken}`,
          },
          body: JSON.stringify({
            query: listQuery,
            variables: { projectId: railwayProjectId },
          }),
        })

        if (listResponse.ok) {
          const listData = await listResponse.json()
          const services = listData.data?.project?.services || []
          if (services.length > 0) {
            // Use the first service (usually the worker)
            const autoServiceId = services[0].id
            console.log(`Auto-detected Service ID: ${autoServiceId} (Service: ${services[0].name})`)
            // Continue with auto-detected service ID
            // But we still need to set it in env for production
          }
        }
      } catch (e) {
        // Ignore auto-detection errors
      }
    }

    // Debug: Log what we have (without exposing sensitive data)
    console.log('[RAILWAY LOGS] Environment check:', {
      hasToken: !!railwayApiToken,
      tokenLength: railwayApiToken?.length || 0,
      hasProjectId: !!railwayProjectId,
      projectIdLength: railwayProjectId?.length || 0,
      projectIdPrefix: railwayProjectId?.substring(0, 8) || 'none',
      hasServiceId: !!railwayServiceId,
      serviceIdLength: railwayServiceId?.length || 0,
      serviceIdPrefix: railwayServiceId?.substring(0, 8) || 'none',
    })

    if (!railwayApiToken || !railwayProjectId || !railwayServiceId) {
      const missing = []
      if (!railwayApiToken) missing.push('RAILWAY_API_TOKEN')
      if (!railwayProjectId) missing.push('RAILWAY_PROJECT_ID')
      if (!railwayServiceId) missing.push('RAILWAY_SERVICE_ID')
      
      return NextResponse.json({
        error: 'Railway API not configured',
        message: `Missing environment variables: ${missing.join(', ')}`,
        hint: railwayProjectId && railwayApiToken && !railwayServiceId 
          ? 'Service ID missing. Go to Railway → Your Service → Settings → General to find Service ID'
          : 'Please set all three variables in Vercel: Settings → Environment Variables',
        missing: missing,
      }, { status: 500 })
    }

    // Get query parameters
    const searchParams = request.nextUrl.searchParams
    const limit = parseInt(searchParams.get('limit') || '100')
    const since = searchParams.get('since') // ISO timestamp

    // Build Railway API URL
    // Railway GraphQL API endpoint
    const railwayApiUrl = 'https://backboard.railway.app/graphql/v1'

    // GraphQL query to get logs
    const query = `
      query GetLogs($projectId: String!, $serviceId: String!, $limit: Int, $since: String) {
        project(id: $projectId) {
          service(id: $serviceId) {
            deployments(limit: 1) {
              id
              logs(limit: $limit, since: $since) {
                timestamp
                message
                level
              }
            }
          }
        }
      }
    `

    const variables = {
      projectId: railwayProjectId,
      serviceId: railwayServiceId,
      limit,
      since,
    }

    try {
      console.log('[RAILWAY LOGS] Making request to:', railwayApiUrl)
      console.log('[RAILWAY LOGS] Variables:', { 
        projectId: railwayProjectId?.substring(0, 8) + '...',
        serviceId: railwayServiceId?.substring(0, 8) + '...',
        limit,
        hasToken: !!railwayApiToken,
      })
      
      const response = await fetch(railwayApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${railwayApiToken}`,
        },
        body: JSON.stringify({
          query,
          variables,
        }),
      })
      
      console.log('[RAILWAY LOGS] Response status:', response.status, response.statusText)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Railway API error:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText.substring(0, 500), // Limit error text length
          url: railwayApiUrl,
          hasToken: !!railwayApiToken,
          tokenLength: railwayApiToken?.length,
          projectId: railwayProjectId?.substring(0, 8) + '...',
          serviceId: railwayServiceId?.substring(0, 8) + '...',
        })
        
        // Provide user-friendly error message
        let userMessage = 'Failed to fetch logs from Railway'
        let debugInfo: any = {}
        
        if (response.status === 401) {
          userMessage = 'Railway API authentication failed. Please check your RAILWAY_API_TOKEN.'
          debugInfo = {
            hint: 'The API token might be invalid or expired. Generate a new Account Token in Railway → Account Settings → Tokens',
            tokenLength: railwayApiToken?.length || 0,
          }
        } else if (response.status === 404) {
          userMessage = 'Railway project or service not found. Please check your RAILWAY_PROJECT_ID and RAILWAY_SERVICE_ID.'
          debugInfo = {
            hint: 'Verify the IDs are correct in Vercel environment variables. Check Railway dashboard to confirm the IDs.',
            projectIdPrefix: railwayProjectId?.substring(0, 12) || 'not set',
            serviceIdPrefix: railwayServiceId?.substring(0, 12) || 'not set',
            errorResponse: errorText.substring(0, 300),
          }
        } else if (response.status >= 500) {
          userMessage = 'Railway API server error. Please try again later.'
        }
        
        return NextResponse.json({
          error: userMessage,
          details: errorText.substring(0, 200), // Limit details length
          status: response.status,
          statusText: response.statusText,
          debug: debugInfo,
        }, { status: response.status })
      }

      const data = await response.json()

      if (data.errors) {
        console.error('Railway GraphQL errors:', data.errors)
        return NextResponse.json({
          error: 'Railway API error',
          details: data.errors,
          message: data.errors[0]?.message || 'Unknown GraphQL error',
        }, { status: 500 })
      }

      // Extract logs from response
      const deployments = data.data?.project?.service?.deployments || []
      const logs = deployments[0]?.logs || []

      return NextResponse.json({
        logs: logs.map((log: any) => ({
          timestamp: log.timestamp,
          message: log.message,
          level: log.level || 'info',
        })),
        count: logs.length,
      })
    } catch (error: any) {
      console.error('Error fetching Railway logs:', {
        error: error.message,
        stack: error.stack,
        name: error.name,
        url: railwayApiUrl,
        cause: error.cause,
      })
      
      // Provide more helpful error message
      let errorMessage = 'Failed to fetch logs from Railway'
      let errorDetails = error.message
      
      if (error.message?.includes('fetch')) {
        errorMessage = 'Network error connecting to Railway API'
        errorDetails = 'Could not reach Railway API. Check your internet connection and Railway API status.'
      } else if (error.message?.includes('JSON')) {
        errorMessage = 'Invalid response from Railway API'
        errorDetails = 'Railway API returned invalid data. The API token might be incorrect.'
      }
      
      return NextResponse.json({
        error: errorMessage,
        details: errorDetails,
        type: error.name || 'UnknownError',
      }, { status: 500 })
    }
  } catch (error: any) {
    console.error('Error in logs route:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    )
  }
}


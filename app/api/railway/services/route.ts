import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'

/**
 * List all services in a Railway project
 * This helps find the Service ID
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const railwayApiToken = process.env.RAILWAY_API_TOKEN
    const railwayProjectId = process.env.RAILWAY_PROJECT_ID

    if (!railwayApiToken || !railwayProjectId) {
      return NextResponse.json({
        error: 'Railway API not configured',
        message: 'Please set RAILWAY_API_TOKEN and RAILWAY_PROJECT_ID in environment variables',
      }, { status: 500 })
    }

    // GraphQL query to list all services
    const query = `
      query GetServices($projectId: String!) {
        project(id: $projectId) {
          id
          name
          services {
            id
            name
            createdAt
          }
        }
      }
    `

    try {
      const response = await fetch('https://backboard.railway.app/graphql/v1', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${railwayApiToken}`,
        },
        body: JSON.stringify({
          query,
          variables: { projectId: railwayProjectId },
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        return NextResponse.json({
          error: 'Failed to fetch services from Railway',
          details: errorText,
        }, { status: response.status })
      }

      const data = await response.json()

      if (data.errors) {
        return NextResponse.json({
          error: 'Railway API error',
          details: data.errors,
        }, { status: 500 })
      }

      const project = data.data?.project
      const services = project?.services || []

      return NextResponse.json({
        project: {
          id: project?.id,
          name: project?.name,
        },
        services: services.map((service: any) => ({
          id: service.id,
          name: service.name,
          createdAt: service.createdAt,
        })),
        hint: services.length > 0 
          ? `Use the Service ID from the service you want to monitor (usually the worker service)`
          : 'No services found in this project',
      })
    } catch (error: any) {
      console.error('Error fetching Railway services:', error)
      return NextResponse.json({
        error: 'Failed to fetch services',
        details: error.message,
      }, { status: 500 })
    }
  } catch (error: any) {
    console.error('Error in services route:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    )
  }
}


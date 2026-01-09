import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import fs from 'fs'
import path from 'path'

/**
 * Get all pending products for batch processing
 * This endpoint returns all products with status 'pending' for the authenticated user
 */
export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession()
    
    // Allow authentication via session or API key (for Python script)
    const apiKeyHeader = request.headers.get('x-api-key')
    const apiKeyQuery = request.nextUrl.searchParams.get('api_key')
    const apiKey = apiKeyHeader || apiKeyQuery
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    // Log for debugging (only in development or if key mismatch)
    const trimmedApiKey = apiKey?.trim()
    const trimmedValidKey = validApiKey.trim()
    const keysMatch = trimmedApiKey === trimmedValidKey
    
    if (process.env.NODE_ENV !== 'production' || !keysMatch) {
      console.log('[PENDING API] Auth check:', {
        hasHeader: !!apiKeyHeader,
        hasQuery: !!apiKeyQuery,
        keyLength: apiKey?.length,
        validKeyLength: validApiKey.length,
        keysMatch: keysMatch,
        keyPrefix: apiKey?.substring(0, 10) + '...',
        validPrefix: validApiKey.substring(0, 10) + '...'
      })
    }
    
    // Try session first, then API key
    let session_user = null
    try {
      session_user = await getServerSession()
    } catch {
      // Session check failed, try API key
    }
    
    // Validate API key if no session (trim whitespace for comparison)
    const isApiKeyValid = trimmedApiKey && (trimmedApiKey === trimmedValidKey)
    
    if (!session_user && !isApiKeyValid) {
      console.error('[PENDING API] Unauthorized:', {
        hasSession: !!session_user,
        hasApiKey: !!apiKey,
        keysMatch: keysMatch
      })
      return NextResponse.json({ 
        error: 'Unauthorized',
        hint: !apiKey ? 'No API key provided. Include x-api-key header or api_key query parameter.' : 'Invalid API key.'
      }, { status: 401 })
    }

    // Get user ID from session or use a default (for API key mode, get all pending products)
    let userId: string | null = null
    if (session_user) {
      userId = session_user.user.id
    } else if (isApiKeyValid) {
      // For API key mode, get ALL pending products from ALL users
      // This allows the worker script to process products from any user
      userId = null // null means get all users' products
    } else {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // First, let's check ALL products to see what we have
    const allProductsCheck = await prisma.product.findMany({
      select: {
        id: true,
        title: true,
        status: true,
        userId: true,
      },
      take: 20, // Check first 20
    })

    const totalInDb = await prisma.product.count()
    const uniqueStatuses = [...new Set(allProductsCheck.map(p => p.status))]
    const uniqueUserIds = [...new Set(allProductsCheck.map(p => p.userId))]

    console.log('[PENDING API] Database check:', {
      totalInDb,
      uniqueStatuses,
      uniqueUserIds,
      sampleProducts: allProductsCheck.map(p => ({
        id: p.id,
        title: p.title.substring(0, 30),
        status: p.status,
        userId: p.userId,
      })),
    })

    // Build where clause - if userId is null, get all pending products
    let whereClause: any
    if (userId) {
      whereClause = { 
        userId: userId,
        status: 'pending',
      }
    } else {
      // Get all pending products from all users
      whereClause = { 
        status: 'pending',
      }
    }

    console.log('[PENDING API] Query params:', {
      hasUserId: !!userId,
      userId: userId,
      whereClause,
    })

    const products = await prisma.product.findMany({
      where: whereClause,
      include: {
        category: true,
      },
      orderBy: { createdAt: 'asc' },
    })

    // Debug logging
    console.log('[PENDING API] Query result:', {
      userId: userId,
      whereClause,
      productCount: products.length,
      productIds: products.map(p => p.id),
      productTitles: products.map(p => p.title),
    })

    // Helper function to get category fields (same logic as /api/categories/[id]/fields)
    const getCategoryFields = async (categoryId: string | null, categoryPath: string | null): Promise<Record<string, any>> => {
      if (!categoryId) return {}
      
      try {
        const jsonPath = path.join(process.cwd(), 'category_fields_v2.json')
        if (!fs.existsSync(jsonPath)) {
          console.warn(`category_fields_v2.json not found at ${jsonPath}`)
          return {}
        }
        
        const fileContent = fs.readFileSync(jsonPath, 'utf-8')
        const data = JSON.parse(fileContent)
        const allCategories = data?.categorySpecificFields?.categories || {}
        
        // First, try direct match by category ID
        let categoryFields = allCategories[categoryId]
        
        // If not found and we have a category path, try matching by path
        if (!categoryFields && categoryPath) {
          // Try exact path match
          const foundByPath = Object.values(allCategories).find((cat: any) => 
            cat.categoryPath?.toLowerCase() === categoryPath.toLowerCase()
          )
          
          if (foundByPath) {
            categoryFields = foundByPath
          } else {
            // Try fuzzy match on path
            const normalizedDbPath = categoryPath.toLowerCase().replace(/\s*>\s*/g, ' > ').trim()
            const foundByFuzzyPath = Object.values(allCategories).find((cat: any) => {
              if (!cat.categoryPath) return false
              const normalizedCatPath = cat.categoryPath.toLowerCase().replace(/\s*>\s*/g, ' > ').trim()
              return normalizedCatPath === normalizedDbPath
            })
            
            if (foundByFuzzyPath) {
              categoryFields = foundByFuzzyPath
            } else {
              // Try partial match
              const dbPathParts = normalizedDbPath.split(' > ').map((p: string) => p.trim())
              const foundByPartial = Object.values(allCategories).find((cat: any) => {
                if (!cat.categoryPath) return false
                const catPathParts = cat.categoryPath.toLowerCase().split(' > ').map((p: string) => p.trim())
                if (dbPathParts.length > catPathParts.length) return false
                let dbIndex = 0
                for (let i = 0; i < catPathParts.length && dbIndex < dbPathParts.length; i++) {
                  if (catPathParts[i].includes(dbPathParts[dbIndex]) || dbPathParts[dbIndex].includes(catPathParts[i])) {
                    dbIndex++
                  }
                }
                return dbIndex === dbPathParts.length
              })
              
              if (foundByPartial) {
                categoryFields = foundByPartial
              }
            }
          }
        }
        
        if (categoryFields?.fields) {
          // Convert fields array to object format expected by Python script
          const fieldsObj: Record<string, any> = {}
          categoryFields.fields.forEach((field: any) => {
            const fieldKey = field.name || field.id
            if (fieldKey) {
              // For now, return empty values - the Python script will fill them from product data
              // In the future, we could store categoryFields in the product model
              fieldsObj[fieldKey] = ''
            }
          })
          return fieldsObj
        }
      } catch (error) {
        console.error(`Error loading category fields for ${categoryId}:`, error)
      }
      
      return {}
    }

    // Format products for Python script compatibility
    const exportDataPromises = products.map(async (product) => {
      const categoryFields = await getCategoryFields(product.categoryId, product.category?.path || null)
      
      return {
        id: product.id,
        title: product.title,
        description: product.description,
        price: product.price.toString(),
        location: product.location || '',
        photos: [], // Photos are found via article_number in media folder
        article_number: product.articleNumber,
        condition: product.condition || 'Gebruikt',
        delivery_methods: [],
        material: product.material || '',
        thickness: product.thickness || '',
        total_surface: product.totalSurface || '',
        delivery_option: product.deliveryOption || 'Ophalen of Verzenden',
        category_path: product.category?.path || null,
        category_fields: categoryFields, // Add category-specific fields
      }
    })
    
    const exportData = await Promise.all(exportDataPromises)

    // Always include debug info when using API key (for troubleshooting)
    if (isApiKeyValid && exportData.length === 0) {
      return NextResponse.json({
        products: exportData,
        debug: {
          totalInDb,
          uniqueStatuses,
          uniqueUserIds: uniqueUserIds.length,
          whereClause,
          hasUserId: !!userId,
          userId: userId,
          sampleProducts: allProductsCheck.slice(0, 10).map(p => ({
            title: p.title.substring(0, 50),
            status: p.status,
            userId: p.userId.substring(0, 15) + '...',
          })),
          allStatusCounts: {
            pending: allProductsCheck.filter(p => p.status === 'pending').length,
            processing: allProductsCheck.filter(p => p.status === 'processing').length,
            completed: allProductsCheck.filter(p => p.status === 'completed').length,
            failed: allProductsCheck.filter(p => p.status === 'failed').length,
          },
        },
      })
    }

    return NextResponse.json(exportData)
  } catch (error) {
    console.error('Error fetching pending products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { getServerSession } from '@/lib/auth'

export async function GET() {
  try {
    // Haal alle categorieën op, gegroepeerd per level
    const categories = await prisma.category.findMany({
      orderBy: [
        { level: 'asc' },
        { name: 'asc' },
      ],
      include: {
        parent: true,
        children: {
          orderBy: { name: 'asc' },
        },
      },
    })

    // Organiseer in hiërarchische structuur
    const tree = buildCategoryTree(categories)

    return NextResponse.json(tree)
  } catch (error) {
    console.error('Error fetching categories:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    // Check authentication (session or API key)
    const session = await getServerSession()
    const apiKey = request.headers.get('x-api-key') || request.nextUrl.searchParams.get('api_key')
    const validApiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
    
    if (!session && (!apiKey || apiKey !== validApiKey)) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { categories: categoriesToAdd } = body

    if (!Array.isArray(categoriesToAdd)) {
      return NextResponse.json({ error: 'Categories must be an array' }, { status: 400 })
    }

    const results = {
      created: 0,
      updated: 0,
      skipped: 0,
      errors: [] as string[],
    }

    // Process categories in order (parents first)
    const sortedCategories = [...categoriesToAdd].sort((a, b) => (a.level || 0) - (b.level || 0))

    for (const catData of sortedCategories) {
      try {
        const { id, name, level, parentId, path, marktplaatsId } = catData

        if (!name || !level) {
          results.skipped++
          results.errors.push(`Skipped category: missing name or level`)
          continue
        }

        // Generate ID if not provided
        const categoryId = id || name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')

        // Find parent category if parentId is provided
        let parentCategoryId: string | null = null
        if (parentId) {
          const parent = await prisma.category.findFirst({
            where: {
              OR: [
                { id: parentId },
                { name: parentId },
              ],
            },
          })
          if (parent) {
            parentCategoryId = parent.id
          }
        }

        // Check if category already exists
        const existing = await prisma.category.findFirst({
          where: {
            OR: [
              { id: categoryId },
              { path: path || name },
            ],
          },
        })

        if (existing) {
          // Update existing category
          await prisma.category.update({
            where: { id: existing.id },
            data: {
              name,
              level,
              parentId: parentCategoryId,
              path: path || name,
              marktplaatsId: marktplaatsId || existing.marktplaatsId,
            },
          })
          results.updated++
        } else {
          // Create new category
          await prisma.category.create({
            data: {
              id: categoryId,
              name,
              level,
              parentId: parentCategoryId,
              path: path || name,
              marktplaatsId: marktplaatsId || null,
            },
          })
          results.created++
        }
      } catch (error: any) {
        results.skipped++
        results.errors.push(`Error processing ${catData.name}: ${error.message}`)
        console.error(`Error processing category ${catData.name}:`, error)
      }
    }

    return NextResponse.json({
      success: true,
      ...results,
    })
  } catch (error) {
    console.error('Error adding categories:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

function buildCategoryTree(categories: any[]) {
  const map = new Map()
  const roots: any[] = []

  // Maak een map van alle categorieën
  categories.forEach(cat => {
    map.set(cat.id, { ...cat, children: [] })
  })

  // Bouw de tree
  categories.forEach(cat => {
    const node = map.get(cat.id)
    if (cat.parentId) {
      const parent = map.get(cat.parentId)
      if (parent) {
        parent.children.push(node)
      } else {
        roots.push(node)
      }
    } else {
      roots.push(node)
    }
  })

  return roots
}


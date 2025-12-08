import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET() {
  try {
    // Haal eerst alleen categorieën op die fields hebben (selecteer alleen benodigde velden)
    const categoriesWithFields = await prisma.category.findMany({
      where: {
        fields: {
          not: null,
        },
      },
      select: {
        id: true,
        name: true,
        level: true,
        path: true,
        parentId: true,
        fields: true,
      },
      orderBy: [
        { level: 'asc' },
        { name: 'asc' },
      ],
    })

    // Filter op niet-lege arrays
    const validCategories = categoriesWithFields.filter(cat => {
      if (!cat.fields) return false
      const fields = cat.fields as any[]
      return Array.isArray(fields) && fields.length > 0
    })

    if (validCategories.length === 0) {
      return NextResponse.json([])
    }

    // Verzamel alle benodigde IDs: categorieën met fields + hun parents + grandparents
    const neededIds = new Set<string>()
    
    validCategories.forEach(cat => {
      neededIds.add(cat.id)
      if (cat.parentId) neededIds.add(cat.parentId)
    })

    // Haal parents op om grandparents te vinden (iteratief tot we alle ancestors hebben)
    let hasMore = true
    while (hasMore) {
      const currentIds = Array.from(neededIds)
      const parents = await prisma.category.findMany({
        where: {
          id: { in: currentIds },
          parentId: { not: null },
        },
        select: {
          id: true,
          parentId: true,
        },
      })

      const beforeSize = neededIds.size
      parents.forEach(p => {
        if (p.parentId) neededIds.add(p.parentId)
      })
      
      // Stop als we geen nieuwe parents meer vinden
      hasMore = neededIds.size > beforeSize
    }

    // Haal alle benodigde categorieën op (zonder fields om grootte te beperken)
    const neededCategories = await prisma.category.findMany({
      where: {
        id: { in: Array.from(neededIds) },
      },
      select: {
        id: true,
        name: true,
        level: true,
        path: true,
        parentId: true,
        fields: true, // Alleen voor categorieën die fields hebben
      },
      orderBy: [
        { level: 'asc' },
        { name: 'asc' },
      ],
    })

    // Bouw de tree
    const tree = buildCategoryTree(neededCategories)

    return NextResponse.json(tree)
  } catch (error: any) {
    console.error('Error fetching categories with fields:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

function buildCategoryTree(categories: any[]) {
  if (categories.length === 0) return []

  const map = new Map<string, any>()
  const roots: any[] = []

  // Maak nodes voor alle categorieën
  categories.forEach((cat) => {
    const hasFields = !!cat.fields && Array.isArray(cat.fields) && (cat.fields as any[]).length > 0
    
    map.set(cat.id, {
      id: cat.id,
      name: cat.name,
      level: cat.level,
      path: cat.path,
      children: [],
      hasFields,
    })
  })

  // Bouw parent-child relaties
  categories.forEach((cat) => {
    const node = map.get(cat.id)
    if (!node) return

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

  // Filter tree recursief
  const filterTree = (nodes: any[]): any[] => {
    const result: any[] = []
    
    for (const node of nodes) {
      const filteredChildren = filterTree(node.children || [])
      
      if (node.hasFields || filteredChildren.length > 0) {
        result.push({
          id: node.id,
          name: node.name,
          level: node.level,
          path: node.path,
          children: filteredChildren,
        })
      }
    }
    
    return result
  }

  return filterTree(roots)
}

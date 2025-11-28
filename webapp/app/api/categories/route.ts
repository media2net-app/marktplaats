import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

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


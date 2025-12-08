import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const categoryId = params.id

    const category = await prisma.category.findUnique({
      where: { id: categoryId },
    })

    if (!category) {
      return NextResponse.json(
        { error: 'Category not found' },
        { status: 404 }
      )
    }

    // Return fields (or empty array if null)
    const fields = (category.fields as any[]) || []

    return NextResponse.json({
      categoryId: category.id,
      categoryName: category.name,
      categoryPath: category.path,
      level: category.level,
      fields: fields,
    })
  } catch (error: any) {
    console.error('Error fetching category fields:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}


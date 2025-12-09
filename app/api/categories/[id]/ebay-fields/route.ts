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

    // Return eBay fields (or empty array if null)
    const ebayFields = (category.ebayFields as any[]) || []

    return NextResponse.json({
      categoryId: category.id,
      categoryName: category.name,
      categoryPath: category.path,
      ebayCategoryId: category.ebayCategoryId,
      ebayFields: ebayFields,
    })
  } catch (error: any) {
    console.error('Error fetching eBay category fields:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}





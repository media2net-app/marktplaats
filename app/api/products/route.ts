import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    // Get default category if no categoryId provided
    let defaultCategoryId = body.categoryId || null
    if (!defaultCategoryId) {
      const defaultCategory = await prisma.category.findFirst({
        where: { path: 'Hobby en Vrije tijd > Overige > Overige Hobby en Vrije tijd' }
      })
      if (defaultCategory) {
        defaultCategoryId = defaultCategory.id
      }
    }
    
    const product = await prisma.product.create({
      data: {
        title: body.title,
        description: body.description,
        price: body.price,
        articleNumber: body.articleNumber,
        condition: body.condition,
        material: body.material,
        thickness: body.thickness,
        totalSurface: body.totalSurface,
        deliveryOption: body.deliveryOption,
        location: body.location,
        categoryId: defaultCategoryId,
        status: 'pending', // Always set to pending for new products
        userId: session.user.id,
      },
    })

    return NextResponse.json(product)
  } catch (error) {
    console.error('Error creating product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function GET() {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const products = await prisma.product.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
    })

    return NextResponse.json(products)
  } catch (error) {
    console.error('Error fetching products:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


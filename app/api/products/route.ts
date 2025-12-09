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
    
    // Process categoryFields - if empty object, set to null
    let categoryFields = null
    if (body.categoryFields && typeof body.categoryFields === 'object' && Object.keys(body.categoryFields).length > 0) {
      categoryFields = body.categoryFields
    }
    
    // Process ebayFields - if empty object, set to null
    let ebayFields = null
    if (body.ebayFields && typeof body.ebayFields === 'object' && Object.keys(body.ebayFields).length > 0) {
      ebayFields = body.ebayFields
    }
    
    const product = await prisma.product.create({
      data: {
        title: body.title,
        description: body.description,
        price: body.price,
        articleNumber: body.articleNumber,
        condition: body.condition,
        deliveryOption: body.deliveryOption,
        location: body.location,
        categoryId: body.categoryId || null,
        categoryFields: categoryFields,
        ebayFields: ebayFields,
        platforms: body.platforms || ['marktplaats'],
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


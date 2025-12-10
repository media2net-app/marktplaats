import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const session = await getServerSession()
    
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
      include: {
        category: true,
      },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    return NextResponse.json(product)
  } catch (error) {
    console.error('Error fetching product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const session = await getServerSession()
    
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    const body = await request.json()
    
    // Don't allow updating status, marktplaatsUrl, marktplaatsAdId, views, saves, postedAt via this endpoint
    // These are managed by the posting process
    
    // Build update data object, only including fields that are provided
    const updateData: any = {
      title: body.title,
      description: body.description,
      price: body.price,
      articleNumber: body.articleNumber,
      condition: body.condition,
      deliveryOption: body.deliveryOption,
      location: body.location,
      manufacturerName: body.manufacturerName !== undefined ? (body.manufacturerName || null) : undefined,
      manufacturerAddress: body.manufacturerAddress !== undefined ? (body.manufacturerAddress || null) : undefined,
      manufacturerEmail: body.manufacturerEmail !== undefined ? (body.manufacturerEmail || null) : undefined,
      categoryId: body.categoryId !== undefined ? (body.categoryId || null) : undefined,
      platforms: body.platforms || ['marktplaats'],
    }
    
    // Handle categoryFields - only update if explicitly provided
    if (body.categoryFields !== undefined) {
      // If it's an empty object, set to null, otherwise use the provided value
      if (body.categoryFields && typeof body.categoryFields === 'object' && Object.keys(body.categoryFields).length > 0) {
        updateData.categoryFields = body.categoryFields
      } else {
        updateData.categoryFields = null
      }
    }
    
    // Handle ebayFields - only update if explicitly provided
    if (body.ebayFields !== undefined) {
      if (body.ebayFields && typeof body.ebayFields === 'object' && Object.keys(body.ebayFields).length > 0) {
        updateData.ebayFields = body.ebayFields
      } else {
        updateData.ebayFields = null
      }
    }
    
    const updatedProduct = await prisma.product.update({
      where: { id: params.id },
      data: updateData,
      include: {
        category: true,
      },
    })

    return NextResponse.json(updatedProduct)
  } catch (error) {
    console.error('Error updating product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const session = await getServerSession()
    
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    await prisma.product.delete({
      where: { id: params.id },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error deleting product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


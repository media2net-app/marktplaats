import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

/**
 * Set product status to a specific value
 * Allows users to manually change status (e.g., completed -> pending)
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const productId = body.productId as string
    const status = body.status as string

    if (!productId || !status) {
      return NextResponse.json({ error: 'Product ID and status are required' }, { status: 400 })
    }

    // Validate status
    const validStatuses = ['pending', 'processing', 'completed', 'failed']
    if (!validStatuses.includes(status)) {
      return NextResponse.json({ error: 'Invalid status' }, { status: 400 })
    }

    // Check if product exists and belongs to user
    const product = await prisma.product.findUnique({
      where: { id: productId },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Update product status
    const updateData: any = {
      status: status,
    }

    // If resetting to pending, clear posted data
    if (status === 'pending') {
      updateData.marktplaatsUrl = null
      updateData.marktplaatsAdId = null
      updateData.views = 0
      updateData.saves = 0
      updateData.postedAt = null
    }

    const updatedProduct = await prisma.product.update({
      where: { id: productId },
      data: updateData,
    })

    return NextResponse.json({
      success: true,
      message: `Product status bijgewerkt naar ${status}`,
      product: updatedProduct,
    })
  } catch (error) {
    console.error('Error setting product status:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


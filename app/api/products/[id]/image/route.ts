import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { listFiles } from '@/lib/storage'

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
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Find first image (blob or local)
    const files = await listFiles(product.articleNumber)
    const first = files[0] || null

    return NextResponse.json({ image: first })
  } catch (error) {
    console.error('Error getting product image:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}



import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import fs from 'fs'
import path from 'path'

const ALLOWED_IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.heic']

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const session = await getServerSession()
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Find all images in media folder for this article number
    const mediaRoot = process.env.MEDIA_ROOT 
      ? path.resolve(process.env.MEDIA_ROOT)
      : path.resolve(process.cwd(), '..', 'public', 'media')
    
    const articleDir = path.join(mediaRoot, product.articleNumber)
    
    if (!fs.existsSync(articleDir)) {
      return NextResponse.json({ images: [] })
    }

    // Find all image files
    const files = fs.readdirSync(articleDir)
      .filter(file => {
        const ext = path.extname(file).toLowerCase()
        return ALLOWED_IMAGE_EXTS.includes(ext)
      })
      .sort()
      .map(file => `/media/${product.articleNumber}/${file}`)

    return NextResponse.json({ images: files })
  } catch (error) {
    console.error('Error getting product images:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


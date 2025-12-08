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
    
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const product = await prisma.product.findUnique({
      where: { id: params.id },
    })

    if (!product || product.userId !== session.user.id) {
      return NextResponse.json({ error: 'Product not found' }, { status: 404 })
    }

    // Find first image in media folder for this article number
    const mediaRoot = process.env.MEDIA_ROOT 
      ? path.resolve(process.env.MEDIA_ROOT)
      : path.resolve(process.cwd(), '..', 'public', 'media')
    
    const articleDir = path.join(mediaRoot, product.articleNumber)
    
    if (!fs.existsSync(articleDir)) {
      return NextResponse.json({ image: null })

    }

    // Find first image file
    const files = fs.readdirSync(articleDir)
      .filter(file => {
        const ext = path.extname(file).toLowerCase()
        return ALLOWED_IMAGE_EXTS.includes(ext)
      })
      .sort()

    if (files.length === 0) {
      return NextResponse.json({ image: null })
    }

    // Read the image file and return it
    const imagePath = path.join(articleDir, files[0])
    const imageBuffer = fs.readFileSync(imagePath)
    const ext = path.extname(files[0]).toLowerCase()
    
    // Determine content type
    const contentType = ext === '.png' ? 'image/png' 
      : ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg'
      : ext === '.heic' ? 'image/heic'
      : 'image/jpeg'
    
    // Return the image directly
    return new NextResponse(imageBuffer, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    })
  } catch (error) {
    console.error('Error getting product image:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}



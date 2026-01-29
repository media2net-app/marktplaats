import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { listFiles } from '@/lib/storage'
import fs from 'fs'
import path from 'path'

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

    if (!first) {
      return NextResponse.json({ error: 'No image found' }, { status: 404 })
    }

    // If it's a URL (blob storage), redirect to it
    if (first.startsWith('http://') || first.startsWith('https://')) {
      return NextResponse.redirect(first)
    }

    // If it's a local path, serve the file
    if (first.startsWith('/media/')) {
      const filePath = path.join(process.cwd(), 'public', first)
      
      if (fs.existsSync(filePath)) {
        const fileBuffer = await fs.promises.readFile(filePath)
        const ext = path.extname(filePath).toLowerCase()
        const contentType = 
          ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' :
          ext === '.png' ? 'image/png' :
          ext === '.heic' ? 'image/heic' :
          'image/jpeg'
        
        return new NextResponse(fileBuffer, {
          headers: {
            'Content-Type': contentType,
            'Cache-Control': 'public, max-age=31536000, immutable',
          },
        })
      }
    }

    // Fallback: return JSON with path
    return NextResponse.json({ image: first })
  } catch (error) {
    console.error('Error getting product image:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}



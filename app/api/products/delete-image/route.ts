import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { deleteFile } from '@/lib/storage'
import path from 'path'

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { imagePath, articleNumber, filename } = body

    if (!imagePath && (!articleNumber || !filename)) {
      return NextResponse.json({ error: 'Image path or articleNumber/filename is required' }, { status: 400 })
    }

    // Extract articleNumber and filename from imagePath if provided
    let finalArticleNumber = articleNumber
    let finalFilename = filename

    if (imagePath && imagePath.startsWith('/media/')) {
      // Path is relative like /media/articleNumber/filename.jpg
      const relativePath = imagePath.replace('/media/', '')
      const parts = relativePath.split('/')
      if (parts.length >= 2) {
        finalArticleNumber = parts[0]
        finalFilename = parts.slice(1).join('/')
      }
    }

    // For blob URLs we don't need articleNumber/filename
    const isBlobUrl = imagePath && imagePath.startsWith('http')

    if (!isBlobUrl && (!finalArticleNumber || !finalFilename)) {
      return NextResponse.json({ error: 'Invalid path format' }, { status: 400 })
    }

    try {
      await deleteFile(
        imagePath || `/media/${finalArticleNumber}/${finalFilename}`,
        finalArticleNumber
      )
      return NextResponse.json({ success: true })
    } catch (error: any) {
      console.error('Error deleting file:', error)
      // Don't fail if file doesn't exist (might already be deleted)
      return NextResponse.json({ success: true, message: 'File may not exist' })
    }
  } catch (error) {
    console.error('Error deleting image:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


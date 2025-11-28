import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import fs from 'fs'
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

    // Determine media root path
    const mediaRoot = process.env.MEDIA_ROOT 
      ? path.resolve(process.env.MEDIA_ROOT)
      : path.resolve(process.cwd(), '..', 'public', 'media')

    // Build file path
    let filePath: string
    if (imagePath && imagePath.startsWith('/media/')) {
      // Path is relative like /media/articleNumber/filename.jpg
      const relativePath = imagePath.replace('/media/', '')
      filePath = path.join(mediaRoot, relativePath)
    } else if (articleNumber && filename) {
      // Use articleNumber and filename
      filePath = path.join(mediaRoot, articleNumber, filename)
    } else {
      return NextResponse.json({ error: 'Invalid path format' }, { status: 400 })
    }

    // Verify the path is within the media directory for security
    const resolvedPath = path.resolve(filePath)
    const resolvedMediaRoot = path.resolve(mediaRoot)
    
    if (!resolvedPath.startsWith(resolvedMediaRoot)) {
      return NextResponse.json({ error: 'Invalid path - outside media directory' }, { status: 400 })
    }

    // Delete the file
    if (fs.existsSync(resolvedPath)) {
      fs.unlinkSync(resolvedPath)
      return NextResponse.json({ success: true })
    } else {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('Error deleting image:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


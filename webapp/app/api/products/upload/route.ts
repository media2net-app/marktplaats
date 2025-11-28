import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import fs from 'fs'
import path from 'path'

const ALLOWED_IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.heic']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    const articleNumber = formData.get('articleNumber') as string

    if (!articleNumber) {
      return NextResponse.json({ error: 'Article number is required' }, { status: 400 })
    }

    if (!files || files.length === 0) {
      return NextResponse.json({ error: 'No files provided' }, { status: 400 })
    }

    // Determine media root path (same as Python script uses)
    // Python script uses: ./public/media (relative to project root)
    // Next.js runs from webapp/, so we need to go up one level
    const mediaRoot = process.env.MEDIA_ROOT 
      ? path.resolve(process.env.MEDIA_ROOT)
      : path.resolve(process.cwd(), '..', 'public', 'media')

    // Create article number directory
    const articleDir = path.join(mediaRoot, articleNumber)
    if (!fs.existsSync(articleDir)) {
      fs.mkdirSync(articleDir, { recursive: true })
    }

    const uploadedFiles: string[] = []

    for (const file of files) {
      // Validate file type
      const ext = path.extname(file.name).toLowerCase()
      if (!ALLOWED_IMAGE_EXTS.includes(ext)) {
        continue // Skip invalid files
      }

      // Validate file size
      if (file.size > MAX_FILE_SIZE) {
        continue // Skip files that are too large
      }

      // Generate unique filename
      const timestamp = Date.now()
      const randomStr = Math.random().toString(36).substring(2, 8)
      const filename = `${timestamp}-${randomStr}${ext}`
      const filePath = path.join(articleDir, filename)

      // Save file
      const bytes = await file.arrayBuffer()
      const buffer = Buffer.from(bytes)
      fs.writeFileSync(filePath, buffer)

      uploadedFiles.push(path.join(articleNumber, filename))
    }

    if (uploadedFiles.length === 0) {
      return NextResponse.json({ error: 'No valid files uploaded' }, { status: 400 })
    }

    return NextResponse.json({ 
      success: true, 
      files: uploadedFiles,
      count: uploadedFiles.length 
    })
  } catch (error) {
    console.error('Error uploading files:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


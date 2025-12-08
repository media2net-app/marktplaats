import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { uploadFile } from '@/lib/storage'
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

      try {
        // Upload file (to cloud storage on Vercel, local filesystem locally)
        const result = await uploadFile(file, articleNumber, filename)
        uploadedFiles.push(result.path.replace('/media/', '')) // Remove /media/ prefix for compatibility
      } catch (error: any) {
        console.error('Error uploading file:', error)
        // Continue with other files even if one fails
        continue
      }
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


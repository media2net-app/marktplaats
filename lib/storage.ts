import { put, list, del, head } from '@vercel/blob'
import path from 'path'
import fs from 'fs'

const MEDIA_ROOT = process.env.MEDIA_ROOT || './public/media'
const USE_BLOB_STORAGE = !!process.env.BLOB_READ_WRITE_TOKEN

/**
 * Upload a file to storage (Vercel Blob or local filesystem)
 */
export async function uploadFile(
  file: File,
  articleNumber: string,
  filename: string
): Promise<{ path: string; url?: string }> {
  if (USE_BLOB_STORAGE) {
    // Use Vercel Blob Storage
    const blob = await put(filename, file, {
      access: 'public',
      addRandomSuffix: false,
    })
    return {
      path: blob.url,
      url: blob.url,
    }
  } else {
    // Use local filesystem
    const articleDir = path.join(MEDIA_ROOT, articleNumber)
    await fs.promises.mkdir(articleDir, { recursive: true })
    
    const filePath = path.join(articleDir, filename)
    const buffer = Buffer.from(await file.arrayBuffer())
    await fs.promises.writeFile(filePath, buffer)
    
    // Return relative path for local storage
    const relativePath = `/media/${articleNumber}/${filename}`
    return {
      path: relativePath,
    }
  }
}

/**
 * List all files for an article number
 */
export async function listFiles(articleNumber: string): Promise<string[]> {
  if (!articleNumber) {
    return []
  }
  
  if (USE_BLOB_STORAGE) {
    // List from Vercel Blob Storage
    // Note: Vercel Blob doesn't have a direct way to list by prefix
    // We'll need to store file metadata or use a different approach
    // For now, return empty array - files should be tracked in database
    try {
      // Try to list blobs with prefix (if articleNumber is used as prefix)
      const { list } = await import('@vercel/blob')
      const blobs = await list({ prefix: articleNumber })
      return blobs.blobs.map(blob => blob.url)
    } catch (error) {
      console.error('Error listing blobs:', error)
      return []
    }
  } else {
    // List from local filesystem
    const articleDir = path.join(MEDIA_ROOT, articleNumber)
    
    try {
      // Check if MEDIA_ROOT exists
      if (!fs.existsSync(MEDIA_ROOT)) {
        return []
      }
      
      // Check if article directory exists
      if (!fs.existsSync(articleDir)) {
        return []
      }
      
      const files = await fs.promises.readdir(articleDir)
      const imageFiles = files.filter(file => {
        const ext = path.extname(file).toLowerCase()
        return ['.jpg', '.jpeg', '.png', '.heic'].includes(ext)
      })
      
      return imageFiles.map(file => `/media/${articleNumber}/${file}`)
    } catch (error) {
      // Directory doesn't exist or can't be read
      console.error('Error listing local files:', error)
      return []
    }
  }
}

/**
 * Delete a file from storage
 */
export async function deleteFile(
  filePath: string,
  articleNumber?: string
): Promise<void> {
  if (filePath.startsWith('http')) {
    // Blob URL - delete from Vercel Blob
    if (USE_BLOB_STORAGE) {
      try {
        await del(filePath)
      } catch (error) {
        // File might not exist, that's okay
        console.warn('Error deleting blob file:', error)
      }
    }
  } else {
    // Local file path
    const fullPath = filePath.startsWith('/')
      ? path.join('./public', filePath)
      : path.join(MEDIA_ROOT, articleNumber || '', filePath)
    
    try {
      await fs.promises.unlink(fullPath)
    } catch (error) {
      // File might not exist, that's okay
      console.warn('Error deleting local file:', error)
    }
  }
}

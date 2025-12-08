import { writeFile, mkdir, readdir, unlink, stat } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

const MEDIA_DIR = join(process.cwd(), 'public', 'media')

/**
 * Upload a file to local storage
 */
export async function uploadFile(file: File, articleNumber: string, filename: string): Promise<{ path: string }> {
  const articleDir = join(MEDIA_DIR, articleNumber)
  
  // Create directory if it doesn't exist
  if (!existsSync(articleDir)) {
    await mkdir(articleDir, { recursive: true })
  }
  
  const filePath = join(articleDir, filename)
  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)
  
  await writeFile(filePath, buffer)
  
  return {
    path: `/media/${articleNumber}/${filename}`
  }
}

/**
 * List all files for a given article number
 */
export async function listFiles(articleNumber: string): Promise<string[]> {
  const articleDir = join(MEDIA_DIR, articleNumber)
  
  if (!existsSync(articleDir)) {
    return []
  }
  
  try {
    const files = await readdir(articleDir)
    return files
      .filter(file => {
        const ext = file.toLowerCase()
        return ext.endsWith('.jpg') || ext.endsWith('.jpeg') || ext.endsWith('.png') || ext.endsWith('.heic')
      })
      .map(file => `/media/${articleNumber}/${file}`)
  } catch (error) {
    console.error('Error listing files:', error)
    return []
  }
}

/**
 * Delete a file
 */
export async function deleteFile(imagePath: string, articleNumber: string): Promise<void> {
  // Extract filename from path
  const filename = imagePath.split('/').pop() || ''
  const filePath = join(MEDIA_DIR, articleNumber, filename)
  
  if (existsSync(filePath)) {
    await unlink(filePath)
  }
}

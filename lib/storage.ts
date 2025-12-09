import { writeFile, mkdir, readdir, unlink } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'
import { put, list, del } from '@vercel/blob'

const MEDIA_DIR = join(process.cwd(), 'public', 'media')
const BLOB_TOKEN = process.env.BLOB_READ_WRITE_TOKEN
const useBlob = Boolean(BLOB_TOKEN)

/**
 * Upload a file to either Vercel Blob (if configured) or local storage.
 */
export async function uploadFile(file: File, articleNumber: string, filename: string): Promise<{ path: string }> {
  if (useBlob) {
    const key = `${articleNumber}/${filename}`
    const bytes = await file.arrayBuffer()
    const { url } = await put(key, bytes, {
      access: 'public',
      token: BLOB_TOKEN,
      contentType: file.type || 'application/octet-stream',
    })
    return { path: url }
  }

  const articleDir = join(MEDIA_DIR, articleNumber)
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
 * List all files for a given article number as absolute URLs (blob) or public paths (local).
 */
export async function listFiles(articleNumber: string): Promise<string[]> {
  if (useBlob) {
    const result = await list({
      prefix: `${articleNumber}/`,
      token: BLOB_TOKEN,
    })
    return result.blobs.map(b => b.url)
  }

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
 * Delete a file from blob or local storage.
 */
export async function deleteFile(imagePath: string, articleNumber?: string): Promise<void> {
  if (useBlob) {
    await del(imagePath, { token: BLOB_TOKEN })
    return
  }

  if (!articleNumber) return

  const filename = imagePath.split('/').pop() || ''
  const filePath = join(MEDIA_DIR, articleNumber, filename)

  if (existsSync(filePath)) {
    await unlink(filePath)
  }
}

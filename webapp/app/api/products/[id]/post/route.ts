import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'
import fs from 'fs'

const execAsync = promisify(exec)

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  const params = await context.params
  try {
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

    // Update status to processing
    await prisma.product.update({
      where: { id: params.id },
      data: { status: 'processing' },
    })

    // Get paths from environment
    // webapp/ is current working directory, so go up one level to project root
    const projectRoot = path.join(process.cwd(), '..')
    const scriptPath = process.env.PYTHON_SCRIPT_PATH || path.join(projectRoot, 'scripts', 'post_ads.py')
    const pythonCmd = process.env.PYTHON_CMD || 'python'
    
    // Get base URL for API calls
    // In production, use NEXTAUTH_URL or VERCEL_URL
    // In development, default to localhost:3000
    const baseUrl = process.env.NEXTAUTH_URL 
      || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null)
      || 'http://localhost:3000'
    
    console.log(`[POST] Project root: ${projectRoot}`)
    console.log(`[POST] Script path: ${scriptPath}`)
    console.log(`[POST] Python command: ${pythonCmd}`)
    console.log(`[POST] API base URL: ${baseUrl}`)

    try {
      // Verify script exists
      if (!fs.existsSync(scriptPath)) {
        throw new Error(`Python script not found at: ${scriptPath}`)
      }

      // Get API key for internal calls
      const apiKey = process.env.INTERNAL_API_KEY || 'internal-key-change-in-production'
      const apiUrl = `${baseUrl}/api/products/export/${params.id}?api_key=${apiKey}`
      
      console.log(`[POST] Executing: ${pythonCmd} "${scriptPath}" --api "${apiUrl}" --product-id "${params.id}"`)
      console.log(`[POST] Working directory: ${path.dirname(scriptPath)}`)
      
      // Execute Python script with API endpoint instead of CSV
      const { stdout, stderr } = await execAsync(
        `${pythonCmd} "${scriptPath}" --api "${apiUrl}" --product-id "${params.id}"`,
        { 
          cwd: path.dirname(scriptPath),
          maxBuffer: 10 * 1024 * 1024, // 10MB buffer
          timeout: 300000, // 5 minutes timeout
          env: {
            ...process.env,
            PRODUCT_API_URL: apiUrl,
            PRODUCT_ID: params.id,
            INTERNAL_API_KEY: apiKey,
          }
        }
      )

      console.log(`[POST] Script stdout: ${stdout}`)
      if (stderr) {
        console.log(`[POST] Script stderr: ${stderr}`)
      }

      // Check if script succeeded (look for success indicators in output)
      const output = stdout + stderr
      const hasError = output.toLowerCase().includes('error') || 
                       output.toLowerCase().includes('failed') ||
                       output.toLowerCase().includes('exception')

      if (hasError && !output.includes('✔ Succesvol verwerkt')) {
        // Script ran but had errors
        await prisma.product.update({
          where: { id: params.id },
          data: { status: 'failed' },
        })

        return NextResponse.json({ 
          success: false,
          error: 'Script execution had errors',
          output: output,
        }, { status: 500 })
      }

      // Try to extract result JSON from output
      let adStats: any = null
      const resultMatch = output.match(/RESULT_JSON:({.+})/)
      if (resultMatch) {
        try {
          adStats = JSON.parse(resultMatch[1])
        } catch (e) {
          console.error('Failed to parse result JSON:', e)
        }
      }

      // Parse posted_at date if available
      let postedAtDate: Date | null = null
      if (adStats?.posted_at) {
        // Try to parse Dutch date format like "6 nov '25"
        // For now, we'll store the raw string and parse it properly later
        // Or use current date as fallback
        postedAtDate = new Date()
      }

      // Update product status to completed with stats
      await prisma.product.update({
        where: { id: params.id },
        data: { 
          status: 'completed',
          marktplaatsUrl: adStats?.ad_url || null,
          marktplaatsAdId: adStats?.ad_id || null,
          views: adStats?.views || 0,
          saves: adStats?.saves || 0,
          postedAt: postedAtDate,
        },
      })

      return NextResponse.json({ 
        success: true,
        message: 'Product succesvol geplaatst',
        output: output,
      })
    } catch (execError: any) {
      console.error('[POST] Error executing script:', execError)

      // Update product status
      await prisma.product.update({
        where: { id: params.id },
        data: { status: 'failed' },
      })

      // Extract more detailed error info
      const errorMessage = execError.message || 'Unknown error'
      const errorStderr = execError.stderr || ''
      const errorStdout = execError.stdout || ''

      return NextResponse.json({ 
        success: false,
        error: errorMessage,
        details: {
          stderr: errorStderr,
          stdout: errorStdout,
          code: execError.code,
          signal: execError.signal,
        },
      }, { status: 500 })
    }
  } catch (error: any) {
    console.error('Error posting product:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}


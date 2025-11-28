import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'
import fs from 'fs'

const execAsync = promisify(exec)

/**
 * Sync statistics for all completed products from Marktplaats user page
 */
export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession()
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user URL from request or use default
    const body = await request.json().catch(() => ({}))
    const userUrl = body.userUrl || 'https://www.marktplaats.nl/u/chiel/23777446/'

    // Get all completed products for this user
    const products = await prisma.product.findMany({
      where: {
        userId: session.user.id,
        status: 'completed',
        marktplaatsUrl: { not: null },
      },
    })

    if (products.length === 0) {
      return NextResponse.json({ message: 'No completed products found', updated: 0 })
    }

    // Get paths - script is in parent directory
    const projectRoot = path.resolve(process.cwd(), '..')
    const scriptPath = path.join(projectRoot, 'scripts', 'scrape_user_ads.py')
    const pythonCmd = process.env.PYTHON_CMD || 'python'

    // Verify script exists
    if (!fs.existsSync(scriptPath)) {
      return NextResponse.json({ 
        error: `Script not found at ${scriptPath}` 
      }, { status: 500 })
    }

    // Run Python script to scrape user page
    const { stdout, stderr } = await execAsync(
      `"${pythonCmd}" "${scriptPath}" --url "${userUrl}"`,
      {
        cwd: projectRoot,
        maxBuffer: 10 * 1024 * 1024,
        timeout: 120000, // 2 minutes
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1',
        },
      }
    )

    // Parse JSON output from script
    const output = stdout + stderr
    const jsonMatch = output.match(/USER_ADS_JSON:(\[.+?\])/s)
    
    if (!jsonMatch) {
      return NextResponse.json({ 
        error: 'Could not parse ads from script output',
        output: output 
      }, { status: 500 })
    }

    const userAds = JSON.parse(jsonMatch[1])
    let updated = 0

    // Match and update products
    for (const product of products) {
      // Try to find matching ad
      const matchingAd = userAds.find((ad: any) => {
        // Match by ad ID (most reliable)
        if (product.marktplaatsAdId && ad.ad_id && ad.ad_id === product.marktplaatsAdId) {
          return true
        }
        // Match by URL (exact match)
        if (product.marktplaatsUrl && ad.ad_url) {
          // Normalize URLs for comparison
          const productUrl = product.marktplaatsUrl.replace(/\/$/, '')
          const adUrl = ad.ad_url.replace(/\/$/, '')
          if (productUrl === adUrl || productUrl.includes(adUrl) || adUrl.includes(productUrl)) {
            return true
          }
        }
        // Match by title similarity (fuzzy match)
        if (product.title && ad.title) {
          const productTitleLower = product.title.toLowerCase().trim()
          const adTitleLower = ad.title.toLowerCase().trim()
          // Check if titles are similar (at least 70% match)
          if (productTitleLower === adTitleLower || 
              productTitleLower.includes(adTitleLower) || 
              adTitleLower.includes(productTitleLower)) {
            return true
          }
        }
        // Match by article number in title (last resort)
        if (product.articleNumber && ad.title && ad.title.includes(product.articleNumber)) {
          return true
        }
        return false
      })

      if (matchingAd) {
        // Parse posted_at date
        let postedAtDate: Date | null = null
        if (matchingAd.posted_at) {
          // Try to parse Dutch date format
          const dateStr = matchingAd.posted_at
          if (dateStr === 'Vandaag') {
            postedAtDate = new Date()
          } else if (dateStr === 'Gisteren') {
            const yesterday = new Date()
            yesterday.setDate(yesterday.getDate() - 1)
            postedAtDate = yesterday
          } else if (dateStr.startsWith('Sinds')) {
            // Try to parse date from "Sinds X" format
            postedAtDate = new Date() // Fallback to current date
          } else {
            postedAtDate = new Date() // Default to current date
          }
        }

        const updateData: any = {
          views: matchingAd.views || 0,
          saves: matchingAd.saves || 0,
        }

        // Only update these if we have new values
        if (matchingAd.ad_id) {
          updateData.marktplaatsAdId = matchingAd.ad_id
        }
        if (matchingAd.ad_url) {
          updateData.marktplaatsUrl = matchingAd.ad_url
        }
        if (postedAtDate) {
          updateData.postedAt = postedAtDate
        }

        await prisma.product.update({
          where: { id: product.id },
          data: updateData,
        })
        updated++
        console.log(`Updated product ${product.id}: views=${updateData.views}, saves=${updateData.saves}`)
      } else {
        console.log(`No matching ad found for product ${product.id} (${product.title})`)
      }
    }

    return NextResponse.json({
      success: true,
      message: `Updated ${updated} of ${products.length} products`,
      updated,
      total: products.length,
    })
  } catch (error: any) {
    console.error('Error syncing stats:', error)
    return NextResponse.json({
      error: error.message || 'Internal server error',
      details: error.stderr || error.stdout,
    }, { status: 500 })
  }
}


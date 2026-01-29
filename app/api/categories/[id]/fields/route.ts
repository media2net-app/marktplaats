import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import { prisma } from '@/lib/prisma'

/**
 * Get category-specific fields for a given category ID
 * Reads from category_fields_v2.json file
 * Matches by category ID or category path from database
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const categoryId = params.id

    if (!categoryId) {
      return NextResponse.json({ error: 'Category ID is required' }, { status: 400 })
    }

    // Read category fields from JSON file
    const jsonPath = path.join(process.cwd(), 'category_fields_v2.json')
    
    if (!fs.existsSync(jsonPath)) {
      console.warn(`category_fields_v2.json not found at ${jsonPath}`)
      return NextResponse.json({ fields: null, message: 'Category fields file not found' })
    }

    const fileContent = fs.readFileSync(jsonPath, 'utf-8')
    const data = JSON.parse(fileContent)
    const allCategories = data?.categorySpecificFields?.categories || {}

    // First, try direct match by category ID
    let categoryFields = allCategories[categoryId]

    // If not found, try to get category from database to get the path
    if (!categoryFields) {
      try {
        const dbCategory = await prisma.category.findUnique({
          where: { id: categoryId },
          include: {
            parent: {
              include: {
                parent: true
              }
            }
          }
        })

        if (dbCategory) {
          if (dbCategory.path) {
            console.log(`[CATEGORY FIELDS] Looking for category: ${categoryId}, Path: ${dbCategory.path}, Level: ${dbCategory.level}`)
            // Try to find by exact path match
            const foundByPath = Object.values(allCategories).find((cat: any) => 
              cat.categoryPath?.toLowerCase() === dbCategory.path.toLowerCase()
            )

            if (foundByPath) {
              categoryFields = foundByPath
            } else {
              // Try fuzzy match on path (handles variations in formatting)
              const normalizedDbPath = dbCategory.path.toLowerCase().replace(/\s*>\s*/g, ' > ').trim()
              const foundByFuzzyPath = Object.values(allCategories).find((cat: any) => {
                if (!cat.categoryPath) return false
                const normalizedCatPath = cat.categoryPath.toLowerCase().replace(/\s*>\s*/g, ' > ').trim()
                return normalizedCatPath === normalizedDbPath
              })

              if (foundByFuzzyPath) {
                categoryFields = foundByFuzzyPath
              } else {
                // Try partial match - check if category path contains key parts
                const dbPathParts = normalizedDbPath.split(' > ').map((p: string) => p.trim())
                
                // First try: match all parts in order (for exact sub-subcategory match)
                let foundByPartial = Object.values(allCategories).find((cat: any) => {
                  if (!cat.categoryPath) return false
                  const catPathParts = cat.categoryPath.toLowerCase().split(' > ').map((p: string) => p.trim())
                  // Check if all parts of db path are in cat path (in order)
                  if (dbPathParts.length > catPathParts.length) return false
                  let dbIndex = 0
                  for (let i = 0; i < catPathParts.length && dbIndex < dbPathParts.length; i++) {
                    if (catPathParts[i].includes(dbPathParts[dbIndex]) || dbPathParts[dbIndex].includes(catPathParts[i])) {
                      dbIndex++
                    }
                  }
                  return dbIndex === dbPathParts.length
                })

              // If not found, try matching only the last 2-3 parts (for sub-subcategories)
              // This is more specific: match the last 2 parts at the END of the category path
              if (!foundByPartial && dbPathParts.length >= 2) {
                const lastParts = dbPathParts.slice(-2) // Last 2 parts
                foundByPartial = Object.values(allCategories).find((cat: any) => {
                  if (!cat.categoryPath) return false
                  const catPathParts = cat.categoryPath.toLowerCase().split(' > ').map((p: string) => p.trim())
                  
                  // Must have at least as many parts as we're matching
                  if (catPathParts.length < lastParts.length) return false
                  
                  // Check if last parts match at the END of cat path (exact position match)
                  let matchCount = 0
                  const startIndex = catPathParts.length - lastParts.length
                  for (let i = 0; i < lastParts.length; i++) {
                    const catPart = catPathParts[startIndex + i]
                    const dbPart = lastParts[i]
                    // More strict matching: both parts should match (not just contain)
                    if (catPart === dbPart || 
                        (catPart.includes(dbPart) && dbPart.length > 3) || // Only if dbPart is substantial
                        (dbPart.includes(catPart) && catPart.length > 3)) {
                      matchCount++
                    }
                  }
                  // All parts must match
                  return matchCount === lastParts.length
                })
              }

                // If still not found and we have 3+ parts, try matching last 3 parts (for sub-subcategories)
                if (!foundByPartial && dbPathParts.length >= 3) {
                  const lastParts = dbPathParts.slice(-3) // Last 3 parts
                  foundByPartial = Object.values(allCategories).find((cat: any) => {
                    if (!cat.categoryPath) return false
                    const catPathParts = cat.categoryPath.toLowerCase().split(' > ').map((p: string) => p.trim())
                    
                    if (catPathParts.length < lastParts.length) return false
                    
                    // Check if last 3 parts match at the END of cat path
                    let matchCount = 0
                    const startIndex = catPathParts.length - lastParts.length
                    for (let i = 0; i < lastParts.length; i++) {
                      const catPart = catPathParts[startIndex + i]
                      const dbPart = lastParts[i]
                      if (catPart === dbPart || 
                          (catPart.includes(dbPart) && dbPart.length > 3) ||
                          (dbPart.includes(catPart) && catPart.length > 3)) {
                        matchCount++
                      }
                    }
                    return matchCount === lastParts.length
                  })
                }

                // If still not found, try matching only the last part (for any subcategory)
                // But only if we haven't found anything yet and we have a single part
                if (!foundByPartial && dbPathParts.length === 1) {
                  const lastPart = dbPathParts[dbPathParts.length - 1]
                  foundByPartial = Object.values(allCategories).find((cat: any) => {
                    if (!cat.categoryPath) return false
                    const catPathParts = cat.categoryPath.toLowerCase().split(' > ').map((p: string) => p.trim())
                    // Check if last part of db path matches the last part of cat path
                    return catPathParts[catPathParts.length - 1] === lastPart ||
                           (catPathParts[catPathParts.length - 1].includes(lastPart) && lastPart.length > 3)
                  })
                }

                if (foundByPartial) {
                  categoryFields = foundByPartial
                  console.log(`[CATEGORY FIELDS] Found by partial match: ${(foundByPartial as any).categoryPath}`)
                } else {
                  console.log(`[CATEGORY FIELDS] No partial match found for path: ${dbCategory.path}`)
                }
              }
          }
        } else {
          console.log(`[CATEGORY FIELDS] Category found in DB but no path: ${categoryId}`)
        }
        } else {
          console.log(`[CATEGORY FIELDS] Category not found in database: ${categoryId}`)
        }
      } catch (dbError) {
        console.warn(`[CATEGORY FIELDS] Could not fetch category from database: ${dbError}`)
        // Continue with other matching strategies
      }
    }

    // If still not found, try direct string matching on category ID or path
    if (!categoryFields) {
      const found = Object.values(allCategories).find((cat: any) => 
        cat.categoryId === categoryId || 
        cat.categoryId?.toLowerCase().includes(categoryId.toLowerCase()) ||
        cat.categoryPath?.toLowerCase().includes(categoryId.toLowerCase())
      )
      
      if (found) {
        categoryFields = found
      }
    }

    if (!categoryFields) {
      // Get category from database for better debugging
      let dbCategoryInfo = null
      try {
        const dbCategory = await prisma.category.findUnique({
          where: { id: categoryId },
          include: {
            parent: {
              include: {
                parent: true
              }
            }
          }
        })
        if (dbCategory) {
          dbCategoryInfo = {
            id: dbCategory.id,
            name: dbCategory.name,
            path: dbCategory.path,
            level: dbCategory.level,
            parentPath: dbCategory.parent?.path || null,
            grandParentPath: dbCategory.parent?.parent?.path || null
          }
          
          // Find similar paths for debugging
          const pathParts = dbCategory.path.toLowerCase().split(' > ')
          const lastPart = pathParts[pathParts.length - 1] || ''
          const similarPaths = Object.values(allCategories)
            .filter((cat: any) => {
              if (!cat.categoryPath) return false
              const catPath = cat.categoryPath.toLowerCase()
              return catPath.includes(lastPart) || lastPart.includes(catPath.split(' > ')[catPath.split(' > ').length - 1] || '')
            })
            .slice(0, 10)
            .map((cat: any) => ({
              id: cat.categoryId,
              path: cat.categoryPath
            }))
          
          console.log(`[CATEGORY FIELDS] No match found. Similar paths:`, similarPaths)
        }
      } catch (e) {
        console.error(`[CATEGORY FIELDS] Error getting debug info:`, e)
      }

      return NextResponse.json({ 
        fields: null, 
        message: `No fields found for category: ${categoryId}`,
        debug: {
          categoryId,
          dbCategory: dbCategoryInfo,
          totalCategoriesInFile: Object.keys(allCategories).length
        }
      })
    }
    
    console.log(`[CATEGORY FIELDS] Successfully found fields for: ${categoryFields.categoryPath}`)

    return NextResponse.json({
      fields: categoryFields.fields || null,
      categoryInfo: {
        id: categoryFields.categoryId,
        name: categoryFields.categoryName,
        path: categoryFields.categoryPath
      }
    })
  } catch (error: any) {
    console.error('Error fetching category fields:', error)
    return NextResponse.json({ 
      error: 'Internal server error',
      message: error.message 
    }, { status: 500 })
  }
}

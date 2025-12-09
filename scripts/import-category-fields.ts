/**
 * Import category fields van category_fields_v2.json naar de database.
 */
import { PrismaClient } from '@prisma/client'
import * as fs from 'fs'
import * as path from 'path'

const prisma = new PrismaClient()

interface CategoryField {
  name: string
  type: string
  label: string
  required?: boolean
  isBaseField?: boolean
  options?: Array<{ label: string; value: string }>
  placeholder?: string
  min?: number
  max?: number
  step?: number
  maxLength?: number
}

interface CategoryData {
  categoryPath: string
  categoryName: string
  categoryId: string
  level: number
  parentId: string
  fields: CategoryField[]
}

interface CategoryFieldsData {
  categorySpecificFields: {
    categories: Record<string, CategoryData>
  }
}

async function importCategoryFields() {
  try {
    // Pad naar JSON bestand
    const jsonFile = path.join(process.cwd(), 'category_fields_v2.json')
    
    if (!fs.existsSync(jsonFile)) {
      console.error(`❌ Bestand niet gevonden: ${jsonFile}`)
      process.exit(1)
    }
    
    console.log(`📖 Lezen van ${jsonFile}...`)
    const fileContent = fs.readFileSync(jsonFile, 'utf-8')
    const data: CategoryFieldsData = JSON.parse(fileContent)
    
    const categoriesData = data.categorySpecificFields?.categories || {}
    
    if (Object.keys(categoriesData).length === 0) {
      console.error('❌ Geen categorieën gevonden in JSON bestand!')
      process.exit(1)
    }
    
    console.log(`✅ ${Object.keys(categoriesData).length} categorieën gevonden in JSON`)
    console.log('\n📤 Importeren naar database...')
    console.log('='.repeat(70))
    
    let updated = 0
    let notFound = 0
    let errors = 0
    
    for (const [categoryKey, categoryInfo] of Object.entries(categoriesData)) {
      try {
        const categoryPath = categoryInfo.categoryPath || ''
        const fields = categoryInfo.fields || []
        
        // Filter out base fields (we only want category-specific fields)
        const categorySpecificFields = fields.filter(
          field => !field.isBaseField
        )
        
        // Skip if no category-specific fields
        if (categorySpecificFields.length === 0) {
          continue
        }
        
        // Find category in database by path
        let category = await prisma.category.findFirst({
          where: {
            path: categoryPath
          }
        })
        
        if (!category) {
          // Try to find by name (last part of path)
          const categoryName = categoryPath.split(' > ').pop() || ''
          category = await prisma.category.findFirst({
            where: {
              name: categoryName,
              level: categoryInfo.level || 3
            }
          })
        }
        
        if (category) {
          // Update category with fields
          await prisma.category.update({
            where: { id: category.id },
            data: { fields: categorySpecificFields as any }
          })
          updated++
          if (updated % 100 === 0) {
            console.log(`  ✅ ${updated} categorieën bijgewerkt...`)
          }
        } else {
          notFound++
          if (notFound <= 10) {
            console.log(`  ⚠️  Categorie niet gevonden: ${categoryPath}`)
          }
        }
      } catch (error: any) {
        errors++
        console.error(`  ❌ Fout bij ${categoryKey}: ${error.message}`)
      }
    }
    
    console.log('='.repeat(70))
    console.log(`\n✅ Klaar!`)
    console.log(`   📊 Bijgewerkt: ${updated}`)
    console.log(`   ⚠️  Niet gevonden: ${notFound}`)
    console.log(`   ❌ Fouten: ${errors}`)
    
  } catch (error: any) {
    console.error(`❌ Fout: ${error.message}`)
    console.error(error)
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

// Run import
importCategoryFields()
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })





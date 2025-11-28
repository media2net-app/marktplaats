const { PrismaClient } = require('@prisma/client')
const fs = require('fs')
const path = require('path')

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL || 'file:./dev.db',
    },
  },
})

async function importCategories() {
  try {
    const categoriesFile = path.join(__dirname, '..', '..', 'categories.json')
    
    if (!fs.existsSync(categoriesFile)) {
      console.log('❌ categories.json niet gevonden. Run eerst scrape_categories.py')
      return
    }

    const categories = JSON.parse(fs.readFileSync(categoriesFile, 'utf-8'))
    
    console.log(`📥 Importeren van ${categories.length} categorieën...`)

    // Verwijder bestaande categorieën
    await prisma.category.deleteMany({})
    console.log('🗑️  Bestaande categorieën verwijderd')

    // Importeer categorieën in volgorde van level (eerst level 1, dan 2, dan 3)
    const sortedCategories = categories.sort((a, b) => a.level - b.level)
    
    for (const cat of sortedCategories) {
      // Zoek parent category als parentId is opgegeven
      let parentCategory = null
      if (cat.parentId) {
        parentCategory = await prisma.category.findFirst({
          where: { 
            OR: [
              { id: cat.parentId },
              { marktplaatsId: cat.parentId },
              { name: cat.parentId }
            ]
          }
        })
      }

      await prisma.category.create({
        data: {
          name: cat.name,
          level: cat.level,
          parentId: parentCategory?.id || null,
          path: cat.path,
          marktplaatsId: cat.id,
        },
      })
    }

    console.log(`✅ ${categories.length} categorieën geïmporteerd!`)
    
    // Toon statistieken
    const stats = await prisma.category.groupBy({
      by: ['level'],
      _count: true,
    })
    
    console.log('\n📊 Statistieken:')
    stats.forEach(stat => {
      console.log(`  Level ${stat.level}: ${stat._count} categorieën`)
    })
    
  } catch (error) {
    console.error('❌ Fout bij importeren:', error)
  } finally {
    await prisma.$disconnect()
  }
}

importCategories()


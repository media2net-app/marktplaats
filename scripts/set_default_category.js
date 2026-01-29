// Script om standaard categorie in te stellen en bestaande producten bij te werken
const { PrismaClient } = require('@prisma/client')
const prisma = new PrismaClient()

async function main() {
  const categoryPath = 'Hobby en Vrije tijd > Overige Hobby en Vrije tijd'
  
  // Find or create the category
  let category = await prisma.category.findFirst({
    where: { path: categoryPath }
  })
  
  if (!category) {
    // Find parent category first
    const parentCategory = await prisma.category.findFirst({
      where: { path: 'Hobby en Vrije tijd' }
    })
    
    if (!parentCategory) {
      // Create parent category first
      const parent = await prisma.category.create({
        data: {
          name: 'Hobby en Vrije tijd',
          level: 1,
          path: 'Hobby en Vrije tijd',
        }
      })
      
      // Create child category
      category = await prisma.category.create({
        data: {
          name: 'Overige Hobby en Vrije tijd',
          level: 2,
          parentId: parent.id,
          path: categoryPath,
        }
      })
      console.log('✅ Categorieën aangemaakt')
    } else {
      // Create child category
      category = await prisma.category.create({
        data: {
          name: 'Overige Hobby en Vrije tijd',
          level: 2,
          parentId: parentCategory.id,
          path: categoryPath,
        }
      })
      console.log('✅ Categorie aangemaakt')
    }
  } else {
    console.log('✅ Categorie gevonden:', category.id)
  }
  
  // Update all products to use this category
  const result = await prisma.product.updateMany({
    data: {
      categoryId: category.id,
    }
  })
  
  console.log(`✅ ${result.count} product(en) bijgewerkt naar categorie: ${categoryPath}`)
  console.log(`   Categorie ID: ${category.id}`)
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())

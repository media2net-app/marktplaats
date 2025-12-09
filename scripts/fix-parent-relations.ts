import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('Herstellen van parent-child relaties...')
  
  // Fix level 2 categorieën in batches
  let offset = 0
  const batchSize = 100
  let totalUpdated = 0
  
  while (true) {
    const level2Categories = await prisma.category.findMany({
      where: {
        level: 2,
        parentId: null,
      },
      select: {
        id: true,
        path: true,
      },
      skip: offset,
      take: batchSize,
    })
    
    if (level2Categories.length === 0) break
    
    for (const cat of level2Categories) {
      if (cat.path.includes(' > ')) {
        const parts = cat.path.split(' > ')
        if (parts.length >= 2) {
          const parentPath = parts[0]
          const parent = await prisma.category.findFirst({
            where: {
              path: parentPath,
              level: 1,
            },
            select: { id: true },
          })
          
          if (parent) {
            await prisma.category.update({
              where: { id: cat.id },
              data: { parentId: parent.id },
            })
            totalUpdated++
          }
        }
      }
    }
    
    offset += batchSize
    if (totalUpdated % 50 === 0 && totalUpdated > 0) {
      console.log(`  ✅ ${totalUpdated} level 2 categorieën bijgewerkt...`)
    }
  }
  
  // Fix level 3 categorieën
  offset = 0
  while (true) {
    const level3Categories = await prisma.category.findMany({
      where: {
        level: 3,
        parentId: null,
      },
      select: {
        id: true,
        path: true,
      },
      skip: offset,
      take: batchSize,
    })
    
    if (level3Categories.length === 0) break
    
    for (const cat of level3Categories) {
      if (cat.path.includes(' > ')) {
        const parts = cat.path.split(' > ')
        if (parts.length >= 3) {
          const parentPath = parts.slice(0, 2).join(' > ')
          const parent = await prisma.category.findFirst({
            where: {
              path: parentPath,
              level: 2,
            },
            select: { id: true },
          })
          
          if (parent) {
            await prisma.category.update({
              where: { id: cat.id },
              data: { parentId: parent.id },
            })
            totalUpdated++
          }
        }
      }
    }
    
    offset += batchSize
    if (totalUpdated % 50 === 0 && totalUpdated > 0) {
      console.log(`  ✅ ${totalUpdated} categorieën bijgewerkt...`)
    }
  }
  
  console.log(`\n✅ Klaar! ${totalUpdated} categorieën bijgewerkt.`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })




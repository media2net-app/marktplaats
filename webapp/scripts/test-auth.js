const { PrismaClient } = require('@prisma/client')
const { compare } = require('bcryptjs')

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL || 'file:./dev.db',
    },
  },
})

async function testAuth() {
  try {
    console.log('Testing database connection...')
    const user = await prisma.user.findUnique({
      where: { email: 'admin@example.com' }
    })
    
    if (!user) {
      console.log('❌ User not found!')
      return
    }
    
    console.log('✅ User found:', user.email)
    console.log('Testing password...')
    
    const isValid = await compare('admin123', user.password)
    
    if (isValid) {
      console.log('✅ Password is correct!')
    } else {
      console.log('❌ Password is incorrect!')
    }
  } catch (error) {
    console.error('❌ Error:', error)
  } finally {
    await prisma.$disconnect()
  }
}

testAuth()


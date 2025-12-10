import { PrismaClient } from '@prisma/client'
import { hash } from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  const email = process.argv[2] || 'admin@example.com'
  const password = process.argv[3] || 'admin123'
  const name = process.argv[4] || 'Admin'

  console.log('Creating user...')
  console.log(`Email: ${email}`)
  console.log(`Name: ${name}`)

  // Check if user already exists
  const existingUser = await prisma.user.findUnique({
    where: { email }
  })

  if (existingUser) {
    console.log('User already exists. Updating password...')
    const hashedPassword = await hash(password, 10)
    await prisma.user.update({
      where: { email },
      data: { password: hashedPassword }
    })
    console.log('✅ Password updated successfully!')
  } else {
    const hashedPassword = await hash(password, 10)
    await prisma.user.create({
      data: {
        email,
        name,
        password: hashedPassword,
      }
    })
    console.log('✅ User created successfully!')
  }

  console.log('\nYou can now login with:')
  console.log(`  Email: ${email}`)
  console.log(`  Password: ${password}`)
}

main()
  .catch((e) => {
    console.error('Error:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })


















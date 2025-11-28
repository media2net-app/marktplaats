import { PrismaClient } from '@prisma/client'
import { PrismaClient as PrismaClientAccelerate } from '@prisma/client/edge'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | PrismaClientAccelerate | undefined
}

// Check if using Prisma Accelerate (prisma+postgres://)
const isAccelerate = process.env.DATABASE_URL?.startsWith('prisma+postgres://')

export const prisma = globalForPrisma.prisma ?? (
  isAccelerate
    ? new PrismaClientAccelerate({
        datasourceUrl: process.env.DATABASE_URL,
      })
    : new PrismaClient({
        log: process.env.NODE_ENV === 'development' ? ['error', 'warn'] : ['error'],
      })
)

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma


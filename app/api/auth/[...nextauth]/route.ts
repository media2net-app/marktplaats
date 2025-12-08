import NextAuth from 'next-auth'
import { authOptions } from '@/lib/auth'

// Ensure DATABASE_URL is set before initializing auth
if (!process.env.DATABASE_URL) {
  process.env.DATABASE_URL = 'file:./dev.db'
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }


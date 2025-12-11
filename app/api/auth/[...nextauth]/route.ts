import NextAuth from 'next-auth'
import { authOptions } from '@/lib/auth'

// Validate required environment variables
if (!process.env.DATABASE_URL) {
  console.error('[NEXTAUTH] ERROR: DATABASE_URL is not set!')
  console.error('[NEXTAUTH] This is required for the app to work.')
  console.error('[NEXTAUTH] Please set DATABASE_URL in Vercel environment variables.')
}

if (!process.env.NEXTAUTH_SECRET) {
  console.warn('[NEXTAUTH] WARNING: NEXTAUTH_SECRET is not set!')
  console.warn('[NEXTAUTH] Using fallback secret. This is not secure for production!')
}

if (!process.env.NEXTAUTH_URL) {
  console.warn('[NEXTAUTH] WARNING: NEXTAUTH_URL is not set!')
  console.warn('[NEXTAUTH] This may cause authentication issues.')
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }


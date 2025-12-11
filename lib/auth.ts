import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { compare } from 'bcryptjs'
import { prisma } from './prisma'

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET || 'fallback-secret-change-in-production',
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        try {
          if (!credentials?.email || !credentials?.password) {
            console.log('[AUTH] Missing credentials')
            return null
          }

          console.log('[AUTH] Attempting login for:', credentials.email)
          
          // Check if DATABASE_URL is set (required for production)
          if (!process.env.DATABASE_URL) {
            console.error('[AUTH] DATABASE_URL is not set! This is required for production.')
            throw new Error('Database not configured. Please set DATABASE_URL environment variable.')
          }
          
          const user = await prisma.user.findUnique({
            where: { email: credentials.email }
          })

          if (!user) {
            console.log('[AUTH] User not found:', credentials.email)
            return null
          }

          if (!user.password) {
            console.log('[AUTH] User has no password')
            return null
          }

          console.log('[AUTH] Comparing password...')
          const isValid = await compare(credentials.password, user.password)

          if (!isValid) {
            console.log('[AUTH] Invalid password for:', credentials.email)
            return null
          }

          console.log('[AUTH] Login successful for:', credentials.email)
          return {
            id: user.id,
            email: user.email,
            name: user.name,
          }
        } catch (error: any) {
          console.error('[AUTH] Error:', error)
          console.error('[AUTH] Error details:', error?.message, error?.stack)
          return null
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    },
  },
}

export async function getServerSession() {
  const { getServerSession: getSession } = await import('next-auth')
  return await getSession({ ...authOptions })
}


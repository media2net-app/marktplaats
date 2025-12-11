'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const router = useRouter()

  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Er is een fout opgetreden</h1>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            {error.message || 'Er is een onverwachte fout opgetreden.'}
          </p>
          
          {error.message?.includes('DATABASE_URL') && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-yellow-800 mb-2">Database niet geconfigureerd</h3>
              <p className="text-sm text-yellow-700 mb-2">
                De DATABASE_URL environment variable is niet ingesteld in Vercel.
              </p>
              <ol className="text-sm text-yellow-700 list-decimal list-inside space-y-1">
                <li>Ga naar Vercel Dashboard → Settings → Environment Variables</li>
                <li>Voeg toe: <code className="bg-yellow-100 px-1 rounded">DATABASE_URL</code></li>
                <li>Waarde: Je PostgreSQL connection string (bijv. Prisma Accelerate URL)</li>
                <li>Redeploy de applicatie</li>
              </ol>
            </div>
          )}
          
          {error.message?.includes('NEXTAUTH') && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-yellow-800 mb-2">NextAuth niet geconfigureerd</h3>
              <p className="text-sm text-yellow-700 mb-2">
                NEXTAUTH_SECRET of NEXTAUTH_URL ontbreekt.
              </p>
              <ol className="text-sm text-yellow-700 list-decimal list-inside space-y-1">
                <li>Ga naar Vercel Dashboard → Settings → Environment Variables</li>
                <li>Voeg toe: <code className="bg-yellow-100 px-1 rounded">NEXTAUTH_SECRET</code></li>
                <li>Voeg toe: <code className="bg-yellow-100 px-1 rounded">NEXTAUTH_URL</code></li>
                <li>Redeploy de applicatie</li>
              </ol>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => reset()}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
          >
            Opnieuw proberen
          </button>
          <button
            onClick={() => router.push('/login')}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
          >
            Naar Login
          </button>
        </div>
      </div>
    </div>
  )
}

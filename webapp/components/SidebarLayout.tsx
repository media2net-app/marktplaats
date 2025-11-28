'use client'

import { ReactNode } from 'react'
import { signOut } from 'next-auth/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface SidebarLayoutProps {
  user: {
    email: string
    name?: string | null
  }
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Producten', href: '/products' },
]

export default function SidebarLayout({ user, children }: SidebarLayoutProps) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <p className="text-sm text-gray-500">Ingelogd als</p>
          <p className="font-semibold text-gray-900">{user.email}</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-4 py-2 rounded-md font-medium ${
                  isActive
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => signOut({ callbackUrl: '/login' })}
            className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
          >
            Uitloggen
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="md:hidden bg-white border-b border-gray-200 px-4 py-3 flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-500">Ingelogd als</p>
            <p className="font-semibold text-gray-900">{user.email}</p>
          </div>
          <button
            onClick={() => signOut({ callbackUrl: '/login' })}
            className="px-3 py-1 text-sm font-medium text-white bg-indigo-600 rounded-md"
          >
            Uitloggen
          </button>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}


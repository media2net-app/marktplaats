import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import SidebarLayout from '@/components/SidebarLayout'
import ProductsClient from '@/components/ProductsClient'

export default async function ProductsPage() {
  const session = await getServerSession()

  if (!session || !session.user) {
    redirect('/login')
  }

  const products = await prisma.product.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: 'desc' },
  })

  return (
    <SidebarLayout user={{ email: session.user.email || '', name: session.user.name }}>
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Producten</h1>
            <p className="text-gray-600 mt-1">
              Beheer hier al je producten en verstuur ze met één klik naar Marktplaats.
            </p>
          </div>
        </div>
      </div>
      <ProductsClient products={products} />
    </SidebarLayout>
  )
}


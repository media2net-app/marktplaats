import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import SidebarLayout from '@/components/SidebarLayout'
import ProductEditForm from '@/components/ProductEditForm'

export default async function EditProductPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const resolvedParams = await params
  const session = await getServerSession()

  if (!session || !session.user) {
    redirect('/login')
  }

  const product = await prisma.product.findUnique({
    where: { id: resolvedParams.id },
    include: {
      category: true,
    },
  })

  if (!product || product.userId !== session.user.id) {
    redirect('/products')
  }

  // Serialize product for client component (ensure JSON fields are properly parsed)
  const serializedProduct = {
    ...product,
    createdAt: product.createdAt.toISOString(),
    updatedAt: product.updatedAt.toISOString(),
    postedAt: product.postedAt ? product.postedAt.toISOString() : null,
    ebayPostedAt: product.ebayPostedAt ? product.ebayPostedAt.toISOString() : null,
    // Ensure categoryFields and ebayFields are properly serialized
    categoryFields: product.categoryFields ? (typeof product.categoryFields === 'object' ? product.categoryFields : JSON.parse(product.categoryFields as any)) : null,
    ebayFields: product.ebayFields ? (typeof product.ebayFields === 'object' ? product.ebayFields : JSON.parse(product.ebayFields as any)) : null,
  }

  return (
    <SidebarLayout user={{ email: session.user.email || '', name: session.user.name }}>
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Product Bewerken</h1>
            <p className="text-gray-600 mt-1">
              Wijzig de gegevens van je product
            </p>
          </div>
        </div>
      </div>
      <ProductEditForm product={serializedProduct as any} />
    </SidebarLayout>
  )
}


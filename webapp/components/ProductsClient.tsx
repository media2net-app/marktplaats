'use client'

import { useState } from 'react'
import ProductForm from './ProductForm'
import ProductList from './ProductList'

interface Product {
  id: string
  title: string
  description: string
  price: number
  articleNumber: string
  status: string
  marktplaatsUrl?: string | null
  createdAt: Date
}

interface ProductsClientProps {
  products: Product[]
}

export default function ProductsClient({ products: initialProducts }: ProductsClientProps) {
  const [products, setProducts] = useState(initialProducts)

  const handleProductAdded = (product: Product) => {
    setProducts([product, ...products])
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Nieuw product toevoegen</h2>
              <p className="text-sm text-white/90 mt-0.5">Vul de velden in en upload foto&apos;s voor je product.</p>
            </div>
          </div>
        </div>
        <div className="p-8">
          <ProductForm onSuccess={handleProductAdded} />
        </div>
      </section>

      <section className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-5 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Bestaande producten</h2>
                <p className="text-sm text-gray-600 mt-0.5">Klik op &quot;Plaats op Marktplaats&quot; wanneer alles klaar is.</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <span className="text-sm font-semibold text-gray-700">{products.length}</span>
              <span className="text-sm text-gray-500">items</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <ProductList products={products} />
        </div>
      </section>
    </div>
  )
}


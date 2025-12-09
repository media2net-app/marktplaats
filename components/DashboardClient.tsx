'use client'

import { useState } from 'react'
import ProductForm from './ProductForm'
import ProductList from './ProductList'
import AdStatsTable from './AdStatsTable'

interface Product {
  id: string
  title: string
  description: string
  price: number
  articleNumber: string
  status: string
  marktplaatsUrl?: string | null
  marktplaatsAdId?: string | null
  views: number
  saves: number
  postedAt?: Date | null
  createdAt: Date
}

interface DashboardClientProps {
  products: Product[]
}

export default function DashboardClient({ products: initialProducts }: DashboardClientProps) {
  const [products, setProducts] = useState(initialProducts)
  const [showForm, setShowForm] = useState(false)

  const handleProductAdded = (newProduct: any) => {
    // Convert the new product to match our Product interface
    const fullProduct: Product = {
      id: newProduct.id,
      title: newProduct.title,
      description: newProduct.description,
      price: newProduct.price,
      articleNumber: newProduct.articleNumber,
      status: newProduct.status || 'pending',
      marktplaatsUrl: newProduct.marktplaatsUrl || null,
      marktplaatsAdId: newProduct.marktplaatsAdId || null,
      views: newProduct.views || 0,
      saves: newProduct.saves || 0,
      postedAt: newProduct.postedAt || null,
      createdAt: newProduct.createdAt || new Date(),
    }
    setProducts([fullProduct, ...products])
    setShowForm(false)
  }

  const handleRefresh = async () => {
    // Refresh products from server
    const response = await fetch('/api/products')
    if (response.ok) {
      const updatedProducts = await response.json()
      setProducts(updatedProducts)
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Overzicht van je producten en advertentie statistieken</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="w-full sm:w-auto bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:from-indigo-700 hover:to-purple-700 transition-all text-sm sm:text-base"
        >
          {showForm ? 'Annuleren' : '+ Nieuw Product'}
        </button>
      </div>

      {showForm && (
        <div className="mb-8">
          <ProductForm onSuccess={handleProductAdded} />
        </div>
      )}

      {/* Advertentie Statistieken Tabel */}
      <AdStatsTable products={products} onRefresh={handleRefresh} />

      {/* Product Lijst */}
      <div>
        <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Alle Producten</h3>
        <ProductList products={products} />
      </div>
    </div>
  )
}


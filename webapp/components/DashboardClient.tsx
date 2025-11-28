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

  const handleProductAdded = (newProduct: Product) => {
    setProducts([newProduct, ...products])
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
    <div className="space-y-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">Overzicht van je producten en advertentie statistieken</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:from-indigo-700 hover:to-purple-700 transition-all"
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
        <h3 className="text-xl font-bold text-gray-900 mb-4">Alle Producten</h3>
        <ProductList products={products} />
      </div>
    </div>
  )
}


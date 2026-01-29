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

  // Calculate status counts
  const statusCounts = {
    pending: products.filter(p => p.status === 'pending').length,
    processing: products.filter(p => p.status === 'processing').length,
    completed: products.filter(p => p.status === 'completed').length,
    failed: products.filter(p => p.status === 'failed').length,
  }

  // Ensure Status Overzicht is always rendered

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

      {/* Status Overzicht */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Status Overzicht</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span className="text-sm font-semibold text-gray-700">Wachtend</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{statusCounts.pending}</div>
            <div className="text-xs text-gray-500 mt-1">Nog niet geplaatst</div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-semibold text-yellow-700">Bezig</span>
            </div>
            <div className="text-2xl font-bold text-yellow-900">{statusCounts.processing}</div>
            <div className="text-xs text-yellow-600 mt-1">Wordt geplaatst</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-semibold text-green-700">Geplaatst</span>
            </div>
            <div className="text-2xl font-bold text-green-900">{statusCounts.completed}</div>
            <div className="text-xs text-green-600 mt-1">Op Marktplaats</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-semibold text-red-700">Mislukt</span>
            </div>
            <div className="text-2xl font-bold text-red-900">{statusCounts.failed}</div>
            <div className="text-xs text-red-600 mt-1">Fout opgetreden</div>
          </div>
        </div>
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
        <ProductList products={products} onRefresh={handleRefresh} />
      </div>
    </div>
  )
}


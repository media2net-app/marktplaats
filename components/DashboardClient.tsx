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
  const [isPosting, setIsPosting] = useState(false)
  const [postingResult, setPostingResult] = useState<string | null>(null)

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

  const handleBatchPost = async () => {
    if (!confirm('Weet je zeker dat je alle pending producten wilt posten? Dit kan even duren.')) {
      return
    }

    setIsPosting(true)
    setPostingResult(null)

    try {
      const response = await fetch('/api/products/batch-post', {
        method: 'POST',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Fout bij batch posting')
      }

      const result = await response.json()
      setPostingResult(result.message || 'Batch posting gestart')
      
      // Refresh products after a short delay
      setTimeout(() => {
        handleRefresh()
      }, 2000)
    } catch (error: any) {
      setPostingResult(`Fout: ${error.message}`)
    } finally {
      setIsPosting(false)
    }
  }

  const pendingCount = products.filter(p => p.status === 'pending').length

  return (
    <div className="space-y-6 sm:space-y-8">
      <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Overzicht van je producten en advertentie statistieken</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          {pendingCount > 0 && (
            <button
              onClick={handleBatchPost}
              disabled={isPosting}
              className="w-full sm:w-auto bg-gradient-to-r from-green-600 to-emerald-600 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:from-green-700 hover:to-emerald-700 transition-all text-sm sm:text-base disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPosting ? 'Bezig met posten...' : `📤 Post ${pendingCount} Pending`}
            </button>
          )}
          <button
            onClick={() => setShowForm(!showForm)}
            className="w-full sm:w-auto bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 py-2.5 rounded-lg font-semibold shadow-md hover:from-indigo-700 hover:to-purple-700 transition-all text-sm sm:text-base"
          >
            {showForm ? 'Annuleren' : '+ Nieuw Product'}
          </button>
        </div>
      </div>

      {postingResult && (
        <div className={`p-4 rounded-lg ${
          postingResult.includes('Fout') 
            ? 'bg-red-50 text-red-800 border border-red-200' 
            : 'bg-green-50 text-green-800 border border-green-200'
        }`}>
          {postingResult}
        </div>
      )}

      {pendingCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Let op:</strong> Batch posting werkt alleen als je een externe server/worker hebt ingesteld. 
            Zie <code className="bg-yellow-100 px-1 rounded">SERVER_BATCH_POSTING.md</code> voor instructies.
          </p>
        </div>
      )}

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


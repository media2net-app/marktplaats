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
  const [showForm, setShowForm] = useState(false)
  const [resetting, setResetting] = useState(false)

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
      createdAt: newProduct.createdAt || new Date(),
    }
    setProducts([fullProduct, ...products])
    setShowForm(false) // Klap formulier in na succesvol toevoegen
  }

  const handleResetAllFailed = async () => {
    const failedCount = products.filter(p => 
      p.status?.toLowerCase() === 'failed' || 
      p.status?.toLowerCase() === 'mislukt'
    ).length
    if (failedCount === 0) {
      alert('Geen mislukte producten gevonden')
      return
    }

    if (!confirm(`Weet je zeker dat je alle ${failedCount} mislukte product(en) wilt resetten naar pending?`)) {
      return
    }

    setResetting(true)
    try {
      const response = await fetch('/api/products/reset-all-failed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })

      if (response.ok) {
        const data = await response.json()
        alert(`✅ ${data.message}`)
        // Refresh products
        window.location.reload()
      } else {
        const error = await response.json()
        alert(`❌ Fout: ${error.error || 'Onbekende fout'}`)
      }
    } catch (error: any) {
      alert(`❌ Fout: ${error.message}`)
    } finally {
      setResetting(false)
    }
  }

  const failedCount = products.filter(p => p.status === 'failed').length

  return (
    <div className="flex flex-col gap-8">
      <section className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div 
          className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-5 cursor-pointer hover:from-indigo-600 hover:to-purple-700 transition-all"
          onClick={() => setShowForm(!showForm)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <svg className={`w-5 h-5 text-white transition-transform ${showForm ? 'rotate-45' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Nieuw product toevoegen</h2>
                <p className="text-sm text-white/90 mt-0.5">Vul de velden in en upload foto&apos;s voor je product.</p>
              </div>
            </div>
            <svg 
              className={`w-6 h-6 text-white transition-transform ${showForm ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        {showForm && (
          <div className="p-8">
            <ProductForm onSuccess={handleProductAdded} />
          </div>
        )}
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
                <p className="text-sm text-gray-600 mt-0.5">Gebruik run_marktplaats.bat om alle pending producten te plaatsen.</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {failedCount > 0 && (
                <button
                  onClick={handleResetAllFailed}
                  disabled={resetting}
                  className="bg-yellow-500 text-white px-4 py-2 rounded-lg font-semibold shadow-sm hover:bg-yellow-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  title={`Reset alle ${failedCount} mislukte product(en) naar pending`}
                >
                  {resetting ? (
                    <>
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Resetten...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Reset {failedCount} mislukt{failedCount !== 1 ? 'e' : ''}
                    </>
                  )}
                </button>
              )}
              <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <span className="text-sm font-semibold text-gray-700">{products.length}</span>
                <span className="text-sm text-gray-500">items</span>
              </div>
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


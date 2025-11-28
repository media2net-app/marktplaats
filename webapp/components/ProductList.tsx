'use client'

import { useState, useEffect } from 'react'

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

interface ProductListProps {
  products: Product[]
}

export default function ProductList({ products }: ProductListProps) {
  const [productImages, setProductImages] = useState<Record<string, string | null>>({})

  useEffect(() => {
    // Load images for all products
    const loadImages = async () => {
      const imageMap: Record<string, string | null> = {}
      
      for (const product of products) {
        try {
          const response = await fetch(`/api/products/${product.id}/image`)
          if (response.ok && response.headers.get('content-type')?.startsWith('image/')) {
            // Image is returned directly, create blob URL
            const blob = await response.blob()
            imageMap[product.id] = URL.createObjectURL(blob)
          } else if (response.ok) {
            // Fallback: JSON response with image path
            const data = await response.json()
            imageMap[product.id] = data.image
          }
        } catch (error) {
          console.error(`Error loading image for product ${product.id}:`, error)
          imageMap[product.id] = null
        }
      }
      
      setProductImages(imageMap)
      
      // Cleanup blob URLs on unmount
      return () => {
        Object.values(imageMap).forEach(url => {
          if (url && url.startsWith('blob:')) {
            URL.revokeObjectURL(url)
          }
        })
      }
    }

    loadImages()
  }, [products])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Geplaatst'
      case 'processing':
        return 'Bezig...'
      case 'failed':
        return 'Mislukt'
      default:
        return 'Wachtend'
    }
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <p className="text-gray-500 text-lg">Nog geen producten toegevoegd</p>
        <p className="text-gray-400 text-sm mt-2">Voeg je eerste product toe om te beginnen</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {products.map((product) => (
        <div
          key={product.id}
          className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all p-6 cursor-pointer"
          onClick={() => window.location.href = `/products/${product.id}/edit`}
        >
          <div className="flex items-start justify-between gap-4">
            {/* Product Image */}
            {productImages[product.id] ? (
              <div className="flex-shrink-0">
                <div className="w-24 h-24 rounded-lg overflow-hidden border border-gray-200 bg-gray-100">
                  <img
                    src={productImages[product.id]!}
                    alt={product.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      // Hide image on error
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                </div>
              </div>
            ) : (
              <div className="flex-shrink-0">
                <div className="w-24 h-24 rounded-lg border border-gray-200 bg-gray-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
            )}
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start gap-3 mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-gray-900 hover:text-indigo-600 transition-colors">{product.title}</h3>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(product.status)}`}>
                      {getStatusText(product.status)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">{product.description}</p>
                </div>
              </div>
              
              <div className="flex flex-wrap items-center gap-4 mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <span className="font-medium">#{product.articleNumber}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-bold text-indigo-600">€{product.price.toFixed(2)}</span>
                </div>
                {product.marktplaatsUrl && (
                  <a
                    href={product.marktplaatsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                  >
                    <span>Bekijk op Marktplaats</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
              </div>
            </div>
            
            <div className="flex-shrink-0 flex items-center gap-2">
              {product.status === 'failed' && (
                <button
                  onClick={async (e) => {
                    e.stopPropagation()
                    if (confirm('Weet je zeker dat je dit product opnieuw wilt proberen te plaatsen?')) {
                      try {
                        const response = await fetch('/api/products/reset-status', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ productIds: [product.id] }),
                        })
                        if (response.ok) {
                          window.location.reload()
                        } else {
                          alert('Fout bij resetten van product status')
                        }
                      } catch (error) {
                        alert('Fout bij resetten van product status')
                      }
                    }
                  }}
                  className="bg-yellow-100 text-yellow-700 px-3 py-2 rounded-lg font-semibold shadow-sm hover:bg-yellow-200 transition-all flex items-center gap-2 whitespace-nowrap text-sm"
                  title="Reset naar pending en probeer opnieuw"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Opnieuw proberen
                </button>
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  window.location.href = `/products/${product.id}/edit`
                }}
                className="bg-gray-100 text-gray-700 px-4 py-2.5 rounded-lg font-semibold shadow-sm hover:bg-gray-200 transition-all flex items-center gap-2 whitespace-nowrap"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Bewerken
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}


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
  ebayUrl?: string | null
  ebayItemId?: string | null
  createdAt: Date | string
}

interface ProductListProps {
  products: Product[]
  onRefresh?: () => void
}

export default function ProductList({ products, onRefresh }: ProductListProps) {
  const [productImages, setProductImages] = useState<Record<string, string | null>>({})
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [postingToEbay, setPostingToEbay] = useState<Record<string, boolean>>({})

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

  // Filter products by status
  const filteredProducts = statusFilter === 'all' 
    ? products 
    : products.filter(p => p.status === statusFilter)

  // Status counts for filter buttons
  const statusCounts = {
    all: products.length,
    pending: products.filter(p => p.status === 'pending').length,
    processing: products.filter(p => p.status === 'processing').length,
    completed: products.filter(p => p.status === 'completed').length,
    failed: products.filter(p => p.status === 'failed').length,
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
      {/* Status Filter */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-gray-700 mr-2">Filter op status:</span>
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              statusFilter === 'all'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Alle ({statusCounts.all})
          </button>
          <button
            onClick={() => setStatusFilter('pending')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              statusFilter === 'pending'
                ? 'bg-gray-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Wachtend ({statusCounts.pending})
          </button>
          <button
            onClick={() => setStatusFilter('processing')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              statusFilter === 'processing'
                ? 'bg-yellow-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Bezig ({statusCounts.processing})
          </button>
          <button
            onClick={() => setStatusFilter('completed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              statusFilter === 'completed'
                ? 'bg-green-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Geplaatst ({statusCounts.completed})
          </button>
          <button
            onClick={() => setStatusFilter('failed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              statusFilter === 'failed'
                ? 'bg-red-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Mislukt ({statusCounts.failed})
          </button>
        </div>
      </div>

      {filteredProducts.length === 0 ? (
        <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
          <p className="text-gray-500">Geen producten gevonden met status "{getStatusText(statusFilter)}"</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredProducts.map((product) => (
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
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <h3 className="text-lg font-bold text-gray-900 hover:text-indigo-600 transition-colors">{product.title}</h3>
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${getStatusColor(product.status)}`}>
                      <span className={`w-2 h-2 rounded-full ${
                        product.status === 'completed' ? 'bg-green-500' :
                        product.status === 'processing' ? 'bg-yellow-500' :
                        product.status === 'failed' ? 'bg-red-500' :
                        'bg-gray-500'
                      }`}></span>
                      {getStatusText(product.status)}
                    </span>
                    {product.status === 'completed' && product.marktplaatsUrl && (
                      <span className="inline-flex items-center gap-1 text-xs text-green-600 font-medium">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Live op Marktplaats
                      </span>
                    )}
                    {product.ebayUrl && (
                      <span className="inline-flex items-center gap-1 text-xs text-blue-600 font-medium">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Live op eBay
                      </span>
                    )}
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
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                  >
                    <span>Bekijk op Marktplaats</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
                {product.ebayUrl && (
                  <a
                    href={product.ebayUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <span>Bekijk op eBay</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
              </div>
            </div>
            
            <div className="flex-shrink-0 flex items-center gap-2">
              {(product.status === 'pending' || product.status === 'failed') && !product.ebayUrl && (
                <button
                  onClick={async (e) => {
                    e.stopPropagation()
                    if (confirm('Weet je zeker dat je dit product op eBay wilt plaatsen?')) {
                      setPostingToEbay(prev => ({ ...prev, [product.id]: true }))
                      try {
                        const response = await fetch(`/api/products/${product.id}/post-ebay`, {
                          method: 'POST',
                        })
                        const data = await response.json()
                        if (response.ok && data.success) {
                          alert('Product succesvol geplaatst op eBay!')
                          if (onRefresh) {
                            onRefresh()
                          } else {
                            window.location.reload()
                          }
                        } else {
                          alert('Fout bij plaatsen op eBay: ' + (data.error || data.details || 'Onbekende fout'))
                        }
                      } catch (error) {
                        alert('Fout bij plaatsen op eBay')
                      } finally {
                        setPostingToEbay(prev => ({ ...prev, [product.id]: false }))
                      }
                    }
                  }}
                  disabled={postingToEbay[product.id]}
                  className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg font-semibold shadow-sm hover:bg-blue-200 transition-all flex items-center gap-2 whitespace-nowrap text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Plaats op eBay"
                >
                  {postingToEbay[product.id] ? (
                    <>
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Plaatsen...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Plaats op eBay
                    </>
                  )}
                </button>
              )}
              {product.status === 'completed' && (
                <button
                  onClick={async (e) => {
                    e.stopPropagation()
                    if (confirm('Weet je zeker dat je dit geplaatste product terug wilt zetten naar wachtend? Dit zal de Marktplaats link en statistieken wissen.')) {
                      try {
                        const response = await fetch('/api/products/set-status', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ productId: product.id, status: 'pending' }),
                        })
                        if (response.ok) {
                          if (onRefresh) {
                            onRefresh()
                          } else {
                            window.location.reload()
                          }
                        } else {
                          const error = await response.json()
                          alert('Fout bij resetten: ' + (error.error || 'Onbekende fout'))
                        }
                      } catch (error) {
                        alert('Fout bij resetten van product status')
                      }
                    }
                  }}
                  className="bg-orange-100 text-orange-700 px-3 py-2 rounded-lg font-semibold shadow-sm hover:bg-orange-200 transition-all flex items-center gap-2 whitespace-nowrap text-sm"
                  title="Zet terug naar wachtend"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 15l-3-3m0 0l3-3m-3 3h8M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
                  </svg>
                  Terug naar wachtend
                </button>
              )}
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
                          if (onRefresh) {
                            onRefresh()
                          } else {
                            window.location.reload()
                          }
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
      )}
    </div>
  )
}


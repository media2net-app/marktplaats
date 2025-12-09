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
  marktplaatsAdId?: string | null
  views?: number
  saves?: number
  postedAt?: string | Date | null
  deliveryOption?: string | null
  condition?: string | null
  material?: string | null
  thickness?: string | null
  totalSurface?: string | null
  location?: string | null
  platforms?: string[]
  categoryId?: string | null
  category?: {
    id: string
    name: string
    path: string
  } | null
  categoryFields?: Record<string, any> | null
  createdAt: Date | string
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
          if (response.ok) {
            const data = await response.json()
            imageMap[product.id] = data.image || null
          } else {
            imageMap[product.id] = null
          }
        } catch (error) {
          console.error(`Error loading image for product ${product.id}:`, error)
          imageMap[product.id] = null
        }
      }
      
      setProductImages(imageMap)
    }

    loadImages()
  }, [products])

  const formatDate = (value?: string | Date | null) => {
    if (!value) return '-'
    const date = typeof value === 'string' ? new Date(value) : value
    if (Number.isNaN(date.getTime())) return '-'
    return date.toLocaleDateString('nl-NL', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  const formatList = (items?: string[] | null) => {
    if (!items || items.length === 0) return '-'
    return items.join(', ')
  }

  const formatFieldValue = (value: any): string => {
    if (value === null || value === undefined) return '-'
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : '-'
    }
    if (typeof value === 'object') {
      return JSON.stringify(value)
    }
    return String(value)
  }

  const renderCategoryFields = (fields?: Record<string, any> | null) => {
    if (!fields || typeof fields !== 'object') return null
    
    // Filter out empty values and convert to entries
    const entries = Object.entries(fields).filter(([key, val]) => {
      if (val === null || val === undefined || val === '') return false
      if (Array.isArray(val) && val.length === 0) return false
      if (typeof val === 'object' && Object.keys(val).length === 0) return false
      return true
    })
    
    if (entries.length === 0) return null
    
    return (
      <div className="mt-5 pt-5 border-t border-gray-200">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Categorie Specifieke Velden</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {entries.map(([key, val]) => {
            const displayValue = formatFieldValue(val)
            return (
              <div key={key} className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100 rounded-lg px-4 py-3 hover:shadow-sm transition-shadow">
                <div className="text-indigo-600 text-xs font-semibold uppercase tracking-wide mb-1.5">{key}</div>
                <div className="font-semibold text-gray-900 text-sm break-words">{displayValue}</div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

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
    <div className="space-y-4 sm:space-y-6">
      {products.map((product) => (
        <div
          key={product.id}
          className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all overflow-hidden"
        >
          {/* Header Section */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 sm:px-6 py-4 border-b border-gray-200">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div className="flex items-start gap-3 sm:gap-4 flex-1 min-w-0">
                {/* Product Image */}
                {productImages[product.id] ? (
                  <div className="flex-shrink-0">
                    <div className="w-20 h-20 sm:w-32 sm:h-32 rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-100 shadow-sm">
                      <img
                        src={productImages[product.id]!}
                        alt={product.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="flex-shrink-0">
                    <div className="w-20 h-20 sm:w-32 sm:h-32 rounded-lg border-2 border-gray-200 bg-gray-100 flex items-center justify-center shadow-sm">
                      <svg className="w-6 h-6 sm:w-10 sm:h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                )}
                
                {/* Title and Basic Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 sm:gap-3 mb-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-1 truncate">{product.title}</h3>
                      <p className="text-xs sm:text-sm text-gray-600 line-clamp-2 mb-2 sm:mb-3">{product.description}</p>
                    </div>
                    <span className={`flex-shrink-0 inline-flex items-center px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${getStatusColor(product.status)}`}>
                      {getStatusText(product.status)}
                    </span>
                  </div>
                  
                  {/* Key Info Row */}
                  <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm">
                    <div className="flex items-center gap-1 sm:gap-1.5 text-gray-700">
                      <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-bold text-indigo-600 text-sm sm:text-base">€{product.price.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center gap-1 sm:gap-1.5 text-gray-600">
                      <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                      <span className="font-medium">#{product.articleNumber}</span>
                    </div>
                    {product.category?.path && (
                      <div className="flex items-center gap-1 sm:gap-1.5 text-gray-600">
                        <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7l9-4 9 4-9 4-9-4zm0 8l9 4 9-4" />
                        </svg>
                        <span className="font-medium max-w-[120px] sm:max-w-xs truncate" title={product.category.path}>{product.category.path}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex-shrink-0 flex flex-row sm:flex-col items-center sm:items-end gap-2 sm:gap-2">
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
                    className="bg-yellow-100 text-yellow-700 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg font-semibold shadow-sm hover:bg-yellow-200 transition-all flex items-center gap-1.5 sm:gap-2 whitespace-nowrap text-xs sm:text-sm"
                    title="Reset naar pending en probeer opnieuw"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Opnieuw proberen
                  </button>
                )}
                {(product.status === 'completed' || product.status === 'geplaatst') && (
                  <button
                    onClick={async (e) => {
                      e.stopPropagation()
                      if (confirm('Weet je zeker dat je dit product terug wilt zetten naar pending? Dit verwijdert de Marktplaats link en statistieken.')) {
                        try {
                          const response = await fetch('/api/products/set-status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                              productId: product.id,
                              status: 'pending'
                            }),
                          })
                          if (response.ok) {
                            alert('Product status bijgewerkt naar pending')
                            window.location.reload()
                          } else {
                            const error = await response.json()
                            alert(`Fout bij bijwerken: ${error.error || 'Onbekende fout'}`)
                          }
                        } catch (error) {
                          alert('Fout bij bijwerken van product status')
                        }
                      }
                    }}
                    className="bg-blue-100 text-blue-700 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg font-semibold shadow-sm hover:bg-blue-200 transition-all flex items-center gap-1.5 sm:gap-2 whitespace-nowrap text-xs sm:text-sm"
                    title="Zet status terug naar pending"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Naar Pending
                  </button>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    window.location.href = `/products/${product.id}/edit`
                  }}
                  className="bg-indigo-600 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-semibold shadow-sm hover:bg-indigo-700 transition-all flex items-center gap-1.5 sm:gap-2 whitespace-nowrap text-xs sm:text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Bewerken
                </button>
                <button
                  onClick={async (e) => {
                    e.stopPropagation()
                    if (confirm(`Weet je zeker dat je "${product.title}" wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.`)) {
                      try {
                        const response = await fetch(`/api/products/${product.id}`, {
                          method: 'DELETE',
                        })
                        if (response.ok) {
                          alert('Product succesvol verwijderd')
                          window.location.reload()
                        } else {
                          const error = await response.json()
                          alert(`Fout bij verwijderen: ${error.error || 'Onbekende fout'}`)
                        }
                      } catch (error: any) {
                        alert(`Fout bij verwijderen: ${error.message}`)
                      }
                    }
                  }}
                  className="bg-red-100 text-red-700 px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg font-semibold shadow-sm hover:bg-red-200 transition-all flex items-center gap-1.5 sm:gap-2 whitespace-nowrap text-xs sm:text-sm"
                  title="Product verwijderen"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Verwijderen
                </button>
              </div>
            </div>
          </div>

          {/* Content Section */}
          <div className="px-4 sm:px-6 py-4 sm:py-5">
            {/* Advertentie Info */}
            {(product.marktplaatsAdId || product.postedAt || product.marktplaatsUrl) && (
              <div className="mb-5 pb-5 border-b border-gray-200">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Advertentie Informatie</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {product.marktplaatsAdId && (
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                      </svg>
                      <span className="text-gray-600">Ad ID:</span>
                      <span className="font-semibold text-gray-900">{product.marktplaatsAdId}</span>
                    </div>
                  )}
                  {product.postedAt && (
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span className="text-gray-600">Geplaatst:</span>
                      <span className="font-semibold text-gray-900">{formatDate(product.postedAt)}</span>
                    </div>
                  )}
                  {product.marktplaatsUrl && (
                    <div className="sm:col-span-2 lg:col-span-1">
                      <a
                        href={product.marktplaatsUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        Bekijk op Marktplaats
                      </a>
                    </div>
                  )}
                </div>
                {(product.views !== undefined || product.saves !== undefined) && (
                  <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
                    {product.views !== undefined && (
                      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700 text-sm font-medium">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <span>{product.views ?? 0} views</span>
                      </div>
                    )}
                    {product.saves !== undefined && (
                      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-pink-50 text-pink-700 text-sm font-medium">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                        <span>{product.saves ?? 0} opgeslagen</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Product Details */}
            <div className="mb-5">
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Product Details</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 sm:px-4 py-2 sm:py-3">
                  <div className="text-gray-500 text-xs font-medium mb-1">Locatie</div>
                  <div className="font-semibold text-gray-900 text-sm">{product.location || '-'}</div>
                </div>
                <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 sm:px-4 py-2 sm:py-3">
                  <div className="text-gray-500 text-xs font-medium mb-1">Staat</div>
                  <div className="font-semibold text-gray-900 text-sm">{product.condition || '-'}</div>
                </div>
                <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 sm:px-4 py-2 sm:py-3">
                  <div className="text-gray-500 text-xs font-medium mb-1">Levering</div>
                  <div className="font-semibold text-gray-900 text-sm">{product.deliveryOption || '-'}</div>
                </div>
                <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 sm:px-4 py-2 sm:py-3">
                  <div className="text-gray-500 text-xs font-medium mb-1">Platforms</div>
                  <div className="font-semibold text-gray-900 text-sm">{formatList(product.platforms)}</div>
                </div>
              </div>
            </div>

            {/* Category Fields */}
            {renderCategoryFields(product.categoryFields)}
          </div>
        </div>
      ))}
    </div>
  )
}


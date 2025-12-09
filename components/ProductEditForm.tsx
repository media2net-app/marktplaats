'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import ProductForm from './ProductForm'

interface Product {
  id: string
  title: string
  description: string
  price: number
  articleNumber: string
  status: string
  condition: string | null
  material: string | null
  thickness: string | null
  totalSurface: string | null
  deliveryOption: string | null
  location: string | null
  categoryId: string | null
  categoryFields?: Record<string, any> | null
  ebayFields?: Record<string, any> | null
  platforms?: string[]
  category?: {
    id: string
    name: string
    path: string
  } | null
}

interface ProductEditFormProps {
  product: Product
}

export default function ProductEditForm({ product }: ProductEditFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [productData, setProductData] = useState<Product | null>(null)

  useEffect(() => {
    setProductData(product)
    setLoading(false)
  }, [product])

  const handleUpdate = async (updatedProduct: any) => {
    // ProductForm handles the update and navigation itself now
    // This callback is kept for compatibility but doesn't need to do anything
  }

  if (loading || !productData) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Product bewerken</h2>
            <p className="text-sm text-white/90 mt-0.5">Wijzig de gegevens en sla op</p>
          </div>
        </div>
      </div>
      <div className="p-8">
        <ProductForm 
          product={productData} 
          onSuccess={handleUpdate}
          mode="edit"
        />
      </div>
    </div>
  )
}


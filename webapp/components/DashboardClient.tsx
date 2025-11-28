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

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Overzicht</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          {showForm ? 'Annuleren' : '+ Nieuw Product'}
        </button>
      </div>

      {showForm && (
        <div className="mb-6">
          <ProductForm onSuccess={handleProductAdded} />
        </div>
      )}

      <ProductList products={products} />
    </div>
  )
}


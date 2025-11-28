'use client'

import { useState, useEffect } from 'react'

interface Product {
  id: string
  title: string
  description: string
  price: number
  articleNumber: string
  status: string
}

interface Category {
  id: string
  name: string
  level: number
  path: string
  children: Category[]
}

interface ProductFormProps {
  product?: Product | null
  onSuccess?: (product: Product) => void
  mode?: 'create' | 'edit'
}

export default function ProductForm({ product, onSuccess, mode = 'create' }: ProductFormProps) {
  const [loading, setLoading] = useState(false)
  const [uploadingPhotos, setUploadingPhotos] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory1, setSelectedCategory1] = useState('')
  const [selectedCategory2, setSelectedCategory2] = useState('')
  const [selectedCategory3, setSelectedCategory3] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const [existingImages, setExistingImages] = useState<string[]>([])
  const [removedImages, setRemovedImages] = useState<string[]>([])
  const [formData, setFormData] = useState({
    title: product?.title || '',
    description: product?.description || '',
    price: product?.price?.toString() || '',
    articleNumber: product?.articleNumber || '',
    condition: product?.condition || 'Gebruikt',
    material: product?.material || '',
    thickness: product?.thickness || '',
    totalSurface: product?.totalSurface || '',
    deliveryOption: product?.deliveryOption || 'Ophalen of Verzenden',
    location: product?.location || '',
    categoryId: product?.categoryId || '',
  })

  // Set initial category selection if editing
  useEffect(() => {
    if (product?.categoryId && categories.length > 0) {
      // Find the category and set the appropriate level
      const findCategory = (cats: Category[], id: string): Category | null => {
        for (const cat of cats) {
          if (cat.id === id) return cat
          if (cat.children) {
            const found = findCategory(cat.children, id)
            if (found) return found
          }
        }
        return null
      }
      const cat = findCategory(categories, product.categoryId)
      if (cat) {
        if (cat.level === 1) setSelectedCategory1(cat.id)
        else if (cat.level === 2) {
          // Find parent
          const parent = categories.find(c => c.children?.some(ch => ch.id === cat.id))
          if (parent) {
            setSelectedCategory1(parent.id)
            setSelectedCategory2(cat.id)
          }
        } else if (cat.level === 3) {
          // Find parent and grandparent
          for (const l1 of categories) {
            for (const l2 of l1.children || []) {
              if (l2.children?.some(ch => ch.id === cat.id)) {
                setSelectedCategory1(l1.id)
                setSelectedCategory2(l2.id)
                setSelectedCategory3(cat.id)
                break
              }
            }
          }
        }
      }
    }
  }, [product, categories])

  useEffect(() => {
    // Laad categorieën
    fetch('/api/categories')
      .then(res => res.json())
      .then(data => setCategories(data))
      .catch(err => console.error('Error loading categories:', err))
  }, [])

  // Load existing images when editing
  useEffect(() => {
    if (mode === 'edit' && product?.id && product?.articleNumber) {
      fetch(`/api/products/${product.id}/images`)
        .then(res => res.json())
        .then(data => {
          if (data.images && Array.isArray(data.images)) {
            setExistingImages(data.images)
          }
        })
        .catch(err => console.error('Error loading existing images:', err))
    }
  }, [mode, product?.id, product?.articleNumber])

  // Filter categorieën per level
  const level1Categories = categories.filter(c => c.level === 1)
  const level2Categories = selectedCategory1 
    ? categories.find(c => c.id === selectedCategory1)?.children || []
    : []
  const level3Categories = selectedCategory2
    ? categories.find(c => c.id === selectedCategory2)?.children || []
    : []

  // Update categoryId wanneer een categorie wordt geselecteerd
  useEffect(() => {
    const finalCategory = selectedCategory3 || selectedCategory2 || selectedCategory1
    setFormData(prev => ({ ...prev, categoryId: finalCategory }))
  }, [selectedCategory1, selectedCategory2, selectedCategory3])

  // Reset subcategorieën wanneer hoofdcategorie verandert
  const handleCategory1Change = (value: string) => {
    setSelectedCategory1(value)
    setSelectedCategory2('')
    setSelectedCategory3('')
  }

  const handleCategory2Change = (value: string) => {
    setSelectedCategory2(value)
    setSelectedCategory3('')
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setSelectedFiles(files)
    
    // Create preview URLs
    const urls = files.map(file => URL.createObjectURL(file))
    setPreviewUrls(urls)
  }

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    const newUrls = previewUrls.filter((_, i) => i !== index)
    
    // Revoke old URL to free memory
    URL.revokeObjectURL(previewUrls[index])
    
    setSelectedFiles(newFiles)
    setPreviewUrls(newUrls)
  }

  const removeExistingImage = (imagePath: string) => {
    setExistingImages(prev => prev.filter(img => img !== imagePath))
    setRemovedImages(prev => [...prev, imagePath])
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Upload photos if any (for new products or when editing with new photos)
      if (selectedFiles.length > 0 && formData.articleNumber) {
        setUploadingPhotos(true)
        const uploadFormData = new FormData()
        selectedFiles.forEach(file => {
          uploadFormData.append('files', file)
        })
        uploadFormData.append('articleNumber', formData.articleNumber)

        const uploadResponse = await fetch('/api/products/upload', {
          method: 'POST',
          body: uploadFormData,
        })

        if (!uploadResponse.ok) {
          throw new Error('Fout bij uploaden van foto\'s')
        }

        setUploadingPhotos(false)
      }

      // Delete removed images if editing
      if (mode === 'edit' && removedImages.length > 0) {
        for (const imagePath of removedImages) {
          try {
            // Extract filename from path like /media/articleNumber/filename.jpg
            const parts = imagePath.split('/')
            const filename = parts[parts.length - 1]
            const articleNumber = parts[parts.length - 2]
            
            // Delete file via API
            await fetch(`/api/products/delete-image`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                imagePath: imagePath,
                articleNumber: articleNumber,
                filename: filename 
              }),
            })
          } catch (error) {
            console.error('Error deleting image:', error)
            // Continue even if deletion fails
          }
        }
      }

      // Create or update the product
      const url = mode === 'edit' && product 
        ? `/api/products/${product.id}`
        : '/api/products'
      const method = mode === 'edit' ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          price: parseFloat(formData.price),
        }),
      })

      if (!response.ok) {
        throw new Error('Fout bij opslaan')
      }

      const updatedProduct = await response.json()
      onSuccess?.(updatedProduct)
      
      // Reset form only if creating new product
      if (mode === 'create') {
        setFormData({
          title: '',
          description: '',
          price: '',
          articleNumber: '',
          condition: 'Gebruikt',
          material: '',
          thickness: '',
          totalSurface: '',
          deliveryOption: 'Ophalen of Verzenden',
          location: '',
          categoryId: '',
        })
        setSelectedCategory1('')
        setSelectedCategory2('')
        setSelectedCategory3('')
        setSelectedFiles([])
        previewUrls.forEach(url => URL.revokeObjectURL(url))
        setPreviewUrls([])
      }
    } catch (error) {
      alert('Er is een fout opgetreden')
    } finally {
      setLoading(false)
      setUploadingPhotos(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Titel</label>
          <input
            type="text"
            required
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Voer producttitel in"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Artikelnummer</label>
          <input
            type="text"
            required
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.articleNumber}
            onChange={(e) => setFormData({ ...formData, articleNumber: e.target.value })}
            placeholder="Bijv. ART-001"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-semibold text-gray-700 mb-3">Categorie</label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-2.5 uppercase tracking-wide">Hoofdcategorie</label>
              <select
                className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer"
                value={selectedCategory1}
                onChange={(e) => handleCategory1Change(e.target.value)}
                style={{ color: '#111827' }}
              >
                <option value="" style={{ color: '#6b7280' }}>Selecteer...</option>
                {level1Categories.map(cat => (
                  <option key={cat.id} value={cat.id} style={{ color: '#111827' }}>{cat.name}</option>
                ))}
              </select>
            </div>

            {selectedCategory1 && level2Categories.length > 0 && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2.5 uppercase tracking-wide">Subcategorie</label>
                <select
                  className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer"
                  value={selectedCategory2}
                  onChange={(e) => handleCategory2Change(e.target.value)}
                  style={{ color: '#111827' }}
                >
                  <option value="" style={{ color: '#6b7280' }}>Selecteer...</option>
                  {level2Categories.map(cat => (
                    <option key={cat.id} value={cat.id} style={{ color: '#111827' }}>{cat.name}</option>
                  ))}
                </select>
              </div>
            )}

            {selectedCategory2 && level3Categories.length > 0 && (
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2.5 uppercase tracking-wide">Sub-subcategorie</label>
                <select
                  className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer"
                  value={selectedCategory3}
                  onChange={(e) => setSelectedCategory3(e.target.value)}
                  style={{ color: '#111827' }}
                >
                  <option value="" style={{ color: '#6b7280' }}>Selecteer...</option>
                  {level3Categories.map(cat => (
                    <option key={cat.id} value={cat.id} style={{ color: '#111827' }}>{cat.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Beschrijving</label>
          <textarea
            required
            rows={4}
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all resize-none placeholder:text-gray-400"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Beschrijf je product..."
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Prijs (€)</label>
          <input
            type="number"
            step="0.01"
            required
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Staat</label>
          <select
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all cursor-pointer"
            value={formData.condition}
            onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
          >
            <option>Nieuw</option>
            <option>Zo goed als nieuw</option>
            <option>Gebruikt</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Materiaal</label>
          <input
            type="text"
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.material}
            onChange={(e) => setFormData({ ...formData, material: e.target.value })}
            placeholder="Bijv. Hardschuim (Pir)"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Dikte</label>
          <input
            type="text"
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.thickness}
            onChange={(e) => setFormData({ ...formData, thickness: e.target.value })}
            placeholder="Bijv. 4 tot 8 cm"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Oppervlakte</label>
          <input
            type="text"
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.totalSurface}
            onChange={(e) => setFormData({ ...formData, totalSurface: e.target.value })}
            placeholder="Bijv. 5 tot 10 m²"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2.5">Locatie</label>
          <input
            type="text"
            className="block w-full px-4 py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            placeholder="Bijv. Amsterdam"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-semibold text-gray-700 mb-2">Foto's</label>
          <div className="mt-1">
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Klik om te uploaden</span> of sleep bestanden hierheen
                  </p>
                  <p className="text-xs text-gray-500">JPG, PNG, HEIC (MAX. 10MB per bestand)</p>
                </div>
                <input
                  type="file"
                  multiple
                  accept="image/jpeg,image/jpg,image/png,image/heic"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
            {selectedFiles.length > 0 && (
              <div className="mt-3 flex items-center gap-2 text-sm text-indigo-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-medium">{selectedFiles.length} bestand(en) geselecteerd</span>
              </div>
            )}
          </div>
          
          {/* Existing images (edit mode) */}
          {existingImages.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Bestaande foto's:</p>
              <div className="grid grid-cols-4 gap-4">
                {existingImages.map((imagePath, index) => (
                  <div key={`existing-${index}`} className="relative group">
                    <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 shadow-sm hover:border-indigo-300 transition-colors">
                      <img
                        src={imagePath}
                        alt={`Bestaande foto ${index + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // Hide image on error
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeExistingImage(imagePath)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm shadow-lg hover:bg-red-600 transition-colors"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Preview thumbnails (newly selected files) */}
          {previewUrls.length > 0 && (
            <div className="mt-4">
              {existingImages.length > 0 && (
                <p className="text-sm font-medium text-gray-700 mb-2">Nieuwe foto's:</p>
              )}
              <div className="grid grid-cols-4 gap-4">
                {previewUrls.map((url, index) => (
                  <div key={`preview-${index}`} className="relative group">
                    <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 shadow-sm hover:border-indigo-300 transition-colors">
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm shadow-lg hover:bg-red-600 transition-colors"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {!formData.articleNumber && selectedFiles.length > 0 && (
            <div className="mt-3 flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-sm text-amber-800">
                Voer eerst een artikelnummer in voordat je foto's uploadt
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-gray-200">
        <button
          type="submit"
          disabled={loading || uploadingPhotos || (selectedFiles.length > 0 && !formData.articleNumber)}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold shadow-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2"
        >
          {uploadingPhotos ? (
            <>
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Foto's uploaden...
            </>
          ) : loading ? (
            <>
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Opslaan...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              {mode === 'edit' ? 'Product Bijwerken' : 'Product Toevoegen'}
            </>
          )}
        </button>
      </div>
    </form>
  )
}


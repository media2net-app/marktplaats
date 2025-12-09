'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface Product {
  id: string
  title: string
  description: string
  price: number
  articleNumber: string
  status: string
  condition?: string | null
  material?: string | null
  thickness?: string | null
  totalSurface?: string | null
  deliveryOption?: string | null
  location?: string | null
  categoryId?: string | null
  categoryFields?: any
  ebayFields?: any
  platforms?: string[]
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

interface CategoryField {
  name: string
  type: string
  label: string
  required?: boolean
  options?: Array<{ label: string; value: string }>
  placeholder?: string
  min?: number
  max?: number
  step?: number
  maxLength?: number
}

export default function ProductForm({ product, onSuccess, mode = 'create' }: ProductFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [uploadingPhotos, setUploadingPhotos] = useState(false)
  const [showLoadingModal, setShowLoadingModal] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory1, setSelectedCategory1] = useState('')
  const [selectedCategory2, setSelectedCategory2] = useState('')
  const [selectedCategory3, setSelectedCategory3] = useState('')
  const [categoryFields, setCategoryFields] = useState<CategoryField[]>([])
  const [ebayFields, setEbayFields] = useState<CategoryField[]>([])
  const [categoryFieldValues, setCategoryFieldValues] = useState<Record<string, any>>({})
  const [ebayFieldValues, setEbayFieldValues] = useState<Record<string, any>>({})
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(product?.platforms || ['marktplaats'])
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
    // Laad categorieën met fields
    fetch('/api/categories/with-fields')
      .then(res => res.json())
      .then(data => setCategories(data))
      .catch(err => console.error('Error loading categories:', err))
  }, [])

  // Load category fields when category is selected (Marktplaats)
  useEffect(() => {
    // Only load fields for the deepest selected level
    // If level 3 exists, wait for it. If only level 2 exists, use level 2. Otherwise use level 1.
    let selectedCategoryId: string | null = null
    
    // Calculate level 2 and 3 categories within the effect
    const level2Cats = selectedCategory1 
      ? categories.find(c => c.id === selectedCategory1)?.children || []
      : []
    const level3Cats = selectedCategory2
      ? categories.find(c => c.id === selectedCategory2)?.children || []
      : []
    
    if (selectedCategory3) {
      // Level 3 is selected, use that
      selectedCategoryId = selectedCategory3
    } else if (selectedCategory2) {
      // Level 2 is selected, check if it has children
      const hasLevel3 = level3Cats.length > 0
      if (!hasLevel3) {
        // No level 3 available, use level 2
        selectedCategoryId = selectedCategory2
      }
      // If level 3 exists, don't load fields yet - wait for level 3 selection
    } else if (selectedCategory1) {
      // Level 1 is selected, check if it has children
      const hasLevel2 = level2Cats.length > 0
      if (!hasLevel2) {
        // No level 2 available, use level 1
        selectedCategoryId = selectedCategory1
      }
      // If level 2 exists, don't load fields yet - wait for deeper selection
    }
    
    if (selectedCategoryId) {
      // Load Marktplaats fields
      fetch(`/api/categories/${selectedCategoryId}/fields`)
        .then(res => res.json())
        .then(data => {
          if (data.fields && Array.isArray(data.fields)) {
            // Filter out "Onbekend veld" and base fields
            const filteredFields = data.fields.filter((field: CategoryField) => 
              field.label !== 'Onbekend veld' && 
              field.name !== 'field_12' &&
              !field.label.toLowerCase().includes('onbekend')
            )
            setCategoryFields(filteredFields)
          } else {
            setCategoryFields([])
          }
        })
        .catch(err => {
          console.error('Error loading category fields:', err)
          setCategoryFields([])
        })

      // Load eBay fields
      fetch(`/api/categories/${selectedCategoryId}/ebay-fields`)
        .then(res => res.json())
        .then(data => {
          if (data.ebayFields && Array.isArray(data.ebayFields)) {
            setEbayFields(data.ebayFields)
          } else {
            setEbayFields([])
          }
        })
        .catch(err => {
          console.error('Error loading eBay fields:', err)
          setEbayFields([])
        })
    } else {
      // No valid category selected yet, clear fields
      setCategoryFields([])
      setEbayFields([])
    }
  }, [selectedCategory1, selectedCategory2, selectedCategory3, categories])

  // Load existing categoryFields when editing
  useEffect(() => {
    if (mode === 'edit') {
      if (product?.categoryFields) {
        setCategoryFieldValues(product.categoryFields as Record<string, any>)
      }
      if (product?.ebayFields) {
        setEbayFieldValues(product.ebayFields as Record<string, any>)
      }
      if (product?.platforms) {
        setSelectedPlatforms(product.platforms)
      }
    }
  }, [mode, product?.categoryFields, product?.ebayFields, product?.platforms])

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
  
  // Find level 2 categories - search in children of selected level 1
  const level2Categories = selectedCategory1 
    ? categories.find(c => c.id === selectedCategory1)?.children || []
    : []
  
  // Find level 3 categories - need to search recursively in the tree
  const findCategoryInTree = (tree: Category[], id: string): Category | null => {
    for (const cat of tree) {
      if (cat.id === id) return cat
      if (cat.children && cat.children.length > 0) {
        const found = findCategoryInTree(cat.children, id)
        if (found) return found
      }
    }
    return null
  }
  
  const level3Categories = selectedCategory2
    ? (findCategoryInTree(categories, selectedCategory2)?.children || [])
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

  const handleCategoryFieldChange = (fieldName: string, value: any) => {
    setCategoryFieldValues(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const handleEbayFieldChange = (fieldName: string, value: any) => {
    setEbayFieldValues(prev => ({
      ...prev,
      [fieldName]: value
    }))
  }

  const handlePlatformToggle = (platform: string) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platform)) {
        return prev.filter(p => p !== platform)
      } else {
        return [...prev, platform]
      }
    })
  }

  const renderCategoryField = (field: CategoryField, isEbay: boolean = false) => {
    const values = isEbay ? ebayFieldValues : categoryFieldValues
    const value = values[field.name] || ''
    const fieldId = isEbay ? `ebay-field-${field.name}` : `category-field-${field.name}`
    const onChange = isEbay ? handleEbayFieldChange : handleCategoryFieldChange

    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <input
            key={fieldId}
            type={field.type}
            id={fieldId}
            name={field.name}
            value={value}
            onChange={(e) => onChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            min={field.min}
            max={field.max}
            step={field.step}
            maxLength={field.maxLength}
            className="block w-full px-4 py-3 sm:px-4 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400 text-base sm:text-base"
          />
        )
      
      case 'textarea':
        return (
          <textarea
            key={fieldId}
            id={fieldId}
            name={field.name}
            value={value}
            onChange={(e) => onChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            maxLength={field.maxLength}
            rows={4}
            className="block w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all resize-none placeholder:text-gray-400 text-base"
          />
        )
      
      case 'select':
        return (
          <select
            key={fieldId}
            id={fieldId}
            name={field.name}
            value={value}
            onChange={(e) => onChange(field.name, e.target.value)}
            required={field.required}
            className="block w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all cursor-pointer text-base"
          >
            <option value="">Selecteer...</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )
      
      case 'radio':
        // Group radio buttons by name
        const fieldsToSearch = isEbay ? ebayFields : categoryFields
        const radioGroup = fieldsToSearch.filter(f => f.name === field.name && f.type === 'radio')
        if (radioGroup[0] === field) {
          return (
            <div key={`radio-group-${field.name}`} className="flex flex-wrap gap-3 sm:gap-4">
              {radioGroup.map((radioField, idx) => (
                <label
                  key={`${fieldId}-${idx}`}
                  className="flex items-center gap-2 cursor-pointer min-h-[44px] touch-manipulation"
                >
                  <input
                    type="radio"
                    name={field.name}
                    value={radioField.label}
                    checked={value === radioField.label}
                    onChange={(e) => onChange(field.name, e.target.value)}
                    required={field.required}
                    className="w-5 h-5 sm:w-4 sm:h-4 text-indigo-600 border-2 border-gray-300 rounded focus:ring-2 focus:ring-indigo-200 flex-shrink-0"
                  />
                  <span className="text-base sm:text-base text-gray-700">{radioField.label}</span>
                </label>
              ))}
            </div>
          )
        }
        return null
      
      case 'checkbox':
        // Group checkboxes by name
        const fieldsToSearchCheckbox = isEbay ? ebayFields : categoryFields
        const checkboxGroup = fieldsToSearchCheckbox.filter(f => f.name === field.name && f.type === 'checkbox')
        if (checkboxGroup[0] === field) {
          const checkboxValues = Array.isArray(value) ? value : []
          return (
            <div key={`checkbox-group-${field.name}`} className="flex flex-wrap gap-3 sm:gap-4">
              {checkboxGroup.map((checkboxField, idx) => (
                <label
                  key={`${fieldId}-${idx}`}
                  className="flex items-center gap-2 cursor-pointer min-h-[44px] touch-manipulation"
                >
                  <input
                    type="checkbox"
                    name={field.name}
                    value={checkboxField.label}
                    checked={checkboxValues.includes(checkboxField.label)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...checkboxValues, checkboxField.label]
                        : checkboxValues.filter(v => v !== checkboxField.label)
                      onChange(field.name, newValues)
                    }}
                    className="w-5 h-5 sm:w-4 sm:h-4 text-indigo-600 border-2 border-gray-300 rounded focus:ring-2 focus:ring-indigo-200 flex-shrink-0"
                  />
                  <span className="text-base sm:text-base text-gray-700">{checkboxField.label}</span>
                </label>
              ))}
            </div>
          )
        }
        return null
      
      default:
        return null
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setShowLoadingModal(true)

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
      
      // Prepare categoryFields - only include fields with actual values
      const cleanCategoryFields: Record<string, any> = {}
      Object.keys(categoryFieldValues).forEach(key => {
        const value = categoryFieldValues[key]
        // Only include if value is not empty/null/undefined
        if (value !== null && value !== undefined && value !== '') {
          // For arrays, check if they have items
          if (Array.isArray(value)) {
            if (value.length > 0) {
              cleanCategoryFields[key] = value
            }
          } else {
            cleanCategoryFields[key] = value
          }
        }
      })
      
      // Prepare eBay field values (remove 'ebay_' prefix)
      const cleanEbayFields: Record<string, any> = {}
      Object.keys(ebayFieldValues).forEach(key => {
        const value = ebayFieldValues[key]
        const cleanKey = key.startsWith('ebay_') ? key.replace('ebay_', '') : key
        
        // Only include if value is not empty/null/undefined
        if (value !== null && value !== undefined && value !== '') {
          if (Array.isArray(value)) {
            if (value.length > 0) {
              cleanEbayFields[cleanKey] = value
            }
          } else {
            cleanEbayFields[cleanKey] = value
          }
        }
      })
      
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          price: parseFloat(formData.price),
          categoryFields: Object.keys(cleanCategoryFields).length > 0 ? cleanCategoryFields : null,
          ebayFields: Object.keys(cleanEbayFields).length > 0 ? cleanEbayFields : null,
          platforms: selectedPlatforms,
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
          deliveryOption: 'Ophalen of Verzenden',
          location: '',
          categoryId: '',
        })
        setSelectedCategory1('')
        setSelectedCategory2('')
        setSelectedCategory3('')
        setCategoryFields([])
        setEbayFields([])
        setCategoryFieldValues({})
        setEbayFieldValues({})
        setSelectedPlatforms(['marktplaats'])
        setSelectedFiles([])
        previewUrls.forEach(url => URL.revokeObjectURL(url))
        setPreviewUrls([])
      }
      
      // Close modal and navigate to products page
      setShowLoadingModal(false)
      router.push('/products')
      router.refresh()
    } catch (error) {
      setShowLoadingModal(false)
      alert('Er is een fout opgetreden')
    } finally {
      setLoading(false)
      setUploadingPhotos(false)
    }
  }

  // Check if a category is selected
  const selectedCategoryId = selectedCategory3 || selectedCategory2 || selectedCategory1

  return (
    <>
      {/* Loading Modal */}
      {showLoadingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl p-6 sm:p-8 max-w-md w-full">
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-b-4 border-indigo-600 mb-4"></div>
              <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2 text-center">
                {uploadingPhotos ? 'Foto\'s uploaden...' : 'Product opslaan...'}
              </h3>
              <p className="text-sm sm:text-base text-gray-600 text-center">
                {uploadingPhotos 
                  ? 'Even geduld terwijl we je foto\'s uploaden...'
                  : 'Je product wordt opgeslagen, even geduld...'}
              </p>
            </div>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6 -mx-4 sm:mx-0 px-4 sm:px-0">
      <div className="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-2">
        {/* Stap 1: Basis informatie */}
        <div>
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Titel</label>
          <input
            type="text"
            required
            className="block w-full px-4 py-3 sm:px-4 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400 text-base sm:text-base"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Voer producttitel in"
          />
        </div>

        <div>
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Artikelnummer</label>
          <input
            type="text"
            required
            className="block w-full px-4 py-3 sm:px-4 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400 text-base sm:text-base"
            value={formData.articleNumber}
            onChange={(e) => setFormData({ ...formData, articleNumber: e.target.value })}
            placeholder="Bijv. ART-001"
          />
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3">Platforms</label>
          <div className="flex flex-wrap gap-3 sm:gap-4 mb-3 sm:mb-4">
            <label className="flex items-center gap-2 cursor-pointer min-h-[44px] touch-manipulation">
              <input
                type="checkbox"
                checked={selectedPlatforms.includes('marktplaats')}
                onChange={() => handlePlatformToggle('marktplaats')}
                className="w-5 h-5 text-indigo-600 border-2 border-gray-300 rounded focus:ring-2 focus:ring-indigo-200 flex-shrink-0"
              />
              <span className="text-base sm:text-base text-gray-700 font-medium">Marktplaats</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer min-h-[44px] touch-manipulation">
              <input
                type="checkbox"
                checked={selectedPlatforms.includes('ebay')}
                onChange={() => handlePlatformToggle('ebay')}
                className="w-5 h-5 text-indigo-600 border-2 border-gray-300 rounded focus:ring-2 focus:ring-indigo-200 flex-shrink-0"
              />
              <span className="text-base sm:text-base text-gray-700 font-medium">eBay</span>
            </label>
          </div>
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2 sm:mb-3">Categorie</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-gray-600 mb-2 uppercase tracking-wide">Hoofdcategorie</label>
              <select
                className="block w-full px-4 py-3 min-h-[48px] rounded-lg border-2 border-gray-300 bg-white text-base sm:text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer touch-manipulation"
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
                <label className="block text-xs sm:text-sm font-semibold text-gray-600 mb-2 uppercase tracking-wide">Subcategorie</label>
                <select
                  className="block w-full px-4 py-3 min-h-[48px] rounded-lg border-2 border-gray-300 bg-white text-base sm:text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer touch-manipulation"
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
                <label className="block text-xs sm:text-sm font-semibold text-gray-600 mb-2 uppercase tracking-wide">Sub-subcategorie</label>
                <select
                  className="block w-full px-4 py-3 min-h-[48px] rounded-lg border-2 border-gray-300 bg-white text-base sm:text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all cursor-pointer touch-manipulation"
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

        {/* Stap 2: Categorie-specifieke velden (alleen tonen als categorie geselecteerd) */}
        {selectedCategoryId && (
          <>
            {/* Marktplaats velden */}
            {selectedPlatforms.includes('marktplaats') && categoryFields.length > 0 && (
              <div className="lg:col-span-2">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            {categoryFields.map((field, index) => {
                // Skip duplicate radio/checkbox fields (they're rendered in groups)
                if (field.type === 'radio' || field.type === 'checkbox') {
                  const isFirstInGroup = categoryFields.findIndex(f => f.name === field.name && f.type === field.type) === index
                  if (!isFirstInGroup) return null
                }
                
                return (
                  <div key={`marktplaats-${field.name}-${index}`} className={field.type === 'radio' || field.type === 'checkbox' || field.type === 'textarea' ? 'lg:col-span-2' : ''}>
                        <label htmlFor={`category-field-${field.name}`} className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">
                          {field.label}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        {renderCategoryField(field, false)}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* eBay velden */}
            {selectedPlatforms.includes('ebay') && ebayFields.length > 0 && (
              <div className="lg:col-span-2">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                  {ebayFields.map((field, index) => {
                    const value = ebayFieldValues[field.name] || ''
                    const fieldId = `ebay-field-${field.name}`
                    
                    // Skip duplicate radio/checkbox fields
                    if (field.type === 'radio' || field.type === 'checkbox') {
                      const isFirstInGroup = ebayFields.findIndex(f => f.name === field.name && f.type === field.type) === index
                      if (!isFirstInGroup) return null
                    }
                    
                    return (
                      <div key={`ebay-${field.name}-${index}`} className={field.type === 'radio' || field.type === 'checkbox' || field.type === 'textarea' ? 'lg:col-span-2' : ''}>
                        <label htmlFor={fieldId} className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">
                          {field.label}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        {renderCategoryField(field, true)}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </>
        )}

        {/* Stap 3: Overige informatie (alleen tonen als categorie geselecteerd) */}
        {selectedCategoryId && (
          <>
        <div className="lg:col-span-2">
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Beschrijving</label>
          <textarea
            required
            rows={4}
            className="block w-full px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all resize-none placeholder:text-gray-400 text-base"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Beschrijf je product..."
          />
        </div>

        <div>
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Prijs (€)</label>
          <input
            type="number"
            step="0.01"
            required
            className="block w-full px-4 py-3 sm:px-4 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400 text-base sm:text-base"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Staat</label>
          <select
            className="block w-full px-4 py-3 min-h-[48px] rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all cursor-pointer text-base sm:text-base touch-manipulation"
            value={formData.condition}
            onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
          >
            <option>Nieuw</option>
            <option>Zo goed als nieuw</option>
            <option>Gebruikt</option>
          </select>
        </div>

        <div>
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Locatie</label>
          <input
            type="text"
            className="block w-full px-4 py-3 sm:px-4 sm:py-3 rounded-lg border-2 border-gray-300 bg-white shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-gray-900 transition-all placeholder:text-gray-400 text-base sm:text-base"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            placeholder="Bijv. Amsterdam"
          />
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm sm:text-base font-semibold text-gray-700 mb-2">Foto's</label>
          <div className="mt-1">
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full min-h-[120px] sm:h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors touch-manipulation">
                <div className="flex flex-col items-center justify-center pt-4 sm:pt-5 pb-4 sm:pb-6 px-4">
                  <svg className="w-8 h-8 sm:w-10 sm:h-10 mb-2 sm:mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-1 sm:mb-2 text-xs sm:text-sm text-gray-500 text-center">
                    <span className="font-semibold">Klik om te uploaden</span>
                    <span className="hidden sm:inline"> of sleep bestanden hierheen</span>
                  </p>
                  <p className="text-xs text-gray-500 text-center">JPG, PNG, HEIC (MAX. 10MB)</p>
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
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
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
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-8 h-8 sm:w-7 sm:h-7 flex items-center justify-center text-base sm:text-sm shadow-lg hover:bg-red-600 transition-colors touch-manipulation"
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
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4">
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
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-8 h-8 sm:w-7 sm:h-7 flex items-center justify-center text-base sm:text-sm shadow-lg hover:bg-red-600 transition-colors touch-manipulation"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {!formData.articleNumber && selectedFiles.length > 0 && (
            <div className="mt-3 flex items-start gap-2 p-3 sm:p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-xs sm:text-sm text-amber-800">
                Voer eerst een artikelnummer in voordat je foto's uploadt
              </p>
            </div>
          )}
        </div>
          </>
        )}
      </div>

      <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200 pb-4 sm:pb-0">
        <button
          type="submit"
          disabled={loading || uploadingPhotos || (selectedFiles.length > 0 && !formData.articleNumber)}
          className="w-full min-h-[48px] bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 sm:py-3 px-6 rounded-lg font-semibold shadow-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 text-base sm:text-lg touch-manipulation"
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
    </>
  )
}


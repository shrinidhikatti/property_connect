import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { propertiesApi } from '../../api/properties'
import { PropertyCard } from './PropertyCard'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'
import { PROPERTY_TYPES } from '../../constants/propertyTypes'

export function PropertyListPage() {
  const [filters, setFilters] = useState({
    search: '', property_type: '', min_price: '', max_price: '',
    min_bedrooms: '', locality: '',
  })
  const [applied, setApplied] = useState({})

  const { data, isLoading, isError } = useQuery({
    queryKey: ['properties', applied],
    queryFn: () => propertiesApi.list(applied).then((r) => r.data),
  })

  const raw = data?.results ?? data
  const properties = Array.isArray(raw) ? raw : []

  const apply = () => {
    const clean = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ''))
    setApplied(clean)
  }

  const reset = () => { setFilters({ search: '', property_type: '', min_price: '', max_price: '', min_bedrooms: '', locality: '' }); setApplied({}) }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Properties in Belagavi</h1>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-gray-100 p-4 mb-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <Input placeholder="Search title / locality…" value={filters.search}
          onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))} />
        <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={filters.property_type}
          onChange={(e) => setFilters(f => ({ ...f, property_type: e.target.value }))}>
          <option value="">All Types</option>
          {PROPERTY_TYPES.map(({ value, label }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        <Input placeholder="Min price (₹)" type="number" value={filters.min_price}
          onChange={(e) => setFilters(f => ({ ...f, min_price: e.target.value }))} />
        <Input placeholder="Max price (₹)" type="number" value={filters.max_price}
          onChange={(e) => setFilters(f => ({ ...f, max_price: e.target.value }))} />
        <Input placeholder="Locality" value={filters.locality}
          onChange={(e) => setFilters(f => ({ ...f, locality: e.target.value }))} />
        <Input placeholder="Min bedrooms" type="number" value={filters.min_bedrooms}
          onChange={(e) => setFilters(f => ({ ...f, min_bedrooms: e.target.value }))} />
        <Button onClick={apply} className="col-span-1">Search</Button>
        <Button variant="secondary" onClick={reset}>Reset</Button>
      </div>

      {/* Results */}
      {isError ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg font-medium">Unable to load properties.</p>
          <p className="text-sm mt-1">The server may be starting up — please try again in a moment.</p>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : properties.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">No properties found.</p>
          <p className="text-sm mt-1">Try adjusting your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {properties.map((p) => <PropertyCard key={p.id} property={p} />)}
        </div>
      )}
    </div>
  )
}

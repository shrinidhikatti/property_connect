import { Link } from 'react-router-dom'
import { StatusBadge } from '../../components/ui/Badge'
import { PROPERTY_TYPE_LABEL } from '../../constants/propertyTypes'

const PLACEHOLDER = 'https://placehold.co/400x240?text=No+Image'

function formatPrice(price) {
  const n = Number(price)
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`
  return `₹${n.toLocaleString('en-IN')}`
}

export function PropertyCard({ property, showStatus = false }) {
  const { id, title, property_type, price, area_sqft, bedrooms, locality, city, cover_image, status } = property

  return (
    <Link to={`/properties/${id}`} className="block group">
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
        <div className="relative h-44 bg-gray-100 overflow-hidden">
          <img
            src={cover_image || PLACEHOLDER}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          <span className="absolute top-2 left-2 bg-white/90 text-xs font-medium px-2 py-0.5 rounded-full text-gray-700">
            {PROPERTY_TYPE_LABEL[property_type] || property_type}
          </span>
          {showStatus && (
            <span className="absolute top-2 right-2">
              <StatusBadge status={status} />
            </span>
          )}
        </div>
        <div className="p-4">
          <p className="font-semibold text-gray-800 text-sm truncate">{title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{locality}, {city}</p>
          <div className="flex items-center justify-between mt-3">
            <span className="text-primary-600 font-bold text-base">{formatPrice(price)}</span>
            <span className="text-xs text-gray-500">{area_sqft.toLocaleString()} sqft</span>
          </div>
          {bedrooms != null && (
            <p className="text-xs text-gray-400 mt-1">{bedrooms} BHK</p>
          )}
        </div>
      </div>
    </Link>
  )
}

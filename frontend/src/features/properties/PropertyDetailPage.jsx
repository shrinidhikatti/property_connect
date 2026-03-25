import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { propertiesApi } from '../../api/properties'
import { useAuthStore } from '../../store/authStore'
import { useToastStore } from '../../components/ui/Toast'
import { Button } from '../../components/ui/Button'
import { StatusBadge } from '../../components/ui/Badge'

const PLACEHOLDER = 'https://placehold.co/800x500?text=No+Image'

function formatPrice(price) {
  const n = Number(price)
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)} Crore`
  if (n >= 100000) return `₹${(n / 100000).toFixed(2)} Lakh`
  return `₹${n.toLocaleString('en-IN')}`
}

export function PropertyDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const addToast = useToastStore((s) => s.add)
  const qc = useQueryClient()
  const [imgIdx, setImgIdx] = useState(0)

  const { data: property, isLoading } = useQuery({
    queryKey: ['property', id],
    queryFn: () => propertiesApi.get(id).then((r) => r.data),
  })

  const favMutation = useMutation({
    mutationFn: (isFav) =>
      isFav ? propertiesApi.removeFavorite(id) : propertiesApi.addFavorite(id),
    onSuccess: () => qc.invalidateQueries(['property', id]),
  })

  if (isLoading) return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="h-96 bg-gray-100 rounded-2xl animate-pulse mb-6" />
    </div>
  )

  if (!property) return <div className="text-center py-16 text-gray-500">Property not found.</div>

  const images = property.images || []
  const currentImg = images[imgIdx]?.image_url || PLACEHOLDER

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Image gallery */}
      <div className="relative rounded-2xl overflow-hidden h-72 md:h-96 bg-gray-100 mb-4">
        <img src={currentImg} alt={property.title} className="w-full h-full object-cover" />
        {images.length > 1 && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
            {images.map((_, i) => (
              <button key={i} onClick={() => setImgIdx(i)}
                className={`w-2 h-2 rounded-full ${i === imgIdx ? 'bg-white' : 'bg-white/50'}`} />
            ))}
          </div>
        )}
      </div>
      {images.length > 1 && (
        <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
          {images.map((img, i) => (
            <button key={i} onClick={() => setImgIdx(i)}
              className={`w-16 h-12 rounded-lg overflow-hidden flex-shrink-0 border-2 ${i === imgIdx ? 'border-primary-500' : 'border-transparent'}`}>
              <img src={img.thumbnail_url || img.image_url} alt="" className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-8">
        {/* Left col */}
        <div className="md:col-span-2 space-y-5">
          <div>
            <div className="flex items-start justify-between gap-3">
              <h1 className="text-2xl font-bold text-gray-800">{property.title}</h1>
              <StatusBadge status={property.status} />
            </div>
            <p className="text-gray-500 text-sm mt-1">{property.locality}, {property.city} {property.pincode}</p>
          </div>

          <p className="text-3xl font-bold text-primary-600">
            {formatPrice(property.price)}
            {property.price_negotiable && <span className="text-sm font-normal text-gray-500 ml-2">(negotiable)</span>}
          </p>

          <div className="grid grid-cols-3 gap-3">
            {[
              ['Area', `${property.area_sqft.toLocaleString()} sqft`],
              property.bedrooms != null && ['Bedrooms', property.bedrooms],
              property.bathrooms != null && ['Bathrooms', property.bathrooms],
            ].filter(Boolean).map(([label, val]) => (
              <div key={label} className="bg-gray-50 rounded-xl p-3 text-center">
                <p className="text-xs text-gray-500">{label}</p>
                <p className="font-semibold text-gray-800 mt-0.5">{val}</p>
              </div>
            ))}
          </div>

          {property.description && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Description</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{property.description}</p>
            </div>
          )}

          {property.amenities?.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Amenities</h3>
              <div className="flex flex-wrap gap-2">
                {property.amenities.map((a) => (
                  <span key={a} className="bg-primary-50 text-primary-600 text-xs px-3 py-1 rounded-full capitalize">{a}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right col — contact card */}
        <div className="space-y-4">
          <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
            <p className="font-semibold text-gray-800">Listed by</p>
            <p className="text-gray-600 text-sm mt-1">{property.owner_name}</p>

            {property.owner_phone ? (
              <a href={`tel:${property.owner_phone}`}
                className="mt-3 flex items-center gap-2 text-primary-600 font-medium text-sm">
                {property.owner_phone}
              </a>
            ) : (
              <p className="text-xs text-gray-400 mt-2">
                Start a conversation to unlock contact details.
              </p>
            )}

            {isAuthenticated && user?.role === 'buyer' && (
              <Button className="w-full mt-4" onClick={() => navigate(`/chat?property=${id}`)}>
                Send Enquiry
              </Button>
            )}

            <Button
              variant={property.is_favorited ? 'secondary' : 'outline'}
              className="w-full mt-2"
              onClick={() => favMutation.mutate(property.is_favorited)}
              loading={favMutation.isPending}
            >
              {property.is_favorited ? '♥ Saved' : '♡ Save Property'}
            </Button>
          </div>

          <div className="bg-green-50 border border-green-100 rounded-2xl p-4">
            <p className="text-xs text-green-700 font-medium">✓ Advocate Verified</p>
            <p className="text-xs text-green-600 mt-1">Documents verified by a registered advocate.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

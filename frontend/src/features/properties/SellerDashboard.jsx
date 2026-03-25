import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { propertiesApi } from '../../api/properties'
import { Button } from '../../components/ui/Button'
import { useToastStore } from '../../components/ui/Toast'
import { PROPERTY_TYPE_LABEL } from '../../constants/propertyTypes'

const PLACEHOLDER = 'https://placehold.co/400x240?text=No+Image'

function formatPrice(price) {
  const n = Number(price)
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)}Cr`
  if (n >= 100000)   return `₹${(n / 100000).toFixed(1)}L`
  return `₹${n.toLocaleString('en-IN')}`
}

const STATUS_INFO = {
  draft:             { color: 'bg-gray-100 text-gray-600',     hint: 'Upload a document then submit for verification.' },
  pending:           { color: 'bg-yellow-100 text-yellow-700', hint: 'Waiting to be assigned to an advocate.' },
  under_review:      { color: 'bg-blue-100 text-blue-700',     hint: 'An advocate is reviewing your documents.' },
  changes_requested: { color: 'bg-orange-100 text-orange-700', hint: 'Advocate has requested document changes.' },
  approved:          { color: 'bg-green-100 text-green-700',   hint: 'Live and visible to buyers.' },
  rejected:          { color: 'bg-red-100 text-red-700',       hint: 'Listing was rejected. Contact support.' },
  expired:           { color: 'bg-gray-100 text-gray-500',     hint: 'Listing expired after 90 days.' },
}

const DOC_TYPES = [
  ['ec','EC'], ['mother_deed','Mother Deed'], ['khata','Khata'], ['rtc','RTC'],
  ['sale_deed','Sale Deed'], ['rera_cert','RERA'], ['tax_receipt','Tax Receipt'],
  ['plan_approval','Plan Approval'], ['other','Other'],
]

function ListingCard({ property, onSubmit, submitting, onDocUploaded }) {
  const info = STATUS_INFO[property.status] || STATUS_INFO.draft
  const canSubmit = property.status === 'draft' || property.status === 'changes_requested'
  const needsDoc = canSubmit && property.document_count === 0
  const [docType, setDocType] = useState('other')
  const fileInputRef = useRef(null)
  const { add: addToast } = useToastStore()

  const uploadMutation = useMutation({
    mutationFn: (file) => {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('doc_type', docType)
      return propertiesApi.uploadDocument(property.id, fd)
    },
    onSuccess: () => {
      addToast('Document uploaded!', 'success')
      if (fileInputRef.current) fileInputRef.current.value = ''
      onDocUploaded()
    },
    onError: (e) => addToast(e.response?.data?.detail || 'Upload failed', 'error'),
  })

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) uploadMutation.mutate(file)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden hover:shadow-md transition-shadow">
      {/* Image */}
      <div className="relative h-40 bg-gray-100">
        <img
          src={property.cover_image || PLACEHOLDER}
          alt={property.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <span className="absolute top-2 left-2 text-xs font-medium bg-white/90 px-2 py-0.5 rounded-full text-gray-700">
          {PROPERTY_TYPE_LABEL[property.property_type] || property.property_type}
        </span>
      </div>

      {/* Details */}
      <div className="p-4 space-y-3">
        <div>
          <p className="font-semibold text-gray-800 truncate">{property.title}</p>
          <p className="text-sm text-gray-500 mt-0.5">{property.locality}, {property.city}</p>
        </div>

        <div className="flex items-center justify-between">
          <span className="font-bold text-primary-600">{formatPrice(property.price)}</span>
          <span className="text-xs text-gray-400">{property.area_sqft?.toLocaleString()} sqft</span>
        </div>

        {/* Status */}
        <div>
          <span className={`inline-block text-xs font-semibold px-2.5 py-1 rounded-full ${info.color}`}>
            {property.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </span>
          {property.document_count > 0 && (
            <span className="ml-2 text-xs text-gray-400">{property.document_count} doc{property.document_count !== 1 ? 's' : ''}</span>
          )}
          <p className="text-xs text-gray-400 mt-1">{info.hint}</p>
        </div>

        {/* Inline doc upload for listings with no documents */}
        {needsDoc && (
          <div className="border border-dashed border-gray-300 rounded-xl p-3 space-y-2">
            <p className="text-xs text-gray-500 font-medium">Upload a document to enable submission</p>
            <div className="flex gap-2">
              <select
                className="flex-1 border border-gray-200 rounded-lg text-xs px-2 py-1.5"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
              >
                {DOC_TYPES.map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
              <label className={`px-3 py-1.5 text-xs font-medium rounded-lg cursor-pointer transition-colors
                ${uploadMutation.isPending
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
                {uploadMutation.isPending ? 'Uploading…' : 'Choose File'}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileChange}
                  disabled={uploadMutation.isPending}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2 pt-1">
          {canSubmit && !needsDoc && (
            <button
              onClick={() => onSubmit(property.id)}
              disabled={submitting === property.id}
              className="flex-1 bg-primary-500 text-white text-sm font-semibold py-2 rounded-xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting === property.id ? 'Submitting…' : 'Submit for Verification'}
            </button>
          )}
          <Link
            to={`/properties/${property.id}`}
            className="px-3 py-2 text-sm border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition-colors"
          >
            View
          </Link>
        </div>
      </div>
    </div>
  )
}

export function SellerDashboard() {
  const qc = useQueryClient()
  const { add: addToast } = useToastStore()

  const { data: listings = [], isLoading } = useQuery({
    queryKey: ['my-listings'],
    queryFn: () => propertiesApi.myListings().then((r) => r.data),
  })

  const submitMutation = useMutation({
    mutationFn: (id) => propertiesApi.submit(id),
    onSuccess: () => {
      qc.invalidateQueries(['my-listings'])
      addToast('Listing submitted for verification!', 'success')
    },
    onError: (e) => {
      addToast(e.response?.data?.message || 'Submission failed.', 'error')
    },
  })

  const counts = {
    draft:    listings.filter(p => p.status === 'draft').length,
    pending:  listings.filter(p => ['pending', 'under_review'].includes(p.status)).length,
    approved: listings.filter(p => p.status === 'approved').length,
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">My Listings</h1>
          {listings.length > 0 && (
            <p className="text-sm text-gray-500 mt-0.5">
              {counts.draft} draft · {counts.pending} in review · {counts.approved} live
            </p>
          )}
        </div>
        <Link to="/properties/new">
          <Button>+ New Listing</Button>
        </Link>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-72 bg-gray-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : listings.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg font-medium">No listings yet.</p>
          <p className="text-sm mt-1 mb-4">Create your first property listing to get started.</p>
          <Link to="/properties/new">
            <Button>Create your first listing</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {listings.map((p) => (
            <ListingCard
              key={p.id}
              property={p}
              onSubmit={(id) => submitMutation.mutate(id)}
              submitting={submitMutation.isPending ? submitMutation.variables : null}
              onDocUploaded={() => qc.invalidateQueries(['my-listings'])}
            />
          ))}
        </div>
      )}
    </div>
  )
}

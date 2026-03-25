import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { propertiesApi } from '../../api/properties'
import { useToastStore } from '../../components/ui/Toast'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'
import { PROPERTY_TYPES } from '../../constants/propertyTypes'

const STEPS = ['Basic Info', 'Location', 'Details', 'Documents', 'Review']

// Per-step schemas — only the fields visible on that step
const step0Schema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters'),
  property_type: z.enum(['agriculture', 'plot', 'flat', 'rent']),
  price: z.coerce.number().positive('Price must be positive'),
  price_negotiable: z.boolean().default(true),
  area_sqft: z.coerce.number().positive('Area must be positive'),
  bedrooms: z.coerce.number().optional(),
  bathrooms: z.coerce.number().optional(),
  description: z.string().optional(),
})

const step1Schema = z.object({
  address: z.string().min(5, 'Address is required'),
  locality: z.string().min(2, 'Locality is required'),
  city: z.string().default('Belagavi'),
  pincode: z.string().regex(/^\d{6}$/, 'Enter a 6-digit pincode').optional().or(z.literal('')),
  lat: z.coerce.number().optional(),
  lng: z.coerce.number().optional(),
})

// Full schema used only for the final API call
const fullSchema = step0Schema.merge(step1Schema)

const AMENITY_OPTIONS = ['parking', 'lift', 'gym', 'swimming_pool', 'security', 'power_backup', 'water_24x7', 'park']

const DOC_TYPES = [
  ['ec','EC'], ['mother_deed','Mother Deed'], ['khata','Khata'], ['rtc','RTC'],
  ['sale_deed','Sale Deed'], ['rera_cert','RERA'], ['tax_receipt','Tax Receipt'],
  ['plan_approval','Plan Approval'], ['other','Other'],
]

export function CreatePropertyPage() {
  const navigate = useNavigate()
  const addToast = useToastStore((s) => s.add)
  const [step, setStep] = useState(0)
  const [amenities, setAmenities] = useState([])
  const [documents, setDocuments] = useState([]) // [{file, doc_type}]
  const [createdId, setCreatedId] = useState(null)
  const fileInputRef = useRef(null)

  // Use the full schema but validate field-by-field per step
  const { register, handleSubmit, trigger, formState: { errors }, getValues } = useForm({
    resolver: zodResolver(fullSchema),
    defaultValues: { city: 'Belagavi', price_negotiable: true },
  })

  const createMutation = useMutation({
    mutationFn: (data) => propertiesApi.create({ ...data, amenities }),
    onSuccess: (res) => { setCreatedId(res.data.id); setStep(3) }, // jump to Documents
    onError: (e) => addToast(e.response?.data?.message || 'Failed to create listing', 'error'),
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      for (const doc of documents) {
        const fd = new FormData()
        fd.append('file', doc.file)
        fd.append('doc_type', doc.doc_type)
        await propertiesApi.uploadDocument(createdId, fd)
      }
      return propertiesApi.submit(createdId)
    },
    onSuccess: () => {
      addToast('Listing submitted for verification!', 'success')
      navigate('/my-listings')
    },
    onError: (e) => addToast(e.response?.data?.message || 'Submission failed', 'error'),
  })

  const toggleAmenity = (a) =>
    setAmenities((prev) => prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a])

  const addDocument = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setDocuments((d) => [...d, { file, doc_type: 'other' }])
      // Reset input so same file can be re-selected
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const updateDocType = (idx, doc_type) =>
    setDocuments((d) => d.map((x, i) => i === idx ? { ...x, doc_type } : x))

  const removeDoc = (idx) => setDocuments((d) => d.filter((_, i) => i !== idx))

  const STEP_FIELDS = {
    0: ['title', 'property_type', 'price', 'price_negotiable', 'area_sqft', 'description'],
    1: ['address', 'locality', 'city', 'pincode', 'lat', 'lng'],
    2: ['bedrooms', 'bathrooms'],
  }

  const onNext = async () => {
    if (step === 0) {
      const valid = await trigger(STEP_FIELDS[0])
      if (!valid) return
      setStep(1)
    } else if (step === 1) {
      const valid = await trigger(STEP_FIELDS[1])
      if (!valid) return
      setStep(2)
    } else if (step === 2) {
      // All form data collected — create the property now (amenities from state)
      const data = getValues()
      createMutation.mutate(data)
      // onSuccess jumps to step 3 (Documents)
    } else if (step < STEPS.length - 1) {
      setStep((s) => s + 1)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-2">List a Property</h1>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
              ${i < step ? 'bg-primary-500 text-white' : i === step ? 'bg-primary-500 text-white ring-4 ring-primary-100' : 'bg-gray-100 text-gray-500'}`}>
              {i < step ? '✓' : i + 1}
            </div>
            {i < STEPS.length - 1 && <div className={`flex-1 h-0.5 ${i < step ? 'bg-primary-500' : 'bg-gray-200'}`} style={{ width: 24 }} />}
          </div>
        ))}
      </div>

      <form className="space-y-5">
        {/* Step 0: Basic Info */}
        {step === 0 && (
          <>
            <Input label="Title" error={errors.title?.message} {...register('title')} placeholder="e.g. 2BHK Apartment in Tilakwadi" />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Property Type</label>
              <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm" {...register('property_type')}>
                {PROPERTY_TYPES.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Input label="Price (₹)" type="number" error={errors.price?.message} {...register('price')} />
              <Input label="Area (sqft)" type="number" error={errors.area_sqft?.message} {...register('area_sqft')} />
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" {...register('price_negotiable')} className="accent-primary-500" />
              Price is negotiable
            </label>
            <Input label="Description (optional)" as="textarea" {...register('description')} />
          </>
        )}

        {/* Step 1: Location */}
        {step === 1 && (
          <>
            <Input label="Full Address" error={errors.address?.message} {...register('address')} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Locality" error={errors.locality?.message} {...register('locality')} placeholder="e.g. Tilakwadi" />
              <Input label="City" {...register('city')} />
            </div>
            <Input label="Pincode" error={errors.pincode?.message} {...register('pincode')} />
            <div className="grid grid-cols-2 gap-3">
              <Input label="Latitude (optional)" type="number" step="any" {...register('lat')} placeholder="15.8497" />
              <Input label="Longitude (optional)" type="number" step="any" {...register('lng')} placeholder="74.4977" />
            </div>
          </>
        )}

        {/* Step 2: Details */}
        {step === 2 && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <Input label="Bedrooms" type="number" {...register('bedrooms')} />
              <Input label="Bathrooms" type="number" {...register('bathrooms')} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Amenities</p>
              <div className="flex flex-wrap gap-2">
                {AMENITY_OPTIONS.map((a) => (
                  <button type="button" key={a} onClick={() => toggleAmenity(a)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors
                      ${amenities.includes(a) ? 'bg-primary-500 text-white border-primary-500' : 'bg-white text-gray-600 border-gray-300 hover:border-primary-300'}`}>
                    {a.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Step 3: Documents */}
        {step === 3 && (
          <div>
            <p className="text-sm text-gray-600 mb-4">Upload property documents (EC, Mother Deed, Khata, etc.)</p>
            <label className="block border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-primary-400 transition-colors">
              <input ref={fileInputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={addDocument} className="hidden" />
              <p className="text-gray-500 text-sm">Click to upload (PDF, JPG, PNG — max 10MB)</p>
            </label>
            {documents.length > 0 && (
              <div className="mt-4 space-y-2">
                {documents.map((doc, i) => (
                  <div key={i} className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                    <p className="text-sm text-gray-700 flex-1 truncate">{doc.file.name}</p>
                    <select className="border border-gray-200 rounded-lg text-xs px-2 py-1"
                      value={doc.doc_type} onChange={(e) => updateDocType(i, e.target.value)}>
                      {DOC_TYPES.map(([v, l]) => (
                        <option key={v} value={v}>{l}</option>
                      ))}
                    </select>
                    <button type="button" onClick={() => removeDoc(i)} className="text-red-400 hover:text-red-600 text-xs">✕</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <div className="space-y-3">
            <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-700 space-y-2">
              <p><strong>Title:</strong> {getValues('title')}</p>
              <p><strong>Type:</strong> {getValues('property_type')}</p>
              <p><strong>Price:</strong> ₹{Number(getValues('price')).toLocaleString('en-IN')}</p>
              <p><strong>Area:</strong> {getValues('area_sqft')} sqft</p>
              <p><strong>Locality:</strong> {getValues('locality')}, {getValues('city')}</p>
              <p><strong>Documents:</strong> {documents.length} uploaded</p>
              <p><strong>Amenities:</strong> {amenities.join(', ') || 'None'}</p>
            </div>
            <p className="text-xs text-gray-500">
              Submitting will send your listing to an advocate for document verification. This usually takes 1–3 business days.
            </p>
          </div>
        )}
      </form>

      <div className="flex justify-between mt-8">
        <Button variant="secondary" onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0}>
          Back
        </Button>
        {step < STEPS.length - 1 ? (
          <Button onClick={onNext} loading={createMutation.isPending}>
            {step === 2 ? 'Save & Continue' : 'Next'}
          </Button>
        ) : (
          <Button onClick={() => submitMutation.mutate()} loading={submitMutation.isPending}
            disabled={documents.length === 0}>
            Submit for Verification
          </Button>
        )}
      </div>
    </div>
  )
}

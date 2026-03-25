import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { verificationsApi } from '../../api/properties'
import { useToastStore } from '../../components/ui/Toast'
import { Button } from '../../components/ui/Button'
import { StatusBadge } from '../../components/ui/Badge'
import { Card } from '../../components/ui/Card'

function formatPrice(price) {
  const n = Number(price)
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`
  return `₹${n.toLocaleString('en-IN')}`
}

function VerificationCard({ v, onAction }) {
  const [open, setOpen] = useState(false)
  const [remarks, setRemarks] = useState('')
  const [feedback, setFeedback] = useState({})
  const prop = v.property_detail

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-gray-800">{prop?.title}</p>
          <p className="text-sm text-gray-500">{prop?.locality}, {prop?.city}</p>
          {prop && <p className="text-primary-600 font-bold mt-1">{formatPrice(prop.price)}</p>}
        </div>
        <StatusBadge status={v.status} />
      </div>

      <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
        <span>{v.documents?.length || 0} document(s)</span>
        <span>·</span>
        <span>Assigned {new Date(v.assigned_at).toLocaleDateString('en-IN')}</span>
      </div>

      <button onClick={() => setOpen(!open)}
        className="text-xs text-primary-500 mt-2 hover:underline">
        {open ? 'Hide documents ▲' : 'Review documents ▼'}
      </button>

      {open && (
        <div className="mt-3 space-y-2">
          {(v.documents || []).map((doc) => (
            <div key={doc.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
              <div>
                <p className="text-xs font-medium text-gray-700">{doc.doc_type_display}</p>
                <p className="text-xs text-gray-400">{doc.file_name}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {v.status === 'pending' && (
        <div className="mt-4 space-y-3">
          <textarea
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none"
            rows={2} placeholder="Remarks (optional)"
            value={remarks} onChange={(e) => setRemarks(e.target.value)}
          />
          <div className="flex gap-2">
            <Button className="flex-1" onClick={() => onAction(v.id, 'approve')}>
              ✓ Approve
            </Button>
            <Button variant="outline" className="flex-1"
              onClick={() => onAction(v.id, 'request_changes', { remarks })}>
              Request Changes
            </Button>
            <Button variant="danger" className="flex-1"
              onClick={() => onAction(v.id, 'reject', { rejection_reason: remarks })}>
              ✕ Reject
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}

export function AdvocateDashboard() {
  const addToast = useToastStore((s) => s.add)
  const qc = useQueryClient()
  const [tab, setTab] = useState('queue')

  const { data: queue = [], isLoading: queueLoading } = useQuery({
    queryKey: ['verification-queue'],
    queryFn: () => verificationsApi.queue().then((r) => r.data),
  })

  const { data: all = [], isLoading: allLoading } = useQuery({
    queryKey: ['verifications-all'],
    queryFn: () => verificationsApi.list().then((r) => r.data),
    enabled: tab === 'history',
  })

  const actionMutation = useMutation({
    mutationFn: ({ id, action, data }) => {
      if (action === 'approve') return verificationsApi.approve(id)
      if (action === 'reject') return verificationsApi.reject(id, data)
      return verificationsApi.requestChanges(id, data)
    },
    onSuccess: (_, { action }) => {
      addToast(`Verification ${action.replace('_', ' ')}d successfully`, 'success')
      qc.invalidateQueries(['verification-queue'])
      qc.invalidateQueries(['verifications-all'])
    },
    onError: (e) => addToast(e.response?.data?.message || 'Action failed', 'error'),
  })

  const onAction = (id, action, data = {}) => actionMutation.mutate({ id, action, data })

  const items = tab === 'queue' ? queue : all
  const isLoading = tab === 'queue' ? queueLoading : allLoading

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Verification Dashboard</h1>

      <div className="flex gap-2 mb-6">
        {[['queue', `Queue (${queue.length})`], ['history', 'History']].map(([val, label]) => (
          <button key={val} onClick={() => setTab(val)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${tab === val ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-32 bg-gray-100 rounded-2xl animate-pulse" />)}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p>{tab === 'queue' ? 'No pending verifications.' : 'No verification history.'}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((v) => <VerificationCard key={v.id} v={v} onAction={onAction} />)}
        </div>
      )}
    </div>
  )
}

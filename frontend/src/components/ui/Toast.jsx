import { create } from 'zustand'

export const useToastStore = create((set) => ({
  toasts: [],
  add: (message, type = 'info') => {
    const id = Date.now()
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 4000)
  },
  remove: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

const colors = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  info: 'bg-primary-500',
  warning: 'bg-yellow-500',
}

export function ToastContainer() {
  const { toasts, remove } = useToastStore()
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`${colors[t.type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 min-w-64 cursor-pointer`}
          onClick={() => remove(t.id)}
        >
          <span className="text-sm">{t.message}</span>
        </div>
      ))}
    </div>
  )
}

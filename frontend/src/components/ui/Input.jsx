export function Input({ label, error, className = '', ...props }) {
  const inputId = props.id ?? props.name
  return (
    <div className="flex flex-col gap-1">
      {label && <label htmlFor={inputId} className="text-sm font-medium text-gray-700">{label}</label>}
      <input
        id={inputId}
        className={`border rounded-lg px-3 py-2 text-sm outline-none transition-colors
          focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
          ${error ? 'border-red-400' : 'border-gray-300'}
          ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}

const variants = {
  primary: 'bg-primary-500 hover:bg-primary-600 text-white',
  secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-800',
  outline: 'border border-primary-500 text-primary-500 hover:bg-primary-50',
  danger: 'bg-red-600 hover:bg-red-700 text-white',
}

export function Button({ children, variant = 'primary', className = '', loading = false, ...props }) {
  return (
    <button
      className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" /> : null}
      {children}
    </button>
  )
}

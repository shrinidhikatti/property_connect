import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useToastStore } from '../../components/ui/Toast'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'

const schema = z.object({
  username: z.string().min(1, 'Email or username is required'),
  password: z.string().min(1, 'Password is required'),
})

const TEST_ACCOUNTS = [
  { label: 'Seller', username: 'seller_ravi', password: 'Seller@1234' },
  { label: 'Buyer', username: 'buyer_amit', password: 'Buyer@1234' },
  { label: 'Advocate', username: 'advocate_priya', password: 'Advocate@1234' },
]

export function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const addToast = useToastStore((s) => s.add)
  const [apiError, setApiError] = useState(null)

  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
  })

  const fillTestAccount = (acc) => {
    setValue('username', acc.username)
    setValue('password', acc.password)
  }

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      await login(data)
      navigate('/properties')
    } catch (err) {
      const msg = err.response?.data?.message || err.response?.data?.detail || 'Login failed. Check your credentials.'
      setApiError(msg)
      addToast(msg, 'error')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-primary-500">Property Connect</h1>
          <p className="text-gray-500 text-sm mt-1">Belagavi's trusted property marketplace</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          {apiError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
              {apiError}
            </div>
          )}
          <Input
            label="Email or Mobile Number"
            type="text"
            placeholder="you@example.com or 9876543210"
            error={errors.username?.message}
            {...register('username')}
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password')}
          />
          <Button type="submit" loading={isSubmitting} className="w-full mt-2">
            Sign In
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-500 font-medium hover:underline">
            Register
          </Link>
        </p>

        {/* Test accounts — quick fill */}
        <div className="mt-6 border-t border-gray-100 pt-4">
          <p className="text-xs text-gray-400 text-center mb-3">Test Accounts (tap to fill)</p>
          <div className="flex flex-col gap-2">
            {TEST_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                type="button"
                onClick={() => fillTestAccount(acc)}
                className="flex items-center justify-between text-left w-full px-3 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div>
                  <span className="text-sm font-medium text-gray-700">{acc.label}</span>
                  <span className="text-xs text-gray-400 ml-2">{acc.username}</span>
                </div>
                <span className="text-xs text-gray-400 font-mono">{acc.password}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

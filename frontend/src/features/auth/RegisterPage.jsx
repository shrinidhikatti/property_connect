import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useToastStore } from '../../components/ui/Toast'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'

const schema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Enter a valid email'),
  phone: z.string().regex(/^[6-9]\d{9}$/, 'Enter a valid 10-digit mobile number'),
  role: z.enum(['buyer', 'seller', 'builder']),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  password2: z.string(),
}).refine((d) => d.password === d.password2, {
  message: 'Passwords do not match',
  path: ['password2'],
})

const ROLES = [
  { value: 'buyer',   label: 'Buyer — I want to buy/rent' },
  { value: 'seller',  label: 'Seller — I want to sell/rent out' },
  { value: 'builder', label: 'Builder — I am a developer' },
]

export function RegisterPage() {
  const navigate = useNavigate()
  const registerUser = useAuthStore((s) => s.register)
  const addToast = useToastStore((s) => s.add)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { role: 'buyer' },
  })

  const onSubmit = async (data) => {
    try {
      await registerUser(data)
      navigate('/verify-phone')
    } catch (err) {
      addToast(err.response?.data?.message || 'Registration failed', 'error')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-primary-500">Create Account</h1>
          <p className="text-gray-500 text-sm mt-1">Join Belagavi's P2P property marketplace</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="First Name" error={errors.first_name?.message} {...register('first_name')} />
            <Input label="Last Name" error={errors.last_name?.message} {...register('last_name')} />
          </div>
          <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />
          <Input label="Mobile Number" type="tel" placeholder="9876543210" error={errors.phone?.message} {...register('phone')} />

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">I am a</label>
            <select
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:border-primary-500"
              {...register('role')}
            >
              {ROLES.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            {errors.role && <p className="text-xs text-red-500">{errors.role.message}</p>}
          </div>

          <Input label="Password" type="password" error={errors.password?.message} {...register('password')} />
          <Input label="Confirm Password" type="password" error={errors.password2?.message} {...register('password2')} />

          <Button type="submit" loading={isSubmitting} className="w-full mt-2">
            Create Account
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-500 font-medium hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  )
}

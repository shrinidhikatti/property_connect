import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { authApi } from '../../api/auth'
import { useToastStore } from '../../components/ui/Toast'
import { Input } from '../../components/ui/Input'
import { Button } from '../../components/ui/Button'

export function OtpVerifyPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const addToast = useToastStore((s) => s.add)
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)

  const phone = user?.phone

  const sendOtp = async () => {
    if (!phone) return
    setSending(true)
    try {
      await authApi.sendOtp(phone)
      addToast('OTP sent to your mobile number', 'success')
    } catch (err) {
      addToast(err.response?.data?.message || 'Failed to send OTP', 'error')
    } finally {
      setSending(false)
    }
  }

  const verifyOtp = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authApi.verifyOtp(phone, otp)
      addToast('Phone verified successfully!', 'success')
      navigate('/')
    } catch (err) {
      addToast(err.response?.data?.message || 'Invalid OTP', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Verify Your Phone</h2>
        <p className="text-gray-500 text-sm mb-6">
          We'll send a 6-digit OTP to <strong>{phone}</strong>
        </p>

        <Button variant="outline" onClick={sendOtp} loading={sending} className="w-full mb-6">
          Send OTP
        </Button>

        <form onSubmit={verifyOtp} className="flex flex-col gap-4">
          <Input
            label="Enter OTP"
            type="text"
            inputMode="numeric"
            maxLength={6}
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
          />
          <Button type="submit" loading={loading} className="w-full" disabled={otp.length !== 6}>
            Verify
          </Button>
        </form>
      </div>
    </div>
  )
}

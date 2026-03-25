import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HelmetProvider } from 'react-helmet-async'
import { useAuthStore } from './store/authStore'
import { Header } from './components/layout/Header'
import { BottomNav } from './components/layout/BottomNav'
import { ProtectedRoute } from './components/layout/ProtectedRoute'
import { ToastContainer } from './components/ui/Toast'
import PwaUpdatePrompt from './components/ui/PwaUpdatePrompt'

// Auth
import { LoginPage } from './features/auth/LoginPage'
import { RegisterPage } from './features/auth/RegisterPage'
import { OtpVerifyPage } from './features/auth/OtpVerifyPage'

// Payments
import PricingPage from './features/payments/PricingPage'
import CheckoutPage from './features/payments/CheckoutPage'

// Chat & Notifications
import ConversationListPage from './features/chat/ConversationListPage'
import ChatPage from './features/chat/ChatPage'
import NotificationPage from './features/notifications/NotificationPage'

// Properties
import { PropertyListPage } from './features/properties/PropertyListPage'
import { PropertyDetailPage } from './features/properties/PropertyDetailPage'
import { CreatePropertyPage } from './features/properties/CreatePropertyPage'
import { SellerDashboard } from './features/properties/SellerDashboard'
import { AdvocateDashboard } from './features/properties/AdvocateDashboard'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 60_000 },
  },
})

function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-16 text-center">
      <h2 className="text-4xl font-bold text-gray-800 mb-4">
        Find Your Dream Property in Belagavi
      </h2>
      <p className="text-gray-500 max-w-xl mx-auto text-lg">
        Browse advocate-verified listings. Connect directly with sellers. No broker fees.
      </p>
      <a href="/properties"
        className="inline-block mt-8 bg-primary-500 text-white px-8 py-3 rounded-xl font-semibold hover:bg-primary-600 transition-colors">
        Browse Properties
      </a>
    </div>
  )
}

export default function App() {
  const init = useAuthStore((s) => s.init)

  useEffect(() => { init() }, [init])

  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Header />
          <main className="pb-16 md:pb-0">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/verify-phone" element={<ProtectedRoute><OtpVerifyPage /></ProtectedRoute>} />

              {/* Properties — public */}
              <Route path="/properties" element={<PropertyListPage />} />
              <Route path="/properties/:id" element={<PropertyDetailPage />} />

              {/* Seller routes */}
              <Route path="/properties/new" element={<ProtectedRoute><CreatePropertyPage /></ProtectedRoute>} />
              <Route path="/my-listings" element={<ProtectedRoute><SellerDashboard /></ProtectedRoute>} />

              {/* Advocate routes */}
              <Route path="/verifications" element={<ProtectedRoute requiredRole="advocate"><AdvocateDashboard /></ProtectedRoute>} />

              {/* Chat routes */}
              <Route path="/chat" element={<ProtectedRoute><ConversationListPage /></ProtectedRoute>} />
              <Route path="/chat/:id" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />

              {/* Notifications */}
              <Route path="/notifications" element={<ProtectedRoute><NotificationPage /></ProtectedRoute>} />

              {/* Payments */}
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/checkout" element={<ProtectedRoute><CheckoutPage /></ProtectedRoute>} />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <BottomNav />
          <ToastContainer />
          <PwaUpdatePrompt />
        </BrowserRouter>
      </QueryClientProvider>
    </HelmetProvider>
  )
}

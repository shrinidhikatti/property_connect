import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { paymentsApi } from '../../api/payments';
import { useAuthStore } from '../../store/authStore';

function formatPrice(paise) {
  if (paise === 0) return 'Free';
  return `₹${(paise / 100).toLocaleString('en-IN')}/mo`;
}

const HIGHLIGHTS = {
  free:    ['1 active listing', '30-day validity', 'Standard support'],
  basic:   ['5 active listings', '30-day validity', 'Standard support'],
  pro:     ['Unlimited listings', '30-day validity', 'Priority support'],
  builder: ['Unlimited listings', 'Featured placement', '30-day validity', 'Dedicated support'],
};

export default function PricingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const { data: plans = [], isLoading } = useQuery({
    queryKey: ['plans'],
    queryFn: () => paymentsApi.plans().then((r) => r.data),
  });

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => paymentsApi.subscription().then((r) => r.data),
    enabled: isAuthenticated,
  });

  const activePlanCode = subscription?.plan?.code;

  const handleSelect = (plan) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (plan.price_paise === 0) return;
    navigate('/checkout', { state: { plan } });
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-80 bg-gray-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900">Simple, Transparent Pricing</h1>
        <p className="text-gray-500 mt-2">Choose the plan that fits your needs. Upgrade anytime.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((plan) => {
          const isActive = activePlanCode === plan.code;
          const isPro = plan.code === 'pro';

          return (
            <div
              key={plan.code}
              className={`relative flex flex-col rounded-2xl border p-6 transition-all ${
                isPro
                  ? 'border-primary-500 shadow-lg shadow-primary-100 bg-primary-50'
                  : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
              }`}
            >
              {isPro && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                  Most Popular
                </span>
              )}

              <div className="mb-4">
                <h2 className="text-lg font-bold text-gray-900">{plan.name}</h2>
                <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
              </div>

              <div className="mb-6">
                <span className={`text-3xl font-extrabold ${isPro ? 'text-primary-600' : 'text-gray-800'}`}>
                  {formatPrice(plan.price_paise)}
                </span>
              </div>

              <ul className="space-y-2 mb-8 flex-1">
                {(HIGHLIGHTS[plan.code] || []).map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm text-gray-600">
                    <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feat}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSelect(plan)}
                disabled={isActive || plan.price_paise === 0}
                className={`w-full py-2.5 rounded-xl font-semibold text-sm transition-colors ${
                  isActive
                    ? 'bg-green-100 text-green-700 cursor-default'
                    : plan.price_paise === 0
                    ? 'bg-gray-100 text-gray-400 cursor-default'
                    : isPro
                    ? 'bg-primary-500 text-white hover:bg-primary-600'
                    : 'border border-primary-500 text-primary-600 hover:bg-primary-50'
                }`}
              >
                {isActive ? '✓ Current Plan' : plan.price_paise === 0 ? 'Default' : 'Get Started'}
              </button>
            </div>
          );
        })}
      </div>

      {subscription?.expires_at && (
        <p className="text-center text-sm text-gray-400 mt-8">
          Your <strong>{subscription.plan?.name}</strong> plan is active until{' '}
          {new Date(subscription.expires_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}.
        </p>
      )}
    </div>
  );
}

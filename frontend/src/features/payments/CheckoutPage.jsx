import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { paymentsApi } from '../../api/payments';
import { useAuthStore } from '../../store/authStore';
import { useToastStore } from '../../components/ui/Toast';

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (document.getElementById('razorpay-script')) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.id = 'razorpay-script';
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export default function CheckoutPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { addToast } = useToastStore();
  const qc = useQueryClient();
  const [processing, setProcessing] = useState(false);

  const plan = state?.plan;

  useEffect(() => {
    if (!plan) navigate('/pricing');
  }, [plan, navigate]);

  const verifyMutation = useMutation({
    mutationFn: paymentsApi.verifyPayment,
    onSuccess: () => {
      qc.invalidateQueries(['subscription']);
      addToast(`${plan?.name} plan activated! 🎉`, 'success');
      navigate('/pricing');
    },
    onError: () => {
      addToast('Payment verification failed. Contact support.', 'error');
    },
  });

  const handlePay = async () => {
    setProcessing(true);
    try {
      const loaded = await loadRazorpayScript();
      if (!loaded) {
        addToast('Could not load payment gateway. Check your internet connection.', 'error');
        setProcessing(false);
        return;
      }

      const { data: order } = await paymentsApi.createOrder(plan.code);

      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: 'Property Connect',
        description: `${plan.name} Plan — 30 days`,
        order_id: order.order_id,
        prefill: {
          name: user?.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : '',
          email: user?.email || '',
          contact: user?.phone || '',
        },
        theme: { color: '#028090' },
        handler: async (response) => {
          await verifyMutation.mutateAsync({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });
        },
        modal: {
          ondismiss: () => setProcessing(false),
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', (resp) => {
        addToast(`Payment failed: ${resp.error.description}`, 'error');
        setProcessing(false);
      });
      rzp.open();
    } catch (err) {
      addToast('Failed to initiate payment. Please try again.', 'error');
      setProcessing(false);
    }
  };

  if (!plan) return null;

  return (
    <div className="max-w-md mx-auto px-4 py-12">
      <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Order Summary</h1>

        <div className="space-y-4 mb-8">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Plan</span>
            <span className="font-semibold text-gray-800">{plan.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Validity</span>
            <span className="font-semibold text-gray-800">{plan.validity_days} days</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Listings</span>
            <span className="font-semibold text-gray-800">
              {plan.listing_limit === -1 ? 'Unlimited' : plan.listing_limit}
            </span>
          </div>
          {plan.is_featured_included && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Featured</span>
              <span className="font-semibold text-green-600">Included ✓</span>
            </div>
          )}
          <div className="border-t pt-4 flex justify-between">
            <span className="font-semibold text-gray-700">Total</span>
            <span className="font-extrabold text-xl text-gray-900">
              ₹{(plan.price_paise / 100).toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        <button
          onClick={handlePay}
          disabled={processing || verifyMutation.isPending}
          className="w-full bg-primary-500 text-white py-3 rounded-xl font-semibold text-base hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {processing ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Processing…
            </span>
          ) : (
            `Pay ₹${(plan.price_paise / 100).toLocaleString('en-IN')}`
          )}
        </button>

        <p className="text-xs text-center text-gray-400 mt-4">
          Secured by Razorpay · Payments are non-refundable after activation.
        </p>
      </div>
    </div>
  );
}

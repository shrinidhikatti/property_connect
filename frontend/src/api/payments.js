import api from './client';

export const paymentsApi = {
  plans: () => api.get('/payments/plans/'),
  subscription: () => api.get('/payments/subscription/'),
  createOrder: (planCode) => api.post('/payments/create-order/', { plan_code: planCode }),
  verifyPayment: (data) => api.post('/payments/verify/', data),
  history: () => api.get('/payments/history/'),
};

import api from './client'

export const authApi = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  sendOtp: (phone) => api.post('/auth/otp/send/', { phone }),
  verifyOtp: (phone, otp) => api.post('/auth/otp/verify/', { phone, otp }),
  getProfile: () => api.get('/auth/me/'),
  updateProfile: (data) => api.patch('/auth/me/', data),
}

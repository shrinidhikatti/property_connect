import { create } from 'zustand'
import { authApi } from '../api/auth'

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  init: () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authApi.getProfile()
        .then(({ data }) => set({ user: data, isAuthenticated: true }))
        .catch(() => {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        })
    }
  },

  login: async (credentials) => {
    set({ isLoading: true })
    const { data } = await authApi.login(credentials)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    const profile = await authApi.getProfile()
    set({ user: profile.data, isAuthenticated: true, isLoading: false })
    return data
  },

  register: async (userData) => {
    set({ isLoading: true })
    const { data } = await authApi.register(userData)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    set({ user: data.user, isAuthenticated: true, isLoading: false })
    return data
  },

  logout: async () => {
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      await authApi.logout(refresh).catch(() => {})
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },
}))

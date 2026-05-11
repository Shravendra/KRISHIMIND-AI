import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const { data } = await api.post('/auth/login', { email, password })
          api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
          // Fetch full profile
          const profile = await api.get('/auth/me')
          set({
            token: data.access_token,
            user: { ...data, ...profile.data },
            isAuthenticated: true,
            isLoading: false,
          })
          return { success: true }
        } catch (err) {
          const message = err.response?.data?.detail || 'Login failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      register: async (formData) => {
        set({ isLoading: true, error: null })
        try {
          const { data } = await api.post('/auth/register', formData)
          api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
          const profile = await api.get('/auth/me')
          set({
            token: data.access_token,
            user: { ...data, ...profile.data },
            isAuthenticated: true,
            isLoading: false,
          })
          return { success: true }
        } catch (err) {
          const message = err.response?.data?.detail || 'Registration failed'
          set({ error: message, isLoading: false })
          return { success: false, error: message }
        }
      },

      logout: async () => {
        try { await api.post('/auth/logout') } catch (_) {}
        delete api.defaults.headers.common['Authorization']
        set({ user: null, token: null, isAuthenticated: false, error: null })
      },

      updateProfile: async (updates) => {
        try {
          const { data } = await api.put('/auth/me', updates)
          set(state => ({ user: { ...state.user, ...data } }))
          return { success: true }
        } catch (err) {
          return { success: false, error: err.response?.data?.detail }
        }
      },

      clearError: () => set({ error: null }),

      // Restore auth header on app load
      initAuth: () => {
        const token = get().token
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        }
      },
    }),
    {
      name: 'krishimind-auth',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

export { useAuthStore }
export default useAuthStore
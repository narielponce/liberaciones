import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '/api/v1' : 'http://localhost:8095/api/v1')

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user_data')) || null,
    token: localStorage.getItem('access_token') || null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.role || null,
    isAdmin: (state) => state.user?.role === 'admin',
    isOperator: (state) => state.user?.role === 'operador',
    isSupervisor: (state) => state.user?.role === 'supervisor',
  },

  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const formData = new URLSearchParams()
        formData.append('username', email)
        formData.append('password', password)

        const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })

        this.token = response.data.access_token
        this.user = response.data.user

        localStorage.setItem('access_token', this.token)
        localStorage.setItem('user_data', JSON.stringify(this.user))

        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error de conexión con el servidor'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_data')
    },

    getAuthHeaders() {
      return {
        Authorization: `Bearer ${this.token}`,
      }
    },
  },
})

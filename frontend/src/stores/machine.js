import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8095/api/v1'

export const useMachineStore = defineStore('machine', {
  state: () => ({
    machines: [],
    loading: false,
    error: null,
  }),

  actions: {
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      }
    },

    async fetchMachines(includeInactive = true) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(
          `${API_BASE_URL}/machines?include_inactive=${includeInactive}`,
          this.getAuthHeaders()
        )
        this.machines = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al cargar los equipos'
        throw err
      } finally {
        this.loading = false
      }
    },

    async createMachine(payload) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(
          `${API_BASE_URL}/machines`,
          payload,
          this.getAuthHeaders()
        )
        await this.fetchMachines()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al crear el equipo'
        throw err
      } finally {
        this.loading = false
      }
    },

    async updateMachine(id, payload) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.put(
          `${API_BASE_URL}/machines/${id}`,
          payload,
          this.getAuthHeaders()
        )
        await this.fetchMachines()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al actualizar el equipo'
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteMachine(id) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(
          `${API_BASE_URL}/machines/${id}`,
          this.getAuthHeaders()
        )
        await this.fetchMachines()
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al eliminar el equipo'
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteParameter(paramId) {
      try {
        await axios.delete(
          `${API_BASE_URL}/machines/parameters/${paramId}`,
          this.getAuthHeaders()
        )
      } catch (err) {
        throw err
      }
    },
  },
})

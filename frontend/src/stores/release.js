import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8095/api/v1'

export const useReleaseStore = defineStore('release', {
  state: () => ({
    currentMachine: null,
    recentReleases: [],
    loading: false,
    error: null,
    lastSubmittedRelease: null,
  }),

  actions: {
    async fetchMachineByCode(code) {
      const authStore = useAuthStore()
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE_URL}/machines/code/${encodeURIComponent(code)}`, {
          headers: authStore.getAuthHeaders(),
        })
        this.currentMachine = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'No se pudo cargar la máquina especificada'
        this.currentMachine = null
        throw err
      } finally {
        this.loading = false
      }
    },

    async submitRelease(payload) {
      const authStore = useAuthStore()
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE_URL}/releases`, payload, {
          headers: authStore.getAuthHeaders(),
        })
        this.lastSubmittedRelease = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al guardar la liberación'
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchReleases(machineId = null) {
      const authStore = useAuthStore()
      this.loading = true
      try {
        let url = `${API_BASE_URL}/releases`
        if (machineId) {
          url += `?machine_id=${machineId}`
        }
        const response = await axios.get(url, {
          headers: authStore.getAuthHeaders(),
        })
        this.recentReleases = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al obtener historial'
      } finally {
        this.loading = false
      }
    },

    clearCurrentMachine() {
      this.currentMachine = null
    },
  },
})

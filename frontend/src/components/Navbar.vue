<template>
  <header class="bg-white border-b border-slate-200 text-slate-800 sticky top-0 z-50 shadow-xs">
    <div class="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-lg bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-700 font-bold text-lg shadow-xs">
          ⚙️
        </div>
        <div>
          <h1 class="text-sm font-extrabold text-slate-900 tracking-tight leading-none">Planta Control</h1>
          <span class="text-[10px] uppercase font-bold tracking-wider text-sky-700">Liberación de Operación</span>
        </div>
      </div>

      <div v-if="authStore.isAuthenticated" class="flex items-center gap-3">
        <router-link
          v-if="authStore.userRole === 'admin'"
          to="/admin/machines"
          class="px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 text-xs font-bold transition-all flex items-center gap-1 shadow-xs"
          active-class="!bg-amber-100 !text-amber-900 !border-amber-300"
        >
          <span>⚙️</span>
          <span class="hidden sm:inline">Equipos</span>
        </router-link>

        <div class="text-right hidden sm:block">
          <p class="text-xs font-bold text-slate-800">{{ authStore.user?.full_name }}</p>
          <span class="inline-block text-[10px] px-1.5 py-0.5 rounded font-extrabold uppercase" :class="roleBadgeClass">
            {{ authStore.userRole }}
          </span>
        </div>

        <button
          @click="handleLogout"
          class="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 border border-slate-200 transition-colors"
          title="Cerrar Sesión"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const roleBadgeClass = computed(() => {
  switch (authStore.userRole) {
    case 'admin': return 'bg-amber-100 text-amber-800 border border-amber-300'
    case 'supervisor': return 'bg-purple-100 text-purple-800 border border-purple-300'
    default: return 'bg-emerald-100 text-emerald-800 border border-emerald-300'
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

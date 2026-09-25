<template>
  <div class="min-h-screen bg-slate-100 text-slate-900 flex flex-col font-sans pb-28">
    <Navbar />

    <main class="flex-1">
      <router-view />
    </main>

    <!-- Bottom Mobile Quick Navigation Bar -->
    <nav
      v-if="authStore.isAuthenticated"
      class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-lg border-t border-slate-200 h-16 px-6 flex justify-around items-center shadow-[0_-4px_20px_rgba(0,0,0,0.06)]"
    >
      <router-link
        v-if="authStore.userRole === 'operador' || authStore.userRole === 'admin'"
        to="/scan"
        class="flex flex-col items-center gap-0.5 text-slate-500 hover:text-slate-800 font-semibold text-[11px] transition-colors py-1.5 px-4 rounded-xl"
        active-class="!text-sky-700 font-bold bg-sky-50 border border-sky-200 shadow-sm"
      >
        <span class="text-lg">📷</span>
        <span>Escanear QR</span>
      </router-link>

      <router-link
        v-if="authStore.userRole === 'supervisor' || authStore.userRole === 'admin'"
        to="/history"
        class="flex flex-col items-center gap-0.5 text-slate-500 hover:text-slate-800 font-semibold text-[11px] transition-colors py-1.5 px-4 rounded-xl"
        active-class="!text-sky-700 font-bold bg-sky-50 border border-sky-200 shadow-sm"
      >
        <span class="text-lg">📋</span>
        <span>Historial</span>
      </router-link>

      <router-link
        v-if="authStore.userRole === 'admin'"
        to="/admin/machines"
        class="flex flex-col items-center gap-0.5 text-slate-500 hover:text-slate-800 font-semibold text-[11px] transition-colors py-1.5 px-4 rounded-xl"
        active-class="!text-amber-800 font-bold bg-amber-50 border border-amber-300 shadow-sm"
      >
        <span class="text-lg">⚙️</span>
        <span>Equipos</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
</script>

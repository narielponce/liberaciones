<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans pb-28">
    <Navbar />

    <main class="flex-1">
      <router-view />
    </main>

    <!-- Bottom Mobile Quick Navigation Bar -->
    <nav
      v-if="authStore.isAuthenticated"
      class="fixed bottom-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-lg border-t border-slate-800 h-16 px-6 flex justify-around items-center shadow-2xl"
    >
      <router-link
        to="/scan"
        class="flex flex-col items-center gap-0.5 text-slate-400 font-semibold text-[11px] transition-colors py-1 px-4 rounded-xl"
        active-class="text-sky-400 font-bold bg-sky-500/10 border border-sky-500/20"
      >
        <span class="text-lg">📷</span>
        <span>Escanear QR</span>
      </router-link>

      <router-link
        to="/history"
        class="flex flex-col items-center gap-0.5 text-slate-400 font-semibold text-[11px] transition-colors py-1 px-4 rounded-xl"
        active-class="text-sky-400 font-bold bg-sky-500/10 border border-sky-500/20"
      >
        <span class="text-lg">📋</span>
        <span>Historial</span>
      </router-link>

      <router-link
        v-if="authStore.userRole === 'admin'"
        to="/admin/machines"
        class="flex flex-col items-center gap-0.5 text-slate-400 font-semibold text-[11px] transition-colors py-1 px-4 rounded-xl"
        active-class="text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20"
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

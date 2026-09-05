<template>
  <div class="min-h-[calc(100vh-60px)] flex flex-col justify-center px-4 py-8 max-w-md mx-auto w-full">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-sky-500/10 border border-sky-500/30 text-sky-400 text-2xl font-bold mb-1">
          🏭
        </div>
        <h2 class="text-xl font-bold text-white tracking-tight">Acceso a Planta</h2>
        <p class="text-xs text-slate-400">Ingrese sus credenciales de operario o administrador</p>
      </div>

      <div v-if="authStore.error" class="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-medium flex items-center gap-2">
        <span>⚠️</span>
        <span>{{ authStore.error }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider">Correo Electrónico</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="operador@planta.com"
            class="w-full h-12 px-4 rounded-xl bg-slate-950 border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-100 placeholder-slate-500 font-medium text-sm outline-none transition-all"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider">Contraseña</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full h-12 px-4 rounded-xl bg-slate-950 border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-slate-100 placeholder-slate-500 font-medium text-sm outline-none transition-all"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full btn-touch bg-sky-600 hover:bg-sky-500 text-white font-bold text-base shadow-lg shadow-sky-600/25 disabled:opacity-50 mt-2"
        >
          <span v-if="authStore.loading" class="animate-pulse">Ingresando...</span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>

      <!-- Quick Test Accounts Helper -->
      <div class="pt-4 border-t border-slate-800/80">
        <p class="text-[11px] font-semibold text-slate-400 mb-2 uppercase text-center tracking-wider">Accesos Rápidos de Prueba (MVP)</p>
        <div class="grid grid-cols-3 gap-2">
          <button
            @click="fillQuick('operador@planta.com', 'operador123')"
            class="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[11px] font-semibold hover:bg-emerald-500/20 transition-colors text-center"
          >
            👷 Operador
          </button>
          <button
            @click="fillQuick('admin@planta.com', 'admin123')"
            class="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-semibold hover:bg-amber-500/20 transition-colors text-center"
          >
            ⚙️ Admin
          </button>
          <button
            @click="fillQuick('supervisor@planta.com', 'supervisor123')"
            class="p-2 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300 text-[11px] font-semibold hover:bg-purple-500/20 transition-colors text-center"
          >
            📊 Supervisor
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')

const handleSubmit = async () => {
  const success = await authStore.login(email.value, password.value)
  if (success) {
    router.push('/scan')
  }
}

const fillQuick = (qEmail, qPass) => {
  email.value = qEmail
  password.value = qPass
}
</script>

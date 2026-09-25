<template>
  <div class="min-h-[calc(100vh-60px)] flex flex-col justify-center px-4 py-8 max-w-md mx-auto w-full">
    <div class="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-sky-50 border border-sky-200 text-sky-700 text-2xl font-bold mb-1 shadow-xs">
          🏭
        </div>
        <h2 class="text-xl font-black text-slate-900 tracking-tight">Acceso a Planta</h2>
        <p class="text-xs text-slate-500 font-medium">Ingrese sus credenciales de operario o administrador</p>
      </div>

      <div v-if="authStore.error" class="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
        <span>⚠️</span>
        <span>{{ authStore.error }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-700 uppercase tracking-wider">Correo Electrónico</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="operador@planta.com"
            class="w-full h-12 px-4 rounded-xl bg-white border border-slate-300 focus:border-sky-600 focus:ring-2 focus:ring-sky-600/20 text-slate-900 placeholder:text-slate-400 font-semibold text-sm outline-none transition-all shadow-xs"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-700 uppercase tracking-wider">Contraseña</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full h-12 px-4 rounded-xl bg-white border border-slate-300 focus:border-sky-600 focus:ring-2 focus:ring-sky-600/20 text-slate-900 placeholder:text-slate-400 font-semibold text-sm outline-none transition-all shadow-xs"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full btn-touch bg-sky-600 hover:bg-sky-700 text-white font-bold text-base shadow-md shadow-sky-600/20 disabled:opacity-50 mt-2 transition-all"
        >
          <span v-if="authStore.loading" class="animate-pulse">Ingresando...</span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>

      <!-- Quick Test Accounts Helper -->
      <div class="pt-4 border-t border-slate-200">
        <p class="text-[11px] font-bold text-slate-500 mb-2 uppercase text-center tracking-wider">Accesos Rápidos de Prueba (MVP)</p>
        <div class="grid grid-cols-3 gap-2">
          <button
            @click="fillQuick('operador@planta.com', 'operador123')"
            class="p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold hover:bg-emerald-100 transition-colors text-center shadow-xs"
          >
            👷 Operador
          </button>
          <button
            @click="fillQuick('admin@planta.com', 'admin123')"
            class="p-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-bold hover:bg-amber-100 transition-colors text-center shadow-xs"
          >
            ⚙️ Admin
          </button>
          <button
            @click="fillQuick('supervisor@planta.com', 'supervisor123')"
            class="p-2 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 text-[11px] font-bold hover:bg-purple-100 transition-colors text-center shadow-xs"
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
    if (authStore.userRole === 'supervisor') {
      router.push('/history')
    } else {
      router.push('/scan')
    }
  }
}

const fillQuick = (qEmail, qPass) => {
  email.value = qEmail
  password.value = qPass
}
</script>

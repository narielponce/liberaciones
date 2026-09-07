<template>
  <div class="max-w-md mx-auto px-4 py-6 pb-28 space-y-6">
    <!-- Error Alert -->
    <div v-if="error" class="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-semibold flex items-start gap-2.5 animate-shake">
      <span class="text-base">⚠️</span>
      <div>
        <p class="font-bold text-sm text-red-200">Error de Identificación</p>
        <p class="mt-0.5 opacity-90">{{ error }}</p>
      </div>
    </div>

    <!-- Scanner Options Cards -->
    <div class="space-y-4">
      <!-- Camera Scanner Toggle Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <button
          @click="toggleCamera"
          class="w-full btn-touch h-14 font-extrabold text-base rounded-xl transition-all shadow-lg flex items-center justify-center gap-2.5"
          :class="isCameraActive ? 'bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30' : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/30'"
        >
          <span class="text-xl">📷</span>
          <span>{{ isCameraActive ? 'Detener Cámara' : 'Escanear QR' }}</span>
        </button>

        <div v-show="isCameraActive" class="space-y-3 pt-2">
          <div id="qr-reader" class="overflow-hidden rounded-xl border border-sky-500/30 bg-slate-950"></div>
          <p class="text-[11px] text-slate-400 text-center">Apunte con la cámara al código QR de la máquina</p>
        </div>
      </div>

      <!-- Manual Code Entry Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 text-xl font-bold">
            ⌨️
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">Ingreso manual</h3>
            <p class="text-[11px] text-slate-400">Ingreso manual de clave alfanumérica</p>
          </div>
        </div>

        <form @submit.prevent="handleManualSubmit" class="space-y-3">
          <input
            v-model="machineCode"
            type="text"
            required
            placeholder="Ej: MACH-CNC-01"
            class="w-full h-14 px-4 rounded-xl bg-slate-950 border border-slate-800 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-white font-mono uppercase font-bold text-base outline-none tracking-wider transition-all placeholder:text-slate-600"
          />
          <button
            type="submit"
            :disabled="loading || !machineCode.trim()"
            class="w-full btn-touch bg-sky-600 hover:bg-sky-500 text-white font-bold text-base shadow-lg shadow-sky-600/20 disabled:opacity-40"
          >
            <span v-if="loading">Buscando máquina...</span>
            <span v-else>Cargar Formulario de Liberación ➔</span>
          </button>
        </form>
      </div>

      <!-- Demo Machines Quick Pick -->
      <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400 block text-center">
          Máquinas de Prueba en Planta
        </span>
        <div class="grid grid-cols-1 gap-2">
          <button
            @click="quickSelect('MACH-CNC-01')"
            class="p-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 text-left flex items-center justify-between transition-colors"
          >
            <div>
              <p class="text-xs font-bold text-white">MACH-CNC-01</p>
              <p class="text-[11px] text-slate-400">Torno CNC Haas ST-20 (Mecanizado)</p>
            </div>
            <span class="text-sky-400 text-xs font-bold bg-sky-500/10 px-2 py-1 rounded">Seleccionar ➔</span>
          </button>

          <button
            @click="quickSelect('MACH-INJ-02')"
            class="p-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 text-left flex items-center justify-between transition-colors"
          >
            <div>
              <p class="text-xs font-bold text-white">MACH-INJ-02</p>
              <p class="text-[11px] text-slate-400">Inyectora Engel Duo 500T (Plásticos)</p>
            </div>
            <span class="text-sky-400 text-xs font-bold bg-sky-500/10 px-2 py-1 rounded">Seleccionar ➔</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReleaseStore } from '../stores/release'
import { Html5Qrcode } from 'html5-qrcode'

const releaseStore = useReleaseStore()
const router = useRouter()

const machineCode = ref('')
const loading = ref(false)
const error = ref(null)
const isCameraActive = ref(false)

let html5QrCode = null

const processCode = async (code) => {
  if (!code) return
  loading.value = true
  error.value = null
  try {
    const cleanCode = code.trim().toUpperCase()
    await releaseStore.fetchMachineByCode(cleanCode)
    if (isCameraActive.value) {
      await stopCamera()
    }
    router.push({ name: 'release-form', params: { code: cleanCode } })
  } catch (err) {
    error.value = err.response?.data?.detail || `No existe la máquina con código '${code}'`
  } finally {
    loading.value = false
  }
}

const handleManualSubmit = () => {
  processCode(machineCode.value)
}

const quickSelect = (code) => {
  machineCode.value = code
  processCode(code)
}

const toggleCamera = async () => {
  if (isCameraActive.value) {
    await stopCamera()
  } else {
    await startCamera()
  }
}

const startCamera = async () => {
  isCameraActive.value = true
  error.value = null
  try {
    html5QrCode = new Html5Qrcode('qr-reader')
    await html5QrCode.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 250, height: 250 } },
      (decodedText) => {
        machineCode.value = decodedText
        processCode(decodedText)
      },
      () => {}
    )
  } catch (err) {
    error.value = 'No se pudo acceder a la cámara del dispositivo.'
    isCameraActive.value = false
  }
}

const stopCamera = async () => {
  if (html5QrCode && html5QrCode.isScanning) {
    await html5QrCode.stop()
    html5QrCode.clear()
  }
  isCameraActive.value = false
}

onUnmounted(() => {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().catch(() => {})
  }
})
</script>

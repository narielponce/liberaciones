<template>
  <div class="max-w-xl mx-auto px-4 py-6 pb-28 space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16 space-y-3">
      <div class="inline-block w-10 h-10 border-4 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-sm font-semibold text-slate-600">Cargando parámetros de la máquina...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="fetchError" class="bg-red-50 border border-red-200 rounded-2xl p-6 text-center space-y-4 shadow-sm">
      <span class="text-3xl">⚠️</span>
      <h3 class="text-lg font-black text-red-900">Error de Carga</h3>
      <p class="text-xs text-red-700 font-medium">{{ fetchError }}</p>
      <button @click="router.push('/scan')" class="btn-touch px-6 bg-slate-800 hover:bg-slate-900 text-white text-sm font-bold shadow-sm">
        Volver a Escanear
      </button>
    </div>

    <!-- Main Dynamic Form Wizard -->
    <div v-else-if="machine" class="space-y-5">
      <!-- Machine Header Card -->
      <div class="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <button
            @click="router.push('/scan')"
            class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1 font-bold transition-colors"
          >
            ← Cambiar Máquina
          </button>
          <span class="text-[10px] font-mono font-extrabold uppercase tracking-widest text-sky-800 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-md">
            {{ machine.code }}
          </span>
        </div>

        <div>
          <h2 class="text-lg font-black text-slate-900 tracking-tight">{{ machine.name }}</h2>
          <p class="text-xs text-slate-500 font-medium">Sección: <span class="text-slate-800 font-bold">{{ machine.section }}</span></p>
        </div>

        <!-- Global Tolerance Real-Time Status Banner -->
        <div
          class="p-2.5 rounded-xl flex items-center justify-between text-xs font-bold transition-all"
          :class="hasAnyOutOfRange ? 'bg-red-50 border border-red-200 text-red-800' : 'bg-emerald-50 border border-emerald-200 text-emerald-800'"
        >
          <div class="flex items-center gap-2">
            <span>{{ hasAnyOutOfRange ? '🚨' : '✅' }}</span>
            <span class="text-[11px] font-extrabold">{{ hasAnyOutOfRange ? 'Parámetros con Desvío (NOk)' : 'Parámetros en Tolerancia (OK)' }}</span>
          </div>
          <span class="px-2 py-0.5 rounded text-[9px] uppercase font-black" :class="hasAnyOutOfRange ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'">
            {{ hasAnyOutOfRange ? 'RECHAZADO' : 'APROBABLE' }}
          </span>
        </div>
      </div>

      <!-- Step Progress Header -->
      <div class="bg-white border border-slate-200 rounded-2xl p-4 space-y-2 shadow-sm">
        <div class="flex items-center justify-between text-xs font-bold">
          <span class="text-sky-800 uppercase tracking-wider font-extrabold">
            Medición {{ currentStep }} de {{ totalSteps }}
          </span>
          <span class="text-slate-500 font-mono text-[11px]">
            {{ Math.round((currentStep / totalSteps) * 100) }}%
          </span>
        </div>

        <!-- Progress Bar Track -->
        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden border border-slate-200">
          <div
            class="bg-gradient-to-r from-sky-600 to-emerald-600 h-full transition-all duration-300 rounded-full"
            :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Step Checklist Parameters (1 per page) -->
      <form @submit.prevent="handleSubmitRelease" class="space-y-4">
        <div class="space-y-4">
          <div
            v-for="param in visibleParameters"
            :key="param.id"
            class="bg-white border rounded-2xl p-5 transition-all space-y-3.5 shadow-sm"
            :class="isParamOutOfRange(param) ? 'border-red-400 bg-red-50/60 out-of-range-pulse' : 'border-slate-200'"
          >
            <!-- Parameter Label Header -->
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="text-sm font-black text-slate-900 leading-snug">{{ param.label }}</h3>
              </div>

              <!-- Out-Of-Range Status Badge & Compact Note Icon -->
              <div class="flex items-center gap-1.5 shrink-0">
                <span
                  v-if="isParamOutOfRange(param)"
                  class="inline-block text-[10px] font-black uppercase px-2 py-0.5 rounded bg-red-600 text-white tracking-wider animate-bounce shadow-xs"
                >
                  FUERA DE RANGO
                </span>

                <!-- Compact Icon Button for Modal -->
                <button
                  v-if="isParamOutOfRange(param)"
                  type="button"
                  @click="openNoteModal(param)"
                  title="Agregar o ver observación"
                  class="text-[11px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 transition-all border shadow-xs"
                  :class="formValues[param.id]?.notes
                    ? 'bg-amber-500 text-white border-amber-600 font-extrabold shadow-amber-500/20'
                    : 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300'"
                >
                  <span>💬</span>
                  <span>{{ formValues[param.id]?.notes ? 'Obs.' : '+Obs' }}</span>
                </button>
              </div>
            </div>

            <!-- BOOLEAN Parameter Component (Large Ok / NOk Touch Buttons) -->
            <div v-if="param.param_type === 'BOOLEAN'" class="grid grid-cols-2 gap-3 pt-1">
              <button
                type="button"
                @click="formValues[param.id].bool_value = true"
                class="btn-touch border font-extrabold text-base transition-all"
                :class="formValues[param.id].bool_value === true
                  ? 'bg-emerald-600 border-emerald-600 text-white shadow-md shadow-emerald-600/30 ring-2 ring-emerald-500/40'
                  : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50 shadow-xs'"
              >
                ✓ OK (Conforme)
              </button>

              <button
                type="button"
                @click="formValues[param.id].bool_value = false"
                class="btn-touch border font-extrabold text-base transition-all"
                :class="formValues[param.id].bool_value === false
                  ? 'bg-red-600 border-red-600 text-white shadow-md shadow-red-600/30 ring-2 ring-red-500/40'
                  : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50 shadow-xs'"
              >
                ✕ NOk (Falla)
              </button>
            </div>

            <!-- NUMERIC Parameter Component (Keypad input + Range guidelines) -->
            <div v-else-if="param.param_type === 'NUMERIC'" class="space-y-2 pt-1">
              <!-- Tolerance Range Guidelines -->
              <div class="flex items-center justify-between text-xs font-semibold text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
                <span>Rango mediciones:</span>
                <span class="text-sky-800 font-mono font-bold">
                  <template v-if="param.min_value !== null">{{ param.min_value }}</template>
                  <template v-else>-∞</template>
                  a
                  <template v-if="param.max_value !== null">{{ param.max_value }}</template>
                  <template v-else>+∞</template>
                  {{ param.unit || '' }}
                </span>
              </div>

              <!-- Keypad Number Input Field -->
              <div class="relative">
                <input
                  v-model.number="formValues[param.id].numeric_value"
                  type="number"
                  step="any"
                  required
                  placeholder="Ingrese medición"
                  class="w-full h-14 pl-4 pr-16 rounded-xl border font-mono font-bold text-lg outline-none transition-all shadow-xs"
                  :class="isParamOutOfRange(param)
                    ? 'border-red-400 text-red-900 bg-red-50/50 focus:ring-2 focus:ring-red-500'
                    : 'border-slate-300 bg-white text-slate-900 focus:border-sky-600 focus:ring-2 focus:ring-sky-600/20'"
                />
                <span v-if="param.unit" class="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-slate-500">
                  {{ param.unit }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons Controls -->
        <div class="flex items-center gap-3 pt-2">
          <!-- Back Button -->
          <button
            v-if="currentStep > 1"
            type="button"
            @click="prevStep"
            class="btn-touch px-5 bg-white hover:bg-slate-50 text-slate-700 font-bold text-sm border border-slate-300 flex items-center justify-center gap-1 shrink-0 shadow-xs transition-colors"
          >
            ← Anterior
          </button>

          <!-- Next Step Button (Shown if not on last step) -->
          <button
            v-if="currentStep < totalSteps"
            type="button"
            @click="nextStep"
            :disabled="!isCurrentStepComplete"
            class="btn-touch flex-1 bg-sky-600 hover:bg-sky-700 text-white font-extrabold text-base shadow-md shadow-sky-600/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2"
          >
            <span>Siguiente</span>
            <span>➔</span>
          </button>

          <!-- Final Submit Button (ONLY SHOWN ON LAST STEP WHEN ALL PARAMETERS COMPLETE) -->
          <button
            v-if="currentStep === totalSteps"
            type="submit"
            :disabled="submitting || !isFormComplete"
            class="btn-touch flex-1 text-white font-extrabold text-base shadow-lg transition-all disabled:opacity-40"
            :class="hasAnyOutOfRange ? 'bg-red-600 hover:bg-red-700 shadow-red-600/25' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-600/25'"
          >
            <span v-if="submitting" class="animate-pulse">Registrando Liberación...</span>
            <span v-else>
              {{ hasAnyOutOfRange ? '⚠️ Registrar Liberación (RECHAZO)' : '✓ Finalizar Liberación Conforme (OK)' }}
            </span>
          </button>
        </div>
      </form>
    </div>

    <!-- Parameter Specific Observation Modal -->
    <div v-if="activeNoteParam" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white border border-slate-200 rounded-3xl p-5 max-w-sm w-full space-y-4 shadow-2xl text-slate-900">
        <div class="flex items-center justify-between border-b border-slate-200 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">📝</span>
            <div>
              <h4 class="text-sm font-black text-slate-900">Observación del Parámetro</h4>
              <p class="text-[11px] text-amber-800 font-bold truncate max-w-[200px]">{{ activeNoteParam.label }}</p>
            </div>
          </div>
          <button @click="closeNoteModal" class="text-slate-400 hover:text-slate-700 text-lg font-bold">✕</button>
        </div>

        <div class="space-y-2">
          <label class="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">Detalle o causa de la desviación</label>
          <textarea
            v-model="tempNoteText"
            rows="3"
            placeholder="Ingrese el motivo de la falla o lectura fuera de tolerancia..."
            class="w-full p-3 rounded-xl bg-white border border-slate-300 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 text-slate-900 placeholder:text-slate-400 text-xs font-medium outline-none transition-all shadow-xs"
          ></textarea>
        </div>

        <div class="flex items-center gap-2 pt-1">
          <button
            type="button"
            @click="closeNoteModal"
            class="btn-touch flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-200 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            @click="saveNoteModal"
            class="btn-touch flex-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-md shadow-amber-600/20 transition-all"
          >
            Guardar Observación
          </button>
        </div>
      </div>
    </div>

    <!-- Result Confirmation Modal -->
    <div v-if="submittedResult" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white border border-slate-200 rounded-3xl p-6 max-w-sm w-full space-y-5 text-center shadow-2xl">
        <div
          class="w-20 h-20 mx-auto rounded-full flex items-center justify-center shadow-lg transition-all"
          :class="submittedResult.status === 'OK' ? 'bg-emerald-600 text-white border-4 border-emerald-200 ring-4 ring-emerald-50' : 'bg-red-600 text-white border-4 border-red-200 ring-4 ring-red-50'"
        >
          <!-- White Checkmark Icon for OK -->
          <svg v-if="submittedResult.status === 'OK'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" class="w-10 h-10">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
          </svg>
          <!-- White Cross Icon for RECHAZADA -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" class="w-10 h-10">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </div>

        <div>
          <span class="text-xs uppercase font-black tracking-widest text-slate-500 block mb-1">Resultado de Inspección</span>
          <h3 class="text-2xl font-black" :class="submittedResult.status === 'OK' ? 'text-emerald-700' : 'text-red-700'">
            LIBERACIÓN {{ submittedResult.status === 'OK' ? 'APROBADA (OK)' : 'RECHAZADA' }}
          </h3>
          <p class="text-xs text-slate-600 mt-2 font-medium">
            La operación ha sido registrada en el sistema a las
            <span class="font-bold text-slate-900">{{ new Date(submittedResult.timestamp).toLocaleTimeString() }}</span>.
          </p>
        </div>

        <div class="pt-2">
          <button
            @click="finishAndScanNew"
            class="w-full btn-touch bg-sky-600 hover:bg-sky-700 text-white font-bold text-base shadow-md shadow-sky-600/20 transition-all"
          >
            Siguiente Liberación ➔
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReleaseStore } from '../stores/release'

const route = useRoute()
const router = useRouter()
const releaseStore = useReleaseStore()

const machine = ref(null)
const loading = ref(true)
const submitting = ref(false)
const fetchError = ref(null)

const PAGE_SIZE = 1
const currentStep = ref(1)

const formValues = reactive({})
const submittedResult = ref(null)

// Modal state for parameter observation
const activeNoteParam = ref(null)
const tempNoteText = ref('')

const loadMachineData = async () => {
  loading.value = true
  fetchError.value = null
  try {
    const code = route.params.code
    const data = await releaseStore.fetchMachineByCode(code)
    machine.value = data
    currentStep.value = 1

    // Initialize form values map for each parameter
    data.parameters.forEach((param) => {
      formValues[param.id] = {
        parameter_id: param.id,
        bool_value: param.param_type === 'BOOLEAN' ? true : null, // default Ok for booleans
        numeric_value: null,
        notes: '',
      }
    })
  } catch (err) {
    fetchError.value = err.response?.data?.detail || 'No se pudieron recuperar los parámetros de la máquina.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMachineData()
})

// Modal actions
const openNoteModal = (param) => {
  activeNoteParam.value = param
  tempNoteText.value = formValues[param.id]?.notes || ''
}

const closeNoteModal = () => {
  activeNoteParam.value = null
  tempNoteText.value = ''
}

const saveNoteModal = () => {
  if (activeNoteParam.value) {
    formValues[activeNoteParam.value.id].notes = tempNoteText.value.trim()
  }
  closeNoteModal()
}

// Wizard Pagination Computeds
const totalSteps = computed(() => {
  if (!machine.value || !machine.value.parameters) return 1
  return Math.ceil(machine.value.parameters.length / PAGE_SIZE)
})

const visibleParameters = computed(() => {
  if (!machine.value || !machine.value.parameters) return []
  const start = (currentStep.value - 1) * PAGE_SIZE
  return machine.value.parameters.slice(start, start + PAGE_SIZE)
})

const getParamIndex = (param) => {
  if (!machine.value || !machine.value.parameters) return 0
  return machine.value.parameters.findIndex((p) => p.id === param.id)
}

// Helper to check if a specific parameter is currently out of range / NOk
const isParamOutOfRange = (param) => {
  const val = formValues[param.id]
  if (!val) return false

  if (param.param_type === 'BOOLEAN') {
    return val.bool_value === false
  } else if (param.param_type === 'NUMERIC') {
    const num = val.numeric_value
    if (num === null || num === undefined || num === '') return false
    if (param.min_value !== null && num < param.min_value) return true
    if (param.max_value !== null && num > param.max_value) return true
  }
  return false
}

// Check if any parameter overall is out of range
const hasAnyOutOfRange = computed(() => {
  if (!machine.value) return false
  return machine.value.parameters.some((p) => isParamOutOfRange(p))
})

// Check if parameters in CURRENT step are filled
const isCurrentStepComplete = computed(() => {
  if (!visibleParameters.value.length) return false
  return visibleParameters.value.every((p) => {
    if (!p.is_required) return true
    const val = formValues[p.id]
    if (!val) return false
    if (p.param_type === 'BOOLEAN') return val.bool_value !== null && val.bool_value !== undefined
    if (p.param_type === 'NUMERIC') return val.numeric_value !== null && val.numeric_value !== '' && !isNaN(val.numeric_value)
    return false
  })
})

// Check if ALL required parameters across the whole form are answered
const isFormComplete = computed(() => {
  if (!machine.value) return false
  return machine.value.parameters.every((p) => {
    if (!p.is_required) return true
    const val = formValues[p.id]
    if (!val) return false
    if (p.param_type === 'BOOLEAN') return val.bool_value !== null && val.bool_value !== undefined
    if (p.param_type === 'NUMERIC') return val.numeric_value !== null && val.numeric_value !== '' && !isNaN(val.numeric_value)
    return false
  })
})

// Step navigation
const nextStep = () => {
  if (isCurrentStepComplete.value && currentStep.value < totalSteps.value) {
    currentStep.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handleSubmitRelease = async () => {
  if (!isFormComplete.value) return
  submitting.value = true
  try {
    const valuesArray = Object.values(formValues).map((v) => ({
      parameter_id: v.parameter_id,
      bool_value: v.bool_value,
      numeric_value: v.numeric_value !== null && v.numeric_value !== '' ? Number(v.numeric_value) : null,
      notes: v.notes || null,
    }))

    const payload = {
      machine_id: machine.value.id,
      notes: null,
      values: valuesArray,
    }

    const result = await releaseStore.submitRelease(payload)
    submittedResult.value = result
  } catch (err) {
    alert(err.response?.data?.detail || 'Error al registrar la liberación.')
  } finally {
    submitting.value = false
  }
}

const finishAndScanNew = () => {
  submittedResult.value = null
  router.push('/scan')
}
</script>

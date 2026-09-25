<template>
  <div class="max-w-6xl mx-auto px-4 py-6 pb-28 space-y-6">
    <!-- Header Title & Refresh -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="text-2xl">📋</span>
          <h2 class="text-xl font-black text-slate-900 tracking-tight">Historial y Auditoría de Liberaciones</h2>
        </div>
        <p class="text-xs text-slate-500 font-medium">
          Módulo de Supervisión — Trazabilidad, control de calidad y registro de mediciones en piso de planta.
        </p>
      </div>

      <button
        @click="loadHistory"
        :disabled="releaseStore.loading"
        class="btn-touch px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-xs"
      >
        <span :class="{ 'animate-spin': releaseStore.loading }">🔄</span>
        <span>Actualizar Datos</span>
      </button>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white border border-slate-200 rounded-xl p-4 space-y-1 shadow-sm">
        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Total Evaluaciones</span>
        <span class="text-2xl font-black text-slate-900 font-mono">{{ releaseStore.recentReleases.length }}</span>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-4 space-y-1 shadow-sm">
        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Conformes (OK)</span>
        <span class="text-2xl font-black text-emerald-700 font-mono">{{ okReleasesCount }}</span>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-4 space-y-1 shadow-sm">
        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Rechazadas (NOk)</span>
        <span class="text-2xl font-black text-red-700 font-mono">{{ rejectedReleasesCount }}</span>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-4 space-y-1 shadow-sm">
        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Tasa de Conformidad</span>
        <span class="text-2xl font-black text-sky-800 font-mono">{{ conformityRate }}%</span>
      </div>
    </div>

    <!-- Filters & Search Toolbar -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-sm">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Search bar across basic columns -->
        <div class="relative lg:col-span-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por ID, máquina, operador o notas..."
            class="w-full h-10 pl-9 pr-3 rounded-lg bg-white border border-slate-300 text-xs font-semibold text-slate-900 placeholder:text-slate-400 focus:border-sky-600 focus:ring-1 focus:ring-sky-600 outline-none transition-all shadow-2xs"
          />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">🔍</span>
        </div>

        <!-- Filter by Status -->
        <div>
          <select
            v-model="statusFilter"
            class="w-full h-10 px-3 rounded-lg bg-white border border-slate-300 text-xs font-bold text-slate-700 focus:border-sky-600 outline-none shadow-2xs"
          >
            <option value="">Todos los Estados</option>
            <option value="OK">Solo Conformes (OK)</option>
            <option value="REJECTED">Solo Rechazados (REJECTED)</option>
          </select>
        </div>

        <!-- Filter by Machine -->
        <div>
          <select
            v-model="machineFilter"
            class="w-full h-10 px-3 rounded-lg bg-white border border-slate-300 text-xs font-bold text-slate-700 focus:border-sky-600 outline-none shadow-2xs"
          >
            <option value="">Todas las Máquinas</option>
            <option v-for="m in machineOptions" :key="m.code" :value="m.code">
              {{ m.code }} - {{ m.name }}
            </option>
          </select>
        </div>

        <!-- Filter by Operator -->
        <div>
          <select
            v-model="operatorFilter"
            class="w-full h-10 px-3 rounded-lg bg-white border border-slate-300 text-xs font-bold text-slate-700 focus:border-sky-600 outline-none shadow-2xs"
          >
            <option value="">Todos los Operadores</option>
            <option v-for="op in operatorOptions" :key="op" :value="op">
              {{ op }}
            </option>
          </select>
        </div>
      </div>

      <!-- Active filters summary & Clear button -->
      <div v-if="hasActiveFilters" class="flex items-center justify-between pt-2 border-t border-slate-200 text-xs">
        <span class="text-slate-500">
          Mostrando <strong class="text-slate-900">{{ filteredReleases.length }}</strong> de <strong class="text-slate-900">{{ releaseStore.recentReleases.length }}</strong> registros
        </span>
        <button
          @click="clearFilters"
          class="text-sky-700 hover:text-sky-900 text-xs font-bold flex items-center gap-1 transition-colors"
        >
          <span>✕</span>
          <span>Limpiar Filtros</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="releaseStore.loading" class="text-center py-16">
      <div class="inline-block w-9 h-9 border-4 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-xs font-semibold text-slate-500 mt-2">Cargando registros de auditoría...</p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredReleases.length === 0"
      class="bg-white border border-slate-200 rounded-2xl p-12 text-center space-y-3 shadow-sm"
    >
      <span class="text-4xl">📋</span>
      <h3 class="text-base font-black text-slate-900">No se encontraron liberaciones</h3>
      <p class="text-xs text-slate-500 max-w-sm mx-auto font-medium">
        {{ releaseStore.recentReleases.length === 0 ? 'No hay liberaciones registradas en el sistema aún.' : 'No existen registros que coincidan con los filtros y búsqueda aplicados.' }}
      </p>
      <button
        v-if="hasActiveFilters"
        @click="clearFilters"
        class="btn-touch px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold rounded-xl shadow-xs"
      >
        Limpiar Filtros
      </button>
    </div>

    <!-- Table View -->
    <div v-else class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-[11px] font-extrabold text-slate-600 uppercase tracking-wider">
              <th class="py-2.5 px-3">ID</th>
              <th class="py-2.5 px-3">Fecha y Hora</th>
              <th class="py-2.5 px-3">Equipo / Máquina</th>
              <th class="py-2.5 px-3">Operador</th>
              <th class="py-2.5 px-3 text-center">Estado</th>
              <th class="py-2.5 px-3">Mediciones</th>
              <th class="py-2.5 px-3 text-center w-12">Detalle</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 font-medium">
            <tr
              v-for="rel in filteredReleases"
              :key="rel.id"
              class="hover:bg-slate-50/80 transition-colors"
            >
              <!-- ID -->
              <td class="py-2.5 px-3 font-mono font-black text-sky-800 whitespace-nowrap">
                #{{ rel.id }}
              </td>

              <!-- Date & Time in single line -->
              <td class="py-2.5 px-3 whitespace-nowrap">
                <span class="font-bold text-slate-800">{{ formatDate(rel.timestamp) }}</span>
                <span class="text-[11px] text-slate-500 font-mono ml-1.5">{{ formatTime(rel.timestamp) }} hs</span>
              </td>

              <!-- Machine Information (single line) -->
              <td class="py-2.5 px-3 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <span class="text-[10px] font-mono font-extrabold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-300">
                    {{ rel.machine?.code || `ID ${rel.machine_id}` }}
                  </span>
                  <span class="font-bold text-slate-900 truncate max-w-[200px]" :title="rel.machine ? `${rel.machine.name} (${rel.machine.section || ''})` : ''">
                    {{ rel.machine?.name || 'Equipo no especificado' }}
                  </span>
                </div>
              </td>

              <!-- Operator (single line) -->
              <td class="py-2.5 px-3 whitespace-nowrap">
                <span class="font-semibold text-slate-700" :title="rel.operator?.email || ''">
                  {{ rel.operator?.full_name || 'Desconocido' }}
                </span>
              </td>

              <!-- Status Badge -->
              <td class="py-2.5 px-3 text-center whitespace-nowrap">
                <span
                  class="inline-block text-[10px] font-black uppercase px-2 py-0.5 rounded border shadow-2xs"
                  :class="rel.status === 'OK'
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                    : 'bg-red-50 text-red-800 border-red-300'"
                >
                  {{ rel.status === 'OK' ? '✓ OK' : '🚨 RECHAZADO' }}
                </span>
              </td>

              <!-- Measurement Summary -->
              <td class="py-2.5 px-3 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <span class="font-mono text-slate-600 text-xs font-bold">
                    {{ rel.values?.length || 0 }} params
                  </span>
                  <span
                    v-if="countOutOfRange(rel) > 0"
                    class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-50 text-red-800 border border-red-300"
                    title="Cantidad de parámetros fuera de rango"
                  >
                    {{ countOutOfRange(rel) }} desvío(s)
                  </span>
                  <span
                    v-else
                    class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-300"
                  >
                    100% OK
                  </span>
                </div>
              </td>

              <!-- Action Button: Details Icon -->
              <td class="py-2.5 px-3 text-center whitespace-nowrap">
                <button
                  @click="openDetailsModal(rel)"
                  title="Ver detalles de mediciones"
                  class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-sky-50 text-slate-600 hover:text-sky-700 border border-slate-200 hover:border-sky-300 flex items-center justify-center transition-all mx-auto shadow-2xs"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3.5 h-3.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Measurement Details Modal -->
    <div
      v-if="selectedRelease"
      class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
    >
      <div
        class="bg-white border border-slate-200 rounded-3xl p-5 sm:p-6 max-w-2xl w-full my-auto space-y-5 shadow-2xl max-h-[92vh] flex flex-col text-slate-900"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-slate-200 pb-4 shrink-0">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold border"
              :class="selectedRelease.status === 'OK' ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'bg-red-50 border-red-300 text-red-700'"
            >
              {{ selectedRelease.status === 'OK' ? '✓' : '🚨' }}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-black text-slate-900">
                  Liberación #{{ selectedRelease.id }}
                </h3>
                <span
                  class="text-[10px] font-black uppercase px-2 py-0.5 rounded border"
                  :class="selectedRelease.status === 'OK' ? 'bg-emerald-50 text-emerald-800 border-emerald-300' : 'bg-red-50 text-red-800 border-red-300'"
                >
                  {{ selectedRelease.status === 'OK' ? 'APROBADA (OK)' : 'RECHAZADA' }}
                </span>
              </div>
              <p class="text-[11px] text-slate-500 font-medium">
                Registrado el {{ formatDate(selectedRelease.timestamp) }} a las {{ formatTime(selectedRelease.timestamp) }} hs
              </p>
            </div>
          </div>

          <button
            @click="closeDetailsModal"
            class="text-slate-400 hover:text-slate-700 text-xl font-bold p-1"
          >
            ✕
          </button>
        </div>

        <!-- Release Summary Header Card -->
        <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs shrink-0">
          <div>
            <span class="text-[10px] text-slate-500 font-bold uppercase block">Equipo / Máquina:</span>
            <span class="font-mono font-black text-slate-900 truncate block">
              {{ selectedRelease.machine?.code || `ID ${selectedRelease.machine_id}` }}
            </span>
            <span class="text-[11px] text-slate-700 truncate block font-medium">
              {{ selectedRelease.machine?.name || '—' }}
            </span>
          </div>

          <div>
            <span class="text-[10px] text-slate-500 font-bold uppercase block">Operador Firmante:</span>
            <span class="font-bold text-slate-900 block">
              {{ selectedRelease.operator?.full_name || 'Desconocido' }}
            </span>
            <span class="text-[10px] text-slate-500 font-mono block">
              {{ selectedRelease.operator?.email || '' }}
            </span>
          </div>

          <div class="col-span-2 sm:col-span-1">
            <span class="text-[10px] text-slate-500 font-bold uppercase block">Sección / Ubicación:</span>
            <span class="text-slate-700 font-semibold block">
              {{ selectedRelease.machine?.section || 'No especificada' }}
            </span>
            <span v-if="selectedRelease.machine?.plant" class="text-[10px] text-sky-800 font-bold block">
              Planta: {{ selectedRelease.machine.plant }}
            </span>
          </div>
        </div>

        <!-- General Release Notes (if any) -->
        <div v-if="selectedRelease.notes" class="bg-amber-50/70 border border-amber-200 rounded-xl p-3 text-xs italic text-amber-900 shrink-0">
          <span class="text-[10px] font-bold text-amber-800 uppercase tracking-wider block not-italic mb-0.5">Observación General de Turno:</span>
          "{{ selectedRelease.notes }}"
        </div>

        <!-- Detailed Measurements Table -->
        <div class="space-y-2 overflow-y-auto flex-1 pr-1">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="font-bold uppercase tracking-wider text-slate-500 text-[11px]">
              Detalle de Parámetros e Inspecciones ({{ selectedRelease.values?.length || 0 }})
            </span>
            <span class="text-[11px] font-mono text-slate-500">
              Desvíos detectados: <strong class="text-red-600 font-bold">{{ countOutOfRange(selectedRelease) }}</strong>
            </span>
          </div>

          <div class="space-y-2">
            <div
              v-for="(val, idx) in selectedRelease.values"
              :key="val.id"
              class="rounded-xl border p-3.5 space-y-2 transition-all text-xs"
              :class="val.is_out_of_range
                ? 'bg-red-50/70 border-red-300 text-red-900'
                : 'bg-white border-slate-200 text-slate-800'"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="space-y-0.5">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[10px] font-mono font-bold text-slate-400">#{{ idx + 1 }}</span>
                    <h4 class="font-black text-slate-900 text-sm">
                      {{ val.parameter?.label || `Parámetro ID ${val.parameter_id}` }}
                    </h4>
                  </div>

                  <!-- Tolerance Specifications -->
                  <p class="text-[11px] text-slate-500 font-medium">
                    <span class="text-slate-600 font-semibold uppercase text-[10px]">Tolerancia:</span>
                    <template v-if="val.parameter?.param_type === 'NUMERIC'">
                      <span class="font-mono text-sky-800 font-bold ml-1">
                        {{ val.parameter.min_value !== null ? val.parameter.min_value : '-∞' }} a {{ val.parameter.max_value !== null ? val.parameter.max_value : '+∞' }} {{ val.parameter.unit || '' }}
                      </span>
                    </template>
                    <template v-else>
                      <span class="text-emerald-700 ml-1 font-bold">Checklist Conforme (OK)</span>
                    </template>
                  </p>
                </div>

                <!-- Status Badge -->
                <div class="text-right shrink-0">
                  <span
                    class="inline-block text-[10px] font-black uppercase px-2 py-0.5 rounded border"
                    :class="val.is_out_of_range
                      ? 'bg-red-600 text-white border-red-500 font-extrabold shadow-2xs'
                      : 'bg-emerald-50 text-emerald-800 border-emerald-300'"
                  >
                    {{ val.is_out_of_range ? '🚨 FUERA DE RANGO' : '✓ CONFORME' }}
                  </span>
                </div>
              </div>

              <!-- Measurement Value Display -->
              <div class="flex items-center justify-between pt-1 border-t border-slate-200 text-xs">
                <span class="text-slate-500 font-medium">Valor Registrado:</span>
                <span class="font-mono font-black text-sm" :class="val.is_out_of_range ? 'text-red-700' : 'text-emerald-700'">
                  <template v-if="val.bool_value !== null">
                    {{ val.bool_value ? '✓ Conforme (OK)' : '✕ No Conforme (Falla)' }}
                  </template>
                  <template v-else-if="val.numeric_value !== null">
                    {{ val.numeric_value }} {{ val.parameter?.unit || '' }}
                  </template>
                  <template v-else>
                    Sin registro
                  </template>
                </span>
              </div>

              <!-- Specific Observation Note -->
              <div
                v-if="val.notes"
                class="bg-amber-50 border border-amber-200 rounded-lg p-2 text-xs text-amber-900 flex items-start gap-1.5 mt-1"
              >
                <span class="text-sm shrink-0">💬</span>
                <div>
                  <strong class="text-[10px] uppercase tracking-wider block text-amber-800">Observación de Desviación:</strong>
                  <span>{{ val.notes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="pt-3 border-t border-slate-200 shrink-0">
          <button
            @click="closeDetailsModal"
            class="w-full btn-touch bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-200 transition-colors"
          >
            Cerrar Detalle
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReleaseStore } from '../stores/release'

const releaseStore = useReleaseStore()

// Filter states
const searchQuery = ref('')
const statusFilter = ref('')
const machineFilter = ref('')
const operatorFilter = ref('')

// Details Modal state
const selectedRelease = ref(null)

const loadHistory = () => {
  releaseStore.fetchReleases()
}

onMounted(() => {
  loadHistory()
})

// Quick Stats computeds
const okReleasesCount = computed(() => {
  return releaseStore.recentReleases.filter((r) => r.status === 'OK').length
})

const rejectedReleasesCount = computed(() => {
  return releaseStore.recentReleases.filter((r) => r.status === 'REJECTED').length
})

const conformityRate = computed(() => {
  const total = releaseStore.recentReleases.length
  if (total === 0) return 0
  return ((okReleasesCount.value / total) * 100).toFixed(1)
})

// Machine filter options (derived from loaded releases)
const machineOptions = computed(() => {
  const map = new Map()
  releaseStore.recentReleases.forEach((r) => {
    if (r.machine) {
      map.set(r.machine.code, { code: r.machine.code, name: r.machine.name })
    } else if (r.machine_id) {
      map.set(`ID-${r.machine_id}`, { code: `ID-${r.machine_id}`, name: `Máquina ID ${r.machine_id}` })
    }
  })
  return Array.from(map.values())
})

// Operator filter options
const operatorOptions = computed(() => {
  const set = new Set()
  releaseStore.recentReleases.forEach((r) => {
    if (r.operator?.full_name) {
      set.add(r.operator.full_name)
    }
  })
  return Array.from(set).sort()
})

// Check if any filter is active
const hasActiveFilters = computed(() => {
  return (
    searchQuery.value.trim() !== '' ||
    statusFilter.value !== '' ||
    machineFilter.value !== '' ||
    operatorFilter.value !== ''
  )
})

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  machineFilter.value = ''
  operatorFilter.value = ''
}

// Filtered Releases
const filteredReleases = computed(() => {
  let list = releaseStore.recentReleases

  // 1. Status Filter
  if (statusFilter.value) {
    list = list.filter((r) => r.status === statusFilter.value)
  }

  // 2. Machine Filter
  if (machineFilter.value) {
    list = list.filter(
      (r) =>
        r.machine?.code === machineFilter.value ||
        `ID-${r.machine_id}` === machineFilter.value
    )
  }

  // 3. Operator Filter
  if (operatorFilter.value) {
    list = list.filter((r) => r.operator?.full_name === operatorFilter.value)
  }

  // 4. Text Search Query across basic columns (ID, Machine Code, Machine Name, Operator, Notes)
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((r) => {
      const matchId = r.id.toString().includes(q) || `#${r.id}`.includes(q)
      const matchMachineCode = r.machine?.code?.toLowerCase().includes(q) || false
      const matchMachineName = r.machine?.name?.toLowerCase().includes(q) || false
      const matchSection = r.machine?.section?.toLowerCase().includes(q) || false
      const matchOperator = r.operator?.full_name?.toLowerCase().includes(q) || false
      const matchOperatorEmail = r.operator?.email?.toLowerCase().includes(q) || false
      const matchNotes = r.notes?.toLowerCase().includes(q) || false

      return (
        matchId ||
        matchMachineCode ||
        matchMachineName ||
        matchSection ||
        matchOperator ||
        matchOperatorEmail ||
        matchNotes
      )
    })
  }

  return list
})

// Helper methods
const countOutOfRange = (release) => {
  if (!release.values) return 0
  return release.values.filter((v) => v.is_out_of_range).length
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleDateString()
}

const formatTime = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const openDetailsModal = (rel) => {
  selectedRelease.value = rel
}

const closeDetailsModal = () => {
  selectedRelease.value = null
}
</script>

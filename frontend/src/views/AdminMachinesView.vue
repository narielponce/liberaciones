<template>
  <div class="max-w-6xl mx-auto px-4 py-6 pb-28 space-y-6">
    <!-- Header Title & Action -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="text-2xl">⚙️</span>
          <h2 class="text-xl font-black text-white tracking-tight">Gestión de Equipos y Máquinas</h2>
        </div>
        <p class="text-xs text-slate-400 font-medium">
          Módulo de Administración — Configure los atributos de la planta y los parámetros dinámicos de liberación.
        </p>
      </div>

      <button @click="openCreateModal"
        class="btn-touch px-5 bg-sky-600 hover:bg-sky-500 text-white font-extrabold text-sm shadow-lg shadow-sky-600/30 flex items-center justify-center gap-2">
        <span>➕</span>
        <span>Nuevo Equipo</span>
      </button>
    </div>

    <!-- Stats Summary Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Equipos</span>
        <span class="text-2xl font-black text-white font-mono">{{ machineStore.machines.length }}</span>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Activos</span>
        <span class="text-2xl font-black text-emerald-400 font-mono">{{ activeMachinesCount }}</span>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Plantas Registradas</span>
        <span class="text-2xl font-black text-sky-400 font-mono">{{ uniquePlantsCount }}</span>
      </div>

      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Parámetros</span>
        <span class="text-2xl font-black text-amber-400 font-mono">{{ totalParametersCount }}</span>
      </div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <input v-model="searchQuery" type="text" placeholder="Buscar por nombre, código QR, planta o sector..."
          class="w-full h-10 pl-9 pr-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-medium text-white placeholder-slate-500 focus:border-sky-500 outline-none transition-all" />
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">🔍</span>
      </div>

      <select v-model="plantFilter"
        class="h-10 px-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-semibold text-slate-300 focus:border-sky-500 outline-none">
        <option value="">Todas las Plantass</option>
        <option v-for="plant in plantOptions" :key="plant" :value="plant">{{ plant }}</option>
      </select>

      <button @click="loadMachines"
        class="px-4 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 flex items-center justify-center gap-1.5 transition-colors">
        <span>🔄</span>
        <span>Refrescar</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="machineStore.loading" class="text-center py-16">
      <div class="inline-block w-9 h-9 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-xs font-semibold text-slate-400 mt-2">Cargando inventario de equipos...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredMachines.length === 0"
      class="bg-slate-900 border border-slate-800 rounded-2xl p-10 text-center space-y-3">
      <span class="text-4xl">🏗️</span>
      <h3 class="text-base font-bold text-white">No se encontraron equipos</h3>
      <p class="text-xs text-slate-400">Pruebe ajustando los filtros de búsqueda o registre un nuevo equipo.</p>
    </div>

    <!-- Machines Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="mac in filteredMachines" :key="mac.id"
        class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 space-y-4 shadow-md transition-all flex flex-col justify-between">
        <div class="space-y-3">
          <!-- Card Header -->
          <div class="flex items-start justify-between gap-2">
            <div>
              <span
                class="text-[10px] font-mono font-extrabold uppercase tracking-widest text-sky-400 bg-sky-500/10 border border-sky-500/20 px-2 py-0.5 rounded-md inline-block mb-1">
                {{ mac.code }}
              </span>
              <h3 class="text-base font-black text-white leading-tight">{{ mac.name }}</h3>
            </div>

            <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded"
              :class="mac.is_active ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'">
              {{ mac.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>

          <!-- Attributes Grid (Planta, Célula, Sector, Sección) -->
          <div class="grid grid-cols-2 gap-2 text-xs bg-slate-950 p-3 rounded-xl border border-slate-800/80">
            <div>
              <span class="text-[10px] text-slate-500 font-bold uppercase block">Planta:</span>
              <span class="text-slate-200 font-semibold truncate block">{{ mac.plant || '—' }}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 font-bold uppercase block">Célula:</span>
              <span class="text-slate-200 font-semibold truncate block">{{ mac.cell || '—' }}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 font-bold uppercase block">Sector:</span>
              <span class="text-slate-200 font-semibold truncate block">{{ mac.sector || '—' }}</span>
            </div>
            <div>
              <span class="text-[10px] text-slate-500 font-bold uppercase block">Sección:</span>
              <span class="text-slate-200 font-semibold truncate block">{{ mac.section || '—' }}</span>
            </div>
          </div>

          <!-- Parameters Summary -->
          <div>
            <div class="flex items-center justify-between text-xs mb-1.5">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Parámetros Dinámicos:</span>
              <span class="text-xs font-bold text-amber-400 font-mono">{{ mac.parameters?.length || 0 }} ítems</span>
            </div>
            <div class="flex flex-wrap gap-1 max-h-16 overflow-y-auto">
              <span v-for="p in mac.parameters" :key="p.id"
                class="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700/60">
                {{ p.label }}
              </span>
            </div>
          </div>
        </div>

        <!-- Card Actions -->
        <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
          <button @click="openQrModal(mac)"
            class="px-2.5 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 text-xs font-bold transition-all flex items-center gap-1"
            title="Generar e imprimir Código QR">
            <span>📷</span>
            <span>QR</span>
          </button>

          <div class="flex items-center gap-1.5">
            <router-link :to="`/release/${mac.code}`"
              class="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-colors"
              title="Probar Liberación">
              📋 Probar
            </router-link>
            <button @click="openEditModal(mac)"
              class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors"
              title="Editar Equipo y Parámetros">
              ✏️ Editar
            </button>
            <button @click="confirmDelete(mac)"
              class="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 text-xs font-bold transition-colors"
              title="Eliminar Equipo">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit Machine & Dynamic Parameter Modal -->
    <div v-if="showFormModal"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
      <div
        class="bg-slate-900 border border-slate-800 rounded-3xl p-5 sm:p-6 max-w-2xl w-full my-auto space-y-5 shadow-2xl max-h-[92vh] flex flex-col">
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-slate-800 pb-3 shrink-0">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl">{{ isEditing ? '✏️' : '✨' }}</span>
            <div>
              <h3 class="text-lg font-black text-white">
                {{ isEditing ? `Editar Equipo: ${form.name}` : 'Registrar Nuevo Equipo' }}
              </h3>
              <p class="text-xs text-slate-400">Configure los atributos generales y los parámetros de liberación</p>
            </div>
          </div>
          <button @click="closeFormModal" class="text-slate-400 hover:text-white text-xl font-bold">✕</button>
        </div>

        <!-- Form Body Scrollable -->
        <form @submit.prevent="saveMachine" class="space-y-5 overflow-y-auto pr-1 flex-1">
          <!-- Section 1: Common Machine Attributes -->
          <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-4">
            <h4 class="text-xs font-bold text-sky-400 uppercase tracking-wider">1. Atributos Comunes del Equipo</h4>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Código QR Único *</label>
                <input v-model="form.code" type="text" required placeholder="Ej: MACH-TOR-01"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 font-mono font-bold text-xs text-white focus:border-sky-500 outline-none" />
              </div>

              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Nombre del Equipo *</label>
                <input v-model="form.name" type="text" required placeholder="Ej: Torno CNC Mazak Quick Turn"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 font-bold text-xs text-white focus:border-sky-500 outline-none" />
              </div>

              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Planta Industrial</label>
                <input v-model="form.plant" type="text" placeholder="Ej: Planta Norte"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:border-sky-500 outline-none" />
              </div>

              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Célula de Trabajo</label>
                <input v-model="form.cell" type="text" placeholder="Ej: Célula Envasado A"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:border-sky-500 outline-none" />
              </div>

              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Sector Operativo</label>
                <input v-model="form.sector" type="text" placeholder="Ej: Sector Mecanizado"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:border-sky-500 outline-none" />
              </div>

              <div>
                <label class="text-[11px] font-bold text-slate-300 uppercase block mb-1">Sección / Ubicación *</label>
                <input v-model="form.section" type="text" required placeholder="Ej: Nave 2 / Fila B"
                  class="w-full h-10 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:border-sky-500 outline-none" />
              </div>
            </div>

            <div class="flex items-center gap-2 pt-1">
              <input id="is_active_cb" v-model="form.is_active" type="checkbox"
                class="w-4 h-4 rounded border-slate-700 bg-slate-900 text-sky-600 focus:ring-sky-500" />
              <label for="is_active_cb" class="text-xs font-bold text-slate-200">Equipo Activo para Inspecciones en
                Planta</label>
            </div>
          </div>

          <!-- Section 2: Dynamic Inspection Parameters Builder -->
          <div class="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-xs font-bold text-amber-400 uppercase tracking-wider">2. Parámetros Dinámicos de
                  Liberación</h4>
                <p class="text-[10px] text-slate-400">Defina las mediciones u homologaciones visuales requeridas para
                  este equipo</p>
              </div>

              <button type="button" @click="addParameterRow"
                class="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-bold transition-all flex items-center gap-1">
                <span>➕</span>
                <span>Agregar Parámetro</span>
              </button>
            </div>

            <!-- Empty Parameters Prompt -->
            <div v-if="form.parameters.length === 0"
              class="text-center py-6 border border-dashed border-slate-800 rounded-xl">
              <p class="text-xs font-medium text-slate-500">No ha definido parámetros aún. Presione "Agregar Parámetro".
              </p>
            </div>

            <!-- Parameters Rows Builder -->
            <div v-else class="space-y-3">
              <div v-for="(p, pIdx) in form.parameters" :key="pIdx"
                class="bg-slate-900 border border-slate-800 rounded-xl p-3 space-y-3 relative group">
                <div class="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                  <span class="text-[10px] font-bold uppercase text-slate-400">Parámetro #{{ pIdx + 1 }}</span>
                  <button type="button" @click="removeParameterRow(pIdx)"
                    class="text-xs text-red-400 hover:text-red-300 font-bold px-2 py-0.5 rounded hover:bg-red-500/10"
                    title="Eliminar este parámetro">
                    🗑️ Quitar
                  </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div class="sm:col-span-2">
                    <label class="text-[10px] font-bold text-slate-400 uppercase block mb-1">Nombre / Etiqueta del
                      Parámetro *</label>
                    <input v-model="p.label" type="text" required placeholder="Ej: Presión de sujeción principal"
                      class="w-full h-9 px-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-bold text-white focus:border-sky-500 outline-none" />
                  </div>

                  <div>
                    <label class="text-[10px] font-bold text-slate-400 uppercase block mb-1">Tipo de Parámetro *</label>
                    <select v-model="p.param_type"
                      class="w-full h-9 px-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-bold text-sky-400 focus:border-sky-500 outline-none">
                      <option value="BOOLEAN">Visual / OK-NOk</option>
                      <option value="NUMERIC">Medición Numérica</option>
                    </select>
                  </div>
                </div>

                <!-- Numeric Parameter Specific Tolerance Ranges -->
                <div v-if="p.param_type === 'NUMERIC'"
                  class="grid grid-cols-3 gap-2 pt-1 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/60">
                  <div>
                    <label class="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">Mínimo Permitido</label>
                    <input v-model.number="p.min_value" type="number" step="any" placeholder="-∞"
                      class="w-full h-8 px-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-white outline-none" />
                  </div>

                  <div>
                    <label class="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">Máximo Permitido</label>
                    <input v-model.number="p.max_value" type="number" step="any" placeholder="+∞"
                      class="w-full h-8 px-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-white outline-none" />
                  </div>

                  <div>
                    <label class="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">Unidad de Medida</label>
                    <input v-model="p.unit" type="text" placeholder="Ej: bar, °C, mm"
                      class="w-full h-8 px-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-bold text-slate-200 outline-none" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Submit Controls -->
          <div class="flex items-center gap-3 pt-2 shrink-0 border-t border-slate-800">
            <button type="button" @click="closeFormModal"
              class="btn-touch px-5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs">
              Cancelar
            </button>

            <button type="submit" :disabled="saving"
              class="btn-touch flex-1 bg-sky-600 hover:bg-sky-500 text-white font-extrabold text-sm shadow-lg shadow-sky-600/30 transition-all disabled:opacity-50">
              <span v-if="saving" class="animate-pulse">Guardando Equipo...</span>
              <span v-else>{{ isEditing ? 'Guardar Cambios' : 'Registrar Equipo' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <div v-if="deletingMachine"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div
        class="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-sm w-full space-y-4 shadow-2xl text-center">
        <span class="text-4xl">⚠️</span>
        <div>
          <h4 class="text-lg font-black text-white">¿Eliminar Equipo?</h4>
          <p class="text-xs text-slate-300 mt-1">
            Está a punto de eliminar <span class="font-bold text-white">{{ deletingMachine.name }}</span> ({{
              deletingMachine.code }}).
          </p>
        </div>

        <div class="flex items-center gap-3 pt-2">
          <button @click="deletingMachine = null"
            class="btn-touch flex-1 bg-slate-800 text-slate-300 font-bold text-xs">
            Cancelar
          </button>
          <button @click="executeDelete"
            class="btn-touch flex-1 bg-red-600 hover:bg-red-500 text-white font-bold text-xs shadow-lg shadow-red-600/30">
            Sí, Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Printable QR Code Modal -->
    <div v-if="qrModalMachine"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div
        class="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-sm w-full space-y-5 shadow-2xl text-center relative">
        <button @click="qrModalMachine = null"
          class="absolute right-4 top-4 text-slate-400 hover:text-white text-lg font-bold">✕</button>

        <div class="space-y-1">
          <span
            class="text-xs font-mono font-extrabold uppercase tracking-widest text-sky-400 bg-sky-500/10 border border-sky-500/20 px-2 py-0.5 rounded-md inline-block">
            {{ qrModalMachine.code }}
          </span>
          <h3 class="text-lg font-black text-white leading-tight">{{ qrModalMachine.name }}</h3>
          <p class="text-[11px] text-slate-400">
            {{ [qrModalMachine.plant, qrModalMachine.cell, qrModalMachine.sector,
            qrModalMachine.section].filter(Boolean).join(' | ') }}
          </p>
        </div>

        <!-- QR Code Card Preview -->
        <div class="bg-white p-5 rounded-2xl border-4 border-slate-800 inline-block shadow-inner">
          <img
            :src="`https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(qrModalMachine.code)}`"
            :alt="`QR ${qrModalMachine.code}`" class="w-44 h-44 mx-auto block" />
          <span class="block text-[10px] font-mono font-extrabold text-slate-900 mt-2 tracking-widest uppercase">
            {{ qrModalMachine.code }}
          </span>
        </div>

        <!-- Action Controls: Print & Copy -->
        <div class="space-y-2 pt-1">
          <div class="grid grid-cols-2 gap-2">
            <button @click="copyToClipboard(qrModalMachine.code, 'code')"
              class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center justify-center gap-1.5">
              <span>📋</span>
              <span>{{ copyStatus === 'code' ? '¡Copiado!' : 'Copiar Código' }}</span>
            </button>

            <button @click="copyToClipboard(`${windowLocationOrigin}/release/${qrModalMachine.code}`, 'link')"
              class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center justify-center gap-1.5">
              <span>🔗</span>
              <span>{{ copyStatus === 'link' ? '¡Copiada!' : 'Copiar URL' }}</span>
            </button>
          </div>

          <button @click="printQrCard"
            class="w-full btn-touch bg-sky-600 hover:bg-sky-500 text-white font-extrabold text-xs shadow-lg shadow-sky-600/30 flex items-center justify-center gap-2">
            <span>🖨️</span>
            <span>Imprimir Etiqueta QR</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMachineStore } from '../stores/machine'

const machineStore = useMachineStore()

const searchQuery = ref('')
const plantFilter = ref('')
const showFormModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const deletingMachine = ref(null)

const form = reactive({
  code: '',
  name: '',
  plant: '',
  cell: '',
  sector: '',
  section: '',
  is_active: true,
  parameters: [],
})

const loadMachines = async () => {
  try {
    await machineStore.fetchMachines(true)
  } catch (err) {
    console.error('Error loading machines:', err)
  }
}

onMounted(() => {
  loadMachines()
})

// Computeds for Statistics and Filtering
const activeMachinesCount = computed(() => machineStore.machines.filter((m) => m.is_active).length)

const plantOptions = computed(() => {
  const plants = machineStore.machines.map((m) => m.plant).filter((p) => p && p.trim() !== '')
  return [...new Set(plants)]
})

const uniquePlantsCount = computed(() => plantOptions.value.length)

const totalParametersCount = computed(() => {
  return machineStore.machines.reduce((acc, m) => acc + (m.parameters?.length || 0), 0)
})

const filteredMachines = computed(() => {
  return machineStore.machines.filter((mac) => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !q ||
      mac.name?.toLowerCase().includes(q) ||
      mac.code?.toLowerCase().includes(q) ||
      mac.plant?.toLowerCase().includes(q) ||
      mac.sector?.toLowerCase().includes(q) ||
      mac.section?.toLowerCase().includes(q)

    const matchesPlant = !plantFilter.value || mac.plant === plantFilter.value
    return matchesSearch && matchesPlant
  })
})

// Modal Openers
const resetForm = () => {
  form.code = ''
  form.name = ''
  form.plant = ''
  form.cell = ''
  form.sector = ''
  form.section = ''
  form.is_active = true
  form.parameters = [
    { label: 'Inspección de Seguridad Visual', param_type: 'BOOLEAN', min_value: null, max_value: null, unit: '', is_required: true },
  ]
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  resetForm()
  showFormModal.value = true
}

const openEditModal = (mac) => {
  isEditing.value = true
  editingId.value = mac.id
  form.code = mac.code || ''
  form.name = mac.name || ''
  form.plant = mac.plant || ''
  form.cell = mac.cell || ''
  form.sector = mac.sector || ''
  form.section = mac.section || ''
  form.is_active = mac.is_active !== undefined ? mac.is_active : true
  form.parameters = (mac.parameters || []).map((p) => ({
    id: p.id,
    label: p.label,
    param_type: p.param_type,
    min_value: p.min_value,
    max_value: p.max_value,
    unit: p.unit || '',
    is_required: p.is_required !== undefined ? p.is_required : true,
  }))
  showFormModal.value = true
}

const closeFormModal = () => {
  showFormModal.value = false
}

const addParameterRow = () => {
  form.parameters.push({
    label: '',
    param_type: 'NUMERIC',
    min_value: null,
    max_value: null,
    unit: '',
    is_required: true,
  })
}

const removeParameterRow = (idx) => {
  form.parameters.splice(idx, 1)
}

const saveMachine = async () => {
  saving.value = true
  try {
    const payload = {
      code: form.code,
      name: form.name,
      plant: form.plant || null,
      cell: form.cell || null,
      sector: form.sector || null,
      section: form.section,
      is_active: form.is_active,
      parameters: form.parameters.map((p, idx) => ({
        label: p.label,
        param_type: p.param_type,
        min_value: p.param_type === 'NUMERIC' && p.min_value !== '' && p.min_value !== null ? Number(p.min_value) : null,
        max_value: p.param_type === 'NUMERIC' && p.max_value !== '' && p.max_value !== null ? Number(p.max_value) : null,
        unit: p.param_type === 'NUMERIC' && p.unit ? p.unit.trim() : null,
        order_index: idx + 1,
        is_required: p.is_required !== false,
      })),
    }

    if (isEditing.value) {
      await machineStore.updateMachine(editingId.value, payload)
    } else {
      await machineStore.createMachine(payload)
    }
    closeFormModal()
  } catch (err) {
    alert(err.response?.data?.detail || 'Error al guardar el equipo.')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (mac) => {
  deletingMachine.value = mac
}

const executeDelete = async () => {
  if (!deletingMachine.value) return
  try {
    await machineStore.deleteMachine(deletingMachine.value.id)
    deletingMachine.value = null
  } catch (err) {
    alert(err.response?.data?.detail || 'Error al eliminar el equipo.')
  }
}

// QR Code Generator & Printing Handlers
const qrModalMachine = ref(null)
const copyStatus = ref(null)
const windowLocationOrigin = computed(() => window.location.origin)

const openQrModal = (mac) => {
  qrModalMachine.value = mac
  copyStatus.value = null
}

const copyToClipboard = async (text, type) => {
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value = type
    setTimeout(() => {
      copyStatus.value = null
    }, 2000)
  } catch (err) {
    alert('Código: ' + text)
  }
}

const printQrCard = () => {
  const mac = qrModalMachine.value
  if (!mac) return

  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=${encodeURIComponent(mac.code)}`
  const locationInfo = [mac.plant, mac.cell, mac.sector, mac.section].filter(Boolean).join(' | ')

  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Etiqueta QR - ${mac.code}</title>
        <style>
          body { font-family: system-ui, -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 98vh; margin: 0; padding: 20px; background: #fff; }
          .label { border: 4px solid #000; border-radius: 20px; padding: 24px; text-align: center; max-width: 320px; width: 100%; box-sizing: border-box; }
          .code { font-size: 15px; font-weight: 900; font-family: monospace; letter-spacing: 2px; text-transform: uppercase; background: #f0f0f0; border: 1px solid #ccc; padding: 4px 10px; border-radius: 8px; display: inline-block; margin-bottom: 8px; }
          .title { font-size: 18px; font-weight: 900; margin: 8px 0 4px 0; color: #000; line-height: 1.2; }
          .location { font-size: 11px; color: #444; font-weight: 700; margin-bottom: 16px; text-transform: uppercase; }
          .qr-img { width: 220px; height: 220px; margin: 0 auto; display: block; }
          .footer { font-size: 10px; font-weight: 800; font-family: monospace; margin-top: 14px; letter-spacing: 1.5px; border-t: 1px solid #ddd; pt-2; color: #333; }
          @media print {
            body { padding: 0; }
            .label { border: 3px solid #000; }
          }
        </style>
      </head>
      <body>
        <div class="label">
          <div class="code">${mac.code}</div>
          <div class="title">${mac.name}</div>
          <div class="location">${locationInfo}</div>
          <img src="${qrUrl}" class="qr-img" />
          <div class="footer">LIBERACION DE MAQUINAS — PLANTA INDUSTRIAL</div>
        </div>
        <script>
          window.onload = function() {
            window.print();
            setTimeout(function() { window.close(); }, 500);
          };
        <\/script>
      </body>
    </html>
  `)
  printWindow.document.close()
}
</script>

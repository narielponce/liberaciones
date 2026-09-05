<template>
  <div class="max-w-2xl mx-auto px-4 py-6 pb-28 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-extrabold text-white">Historial de Liberaciones</h2>
        <p class="text-xs text-slate-400">Auditoría y registro de operaciones en planta</p>
      </div>

      <button
        @click="loadHistory"
        class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
      >
        🔄 Actualizar
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="releaseStore.loading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-xs font-medium text-slate-400 mt-2">Cargando registros de auditoría...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="releaseStore.recentReleases.length === 0" class="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-3">
      <span class="text-4xl">📋</span>
      <h3 class="text-base font-bold text-white">Sin Registros Recientes</h3>
      <p class="text-xs text-slate-400">No hay liberaciones de máquinas registradas aún.</p>
    </div>

    <!-- Releases List -->
    <div v-else class="space-y-4">
      <div
        v-for="rel in releaseStore.recentReleases"
        :key="rel.id"
        class="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3 shadow-md"
      >
        <div class="flex items-start justify-between">
          <div>
            <span class="text-[10px] font-bold text-sky-400 uppercase tracking-wider block">ID #{{ rel.id }}</span>
            <h3 class="text-sm font-bold text-white">Máquina ID: {{ rel.machine_id }}</h3>
            <p class="text-xs text-slate-400">
              Operador: <span class="text-slate-200 font-medium">{{ rel.operator?.full_name || 'Desconocido' }}</span>
            </p>
          </div>

          <div class="text-right">
            <span
              class="inline-block text-[11px] font-black uppercase px-2.5 py-1 rounded-lg"
              :class="rel.status === 'OK' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-red-500/20 text-red-300 border border-red-500/40'"
            >
              {{ rel.status }}
            </span>
            <p class="text-[10px] text-slate-500 font-mono mt-1">
              {{ new Date(rel.timestamp).toLocaleString() }}
            </p>
          </div>
        </div>

        <div v-if="rel.notes" class="text-xs text-slate-300 bg-slate-950 p-2.5 rounded-xl border border-slate-800/80 italic">
          "{{ rel.notes }}"
        </div>

        <!-- Parameter Values Breakdown -->
        <div class="pt-2 border-t border-slate-800/60 space-y-1.5">
          <span class="text-[10px] font-bold uppercase text-slate-400 tracking-wider block">Parámetros Medidos</span>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            <div
              v-for="val in rel.values"
              :key="val.id"
              class="px-2.5 py-1.5 rounded-lg bg-slate-950 border text-[11px] space-y-1"
              :class="val.is_out_of_range ? 'border-red-500/40 text-red-300 bg-red-950/20' : 'border-slate-800 text-slate-300'"
            >
              <div class="flex items-center justify-between">
                <span class="truncate font-medium pr-2">{{ val.parameter?.label || `Param #${val.parameter_id}` }}:</span>
                <span class="font-bold font-mono shrink-0">
                  <template v-if="val.bool_value !== null">
                    {{ val.bool_value ? '✓ OK' : '✕ NOk' }}
                  </template>
                  <template v-else-if="val.numeric_value !== null">
                    {{ val.numeric_value }} {{ val.parameter?.unit || '' }}
                  </template>
                </span>
              </div>
              <div v-if="val.notes" class="text-[10px] text-amber-300/90 italic bg-amber-950/40 p-1.5 rounded border border-amber-500/20">
                💬 Obs: {{ val.notes }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useReleaseStore } from '../stores/release'

const releaseStore = useReleaseStore()

const loadHistory = () => {
  releaseStore.fetchReleases()
}

onMounted(() => {
  loadHistory()
})
</script>

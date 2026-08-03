<script setup>
import { shallowRef } from 'vue';

import { formatDateTime } from '@/utils/formatters';

const props = defineProps({
  events:  { type: Array,   required: true },
  loading: { type: Boolean, default: false },
  inline:  { type: Boolean, default: false },
});

const emit = defineEmits(['show-detail']);

const expandedId = shallowRef(null);

const EVENT_CONFIG = {
  alta:          { label: 'Creación',         badge: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' },
  baja:          { label: 'Baja',             badge: 'bg-red-100 text-red-700',         dot: 'bg-red-500' },
  desactivacion: { label: 'Desactivación',    badge: 'bg-red-100 text-red-700',         dot: 'bg-red-500' },
  actualizacion: { label: 'Actualización',    badge: 'bg-blue-100 text-blue-700',       dot: 'bg-blue-500' },
  cambio_rol:    { label: 'Cambio de rol',    badge: 'bg-violet-100 text-violet-700',   dot: 'bg-violet-500' },
  cambio_estado: { label: 'Cambio de estado', badge: 'bg-amber-100 text-amber-700',     dot: 'bg-amber-500' },
  asignacion:    { label: 'Asignación',       badge: 'bg-primary-100 text-primary-700', dot: 'bg-primary-500' },
  desasignacion: { label: 'Desasignación',    badge: 'bg-slate-100 text-slate-600',     dot: 'bg-slate-400' },
};

const DEFAULT_CONFIG = { label: 'Evento', badge: 'bg-slate-100 text-slate-600', dot: 'bg-slate-400' };

function getConfig(tipoEvento) {
  const accion = tipoEvento?.split('.')?.[1] ?? '';
  return EVENT_CONFIG[accion] ?? DEFAULT_CONFIG;
}

function hasCambios(event) {
  return event?.datos_extra?.cambios?.length > 0;
}

function handleVerCambios(event) {
  if (props.inline) {
    expandedId.value = expandedId.value === event.id ? null : event.id;
  } else {
    emit('show-detail', event);
  }
}
</script>

<template>
  <div class="flex flex-col">

    <div v-if="loading" class="flex items-center justify-center py-12">
      <span class="text-sm text-slate-400">Cargando historial…</span>
    </div>

    <p v-else-if="!events.length" class="py-8 text-center text-sm text-slate-400">
      No hay eventos registrados para este elemento.
    </p>

    <div v-else class="relative">
      <div class="absolute left-5 top-0 h-full w-px bg-slate-200" aria-hidden="true" />

      <div
        v-for="event in events"
        :key="event.id"
        class="relative flex gap-4 pb-6 last:pb-0"
      >
        <div
          class="relative z-10 mt-1 flex size-10 shrink-0 items-center justify-center rounded-full border-2 border-white shadow-sm"
          :class="getConfig(event.tipo_evento).dot"
        />

        <div class="flex flex-1 flex-col gap-1 pt-1">
          <div class="flex flex-wrap items-center gap-2">
            <span
              class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
              :class="getConfig(event.tipo_evento).badge"
            >
              {{ getConfig(event.tipo_evento).label }}
            </span>
            <span class="font-mono text-xs text-slate-400">{{ event.tipo_evento }}</span>
            <span class="ml-auto text-xs text-slate-400">{{ formatDateTime(event.fecha) }}</span>
          </div>

          <p class="text-sm text-slate-700">{{ event.descripcion }}</p>

          <div class="flex items-center justify-between">
            <p v-if="event.usuario_nombre" class="text-xs text-slate-400">
              Por: <span class="text-slate-500">{{ event.usuario_nombre }}</span>
            </p>
            <button
              v-if="hasCambios(event)"
              type="button"
              class="text-xs font-medium text-primary-600 hover:text-primary-700 hover:underline"
              @click="handleVerCambios(event)"
            >
              {{ inline && expandedId === event.id ? 'Ocultar cambios' : 'Ver cambios' }}
            </button>
          </div>

          <div v-if="inline && expandedId === event.id" class="mt-2 overflow-x-auto rounded-xl border border-slate-200">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-200 bg-slate-50">
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-slate-500">Campo</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-red-600">Antes</th>
                  <th class="px-4 py-2.5 text-left text-xs font-semibold text-emerald-600">Después</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="cambio in event.datos_extra.cambios"
                  :key="cambio.campo"
                  class="border-b border-slate-100 last:border-0"
                >
                  <td class="px-4 py-3 font-medium text-slate-700">{{ cambio.campo }}</td>
                  <td class="bg-red-50 px-4 py-3 text-red-700">{{ cambio.antes }}</td>
                  <td class="bg-emerald-50 px-4 py-3 text-emerald-700">{{ cambio.despues }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

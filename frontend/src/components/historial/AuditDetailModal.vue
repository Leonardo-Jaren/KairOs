<script setup>
import { computed, shallowRef, watch } from 'vue';

import BaseModal from '@/components/modals/BaseModal.vue';
import historialService from '@/services/historial.service';
import { formatDateTime } from '@/utils/formatters';
import AuditTimelineList from './AuditTimelineList.vue';

const props = defineProps({
  open:  { type: Boolean, default: false },
  event: { type: Object,  default: null },
});

defineEmits(['close']);

const activeTab      = shallowRef('info');
const timelineEvents = shallowRef([]);
const timelineLoading = shallowRef(false);
const timelineLoaded  = shallowRef(false);

watch(() => props.event, () => {
  activeTab.value      = 'info';
  timelineEvents.value = [];
  timelineLoaded.value = false;
});

async function switchToTimeline() {
  activeTab.value = 'timeline';
  if (timelineLoaded.value || !props.event?.modulo || !props.event?.object_id) return;
  timelineLoading.value = true;
  try {
    const data = await historialService.listar({
      modulo: props.event.modulo,
      object_id: props.event.object_id,
      page_size: 50,
    });
    timelineEvents.value = data.results ?? data;
    timelineLoaded.value = true;
  } finally {
    timelineLoading.value = false;
  }
}

const cambios = computed(() => props.event?.datos_extra?.cambios ?? []);

const EVENT_LABELS = {
  alta: 'Creación', baja: 'Baja', desactivacion: 'Desactivación',
  actualizacion: 'Actualización', cambio_rol: 'Cambio de rol',
  cambio_estado: 'Cambio de estado', asignacion: 'Asignación',
  desasignacion: 'Desasignación',
};

const eventLabel = computed(() => {
  const accion = props.event?.tipo_evento?.split('.')?.[1] ?? '';
  return EVENT_LABELS[accion] ?? accion;
});
</script>

<template>
  <BaseModal :open="open" title="Detalle del evento" size="lg" @close="$emit('close')">
    <div v-if="event" class="flex flex-col">

      <div class="mb-5 flex border-b border-slate-200">
        <button
          type="button"
          class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === 'info'
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="activeTab = 'info'"
        >
          Información
        </button>
        <button
          type="button"
          class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="activeTab === 'timeline'
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="switchToTimeline"
        >
          Línea de Tiempo
        </button>
      </div>

      <div v-if="activeTab === 'info'" class="flex flex-col gap-5">
        <div class="flex flex-wrap items-center gap-2 rounded-xl bg-slate-50 px-4 py-3">
          <span class="rounded-full bg-primary-100 px-3 py-1 text-xs font-bold text-primary-700">
            {{ eventLabel }}
          </span>
          <span class="font-mono text-xs text-slate-500">{{ event.tipo_evento }}</span>
          <span class="ml-auto text-xs text-slate-400">{{ formatDateTime(event.fecha) }}</span>
        </div>

        <div>
          <p class="text-sm text-slate-700">{{ event.descripcion }}</p>
          <p v-if="event.usuario_nombre" class="mt-1 text-xs text-slate-400">
            Realizado por: <span class="font-medium text-slate-600">{{ event.usuario_nombre }}</span>
          </p>
        </div>

        <div v-if="cambios.length" class="overflow-x-auto rounded-xl border border-slate-200">
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
                v-for="cambio in cambios"
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

        <p v-else class="py-2 text-center text-sm text-slate-400">
          Este evento no registra cambios de campo.
        </p>
      </div>

      <div v-else>
        <AuditTimelineList
          :events="timelineEvents"
          :loading="timelineLoading"
          :inline="true"
        />
      </div>

    </div>
  </BaseModal>
</template>

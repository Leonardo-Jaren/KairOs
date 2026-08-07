<script setup>
import BaseTable from '@/components/tables/BaseTable.vue';
import { formatDateTime } from '@/utils/formatters';

defineProps({
  historial: { type: Array, required: true },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(['show-detail']);

const MODULO_LABELS = {
  usuario:        'Usuario',
  espacio:        'Espacio',
  espaciousuario: 'Espacio usuario',
  equipo:         'Equipo',
  mantenimiento:  'Mantenimiento',
  incidencia:     'Incidencia',
  software:       'Software',
};

function formatModulo(modulo) {
  return MODULO_LABELS[modulo] ?? modulo;
}

const COLUMNS = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'usuario_nombre', label: 'Usuario' },
  { key: 'modulo', label: 'Módulo' },
  { key: 'tipo_evento', label: 'Evento' },
  { key: 'descripcion', label: 'Descripción' },
  { key: 'acciones', label: '' },
];
</script>

<template>
  <BaseTable
    :columns="COLUMNS"
    :items="historial"
    :loading="loading"
    empty-message="No hay eventos de auditoría con los filtros seleccionados."
  >
    <template #cell-fecha="{ item }">
      <span class="whitespace-nowrap text-xs text-slate-500">{{ formatDateTime(item.fecha) }}</span>
    </template>

    <template #cell-modulo="{ item }">
      <span class="rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700">
        {{ formatModulo(item.modulo) }}
      </span>
    </template>

    <template #cell-tipo_evento="{ item }">
      <span class="font-mono text-xs text-slate-600">{{ item.tipo_evento }}</span>
    </template>

    <template #cell-descripcion="{ item }">
      <span class="text-sm text-slate-600">{{ item.descripcion }}</span>
    </template>

    <template #cell-acciones="{ item }">
      <button
        type="button"
        class="rounded-lg px-3 py-1.5 text-xs font-medium text-primary-600 hover:bg-primary-50 hover:text-primary-700 transition-colors"
        @click="emit('show-detail', item)"
      >
        Detalles
      </button>
    </template>
  </BaseTable>
</template>

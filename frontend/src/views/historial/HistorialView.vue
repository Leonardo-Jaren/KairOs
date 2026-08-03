<script setup>
import { shallowRef } from 'vue';

import AuditDetailModal from '@/components/historial/AuditDetailModal.vue';
import HistorialFilters from '@/components/historial/HistorialFilters.vue';
import HistorialTable from '@/components/historial/HistorialTable.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useHistorial } from '@/composables/historial/useHistorial';

const {
  historial,
  loading,
  filters,
  pagination,
  toast,
  hasActiveFilters,
  applyFilters,
  clearFilters,
  changePage,
  closeToast,
} = useHistorial();

const selectedEvent = shallowRef(null);
</script>

<template>
  <div class="flex flex-col gap-6">

    <header>
      <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Sistema</p>
      <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Historial de auditoría</h1>
      <p class="mt-2 max-w-2xl text-sm text-slate-500">
        Registro de las acciones realizadas en el sistema.
      </p>
    </header>

    <HistorialFilters
      v-model:modulo="filters.modulo"
      v-model:tipo-evento="filters.tipo_evento"
      v-model:fecha-desde="filters.fecha_desde"
      v-model:fecha-hasta="filters.fecha_hasta"
      :has-active-filters="hasActiveFilters"
      @apply="applyFilters"
      @clear="clearFilters"
    />

    <HistorialTable
      :historial="historial"
      :loading="loading"
      @show-detail="selectedEvent = $event"
    />

    <BasePagination
      :page="filters.page"
      :total-pages="pagination.totalPages"
      :total="pagination.total"
      @change="changePage"
    />

    <AuditDetailModal
      :open="selectedEvent !== null"
      :event="selectedEvent"
      @close="selectedEvent = null"
    />

    <BaseToast
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="closeToast"
    />

  </div>
</template>

<script setup>
import {
  CalendarClock,
  MonitorCog,
  Pencil,
  Plus,
  Search,
  Trash2,
  Wrench,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useMantenimiento } from '@/composables/mantenimiento/useMantenimiento';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'fecha', label: 'Fecha' },
  { key: 'tipo', label: 'Tipo de mantenimiento' },
  { key: 'tecnico', label: 'Técnico responsable' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  mantenimientos,
  loading,
  saving,
  modalOpen,
  deleteModalOpen,
  pendingDelete,
  form,
  formErrors,
  filters,
  pagination,
  stats,
  toast,
  isEditing,
  canDelete,
  tipoOptions,
  estadoOptions,
  equipoSelectOptions,
  tecnicoSelectOptions,
  openCreate,
  openEdit,
  closeModal,
  submit,
  askDelete,
  cancelDelete,
  confirmDelete,
  applyFilters,
  clearFilters,
  changePage,
  closeToast,
} = useMantenimiento();

const estadoClasses = {
  pendiente: 'bg-slate-100 text-slate-600',
  en_proceso: 'bg-success-50 text-success-700',
  resuelto: 'bg-primary-50 text-primary-700',
  cancelado: 'bg-danger-50 text-danger-700',
};

const estadoDotClasses = {
  pendiente: 'bg-slate-400',
  en_proceso: 'bg-success-500',
  resuelto: 'bg-primary-500',
  cancelado: 'bg-danger-500',
};

const estadoLabels = {
  pendiente: 'Pendiente',
  en_proceso: 'En mantenimiento',
  resuelto: 'Terminado',
  cancelado: 'Fuera de servicio',
};

const tipoClasses = {
  preventivo: 'bg-primary-50 text-primary-700',
  correctivo: 'bg-warning-50 text-warning-700',
};

const formatFecha = (fecha) => {
  if (!fecha) return '—';
  const [year, month, day] = fecha.split('-');
  return `${day}/${month}/${year}`;
};
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Operaciones</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Mantenimiento</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Registra y da seguimiento a los tickets de mantenimiento preventivo y correctivo de los equipos.
        </p>
      </div>
      <BaseButton variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Agregar
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Técnicos registrados" :value="stats.total_tecnicos" tone="blue" helper="Personal activo">
        <template #icon><Wrench :size="20" /></template>
      </StatCard>
      <StatCard label="Dispositivos" :value="stats.total_dispositivos" tone="violet" helper="Equipos registrados">
        <template #icon><MonitorCog :size="20" /></template>
      </StatCard>
      <StatCard label="En mantenimiento" :value="stats.en_proceso" tone="emerald" helper="Tickets en curso">
        <template #icon><CalendarClock :size="20" /></template>
      </StatCard>
      <StatCard label="Pendientes" :value="stats.pendientes" tone="amber" helper="Por atender">
        <template #icon><Wrench :size="20" /></template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <h2 class="text-base font-bold text-slate-900">Mantenimiento de equipos</h2>
      </div>
      <form class="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px_180px_auto]" @submit.prevent="applyFilters">
        <BaseInput
          id="mant-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por equipo, descripción o técnico"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <BaseSelect
          id="mant-tipo"
          v-model="filters.tipo_mantenimiento"
          :options="tipoOptions"
          placeholder="Todos los tipos"
        />
        <BaseSelect
          id="mant-estado"
          v-model="filters.estado"
          :options="estadoOptions"
          placeholder="Todos los estados"
        />
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="mantenimientos"
      :loading="loading"
      empty-message="No se encontraron tickets de mantenimiento con los filtros actuales."
    >
      <template #cell-id="{ item }">
        <span class="font-mono text-xs text-slate-500">#{{ item.id }}</span>
      </template>
      <template #cell-equipo="{ item }">
        <div>
          <p class="font-semibold text-slate-900">{{ item.equipo?.codigo }}</p>
          <p class="text-xs text-slate-500">{{ item.equipo?.marca }} {{ item.equipo?.modelo }}</p>
        </div>
      </template>
      <template #cell-fecha="{ item }">
        <span class="text-sm text-slate-600">{{ formatFecha(item.fecha) }}</span>
      </template>
      <template #cell-tipo="{ item }">
        <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="tipoClasses[item.tipo_mantenimiento]">
          {{ item.tipo_mantenimiento_display }}
        </span>
      </template>
      <template #cell-tecnico="{ item }">
        <span class="text-sm text-slate-700">{{ item.tecnico_responsable }}</span>
      </template>
      <template #cell-estado="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="estadoClasses[item.estado]"
        >
          <span class="size-1.5 rounded-full" :class="estadoDotClasses[item.estado]" />
          {{ estadoLabels[item.estado] ?? item.estado_display }}
        </span>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar mantenimiento" @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button
            v-if="canDelete"
            type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
            aria-label="Eliminar mantenimiento"
            @click="askDelete(item)"
          >
            <Trash2 :size="17" />
          </button>
        </div>
      </template>
    </BaseTable>

    <BasePagination
      :page="filters.page"
      :total-pages="pagination.totalPages"
      :total="pagination.total"
      :loading="loading"
      @change="changePage"
    />

    <BaseModal
      :open="modalOpen"
      :title="isEditing ? 'Editar mantenimiento' : 'Nuevo mantenimiento'"
      description="Registra la actividad realizada sobre el equipo y su técnico responsable."
      @close="closeModal"
    >
      <form id="mant-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <div class="sm:col-span-2">
          <BaseSelect
            id="mant-equipo"
            v-model="form.equipo_id"
            label="Equipo"
            :options="equipoSelectOptions"
            placeholder="Selecciona un equipo"
            :error="formErrors.equipo_id"
          />
        </div>
        <BaseInput id="mant-fecha" v-model="form.fecha" type="date" appearance="light" label="Fecha" :error="formErrors.fecha" />
        <BaseSelect
          id="mant-tecnico"
          v-model="form.tecnico_id"
          label="Técnico responsable"
          :options="tecnicoSelectOptions"
          placeholder="Sin asignar"
        />
        <BaseSelect
          id="mant-tipo-form"
          v-model="form.tipo_mantenimiento"
          label="Tipo de mantenimiento"
          :options="tipoOptions"
          :error="formErrors.tipo_mantenimiento"
        />
        <BaseSelect
          id="mant-estado-form"
          v-model="form.estado"
          label="Estado"
          :options="estadoOptions"
          :error="formErrors.estado"
        />
        <div class="sm:col-span-2">
          <BaseTextarea
            id="mant-descripcion"
            v-model="form.descripcion"
            appearance="light"
            label="Descripción"
            placeholder="Describe el problema o la actividad realizada"
            :rows="3"
            :error="formErrors.descripcion"
          />
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="mant-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear ticket' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Eliminar mantenimiento" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        El ticket del equipo <strong class="text-slate-900">{{ pendingDelete?.equipo?.codigo }}</strong> se eliminará, pero se conservará el historial del equipo.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

<script setup>
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ListChecks,
  Pencil,
  Plus,
  Search,
  Trash2,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useIncidencias } from '@/composables/incidencias/useIncidencias';
import { formatDate } from '@/utils/formatters';

const columns = [
  { key: 'tipo_incidencia', label: 'Tipo' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'espacio', label: 'Espacio' },
  { key: 'descripcion', label: 'Descripción' },
  { key: 'reportado_por', label: 'Reportado por' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  incidencias,
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
  canManageAll,
  tipoIncidenciaOptions,
  estadoOptions,
  espacioSelectOptions,
  equipoSelectOptions,
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
} = useIncidencias();

const tipoClasses = {
  hardware: 'bg-primary-50 text-primary-700',
  software: 'bg-violet-50 text-violet-700',
};

const estadoClasses = {
  pendiente: 'bg-slate-100 text-slate-600',
  en_proceso: 'bg-warning-50 text-warning-700',
  resuelto: 'bg-success-50 text-success-700',
};

const estadoDotClasses = {
  pendiente: 'bg-slate-400',
  en_proceso: 'bg-warning-500',
  resuelto: 'bg-success-500',
};
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Soporte</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Incidencias</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Reporta y da seguimiento a fallas de hardware o software en los equipos de cada espacio.
        </p>
      </div>
      <BaseButton variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Reportar
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Incidencias totales" :value="stats.total" tone="blue">
        <template #icon><ListChecks :size="20" /></template>
      </StatCard>
      <StatCard label="Pendientes" :value="stats.pendientes" tone="amber">
        <template #icon><AlertTriangle :size="20" /></template>
      </StatCard>
      <StatCard label="En proceso" :value="stats.en_proceso" tone="violet">
        <template #icon><Clock3 :size="20" /></template>
      </StatCard>
      <StatCard label="Resueltas" :value="stats.resueltas" tone="emerald">
        <template #icon><CheckCircle2 :size="20" /></template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <h2 class="text-base font-bold text-slate-900">Incidencias registradas</h2>
      </div>
      <form class="flex flex-col gap-3" @submit.prevent="applyFilters">
        <BaseInput
          id="incidencias-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por descripción, equipo o espacio"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <div class="flex flex-wrap items-end gap-3">
          <div class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-espacio"
              v-model="filters.espacio_id"
              :options="espacioSelectOptions"
              placeholder="Todos los espacios"
            />
          </div>
          <div class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-equipo"
              v-model="filters.equipo_id"
              :options="equipoSelectOptions"
              placeholder="Todos los equipos"
            />
          </div>
          <div class="w-full min-w-40 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-tipo"
              v-model="filters.tipo_incidencia"
              :options="tipoIncidenciaOptions"
              placeholder="Todos los tipos"
            />
          </div>
          <div class="w-full min-w-40 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-estado"
              v-model="filters.estado"
              :options="estadoOptions"
              placeholder="Todos los estados"
            />
          </div>
          <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
          <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
        </div>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="incidencias"
      :loading="loading"
      empty-message="No se encontraron incidencias con los filtros actuales."
    >
      <template #cell-tipo_incidencia="{ item }">
        <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="tipoClasses[item.tipo_incidencia]">
          {{ item.tipo_incidencia_display }}
        </span>
      </template>
      <template #cell-equipo="{ item }">
        <span class="font-mono text-sm font-semibold text-slate-700">{{ item.equipo_codigo }}</span>
      </template>
      <template #cell-espacio="{ item }">
        <span class="text-sm text-slate-600">{{ item.espacio_nombre }}</span>
      </template>
      <template #cell-descripcion="{ item }">
        <span class="line-clamp-2 max-w-xs text-sm text-slate-600">{{ item.descripcion }}</span>
      </template>
      <template #cell-reportado_por="{ item }">
        <div>
          <p class="text-sm text-slate-700">{{ item.reportado_por ?? '—' }}</p>
          <p class="text-xs capitalize text-slate-400">{{ item.reportado_por_rol }}</p>
        </div>
      </template>
      <template #cell-estado="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="estadoClasses[item.estado]"
        >
          <span class="size-1.5 rounded-full" :class="estadoDotClasses[item.estado]" />
          {{ item.estado_display }}
        </span>
        <p v-if="item.fecha_resolucion" class="mt-1 text-xs text-slate-400">
          Resuelta el {{ formatDate(item.fecha_resolucion) }}
        </p>
      </template>
      <template #cell-acciones="{ item }">
        <div v-if="canManageAll" class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar incidencia" @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Eliminar incidencia" @click="askDelete(item)">
            <Trash2 :size="17" />
          </button>
        </div>
        <span v-else class="text-xs text-slate-400">Solo lectura</span>
      </template>
    </BaseTable>

    <BasePagination
      :page="filters.page"
      :total-pages="pagination.totalPages"
      :total="pagination.total"
      @change="changePage"
    />

    <BaseModal
      :open="modalOpen"
      :title="isEditing ? 'Editar incidencia' : 'Reportar incidencia'"
      description="Indica el espacio, equipo y el detalle de lo ocurrido."
      size="lg"
      @close="closeModal"
    >
      <form id="incidencia-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <BaseSelect id="inc-espacio" v-model="form.espacio" label="Espacio" :options="espacioSelectOptions" placeholder="Selecciona un espacio" :error="formErrors.espacio" />
        <BaseSelect id="inc-equipo" v-model="form.equipo" label="Equipo afectado" :options="equipoSelectOptions" placeholder="Selecciona un equipo" :error="formErrors.equipo" />
        <BaseSelect id="inc-tipo" v-model="form.tipo_incidencia" label="Tipo de incidencia" :options="tipoIncidenciaOptions" :error="formErrors.tipo_incidencia" />
        <BaseSelect v-if="canManageAll && isEditing" id="inc-estado" v-model="form.estado" label="Estado" :options="estadoOptions" />
        <div class="sm:col-span-2">
          <BaseTextarea id="inc-descripcion" v-model="form.descripcion" appearance="light" label="Descripción de lo ocurrido" placeholder="Describe la falla o el problema" :rows="3" :error="formErrors.descripcion" />
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="incidencia-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Reportar' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Eliminar incidencia" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        La incidencia sobre <strong class="text-slate-900">{{ pendingDelete?.equipo_codigo }}</strong> se eliminará. Esta acción no se puede deshacer.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

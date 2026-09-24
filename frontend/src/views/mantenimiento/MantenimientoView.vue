<script setup>
import { watch } from 'vue';
import { useRoute } from 'vue-router';

import {
  CalendarClock,
  CheckCircle2,
  Eye,
  MonitorCog,
  Pencil,
  Play,
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
import MantenimientoFinalizeModal from '@/components/mantenimiento/MantenimientoFinalizeModal.vue';
import { useMantenimiento } from '@/composables/mantenimiento/useMantenimiento';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'fecha', label: 'Fecha' },
  { key: 'tipo', label: 'Tipo de mantenimiento' },
  { key: 'incidencia', label: 'Origen' },
  { key: 'tecnico', label: 'Técnico responsable' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  mantenimientos,
  loading,
  saving,
  finalizing,
  modalOpen,
  finalizeModalOpen,
  detailOpen,
  deleteModalOpen,
  pendingDelete,
  form,
  finalizeForm,
  formErrors,
  finalizeErrors,
  finalizingTicket,
  selectedTicket,
  filters,
  pagination,
  stats,
  toast,
  isEditing,
  canDelete,
  canCreate,
  canEdit,
  tipoOptions,
  estadoOptions,
  estadoEdicionOptions,
  equipoSelectOptions,
  tecnicoSelectOptions,
  resultadoFinalOptions,
  openCreate,
  openEdit,
  openFinalize,
  closeFinalize,
  startMaintenance,
  finalizeMaintenance,
  openDetail,
  closeDetail,
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

const route = useRoute();

watch(
  mantenimientos,
  (tickets) => {
    const ticketId = Number(route.query.ticket_id);
    if (!ticketId || detailOpen.value) return;
    const ticket = tickets.find((item) => item.id === ticketId);
    if (ticket) openDetail(ticket);
  },
  { immediate: true },
);

const estadoClasses = {
  pendiente: 'bg-slate-100 text-slate-600',
  en_proceso: 'bg-warning-50 text-warning-700',
  resuelto: 'bg-success-50 text-success-700',
  cancelado: 'bg-danger-50 text-danger-700',
};

const estadoDotClasses = {
  pendiente: 'bg-slate-400',
  en_proceso: 'bg-warning-500',
  resuelto: 'bg-success-500',
  cancelado: 'bg-danger-500',
};

const estadoLabels = {
  pendiente: 'Pendiente',
  en_proceso: 'En atención',
  resuelto: 'Finalizado',
  cancelado: 'Cancelado',
};

const resultadoLabels = {
  en_uso: 'Funcional / en uso',
  en_mantenimiento: 'En mantenimiento',
  dañado: 'Dañado',
  de_baja: 'De baja',
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
      <BaseButton v-if="canCreate" variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Agregar
      </BaseButton>
    </header>

    <section class="grid grid-cols-2 gap-2 sm:gap-4 xl:grid-cols-4">
      <StatCard label="Técnicos registrados" :value="stats.total_tecnicos" tone="blue" helper="Personal activo">
        <template #icon><Wrench :size="20" /></template>
      </StatCard>
      <StatCard label="Dispositivos" :value="stats.total_dispositivos" tone="violet" helper="Equipos registrados">
        <template #icon><MonitorCog :size="20" /></template>
      </StatCard>
      <StatCard label="En atención" :value="stats.en_proceso" tone="emerald" helper="Tickets en curso">
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
      <template #cell-incidencia="{ item }">
        <span v-if="item.incidencia_origen_id" class="font-mono text-xs font-semibold text-warning-700">INC-{{ item.incidencia_origen_id }}</span>
        <span v-else class="text-xs text-slate-400">Preventivo / directo</span>
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
        <div class="flex flex-wrap justify-end gap-1.5">
          <BaseButton
            v-if="canEdit && item.estado === 'pendiente'"
            variant="secondary"
            size="sm"
            :full-width="false"
            @click="startMaintenance(item)"
          >
            <template #icon><Play :size="14" aria-hidden="true" /></template>
            Iniciar atención
          </BaseButton>
          <BaseButton
            v-if="canEdit && item.estado === 'en_proceso'"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="openFinalize(item)"
          >
            <template #icon><CheckCircle2 :size="14" aria-hidden="true" /></template>
            Finalizar mantenimiento
          </BaseButton>
          <BaseButton
            v-if="['resuelto', 'cancelado'].includes(item.estado)"
            variant="ghost"
            size="sm"
            :full-width="false"
            @click="openDetail(item)"
          >
            <template #icon><Eye :size="14" aria-hidden="true" /></template>
            Ver detalle
          </BaseButton>
          <button
            v-if="canEdit && ['pendiente', 'en_proceso'].includes(item.estado)"
            type="button"
            class="grid size-9 place-items-center rounded-lg text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            aria-label="Editar datos del mantenimiento"
            @click="openEdit(item)"
          >
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
        <div v-if="isEditing && form.incidencia_id" class="sm:col-span-2 rounded-xl border border-warning-100 bg-warning-50 px-3 py-2 text-xs text-warning-800">
          Orden correctiva derivada de la incidencia <strong>INC-{{ form.incidencia_id }}</strong>.
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
        <BaseSelect v-if="isEditing"
          id="mant-estado-form"
          v-model="form.estado"
          label="Estado"
          :options="estadoEdicionOptions"
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

    <MantenimientoFinalizeModal
      :open="finalizeModalOpen"
      :ticket="finalizingTicket"
      :form="finalizeForm"
      :errors="finalizeErrors"
      :saving="finalizing"
      :resultado-options="resultadoFinalOptions"
      @close="closeFinalize"
      @submit="finalizeMaintenance"
    />

    <BaseModal
      :open="detailOpen"
      :title="selectedTicket ? `Mantenimiento #${selectedTicket.id}` : 'Detalle de mantenimiento'"
      description="Consulta el resultado y la trazabilidad de la orden."
      size="lg"
      @close="closeDetail"
    >
      <div v-if="selectedTicket" class="grid gap-5">
        <section class="grid gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:grid-cols-2">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Equipo</p>
            <p class="mt-1 text-sm font-bold text-slate-900">{{ selectedTicket.equipo?.codigo || '—' }}</p>
            <p class="text-xs text-slate-500">{{ selectedTicket.equipo?.marca }} {{ selectedTicket.equipo?.modelo }}</p>
          </div>
          <div>
            <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Estado</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ estadoLabels[selectedTicket.estado] ?? selectedTicket.estado_display }}</p>
          </div>
          <div>
            <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Tipo</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ selectedTicket.tipo_mantenimiento_display }}</p>
          </div>
          <div>
            <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Resultado del equipo</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ resultadoLabels[selectedTicket.resultado_equipo] || 'Pendiente de resultado' }}</p>
          </div>
          <div v-if="selectedTicket.incidencia_origen_id" class="sm:col-span-2">
            <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Incidencia relacionada</p>
            <p class="mt-1 text-sm font-semibold text-warning-700">INC-{{ selectedTicket.incidencia_origen_id }}</p>
          </div>
        </section>
        <section class="grid gap-4 sm:grid-cols-2">
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Diagnóstico</p>
            <p class="mt-1 whitespace-pre-line text-sm leading-6 text-slate-700">{{ selectedTicket.diagnostico || 'No registrado' }}</p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Trabajo realizado</p>
            <p class="mt-1 whitespace-pre-line text-sm leading-6 text-slate-700">{{ selectedTicket.trabajo_realizado || 'No registrado' }}</p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Prueba de funcionamiento</p>
            <p class="mt-1 text-sm text-slate-700">{{ selectedTicket.prueba_realizada ? 'Realizada' : 'No registrada' }}</p>
            <p v-if="selectedTicket.observacion_prueba" class="mt-1 whitespace-pre-line text-xs text-slate-500">{{ selectedTicket.observacion_prueba }}</p>
          </div>
          <div>
            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Técnico responsable</p>
            <p class="mt-1 text-sm text-slate-700">{{ selectedTicket.tecnico_responsable || 'Sin asignar' }}</p>
          </div>
        </section>
      </div>
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

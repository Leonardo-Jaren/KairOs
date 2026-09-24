<script setup>
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Eye,
  ListChecks,
  Pencil,
  Plus,
  Search,
  Trash2,
  Wrench,
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
import AuditTimelineList from '@/components/historial/AuditTimelineList.vue';
import { useIncidencias } from '@/composables/incidencias/useIncidencias';
import { formatDate } from '@/utils/formatters';

const columns = [
  { key: 'tipo_incidencia', label: 'Tipo' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'espacio', label: 'Espacio' },
  { key: 'prioridad', label: 'Prioridad' },
  { key: 'antiguedad', label: 'Antigüedad' },
  { key: 'descripcion', label: 'Descripción' },
  { key: 'reportado_por', label: 'Reportado por' },
  { key: 'tecnico', label: 'Técnico asignado' },
  { key: 'mantenimiento', label: 'Órdenes' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  incidencias,
  loading,
  saving,
  correctiveSaving,
  modalOpen,
  deleteModalOpen,
  detailOpen,
  detailLoading,
  selectedIncidencia,
  detailEvents,
  detailMaintenances,
  pendingDelete,
  form,
  formErrors,
  filters,
  pagination,
  stats,
  toast,
  isEditing,
  canManageAll,
  canCreate,
  canDelete,
  tipoIncidenciaOptions,
  estadoOptions,
  espacioSelectOptions,
  equipoSelectOptions,
  formEquipoSelectOptions,
  tecnicoSelectOptions,
  prioridadOptions,
  openCreate,
  openEdit,
  closeModal,
  openDetail,
  closeDetail,
  submit,
  attendIncident,
  closeIncident,
  askDelete,
  cancelDelete,
  confirmDelete,
  createCorrective,
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
  cerrado: 'bg-success-100 text-success-800',
  cancelado: 'bg-danger-50 text-danger-700',
  duplicado: 'bg-slate-100 text-slate-500',
};

const estadoDotClasses = {
  pendiente: 'bg-slate-400',
  en_proceso: 'bg-warning-500',
  resuelto: 'bg-success-500',
  cerrado: 'bg-success-600',
  cancelado: 'bg-danger-500',
  duplicado: 'bg-slate-400',
};

const estadoLabels = {
  pendiente: 'Pendiente de atención',
  en_proceso: 'En atención',
  resuelto: 'Resuelta',
  cerrado: 'Cerrada',
  cancelado: 'Cancelada',
  duplicado: 'Duplicada',
};

const progressSteps = [
  { key: 'reporte', label: 'Reportada' },
  { key: 'atencion', label: 'En atención' },
  { key: 'mantenimiento', label: 'Mantenimiento' },
  { key: 'verificacion', label: 'Equipo verificado' },
  { key: 'cierre', label: 'Cerrada' },
];

const progressIndex = (incidencia) => {
  if (!incidencia) return 0;
  if (incidencia.estado === 'cerrado') return 4;
  if (incidencia.estado === 'resuelto') return 3;
  if (incidencia.estado === 'en_proceso') {
    const hasMaintenance = detailOpen.value && selectedIncidencia.value?.id === incidencia.id
      ? detailMaintenances.value.length > 0
      : incidencia.mantenimientos_count > 0;
    return hasMaintenance ? 2 : 1;
  }
  return 0;
};

const cerradaPorMantenimiento = (incidencia) => (
  incidencia?.estado === 'cerrado'
  && detailMaintenances.value.some(
    (ticket) => ticket.estado === 'resuelto'
      && ticket.resultado_equipo === 'en_uso'
      && ticket.prueba_realizada,
  )
);

const prioridadClasses = {
  baja: 'bg-slate-100 text-slate-600',
  media: 'bg-primary-50 text-primary-700',
  alta: 'bg-warning-50 text-warning-700',
  critica: 'bg-danger-50 text-danger-700',
};

const formatAge = (createdAt) => {
  if (!createdAt) return '—';
  const minutes = Math.max(0, Math.floor((Date.now() - new Date(createdAt).getTime()) / 60000));
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h`;
  const days = Math.floor(hours / 24);
  return `${days} día${days === 1 ? '' : 's'}`;
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
      <BaseButton v-if="canCreate" variant="accent" :full-width="false" @click="openCreate">
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
          <div class="w-full min-w-40 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-prioridad"
              v-model="filters.prioridad"
              :options="prioridadOptions"
              placeholder="Todas las prioridades"
            />
          </div>
          <div v-if="canManageAll" class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="incidencias-asignado"
              v-model="filters.asignado_a_id"
              :options="tecnicoSelectOptions"
              placeholder="Todos los técnicos"
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
      <template #cell-prioridad="{ item }">
        <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold" :class="prioridadClasses[item.prioridad]">
          {{ item.prioridad_display }}
        </span>
      </template>
      <template #cell-antiguedad="{ item }">
        <span class="whitespace-nowrap text-xs font-semibold text-slate-500">{{ formatAge(item.created_at) }}</span>
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
          {{ estadoLabels[item.estado] ?? item.estado_display }}
        </span>
        <p v-if="item.fecha_resolucion" class="mt-1 text-xs text-slate-400">
          Resuelta el {{ formatDate(item.fecha_resolucion) }}
        </p>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex flex-wrap justify-end gap-1.5">
          <BaseButton
            v-if="canManageAll && item.estado === 'pendiente'"
            variant="secondary"
            size="sm"
            :full-width="false"
            @click="attendIncident(item)"
          >
            Atender incidencia
          </BaseButton>
          <BaseButton
            v-if="canManageAll && (item.estado === 'en_proceso' || item.requiere_otra_intervencion) && !['cerrado', 'cancelado', 'duplicado'].includes(item.estado)"
            variant="accent"
            size="sm"
            :full-width="false"
            :disabled="correctiveSaving"
            @click="createCorrective(item)"
          >
            <template #icon><Wrench :size="14" aria-hidden="true" /></template>
            {{ item.requiere_otra_intervencion ? 'Otra intervención' : 'Crear correctivo' }}
          </BaseButton>
          <BaseButton
            v-if="canManageAll && item.estado === 'resuelto'"
            variant="secondary"
            size="sm"
            :full-width="false"
            @click="closeIncident(item)"
          >
            Cerrar incidencia
          </BaseButton>
          <button type="button" class="grid size-9 place-items-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500" aria-label="Ver detalle de incidencia" @click="openDetail(item)">
            <Eye :size="17" />
          </button>
          <template v-if="canManageAll">
          <button v-if="!['cerrado', 'cancelado', 'duplicado'].includes(item.estado)" type="button" class="grid size-9 place-items-center rounded-lg text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500" aria-label="Editar datos de incidencia" @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button v-if="canDelete && !['cerrado', 'cancelado', 'duplicado'].includes(item.estado)" type="button" class="grid size-9 place-items-center rounded-lg text-slate-400 transition-colors hover:bg-danger-50 hover:text-danger-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger-500" aria-label="Eliminar incidencia" @click="askDelete(item)">
            <Trash2 :size="17" />
          </button>
          </template>
        </div>
      </template>
      <template #cell-tecnico="{ item }">
        <span class="text-xs text-slate-600">{{ item.tecnico_asignado?.nombre_completo || 'Sin asignar' }}</span>
      </template>
      <template #cell-mantenimiento="{ item }">
        <span class="rounded-full px-2 py-1 text-[10px] font-bold" :class="item.mantenimientos_count ? 'bg-warning-50 text-warning-700' : 'bg-slate-100 text-slate-500'">
          {{ item.mantenimientos_count || 0 }}
        </span>
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
        <BaseSelect id="inc-equipo" v-model="form.equipo" label="Equipo afectado" :options="formEquipoSelectOptions" placeholder="Selecciona primero un espacio" :error="formErrors.equipo" />
        <BaseSelect id="inc-tipo" v-model="form.tipo_incidencia" label="Tipo de incidencia" :options="tipoIncidenciaOptions" :error="formErrors.tipo_incidencia" />
        <BaseSelect id="inc-prioridad" v-model="form.prioridad" label="Prioridad" :options="prioridadOptions" :error="formErrors.prioridad" />
        <BaseSelect v-if="canManageAll && isEditing" id="inc-estado" v-model="form.estado" label="Estado" :options="estadoOptions" />
        <BaseSelect v-if="canManageAll && isEditing" id="inc-asignado" v-model="form.asignado_a" label="Técnico asignado" :options="tecnicoSelectOptions" placeholder="Sin asignar" />
        <div class="sm:col-span-2">
          <BaseTextarea id="inc-descripcion" v-model="form.descripcion" appearance="light" label="Descripción de lo ocurrido" placeholder="Describe la falla o el problema" :rows="3" :error="formErrors.descripcion" />
        </div>
        <div v-if="canManageAll && isEditing && ['resuelto', 'cerrado'].includes(form.estado)" class="sm:col-span-2">
          <BaseTextarea id="inc-resolucion" v-model="form.resolucion" appearance="light" label="Resolución" placeholder="Describe cómo se solucionó" :rows="3" :error="formErrors.resolucion" />
        </div>
        <div v-if="canManageAll && isEditing && ['cancelado', 'duplicado'].includes(form.estado)" class="sm:col-span-2">
          <BaseTextarea id="inc-motivo-cierre" v-model="form.motivo_cierre" appearance="light" label="Motivo de cierre" placeholder="Explica por qué se cerró" :rows="2" :error="formErrors.motivo_cierre" />
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

    <BaseModal
      :open="detailOpen"
      :title="selectedIncidencia ? `INC-${selectedIncidencia.id} · ${selectedIncidencia.equipo_codigo}` : 'Detalle de incidencia'"
      description="Seguimiento operativo, resolución y órdenes relacionadas."
      size="lg"
      @close="closeDetail"
    >
      <div v-if="detailLoading" class="py-10 text-center text-sm text-slate-400">Cargando detalle...</div>
      <div v-else-if="selectedIncidencia" class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section>
          <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-sm font-extrabold text-slate-900">Progreso del caso</h3>
              <span class="text-xs font-semibold text-slate-500">{{ estadoLabels[selectedIncidencia.estado] ?? selectedIncidencia.estado_display }}</span>
            </div>
            <div class="mt-4 grid grid-cols-5 gap-1">
              <div v-for="(step, index) in progressSteps" :key="step.key" class="flex min-w-0 flex-col items-center gap-2 text-center">
                <div
                  class="grid size-8 place-items-center rounded-full border text-xs font-bold transition-colors"
                  :class="index <= progressIndex(selectedIncidencia) ? 'border-primary-500 bg-primary-500 text-white' : 'border-slate-200 bg-white text-slate-400'"
                >
                  {{ index + 1 }}
                </div>
                <span class="text-[10px] font-semibold leading-4" :class="index <= progressIndex(selectedIncidencia) ? 'text-primary-700' : 'text-slate-400'">{{ step.label }}</span>
              </div>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3 rounded-2xl border border-slate-200 p-4">
            <div>
              <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Estado</p>
              <p class="mt-1 text-sm font-semibold text-slate-800">{{ estadoLabels[selectedIncidencia.estado] ?? selectedIncidencia.estado_display }}</p>
            </div>
            <div>
              <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Prioridad</p>
              <p class="mt-1 text-sm font-semibold text-slate-800">{{ selectedIncidencia.prioridad_display }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Descripción</p>
              <p class="mt-1 text-sm leading-6 text-slate-700">{{ selectedIncidencia.descripcion }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Resolución</p>
              <p class="mt-1 text-sm leading-6 text-slate-700">{{ selectedIncidencia.resolucion || 'Pendiente de resolución' }}</p>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-2">
            <BaseButton
              v-if="canManageAll && selectedIncidencia.estado === 'pendiente'"
              variant="secondary"
              size="sm"
              :full-width="false"
              @click="attendIncident(selectedIncidencia)"
            >
              Atender incidencia
            </BaseButton>
            <BaseButton
              v-if="canManageAll && (selectedIncidencia.estado === 'en_proceso' || selectedIncidencia.requiere_otra_intervencion)"
              variant="accent"
              size="sm"
              :full-width="false"
              :disabled="correctiveSaving"
              @click="createCorrective(selectedIncidencia)"
            >
              <template #icon><Wrench :size="14" aria-hidden="true" /></template>
              {{ selectedIncidencia.requiere_otra_intervencion ? 'Crear otra intervención' : 'Crear correctivo' }}
            </BaseButton>
            <BaseButton
              v-if="canManageAll && selectedIncidencia.estado === 'resuelto'"
              variant="secondary"
              size="sm"
              :full-width="false"
              @click="closeIncident(selectedIncidencia)"
            >
              Cerrar incidencia
            </BaseButton>
          </div>
          <div v-if="cerradaPorMantenimiento(selectedIncidencia)" class="mt-4 rounded-xl border border-success-200 bg-success-50 px-3 py-3 text-sm text-success-800" role="status">
            Equipo verificado como funcional. Esta incidencia fue cerrada automáticamente al finalizar el mantenimiento.
          </div>
          <div v-if="selectedIncidencia.requiere_otra_intervencion" class="mt-4 flex flex-col gap-3 rounded-xl border border-warning-200 bg-warning-50 px-3 py-3 sm:flex-row sm:items-center sm:justify-between" role="alert">
            <div class="flex items-start gap-2 text-sm text-warning-800">
              <AlertTriangle :size="17" class="mt-0.5 shrink-0" aria-hidden="true" />
              <p>El equipo no quedó funcional. Requiere otra intervención.</p>
            </div>
            <BaseButton v-if="canManageAll" variant="secondary" size="sm" :full-width="false" :disabled="correctiveSaving" @click="createCorrective(selectedIncidencia)">
              <template #icon><Wrench :size="14" aria-hidden="true" /></template>
              Crear correctivo
            </BaseButton>
          </div>
          <h3 class="mt-5 text-sm font-extrabold text-slate-900">Mantenimientos relacionados</h3>
          <div v-if="!detailMaintenances.length" class="mt-3 rounded-xl bg-slate-50 px-4 py-4 text-xs text-slate-500">Esta incidencia todavía no tiene una orden asociada.</div>
          <ul v-else class="mt-3 space-y-2">
            <li v-for="ticket in detailMaintenances" :key="ticket.id" class="rounded-xl border border-slate-200 p-3">
              <div class="flex items-center justify-between gap-3">
                <span class="text-xs font-bold text-slate-800">{{ ticket.tipo_mantenimiento_display }}</span>
                <span class="text-[10px] font-bold uppercase tracking-wide text-primary-600">{{ estadoLabels[ticket.estado] ?? ticket.estado_display }}</span>
              </div>
              <p class="mt-1 text-xs leading-5 text-slate-600">{{ ticket.descripcion }}</p>
              <p v-if="ticket.trabajo_realizado" class="mt-1 text-[11px] text-slate-400">Trabajo: {{ ticket.trabajo_realizado }}</p>
              <p v-if="ticket.resultado_equipo" class="mt-1 text-[11px] font-semibold text-slate-500">Resultado: {{ ticket.resultado_equipo === 'en_uso' ? 'Funcional / en uso' : ticket.resultado_equipo }}</p>
              <RouterLink :to="{ path: '/mantenimiento', query: { ticket_id: ticket.id } }" class="mt-2 inline-flex text-xs font-bold text-primary-600 hover:text-primary-700">
                Ver mantenimiento
              </RouterLink>
            </li>
          </ul>
        </section>
        <section>
          <h3 class="mb-3 text-sm font-extrabold text-slate-900">Línea de tiempo</h3>
          <AuditTimelineList :events="detailEvents" :loading="false" :inline="true" />
        </section>
      </div>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

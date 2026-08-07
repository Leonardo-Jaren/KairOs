<script setup>
import {
  AlertTriangle,
  Boxes,
  Eye,
  MonitorCog,
  Pencil,
  Plus,
  Search,
  Trash2,
  Wrench,
} from '@lucide/vue';
import { shallowRef } from 'vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import EquipoDetailModal from '@/components/equipos/EquipoDetailModal.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useEquipos } from '@/composables/equipos/useEquipos';

const columns = [
  { key: 'codigo', label: 'Código' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'marca_modelo', label: 'Marca y modelo' },
  { key: 'numero_serie', label: 'N° de serie' },
  { key: 'espacio', label: 'Espacio' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  equipos,
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
  tipoEquipoOptions,
  modoAdquisicionOptions,
  estadoOptions,
  espacioSelectOptions,
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
} = useEquipos();

const detailEquipo = shallowRef(null);

const estadoClasses = {
  en_uso: 'bg-success-50 text-success-700',
  en_mantenimiento: 'bg-warning-50 text-warning-700',
  dañado: 'bg-danger-50 text-danger-700',
  de_baja: 'bg-slate-100 text-slate-600',
};

const estadoDotClasses = {
  en_uso: 'bg-success-500',
  en_mantenimiento: 'bg-warning-500',
  dañado: 'bg-danger-500',
  de_baja: 'bg-slate-400',
};
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Inventario</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Equipos</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Administra el inventario de hardware, su ubicación y estado operativo.
        </p>
      </div>
      <BaseButton v-if="canManageAll" variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Agregar
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Equipos registrados" :value="stats.total" tone="blue">
        <template #icon><MonitorCog :size="20" /></template>
      </StatCard>
      <StatCard label="En uso" :value="stats.en_uso" tone="emerald">
        <template #icon><Boxes :size="20" /></template>
      </StatCard>
      <StatCard label="En mantenimiento" :value="stats.en_mantenimiento" tone="amber">
        <template #icon><Wrench :size="20" /></template>
      </StatCard>
      <StatCard label="De baja" :value="stats.de_baja" tone="violet">
        <template #icon><AlertTriangle :size="20" /></template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <h2 class="text-base font-bold text-slate-900">Inventario de equipos</h2>
      </div>
      <form class="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px_180px_auto_auto]" @submit.prevent="applyFilters">
        <BaseInput
          id="equipos-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por código, serie, marca o modelo"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <BaseSelect
          id="equipos-tipo"
          v-model="filters.tipo_equipo"
          :options="tipoEquipoOptions"
          placeholder="Todos los tipos"
        />
        <BaseSelect
          id="equipos-estado"
          v-model="filters.estado"
          :options="estadoOptions"
          placeholder="Todos los estados"
        />
        <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="equipos"
      :loading="loading"
      empty-message="No se encontraron equipos con los filtros actuales."
    >
      <template #cell-codigo="{ item }">
        <span class="font-mono text-sm font-semibold text-slate-900">{{ item.codigo }}</span>
      </template>
      <template #cell-tipo="{ item }">
        <span class="inline-flex rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700">
          {{ item.tipo_equipo_display }}
        </span>
      </template>
      <template #cell-marca_modelo="{ item }">
        <div>
          <p class="font-semibold text-slate-900">{{ item.marca }}</p>
          <p class="text-xs text-slate-500">{{ item.modelo }}</p>
        </div>
      </template>
      <template #cell-numero_serie="{ item }">
        <span class="font-mono text-xs text-slate-600">{{ item.numero_serie }}</span>
      </template>
      <template #cell-espacio="{ item }">
        <span class="text-sm text-slate-600">{{ item.espacio_nombre ?? 'Sin asignar' }}</span>
      </template>
      <template #cell-estado="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="estadoClasses[item.estado]"
        >
          <span class="size-1.5 rounded-full" :class="estadoDotClasses[item.estado]" />
          {{ item.estado_display }}
        </span>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label="Ver detalle" @click="detailEquipo = item">
            <Eye :size="17" />
          </button>
          <template v-if="canManageAll">
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar equipo" @click="openEdit(item)">
              <Pencil :size="17" />
            </button>
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Retirar equipo" @click="askDelete(item)">
              <Trash2 :size="17" />
            </button>
          </template>
        </div>
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
      :title="isEditing ? 'Editar equipo' : 'Nuevo equipo'"
      description="Registra los datos técnicos y de adquisición del equipo."
      size="lg"
      @close="closeModal"
    >
      <form id="equipo-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <BaseInput id="equipo-codigo" v-model="form.codigo" appearance="light" label="Código interno" placeholder="LAB203-PC01" :error="formErrors.codigo" />
        <BaseInput id="equipo-serie" v-model="form.numero_serie" appearance="light" label="Número de serie" placeholder="SN-000123" :error="formErrors.numero_serie" />
        <BaseSelect id="equipo-tipo" v-model="form.tipo_equipo" label="Tipo de equipo" :options="tipoEquipoOptions" :error="formErrors.tipo_equipo" />
        <BaseSelect id="equipo-espacio" v-model="form.espacio" label="Espacio asignado" :options="espacioSelectOptions" placeholder="Sin asignar" />
        <BaseInput id="equipo-marca" v-model="form.marca" appearance="light" label="Marca" placeholder="HP" :error="formErrors.marca" />
        <BaseInput id="equipo-modelo" v-model="form.modelo" appearance="light" label="Modelo" placeholder="ProDesk 400" :error="formErrors.modelo" />
        <BaseInput id="equipo-mac" v-model="form.numero_mac" appearance="light" label="Dirección MAC" placeholder="MAC:10001:10F" />
        <BaseSelect id="equipo-adquisicion" v-model="form.modo_adquisicion" label="Modo de adquisición" :options="modoAdquisicionOptions" :error="formErrors.modo_adquisicion" />
        <BaseInput id="equipo-fecha-adq" v-model="form.fecha_adquisicion" type="date" appearance="light" label="Fecha de adquisición" :error="formErrors.fecha_adquisicion" />
        <BaseInput id="equipo-fecha-ren" v-model="form.fecha_renovacion" type="date" appearance="light" label="Fecha de renovación (opcional)" />
        <BaseSelect id="equipo-estado" v-model="form.estado" label="Estado" :options="estadoOptions" :error="formErrors.estado" />
        <BaseInput id="equipo-responsable" v-model="form.responsable_usuario" appearance="light" label="Usuario responsable (opcional)" placeholder="Nombre del responsable" />
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="equipo-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear equipo' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Retirar equipo" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        El equipo <strong class="text-slate-900">{{ pendingDelete?.codigo }}</strong> se retirará del inventario, pero se conservará su historial de mantenimientos.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Retirar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />

    <EquipoDetailModal
      :open="detailEquipo !== null"
      :equipo="detailEquipo"
      :can-edit="canManageAll"
      @close="detailEquipo = null"
    />
  </div>
</template>

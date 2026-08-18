<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Infraestructura</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Espacios</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Administra laboratorios, aulas, oficinas y la distribución de sus equipos.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <BaseButton variant="secondary" :full-width="false" @click="$router.push('/espacios/mapa')">
          <template #icon><Map :size="18" /></template>
          Mapa de campus
        </BaseButton>
        <BaseButton variant="secondary" :full-width="false" @click="$router.push('/espacios/usuarios')">
          Usuarios por espacio
        </BaseButton>
        <BaseButton v-if="canEdit" variant="accent" :full-width="false" @click="openCreate">
          <template #icon>
            <Plus :size="18" />
          </template>
          Nuevo espacio
        </BaseButton>
      </div>
    </header>

    <section class="grid grid-cols-2 gap-2 sm:gap-4 xl:grid-cols-4">
      <StatCard label="Espacios registrados" :value="stats.total" tone="blue">
        <template #icon>
          <Building2 :size="20" />
        </template>
      </StatCard>
      <StatCard label="Espacios activos" :value="stats.activos" tone="emerald">
        <template #icon>
          <Building2 :size="20" />
        </template>
      </StatCard>
      <StatCard label="Laboratorios activos" :value="stats.laboratorios" tone="violet">
        <template #icon>
          <FlaskConical :size="20" />
        </template>
      </StatCard>
      <StatCard label="Equipos distribuidos" :value="stats.equipos" tone="amber">
        <template #icon>
          <Monitor :size="20" />
        </template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <form class="grid gap-3 md:grid-cols-[minmax(240px,1fr)_190px_170px_auto]" @submit.prevent="applyFilters">
        <BaseInput id="spaces-search" v-model="filters.search" appearance="light"
          placeholder="Buscar por código, pabellón, piso o responsable">
          <template #icon>
            <Search :size="17" />
          </template>
        </BaseInput>
        <BaseSelect id="spaces-type" v-model="filters.tipo" :options="typeOptions" placeholder="Todos los tipos" />
        <BaseSelect id="spaces-status" v-model="filters.activo"
          :options="[{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }]"
          placeholder="Todos los estados" />
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable :columns="columns" :items="espacios" :loading="loading"
      empty-message="No se encontraron espacios con los filtros actuales.">
      <template #cell-espacio="{ item }">
        <div class="flex items-center gap-3">
          <div class="grid size-10 place-items-center rounded-xl bg-primary-50 text-primary-600">
            <Building2 :size="19" />
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ item.codigo_espacio }}</p>
            <p class="text-xs text-slate-500">Actualizado {{ new Date(item.updated_at).toLocaleDateString() }}</p>
          </div>
        </div>
      </template>
      <template #cell-tipo="{ item }">
        <span class="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-700">{{ item.tipo_display
          }}</span>
      </template>
      <template #cell-ubicacion="{ item }">
        <p class="font-medium text-slate-700">{{ item.pabellon }}</p>
        <p class="text-xs text-slate-400">{{ formatFloor(item.piso) }}</p>
      </template>
      <template #cell-responsable="{ item }">
        <div v-if="item.responsable">
          <p class="font-medium text-slate-700">{{ item.responsable.nombre_completo }}</p>
          <p class="text-xs text-slate-400">{{ item.responsable.correo }}</p>
        </div>
        <span v-else class="text-xs text-slate-400">Sin asignar</span>
      </template>
      <template #cell-equipos="{ item }">
        <span class="font-semibold text-slate-700">{{ item.cantidad_equipos }}</span>
      </template>
      <template #cell-estado="{ item }">
        <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="item.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'">
          <span class="size-1.5 rounded-full" :class="item.activo ? 'bg-success-500' : 'bg-slate-400'" />
          {{ item.activo ? 'Activo' : 'Inactivo' }}
        </span>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex justify-end gap-1">
          <button type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Ver espacio"
            @click="detailEspacio = item">
            <Eye :size="17" />
          </button>
          <button v-if="canEdit" type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar espacio"
            @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button v-if="canEdit" type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
            aria-label="Desactivar espacio" @click="askDelete(item)">
            <Trash2 :size="17" />
          </button>
        </div>
      </template>
    </BaseTable>

    <BasePagination :page="filters.page" :total-pages="pagination.totalPages" :total="pagination.total" :loading="loading"
      @change="changePage" />

    <BaseModal :open="modalOpen" :title="isEditing ? 'Editar espacio' : 'Nuevo espacio'"
      description="Registra la ubicación física y su estado operativo." @close="closeModal">
      <form id="space-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <BaseInput id="space-code" v-model="form.codigo_espacio" appearance="light" label="Código" placeholder="LAB-203"
          :error="formErrors.codigo_espacio" />
        <BaseSelect id="space-type-form" v-model="form.tipo" label="Tipo" :options="typeOptions"
          :error="formErrors.tipo" />
        <BaseSelect id="space-building" v-model="form.edificio_id" label="Edificio"
          :options="buildingOptions" placeholder="Seleccionar edificio" :error="formErrors.edificio_id" />
        <BaseInput id="space-floor" v-model="form.piso" appearance="light" type="number" label="Número de piso" placeholder="2"
          :error="formErrors.piso" />
        <label
          class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <input v-model="form.activo" type="checkbox" class="size-4 accent-primary-500" />
          <span>
            <span class="block text-sm font-semibold text-slate-800">Espacio activo</span>
            <span class="block text-xs text-slate-500">Permite asignar usuarios y equipos a este ambiente.</span>
          </span>
        </label>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="space-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear espacio' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Desactivar espacio" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        El espacio <strong class="text-slate-900">{{ pendingDelete?.codigo_espacio }}</strong> dejará de estar
        disponible
        para nuevas asignaciones. Su historial se conservará.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Desactivar
        </BaseButton>
      </template>
    </BaseModal>

    <EntityDetailModal
      :open="detailEspacio !== null"
      :title="detailEspacio?.codigo_espacio ?? ''"
      description="Información del espacio y registro de auditoría."
      modulo="espacio"
      :object-id="detailEspacio?.id"
      @close="detailEspacio = null"
    >
      <template #info>
        <div class="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Código</dt>
            <dd class="mt-1 text-sm font-semibold text-slate-900">{{ detailEspacio?.codigo_espacio }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Tipo</dt>
            <dd class="mt-1">
              <span class="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-700">
                {{ detailEspacio?.tipo_display }}
              </span>
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Pabellón</dt>
            <dd class="mt-1 text-sm text-slate-700">{{ detailEspacio?.pabellon }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Piso</dt>
            <dd class="mt-1 text-sm text-slate-700">{{ detailEspacio?.piso }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Responsable</dt>
            <dd class="mt-1">
              <template v-if="detailEspacio?.responsable">
                <p class="text-sm font-medium text-slate-900">{{ detailEspacio.responsable.nombre_completo }}</p>
                <p class="text-xs text-slate-400">{{ detailEspacio.responsable.correo }}</p>
              </template>
              <span v-else class="text-xs text-slate-400">Sin asignar</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Equipos asignados</dt>
            <dd class="mt-1 text-sm font-semibold text-slate-900">{{ detailEspacio?.cantidad_equipos ?? 0 }}</dd>
          </div>
          <div class="sm:col-span-2">
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Estado</dt>
            <dd class="mt-1">
              <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="detailEspacio?.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'">
                <span class="size-1.5 rounded-full"
                  :class="detailEspacio?.activo ? 'bg-success-500' : 'bg-slate-400'" />
                {{ detailEspacio?.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </dd>
          </div>
        </div>
      </template>
    </EntityDetailModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

<script setup>
import { shallowRef } from 'vue';
import { Building2, Eye, FlaskConical, Map, Monitor, Pencil, Plus, Search, Trash2 } from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import EntityDetailModal from '@/components/shared/EntityDetailModal.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useEspacios } from '@/composables/espacios/useEspacios';
import { formatFloor } from '@/utils/formatters';

const detailEspacio = shallowRef(null);

const columns = [
  { key: 'espacio', label: 'Espacio' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'responsable', label: 'Responsable' },
  { key: 'equipos', label: 'Equipos' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  espacios, loading, saving, modalOpen, deleteModalOpen, pendingDelete,
  form, formErrors, filters, pagination, stats, toast, canEdit, isEditing,
  typeOptions, buildingOptions, openCreate, openEdit, closeModal, submit, askDelete,
  cancelDelete, confirmDelete, applyFilters, clearFilters, changePage,
  closeToast,
} = useEspacios();
</script>

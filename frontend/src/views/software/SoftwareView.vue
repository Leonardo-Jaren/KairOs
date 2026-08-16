<script setup>
import {
  CalendarClock,
  Eye,
  Layers,
  Pencil,
  Plus,
  Search,
  ShieldAlert,
  Trash2,
} from '@lucide/vue';
import { shallowRef } from 'vue';

import ProductoDetailModal from '@/components/software/ProductoDetailModal.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useSoftware } from '@/composables/software/useSoftware';
import { formatDate } from '@/utils/formatters';

const columns = [
  { key: 'software', label: 'Software' },
  { key: 'tipo_licencia', label: 'Licencia' },
  { key: 'licencias', label: 'Licencias (usadas/disp.)' },
  { key: 'fecha_expiracion', label: 'Expiración' },
  { key: 'alertas', label: 'Alertas' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  productos,
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
  tipoLicenciaOptions,
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
} = useSoftware();

const detailProducto = shallowRef(null);
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Inventario</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Software</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Administra el catálogo de productos de software y sus licencias.
        </p>
      </div>
      <BaseButton v-if="canManageAll" variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Agregar
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard label="Productos registrados" :value="stats.total_productos" tone="blue">
        <template #icon><Layers :size="20" /></template>
      </StatCard>
      <StatCard label="Licencias por expirar" :value="stats.licencias_por_expirar" tone="amber">
        <template #icon><CalendarClock :size="20" /></template>
      </StatCard>
      <StatCard label="Productos con sobre-uso" :value="stats.productos_sobre_uso" tone="violet">
        <template #icon><ShieldAlert :size="20" /></template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <h2 class="text-base font-bold text-slate-900">Catálogo de software</h2>
      </div>
      <form class="grid gap-3 md:grid-cols-[minmax(220px,1fr)_200px_auto_auto]" @submit.prevent="applyFilters">
        <BaseInput
          id="software-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por nombre o versión"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <BaseSelect
          id="software-tipo-licencia"
          v-model="filters.tipo_licencia"
          :options="tipoLicenciaOptions"
          placeholder="Todos los tipos de licencia"
        />
        <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="productos"
      :loading="loading"
      empty-message="No se encontraron productos de software con los filtros actuales."
    >
      <template #cell-software="{ item }">
        <div>
          <p class="font-semibold text-slate-900">{{ item.software }}</p>
          <p class="text-xs text-slate-500">v{{ item.version }}</p>
        </div>
      </template>
      <template #cell-tipo_licencia="{ item }">
        <span class="inline-flex rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700">
          {{ item.tipo_licencia_display }}
        </span>
      </template>
      <template #cell-licencias="{ item }">
        <span class="text-sm text-slate-600">
          {{ item.licencias_usadas }} / {{ item.licencias_totales }}
          <span class="text-xs text-slate-400">({{ item.licencias_disponibles }} disp.)</span>
        </span>
      </template>
      <template #cell-fecha_expiracion="{ item }">
        <span class="text-sm text-slate-600">
          {{ item.fecha_expiracion ? formatDate(item.fecha_expiracion) : 'Sin expiración' }}
        </span>
      </template>
      <template #cell-alertas="{ item }">
        <div class="flex flex-wrap gap-1.5">
          <span v-if="item.sobre_uso" class="rounded-full bg-danger-50 px-2 py-0.5 text-xs font-semibold text-danger-700">Sobre-uso</span>
          <span v-if="item.proxima_a_expirar" class="rounded-full bg-warning-50 px-2 py-0.5 text-xs font-semibold text-warning-700">Por expirar</span>
          <span v-if="!item.sobre_uso && !item.proxima_a_expirar" class="text-xs text-slate-400">—</span>
        </div>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label="Ver detalle" @click="detailProducto = item">
            <Eye :size="17" />
          </button>
          <template v-if="canManageAll">
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar producto" @click="openEdit(item)">
              <Pencil :size="17" />
            </button>
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Eliminar producto" @click="askDelete(item)">
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
      :title="isEditing ? 'Editar producto de software' : 'Nuevo producto de software'"
      description="Registra los datos de licenciamiento del producto."
      size="lg"
      @close="closeModal"
    >
      <form id="software-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <BaseInput id="software-nombre" v-model="form.software" appearance="light" label="Software" placeholder="Ej: Office" :error="formErrors.software" />
        <BaseInput id="software-version" v-model="form.version" appearance="light" label="Versión" placeholder="Ej: 2021, 365" :error="formErrors.version" />
        <BaseSelect id="software-tipo" v-model="form.tipo_licencia" label="Tipo de licencia" :options="tipoLicenciaOptions" :error="formErrors.tipo_licencia" />
        <BaseInput id="software-licencias" v-model="form.licencias_totales" type="number" min="0" appearance="light" label="Licencias totales" :error="formErrors.licencias_totales" />
        <BaseInput id="software-expiracion" v-model="form.fecha_expiracion" type="date" appearance="light" label="Fecha de expiración (opcional)" />
        <BaseInput id="software-costo" v-model="form.costo_anual_total" type="number" min="0" step="0.01" appearance="light" label="Costo anual (opcional)" />
        <div class="sm:col-span-2">
          <BaseTextarea id="software-descripcion" v-model="form.descripcion" appearance="light" label="Descripción (opcional)" :rows="2" />
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="software-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear producto' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Eliminar producto de software" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        El producto <strong class="text-slate-900">{{ pendingDelete?.software }} v{{ pendingDelete?.version }}</strong> se eliminará del catálogo. Esta acción solo es posible si no tiene instalaciones vigentes.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />

    <ProductoDetailModal
      :open="detailProducto !== null"
      :producto="detailProducto"
      :can-edit="canManageAll"
      @close="detailProducto = null"
    />
  </div>
</template>

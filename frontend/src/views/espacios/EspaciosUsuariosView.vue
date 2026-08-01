<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Control de acceso</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Usuarios por espacio</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Asigna responsables, técnicos y docentes a los ambientes registrados.
        </p>
      </div>
      <BaseButton v-if="canEdit" variant="accent" :full-width="false" @click="openCreate">
        <template #icon>
          <Plus :size="18" />
        </template>
        Nueva asignación
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <StatCard label="Asignaciones encontradas" :value="pagination.total"
        :helper="`${activeCount} activas en esta página`" tone="blue">
        <template #icon>
          <Link2 :size="20" />
        </template>
      </StatCard>
      <StatCard label="Usuarios en la página" :value="uniqueUsers" tone="emerald">
        <template #icon>
          <UserRoundCheck :size="20" />
        </template>
      </StatCard>
      <StatCard label="Espacios en la página" :value="uniqueSpaces" tone="violet">
        <template #icon>
          <Building2 :size="20" />
        </template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <form class="grid gap-3 md:grid-cols-[minmax(240px,1fr)_180px_auto_auto]" @submit.prevent="applyFilters">
        <BaseInput id="assignments-search" v-model="filters.search" appearance="light"
          placeholder="Buscar por usuario, correo, espacio o pabellón">
          <template #icon>
            <Search :size="17" />
          </template>
        </BaseInput>
        <BaseSelect id="assignments-status" v-model="filters.activo" :options="[
          { value: 'true', label: 'Activas' },
          { value: 'false', label: 'Inactivas' },
        ]" placeholder="Todos los estados" />
        <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable :columns="columns" :items="asignaciones" :loading="loading"
      empty-message="No hay asignaciones que coincidan con los filtros.">
      <template #cell-usuario="{ item }">
        <div>
          <p class="font-semibold text-slate-900">{{ item.usuario.nombre_completo }}</p>
          <p class="text-xs text-slate-500">{{ item.usuario.correo }}</p>
        </div>
      </template>
      <template #cell-espacio="{ item }">
        <div class="flex items-center gap-3">
          <div class="grid size-9 place-items-center rounded-lg bg-primary-50 text-primary-600">
            <Building2 :size="17" />
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ item.espacio.codigo_espacio }}</p>
            <p class="text-xs text-slate-500">{{ item.espacio.pabellon }} · Piso {{ item.espacio.piso }}</p>
          </div>
        </div>
      </template>
      <template #cell-responsabilidad="{ item }">
        <span class="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-700">
          {{ item.tipo_responsabilidad_display }}
        </span>
      </template>
      <template #cell-estado="{ item }">
        <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="item.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'">
          <span class="size-1.5 rounded-full" :class="item.activo ? 'bg-success-500' : 'bg-slate-400'" />
          {{ item.activo ? 'Activa' : 'Inactiva' }}
        </span>
      </template>
      <template #cell-acciones="{ item }">
        <div v-if="canEdit" class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
            aria-label="Editar asignación" @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
            aria-label="Eliminar asignación" @click="askDelete(item)">
            <Trash2 :size="17" />
          </button>
        </div>
        <span v-else class="text-xs text-slate-400">Solo lectura</span>
      </template>
    </BaseTable>

    <BasePagination :page="filters.page" :total-pages="pagination.totalPages" :total="pagination.total"
      @change="changePage" />

    <BaseModal :open="modalOpen" :title="isEditing ? 'Editar asignación' : 'Nueva asignación'"
      description="Relaciona una cuenta activa con un ambiente registrado." @close="closeModal">
      <form id="assignment-form" class="grid gap-4" @submit.prevent="submit">
        <BasePaginatedSelect id="assignment-user" v-model="form.usuario_id" label="Usuario"
          placeholder="Seleccionar usuario" search-placeholder="Buscar por nombre o correo"
          :initial-option="selectedUserOption" :load-options="loadUserOptions" :page-size="10"
          :error="formErrors.usuario_id" />
        <BasePaginatedSelect id="assignment-space" v-model="form.espacio_id" label="Espacio"
          placeholder="Seleccionar espacio" search-placeholder="Buscar por código o ubicación"
          :initial-option="selectedSpaceOption" :load-options="loadSpaceOptions" :page-size="10"
          :error="formErrors.espacio_id" />
        <BaseSelect id="assignment-role" v-model="form.tipo_responsabilidad" label="Responsabilidad"
          :options="responsibilityOptions" :error="formErrors.tipo_responsabilidad" />
        <label class="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <input v-model="form.activo" type="checkbox" class="size-4 accent-primary-500" />
          <span>
            <span class="block text-sm font-semibold text-slate-800">Asignación activa</span>
            <span class="block text-xs text-slate-500">La relación aparecerá vigente para consultas operativas.</span>
          </span>
        </label>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="assignment-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear asignación' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Eliminar asignación" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        Se retirará a <strong class="text-slate-900">{{ pendingDelete?.usuario.nombre_completo }}</strong> del espacio
        <strong class="text-slate-900">{{ pendingDelete?.espacio.codigo_espacio }}</strong>. La trazabilidad se
        conservará.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>
<script setup>
import {
  Building2,
  Link2,
  Pencil,
  Plus,
  Search,
  Trash2,
  UserRoundCheck,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BasePaginatedSelect from '@/components/selects/BasePaginatedSelect.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useEspaciosUsuarios } from '@/composables/espacios/useEspaciosUsuarios';

const columns = [
  { key: 'usuario', label: 'Usuario' },
  { key: 'espacio', label: 'Espacio' },
  { key: 'responsabilidad', label: 'Responsabilidad' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  asignaciones,
  loading,
  saving,
  modalOpen,
  deleteModalOpen,
  pendingDelete,
  form,
  formErrors,
  filters,
  pagination,
  toast,
  canEdit,
  isEditing,
  activeCount,
  uniqueSpaces,
  uniqueUsers,
  responsibilityOptions,
  selectedUserOption,
  selectedSpaceOption,
  loadUserOptions,
  loadSpaceOptions,
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
} = useEspaciosUsuarios();
</script>

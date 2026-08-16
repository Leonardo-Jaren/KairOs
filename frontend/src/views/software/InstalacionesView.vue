<script setup>
import { Pencil, Plus, Search, Trash2 } from '@lucide/vue';
import { onMounted } from 'vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useInstalaciones } from '@/composables/software/useInstalaciones';
import { formatDate } from '@/utils/formatters';

const columns = [
  { key: 'producto', label: 'Software' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'espacio', label: 'Espacio' },
  { key: 'licencia', label: 'N° de licencia' },
  { key: 'fecha_instalacion', label: 'Instalado el' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  instalaciones, loading, saving, formOpen, deleteOpen, pendingDelete,
  form, formErrors, filters, pagination, toast, isEditing, canManageAll,
  equipoSelectOptions, productoSelectOptions, espacioSelectOptions,
  cargar, cargarOpciones, openCreate, openEdit, closeForm, submit,
  askDelete, cancelDelete, confirmDelete, applyFilters, clearFilters,
  changePage, closeToast,
} = useInstalaciones();

onMounted(() => {
  cargarOpciones();
  cargar();
});
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Inventario</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Instalaciones de software</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Consulta qué software está instalado en cada equipo de cada espacio.
        </p>
      </div>
      <BaseButton v-if="canManageAll" variant="accent" :full-width="false" @click="openCreate()">
        <template #icon><Plus :size="18" /></template>
        Instalar software
      </BaseButton>
    </header>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <h2 class="text-base font-bold text-slate-900">Instalaciones registradas</h2>
      </div>
      <form class="flex flex-col gap-3" @submit.prevent="applyFilters">
        <BaseInput
          id="instalaciones-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por software, equipo o licencia"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <div class="flex flex-wrap items-end gap-3">
          <div class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="instalaciones-espacio"
              v-model="filters.espacio_id"
              :options="espacioSelectOptions"
              placeholder="Todos los espacios"
            />
          </div>
          <div class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="instalaciones-equipo"
              v-model="filters.equipo_id"
              :options="equipoSelectOptions"
              placeholder="Todos los equipos"
            />
          </div>
          <div class="w-full min-w-44 flex-1 sm:w-auto">
            <BaseSelect
              id="instalaciones-producto"
              v-model="filters.producto_software_id"
              :options="productoSelectOptions"
              placeholder="Todos los productos"
            />
          </div>
          <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
          <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
        </div>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="instalaciones"
      :loading="loading"
      empty-message="No se encontraron instalaciones con los filtros actuales."
    >
      <template #cell-producto="{ item }">
        <span class="font-semibold text-slate-900">{{ item.producto_software_nombre }}</span>
      </template>
      <template #cell-equipo="{ item }">
        <span class="font-mono text-sm font-semibold text-slate-700">{{ item.equipo_codigo }}</span>
      </template>
      <template #cell-espacio="{ item }">
        <span class="text-sm text-slate-600">{{ item.espacio_nombre ?? 'Sin asignar' }}</span>
      </template>
      <template #cell-licencia="{ item }">
        <span class="text-sm text-slate-600">{{ item.numero_licencia_usado || '—' }}</span>
      </template>
      <template #cell-fecha_instalacion="{ item }">
        <span class="text-sm text-slate-600">{{ formatDate(item.fecha_instalacion) }}</span>
      </template>
      <template #cell-acciones="{ item }">
        <div v-if="canManageAll" class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar instalación" @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Eliminar instalación" @click="askDelete(item)">
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
      :open="formOpen"
      :title="isEditing ? 'Editar instalación' : 'Instalar software en un equipo'"
      description="Asocia un producto de software a un equipo del inventario."
      size="md"
      @close="closeForm"
    >
      <form id="instalacion-global-form" class="grid gap-4" @submit.prevent="submit()">
        <BaseSelect
          v-if="!isEditing"
          id="ig-equipo"
          v-model="form.equipo"
          label="Equipo"
          :options="equipoSelectOptions"
          placeholder="Selecciona un equipo"
          :error="formErrors.equipo"
        />
        <BaseSelect
          v-if="!isEditing"
          id="ig-producto"
          v-model="form.producto_software"
          label="Producto de software"
          :options="productoSelectOptions"
          placeholder="Selecciona un producto"
          :error="formErrors.producto_software"
        />
        <BaseInput
          id="ig-licencia"
          v-model="form.numero_licencia_usado"
          appearance="light"
          label="Número de licencia (opcional)"
          placeholder="Ej: LIC-00123"
        />
        <BaseInput
          id="ig-fecha"
          v-model="form.fecha_instalacion"
          type="date"
          appearance="light"
          label="Fecha de instalación"
          :error="formErrors.fecha_instalacion"
        />
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeForm">Cancelar</BaseButton>
        <BaseButton type="submit" form="instalacion-global-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Instalar' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteOpen" title="Eliminar instalación" size="sm" @close="cancelDelete">
      <p class="text-sm text-slate-600">
        ¿Eliminar la instalación de
        <strong class="text-slate-900">{{ pendingDelete?.producto_software_nombre }}</strong>
        en <strong class="text-slate-900">{{ pendingDelete?.equipo_codigo }}</strong>?
        Esto liberará una licencia disponible.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete()">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

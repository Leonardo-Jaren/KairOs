<script setup>
import { Pencil, Plus, Search, Trash2 } from '@lucide/vue';
import { onMounted, ref } from 'vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { TIPO_OPTIONS, getTipoIcon, useComponentes } from '@/composables/equipos/useComponentes';
import { useAuthStore } from '@/stores/auth';
import equiposService from '@/services/equipos.service';

const authStore = useAuthStore();
const canManageAll = ['admin', 'tecnico'].includes(authStore.user?.rol);

const {
  componentes, loading, saving, formOpen, deleteOpen, pendingDelete,
  form, formErrors, filters, pagination, toast, isEditing,
  cargar, openCreate, openEdit, closeForm, submit,
  askDelete, cancelDelete, confirmDelete, clearFilters, changePage, closeToast,
} = useComponentes();

const equipoOptions = ref([]);

const columns = [
  { key: 'tipo',     label: 'Tipo' },
  { key: 'equipo',   label: 'Equipo' },
  { key: 'modelo',   label: 'Modelo' },
  { key: 'desc',     label: 'Descripción' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

onMounted(async () => {
  cargar();
  try {
    const lista = await equiposService.obtenerOpciones();
    equipoOptions.value = lista.map((e) => ({ value: e.id, label: `${e.codigo} — ${e.marca} ${e.modelo}` }));
  } catch { /* no critical */ }
});

</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Inventario</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Componentes</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Listado de todos los componentes de hardware registrados en el sistema.
        </p>
      </div>
      <BaseButton v-if="canManageAll" variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Agregar
      </BaseButton>
    </header>

    <!-- Filtros rápidos por tipo -->
    <section class="flex flex-wrap gap-2">
      <button
        v-for="opt in TIPO_OPTIONS"
        :key="opt.value"
        type="button"
        class="flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold transition-colors"
        :class="filters.tipo === opt.value
          ? 'border-primary-400 bg-primary-50 text-primary-700'
          : 'border-slate-200 bg-white text-slate-600 hover:border-primary-200 hover:text-primary-600'"
        @click="filters.tipo = filters.tipo === opt.value ? '' : opt.value"
      >
        <component :is="opt.icon" :size="14" />
        {{ opt.label }}
      </button>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <form class="grid gap-3 md:grid-cols-[1fr_auto]" @submit.prevent>
        <BaseInput
          id="comp-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por tipo, modelo, descripción o equipo"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="componentes"
      :loading="loading"
      empty-message="No se encontraron componentes con los filtros actuales."
    >
      <template #cell-tipo="{ item }">
        <div class="flex items-center gap-2.5">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
            <component :is="getTipoIcon(item.tipo)" :size="16" />
          </span>
          <span class="text-sm font-semibold text-slate-800">{{ item.tipo_display }}</span>
        </div>
      </template>
      <template #cell-equipo="{ item }">
        <span class="font-mono text-sm font-semibold text-slate-700">{{ item.equipo_codigo ?? '—' }}</span>
      </template>
      <template #cell-modelo="{ item }">
        <span class="text-sm text-slate-700">{{ item.modelo }}</span>
      </template>
      <template #cell-desc="{ item }">
        <span class="text-sm text-slate-500">{{ item.descripcion || '—' }}</span>
      </template>
      <template #cell-acciones="{ item }">
        <div v-if="canManageAll" class="flex justify-end gap-1">
          <button type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
            aria-label="Editar componente"
            @click="openEdit(item)">
            <Pencil :size="17" />
          </button>
          <button type="button"
            class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
            aria-label="Eliminar componente"
            @click="askDelete(item)">
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
      :loading="loading"
      @change="changePage"
    />

    <!-- Modal crear/editar -->
    <BaseModal
      :open="formOpen"
      :title="isEditing ? 'Editar componente' : 'Nuevo componente'"
      description="Registra un componente de hardware asociado a un equipo."
      size="md"
      @close="closeForm"
    >
      <form id="comp-global-form" class="grid gap-4" @submit.prevent="submit(null)">
        <BaseSelect
          v-if="!isEditing"
          id="cg-equipo"
          v-model="form.equipo_id"
          label="Equipo"
          :options="equipoOptions"
          placeholder="Selecciona un equipo"
          :error="formErrors.equipo_id"
        />
        <BaseSelect
          id="cg-tipo"
          v-model="form.tipo"
          label="Tipo"
          :options="TIPO_OPTIONS"
          :error="formErrors.tipo"
        />
        <BaseInput
          id="cg-modelo"
          v-model="form.modelo"
          appearance="light"
          label="Modelo"
          placeholder="Ej: Ryzen 5 5600X"
          :error="formErrors.modelo"
        />
        <BaseTextarea
          id="cg-descripcion"
          v-model="form.descripcion"
          appearance="light"
          label="Descripción (opcional)"
          placeholder="Ej: 16 GB DDR4 3200 MHz"
          :rows="2"
        />
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeForm">Cancelar</BaseButton>
        <BaseButton type="submit" form="comp-global-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear componente' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal eliminar -->
    <BaseModal :open="deleteOpen" title="Eliminar componente" size="sm" @close="cancelDelete">
      <p class="text-sm text-slate-600">
        ¿Eliminar el componente
        <strong class="text-slate-900">{{ pendingDelete?.tipo_display }} · {{ pendingDelete?.modelo }}</strong>?
        Esta acción no se puede deshacer.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete(null)">
          Eliminar
        </BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

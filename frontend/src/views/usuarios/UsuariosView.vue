<script setup>
import {
  Eye,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  UserCheck,
  UsersRound,
  UserX,
  Wrench,
} from '@lucide/vue';
import { shallowRef } from 'vue';

import EntityDetailModal from '@/components/shared/EntityDetailModal.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useUsuarios } from '@/composables/usuarios/useUsuarios';

const detailUsuario = shallowRef(null);

const columns = [
  { key: 'usuario', label: 'Usuario' },
  { key: 'dni', label: 'DNI' },
  { key: 'rol', label: 'Rol' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  usuarios,
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
  canCreate,
  availableRoleOptions,
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
} = useUsuarios();

const roleClasses = {
  admin: 'bg-violet-50 text-violet-700 ring-violet-600/10',
  tecnico: 'bg-primary-50 text-primary-700 ring-primary-600/10',
  docente: 'bg-success-50 text-success-700 ring-success-600/10',
  usuario: 'bg-slate-100 text-slate-700 ring-slate-500/10',
};

const roleLabels = {
  admin: 'Administrador',
  tecnico: 'Técnico',
  docente: 'Docente',
  usuario: 'Usuario',
};
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Administración</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Usuarios</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Gestiona accesos, roles y estado de las cuentas institucionales.
        </p>
      </div>
      <BaseButton v-if="canCreate" variant="accent" :full-width="false" @click="openCreate">
        <template #icon><Plus :size="18" /></template>
        Nuevo usuario
      </BaseButton>
    </header>

    <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Usuarios registrados" :value="stats.total" tone="blue">
        <template #icon><UsersRound :size="20" /></template>
      </StatCard>
      <StatCard label="Cuentas activas" :value="stats.activos" tone="emerald">
        <template #icon><UserCheck :size="20" /></template>
      </StatCard>
      <StatCard label="Administradores" :value="stats.administradores" tone="violet">
        <template #icon><ShieldCheck :size="20" /></template>
      </StatCard>
      <StatCard label="Técnicos y docentes" :value="stats.tecnicos + stats.docentes" tone="amber">
        <template #icon><Wrench :size="20" /></template>
      </StatCard>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <form class="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px_160px_auto_auto]" @submit.prevent="applyFilters">
        <BaseInput
          id="users-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por nombre, correo, usuario o DNI"
        >
          <template #icon><Search :size="17" /></template>
        </BaseInput>
        <BaseSelect
          id="users-role"
          v-model="filters.rol"
          :options="availableRoleOptions"
          placeholder="Todos los roles"
        />
        <BaseSelect
          id="users-status"
          v-model="filters.activo"
          :options="[
            { value: 'true', label: 'Activos' },
            { value: 'false', label: 'Inactivos' },
          ]"
          placeholder="Todos los estados"
        />
        <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
        <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
      </form>
    </section>

    <BaseTable
      :columns="columns"
      :items="usuarios"
      :loading="loading"
      empty-message="No se encontraron usuarios con los filtros actuales."
    >
      <template #cell-usuario="{ item }">
        <div class="flex items-center gap-3">
          <div class="grid size-10 shrink-0 place-items-center rounded-xl bg-primary-50 font-bold text-primary-700">
            {{ item.nombre?.charAt(0) }}{{ item.apellido?.charAt(0) }}
          </div>
          <div>
            <p class="font-semibold text-slate-900">{{ item.nombre_completo }}</p>
            <p class="text-xs text-slate-500">{{ item.correo }} · @{{ item.username }}</p>
          </div>
        </div>
      </template>
      <template #cell-dni="{ item }">
        <span class="font-mono text-xs text-slate-600">{{ item.dni || 'Sin registrar' }}</span>
      </template>
      <template #cell-rol="{ item }">
        <span class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset" :class="roleClasses[item.rol]">
          {{ roleLabels[item.rol] ?? item.rol }}
        </span>
      </template>
      <template #cell-estado="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="item.is_active ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
        >
          <span class="size-1.5 rounded-full" :class="item.is_active ? 'bg-success-500' : 'bg-slate-400'" />
          {{ item.is_active ? 'Activo' : 'Inactivo' }}
        </span>
      </template>
      <template #cell-acciones="{ item }">
        <div class="flex justify-end gap-1">
          <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label="Ver detalle" @click="detailUsuario = item">
            <Eye :size="17" />
          </button>
          <template v-if="canManageAll">
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar usuario" @click="openEdit(item)">
              <Pencil :size="17" />
            </button>
            <button type="button" class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Desactivar usuario" @click="askDelete(item)">
              <UserX :size="17" />
            </button>
          </template>
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
      :title="isEditing ? 'Editar usuario' : 'Nuevo usuario'"
      description="Completa los datos institucionales y define sus permisos de acceso."
      @close="closeModal"
    >
      <form id="user-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submit">
        <BaseInput id="user-name" v-model="form.nombre" appearance="light" label="Nombre" placeholder="Ej. Andrea" :error="formErrors.nombre" />
        <BaseInput id="user-lastname" v-model="form.apellido" appearance="light" label="Apellido" placeholder="Ej. Salazar" />
        <BaseInput id="user-username" v-model="form.username" appearance="light" label="Nombre de usuario" placeholder="asalazar" :error="formErrors.username" />
        <BaseInput id="user-dni" v-model="form.dni" appearance="light" label="DNI" placeholder="12345678" :error="formErrors.dni" />
        <div class="sm:col-span-2">
          <BaseInput id="user-email" v-model="form.correo" type="email" appearance="light" label="Correo institucional" placeholder="usuario@udh.edu.pe" :error="formErrors.correo" autocomplete="email" />
        </div>
        <BaseSelect id="user-role" v-model="form.rol" label="Rol" :options="availableRoleOptions" :error="formErrors.rol" />
        <BaseInput id="user-password" v-model="form.password" type="password" appearance="light" :label="isEditing ? 'Nueva contraseña (opcional)' : 'Contraseña'" placeholder="Mínimo 8 caracteres" :error="formErrors.password" autocomplete="new-password" />
        <label class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <input v-model="form.is_active" type="checkbox" class="size-4 accent-primary-500" />
          <span>
            <span class="block text-sm font-semibold text-slate-800">Cuenta activa</span>
            <span class="block text-xs text-slate-500">Permite que el usuario inicie sesión en KairOs.</span>
          </span>
        </label>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="user-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear usuario' }}
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal :open="deleteModalOpen" title="Desactivar usuario" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        La cuenta de <strong class="text-slate-900">{{ pendingDelete?.nombre_completo }}</strong> perderá el acceso, pero se conservarán sus relaciones e historial.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Desactivar</BaseButton>
      </template>
    </BaseModal>

    <EntityDetailModal
      :open="detailUsuario !== null"
      :title="detailUsuario?.nombre_completo ?? ''"
      description="Información de la cuenta y registro de auditoría."
      modulo="usuario"
      :object-id="detailUsuario?.id"
      @close="detailUsuario = null"
    >
      <template #info>
        <div v-if="detailUsuario" class="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Nombre</p>
            <p class="text-sm font-semibold text-slate-800">{{ detailUsuario.nombre }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Apellido</p>
            <p class="text-sm font-semibold text-slate-800">{{ detailUsuario.apellido }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Usuario</p>
            <p class="font-mono text-sm text-slate-700">@{{ detailUsuario.username }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">DNI</p>
            <p class="font-mono text-sm text-slate-700">{{ detailUsuario.dni || '—' }}</p>
          </div>
          <div class="sm:col-span-2 flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Correo institucional</p>
            <p class="text-sm text-slate-700">{{ detailUsuario.correo }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Rol</p>
            <span
              class="inline-flex w-fit rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset"
              :class="roleClasses[detailUsuario.rol]"
            >
              {{ roleLabels[detailUsuario.rol] ?? detailUsuario.rol }}
            </span>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Estado</p>
            <span
              class="inline-flex w-fit items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="detailUsuario.is_active ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
            >
              <span class="size-1.5 rounded-full" :class="detailUsuario.is_active ? 'bg-success-500' : 'bg-slate-400'" />
              {{ detailUsuario.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
        </div>
      </template>
    </EntityDetailModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

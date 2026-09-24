<template>
  <div class="flex flex-col gap-6">
    <!-- Encabezado de pagina y accion principal -->
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Control territorial</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Usuarios por espacio</h1>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Gestiona las asignaciones territoriales de responsables, técnicos y docentes en sedes, pabellones, pisos y ambientes.
        </p>
      </div>
      <BaseButton v-if="canEdit" variant="accent" :full-width="false" @click="openCreate">
        <template #icon>
          <Plus :size="18" />
        </template>
        Nueva asignación
      </BaseButton>
    </header>

    <!-- Tarjetas de resumen estadistico -->
    <section class="grid grid-cols-2 gap-2 sm:grid-cols-3 sm:gap-4">
      <StatCard
        class="col-span-2 sm:col-span-1"
        label="Asignaciones territoriales"
        :value="pagination.total"
        :helper="`${activeCount} activas en esta página`"
        tone="blue"
      >
        <template #icon>
          <Link2 :size="20" />
        </template>
      </StatCard>
      <StatCard label="Usuarios en la página" :value="uniqueUsers" tone="emerald">
        <template #icon>
          <UserRoundCheck :size="20" />
        </template>
      </StatCard>
      <StatCard label="Ámbitos en la página" :value="uniqueSpaces" tone="violet">
        <template #icon>
          <Building2 :size="20" />
        </template>
      </StatCard>
    </section>

    <!-- Barra de filtros centralizada -->
    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <form
        class="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 xl:grid-cols-[minmax(220px,1.5fr)_180px_180px_160px_140px_auto]"
        @submit.prevent="applyFilters"
      >
        <!-- Busqueda general -->
        <BaseInput
          id="assignments-search"
          v-model="filters.search"
          appearance="light"
          placeholder="Buscar por usuario, correo o ámbito"
        >
          <template #icon>
            <Search :size="17" />
          </template>
        </BaseInput>

        <!-- Selector de Sede -->
        <BaseSelect
          id="assignments-filter-local"
          v-model="filters.local_id"
          :options="localFilterOptions"
          placeholder="Todas las sedes"
          @update:model-value="onLocalFilterChange"
        />

        <!-- Selector de Pabellon dependiente de Sede -->
        <BaseSelect
          id="assignments-filter-edificio"
          v-model="filters.edificio_id"
          :options="edificioFilterOptions"
          placeholder="Todos los pabellones"
          :disabled="!filters.local_id && edificioFilterOptions.length <= 1"
        />

        <!-- Selector de Nivel de Ambito -->
        <BaseSelect
          id="assignments-filter-ambito"
          v-model="filters.ambito"
          :options="ambitoFilterOptions"
          placeholder="Todos los ámbitos"
        />

        <!-- Selector de Estado Operativo -->
        <BaseSelect
          id="assignments-filter-status"
          v-model="filters.activo"
          :options="[
            { value: '', label: 'Todos los estados' },
            { value: 'true', label: 'Activas' },
            { value: 'false', label: 'Inactivas' },
          ]"
          placeholder="Todos los estados"
        />

        <!-- Boton de Limpieza -->
        <div class="flex items-center">
          <BaseButton
            variant="ghost"
            :full-width="false"
            class="w-full xl:w-auto"
            @click="clearFilters"
          >
            <template #icon>
              <RotateCcw :size="16" />
            </template>
            Limpiar
          </BaseButton>
        </div>
      </form>
    </section>

    <!-- Tabla centralizada de asignaciones -->
    <BaseTable
      :columns="columns"
      :items="asignaciones"
      :loading="loading"
      empty-message="No hay asignaciones que coincidan con los filtros seleccionados."
    >
      <!-- Celda de Usuario -->
      <template #cell-usuario="{ item }">
        <div class="flex items-center gap-3">
          <div class="grid size-9 shrink-0 place-items-center rounded-xl bg-slate-100 font-bold text-xs text-slate-700">
            {{ getInitials(item.usuario?.nombre_completo) }}
          </div>
          <div class="min-w-0">
            <p class="truncate font-semibold text-slate-900">{{ item.usuario?.nombre_completo || 'Usuario sin nombre' }}</p>
            <p class="truncate text-xs text-slate-500">{{ item.usuario?.correo || '—' }}</p>
          </div>
        </div>
      </template>

      <!-- Celda de Ambito con Badge Distintivo -->
      <template #cell-ambito="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="getAmbitoBadgeClass(item.ambito)"
        >
          <component :is="getAmbitoIcon(item.ambito)" :size="13" class="shrink-0" />
          {{ item.ambito_display || getAmbitoLabel(item.ambito) }}
        </span>
      </template>

      <!-- Celda de Ubicacion Compuesta Territorial -->
      <template #cell-ubicacion="{ item }">
        <div class="flex items-center gap-3">
          <div
            class="grid size-9 shrink-0 place-items-center rounded-xl"
            :class="getAmbitoIconContainerClass(item.ambito)"
          >
            <component :is="getAmbitoIcon(item.ambito)" :size="17" />
          </div>
          <div class="min-w-0">
            <p class="truncate font-semibold text-slate-900">
              {{ formatUbicacionPrincipal(item) }}
            </p>
            <p class="truncate text-xs text-slate-500">
              {{ formatUbicacionSecundaria(item) }}
            </p>
          </div>
        </div>
      </template>

      <!-- Celda de Responsabilidad -->
      <template #cell-responsabilidad="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="getResponsabilidadBadgeClass(item.tipo_responsabilidad)"
        >
          <component :is="getResponsabilidadIcon(item.tipo_responsabilidad)" :size="13" class="shrink-0" />
          {{ item.tipo_responsabilidad_display || item.tipo_responsabilidad }}
        </span>
      </template>

      <!-- Celda de Estado -->
      <template #cell-estado="{ item }">
        <span
          class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="item.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
        >
          <span class="size-1.5 rounded-full" :class="item.activo ? 'bg-success-500' : 'bg-slate-400'" />
          {{ item.activo ? 'Activa' : 'Inactiva' }}
        </span>
      </template>

      <!-- Celda de Acciones -->
      <template #cell-acciones="{ item }">
        <div v-if="canEdit" class="flex justify-end gap-1">
          <button
            type="button"
            class="rounded-lg p-2 text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            aria-label="Editar asignación"
            @click="openEdit(item)"
          >
            <Pencil :size="17" />
          </button>
          <button
            type="button"
            class="rounded-lg p-2 text-slate-400 transition-colors hover:bg-danger-50 hover:text-danger-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger-500"
            aria-label="Eliminar asignación"
            @click="askDelete(item)"
          >
            <Trash2 :size="17" />
          </button>
        </div>
        <span v-else class="text-xs text-slate-400">Solo lectura</span>
      </template>
    </BaseTable>

    <!-- Paginacion -->
    <BasePagination
      :page="filters.page"
      :total-pages="pagination.totalPages"
      :total="pagination.total"
      :loading="loading"
      @change="changePage"
    />

    <!-- Modal de Asignacion en Cascada (4 Niveles) -->
    <BaseModal
      :open="modalOpen"
      :title="isEditing ? 'Editar asignación territorial' : 'Nueva asignación territorial'"
      description="Relaciona un usuario con un nivel territorial: Sede, Pabellón, Piso o Espacio individual."
      size="lg"
      @close="closeModal"
    >
      <form id="assignment-form" class="grid gap-5" @submit.prevent="submit">
        <!-- Selector de Nivel de Ambito (Segmented Control) -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-semibold tracking-wide text-slate-700 pl-0.5">
            Nivel de ámbito territorial *
          </label>
          <div
            class="grid grid-cols-2 gap-1.5 rounded-xl border border-slate-200 bg-slate-100/70 p-1.5 sm:grid-cols-4"
            role="radiogroup"
            aria-label="Nivel de ámbito territorial"
          >
            <button
              v-for="scope in scopeOptions"
              :key="scope.value"
              type="button"
              role="radio"
              :aria-checked="form.tipo_ambito === scope.value"
              class="flex items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-xs font-semibold transition-all duration-200"
              :class="[
                form.tipo_ambito === scope.value
                  ? 'bg-white text-primary-600 shadow-sm ring-1 ring-slate-200/80'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              ]"
              @click="onAmbitoChange(scope.value)"
            >
              <component :is="scope.icon" :size="15" class="shrink-0" />
              <span>{{ scope.label }}</span>
            </button>
          </div>

          <!-- Mensaje descriptivo contextual del ambito -->
          <div class="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500 border border-slate-100">
            <Info :size="14" class="shrink-0 text-slate-400" />
            <span>{{ currentScopeDescription }}</span>
          </div>
        </div>

        <!-- Banner de error general del formulario -->
        <div
          v-if="formErrors.general"
          class="flex items-center gap-2.5 rounded-xl border border-danger-200 bg-danger-50 px-4 py-3 text-xs text-danger-700"
          role="alert"
        >
          <CircleAlert :size="16" class="shrink-0 text-danger-600" />
          <span>{{ formErrors.general }}</span>
        </div>

        <!-- Campos dinamicos en cascada segun el nivel territorial -->
        <div class="rounded-xl border border-slate-200/80 bg-slate-50/40 p-4 grid gap-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">
            Selección de ubicación territorial
          </h3>

          <!-- Nivel 1: Sede -->
          <template v-if="form.tipo_ambito === 'sede'">
            <BaseSelect
              id="assignment-local"
              v-model="form.local_id"
              label="Sede física *"
              placeholder="Seleccionar sede"
              :options="localSelectOptions"
              :error="formErrors.local_id"
            />
          </template>

          <!-- Nivel 2: Pabellon / Edificio -->
          <template v-else-if="form.tipo_ambito === 'edificio'">
            <div class="grid gap-4 sm:grid-cols-2">
              <BaseSelect
                id="assignment-local"
                v-model="form.local_id"
                label="Sede física *"
                placeholder="Seleccionar sede"
                :options="localSelectOptions"
                :error="formErrors.local_id"
                @update:model-value="onLocalChange"
              />
              <BaseSelect
                id="assignment-edificio"
                v-model="form.edificio_id"
                label="Pabellón / Edificio *"
                placeholder="Seleccionar pabellón"
                :options="filteredEdificioOptions"
                :disabled="!form.local_id"
                :error="formErrors.edificio_id"
              />
            </div>
          </template>

          <!-- Nivel 3: Piso de Pabellon -->
          <template v-else-if="form.tipo_ambito === 'piso'">
            <div class="grid gap-4 sm:grid-cols-2">
              <BaseSelect
                id="assignment-local"
                v-model="form.local_id"
                label="Sede física *"
                placeholder="Seleccionar sede"
                :options="localSelectOptions"
                :error="formErrors.local_id"
                @update:model-value="onLocalChange"
              />
              <BaseSelect
                id="assignment-edificio"
                v-model="form.edificio_id"
                label="Pabellón / Edificio *"
                placeholder="Seleccionar pabellón"
                :options="filteredEdificioOptions"
                :disabled="!form.local_id"
                :error="formErrors.edificio_id"
                @update:model-value="onEdificioChange"
              />
            </div>
            <div class="flex flex-col gap-1.5">
              <BaseInput
                id="assignment-piso"
                v-model="form.piso"
                label="Piso o Nivel *"
                appearance="light"
                placeholder="Ej: 1, 2, PB, Sótano -1"
                :disabled="!form.edificio_id"
                :error="formErrors.piso"
              >
                <template #icon>
                  <Layers :size="17" />
                </template>
              </BaseInput>
              <!-- Chips con pisos detectados para seleccion rapida -->
              <div v-if="availablePisos.length > 0 && form.edificio_id" class="flex flex-wrap items-center gap-1.5 pt-1">
                <span class="text-xs text-slate-400">Pisos detectados en este pabellón:</span>
                <button
                  v-for="p in availablePisos"
                  :key="typeof p === 'object' ? p.value : p"
                  type="button"
                  class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium transition-colors"
                  :class="form.piso === String(typeof p === 'object' ? p.value : p) ? 'bg-primary-500 text-white' : 'bg-slate-200/80 text-slate-700 hover:bg-slate-300/80'"
                  @click="onPisoChange(String(typeof p === 'object' ? p.value : p))"
                >
                  {{ typeof p === 'object' ? p.label : (String(p).toLowerCase().startsWith('piso') ? p : `Piso ${p}`) }}
                </button>
              </div>
            </div>
          </template>

          <!-- Nivel 4: Espacio individual -->
          <template v-else-if="form.tipo_ambito === 'espacio'">
            <div class="grid gap-4 sm:grid-cols-2">
              <BaseSelect
                id="assignment-local"
                v-model="form.local_id"
                label="Sede física"
                placeholder="Filtrar por sede"
                :options="localSelectOptions"
                @update:model-value="onLocalChange"
              />
              <BaseSelect
                id="assignment-edificio"
                v-model="form.edificio_id"
                label="Pabellón / Edificio"
                placeholder="Filtrar por pabellón"
                :options="filteredEdificioOptions"
                :disabled="!form.local_id"
                @update:model-value="onEdificioChange"
              />
            </div>
            <BasePaginatedSelect
              id="assignment-space"
              v-model="form.espacio_id"
              label="Espacio o ambiente específico *"
              placeholder="Seleccionar espacio"
              search-placeholder="Buscar por código o ubicación"
              :initial-option="selectedSpaceOption"
              :load-options="loadSpaceOptions"
              :page-size="10"
              :error="formErrors.espacio_id"
            />
          </template>
        </div>

        <!-- Seccion de Usuario y Rol de Responsabilidad -->
        <div class="grid gap-4">
          <BasePaginatedSelect
            id="assignment-user"
            v-model="form.usuario_id"
            label="Usuario asignado *"
            placeholder="Seleccionar usuario"
            search-placeholder="Buscar por nombre o correo"
            :initial-option="selectedUserOption"
            :load-options="loadUserOptions"
            :page-size="10"
            :error="formErrors.usuario_id"
          />

          <BaseSelect
            id="assignment-role"
            v-model="form.tipo_responsabilidad"
            label="Tipo de responsabilidad *"
            :options="responsibilityOptions"
            :error="formErrors.tipo_responsabilidad"
          />

          <!-- Checkbox de estado activo -->
          <label class="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 transition-colors hover:bg-slate-100/60">
            <input
              v-model="form.activo"
              type="checkbox"
              class="size-4 rounded border-slate-300 text-primary-600 accent-primary-500 focus:ring-primary-500"
            />
            <span>
              <span class="block text-sm font-semibold text-slate-800">Asignación activa</span>
              <span class="block text-xs text-slate-500">
                La asignación figurará vigente para operaciones de mantenimiento y organigrama.
              </span>
            </span>
          </label>
        </div>
      </form>

      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="assignment-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear asignación' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de confirmacion de eliminacion -->
    <BaseModal :open="deleteModalOpen" title="Eliminar asignación" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        Se retirará la asignación de <strong class="text-slate-900">{{ pendingDelete?.usuario?.nombre_completo }}</strong>
        en <strong class="text-slate-900">{{ formatUbicacionPrincipal(pendingDelete) }}</strong>.
        La trazabilidad histórica se conservará intacta.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">Eliminar</BaseButton>
      </template>
    </BaseModal>

    <!-- Notificacion flotante Toast -->
    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {
  Building2,
  CircleAlert,
  DoorClosed,
  GraduationCap,
  Info,
  Landmark,
  Layers,
  Link2,
  Pencil,
  Plus,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
  UserRoundCheck,
  Wrench,
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

// Columnas para la tabla centralizada
const columns = [
  { key: 'usuario', label: 'Usuario' },
  { key: 'ambito', label: 'Ámbito' },
  { key: 'ubicacion', label: 'Área territorial asignada' },
  { key: 'responsabilidad', label: 'Responsabilidad' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

// Opciones de configuracion para los niveles de ambito territorial
const scopeOptions = [
  {
    value: 'sede',
    label: 'Sede',
    icon: Landmark,
    desc: 'Asignación de referencia general para la sede física completa.',
  },
  {
    value: 'edificio',
    label: 'Pabellón',
    icon: Building2,
    desc: 'Responsable operativo y de mantenimiento de un pabellón o edificio.',
  },
  {
    value: 'piso',
    label: 'Piso',
    icon: Layers,
    desc: 'Encargado técnico operativo de un nivel o planta específica.',
  },
  {
    value: 'espacio',
    label: 'Espacio',
    icon: DoorClosed,
    desc: 'Encargado o docente de un ambiente específico (ej. LAB-201).',
  },
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
  localFilterOptions,
  edificioFilterOptions,
  localSelectOptions,
  filteredEdificioOptions,
  availablePisos,
  loadUserOptions,
  loadSpaceOptions,
  onAmbitoChange,
  onLocalChange,
  onEdificioChange,
  onPisoChange,
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

// Opciones para el selector de ambito en la barra de filtros
const ambitoFilterOptions = [
  { value: '', label: 'Todos los ámbitos' },
  { value: 'sede', label: 'Sedes' },
  { value: 'edificio', label: 'Pabellones' },
  { value: 'piso', label: 'Pisos' },
  { value: 'espacio', label: 'Espacios' },
];

const onLocalFilterChange = (val) => {
  filters.local_id = val;
  filters.edificio_id = '';
  filters.page = 1;
};

// Descripcion contextual del ambito seleccionado en el formulario
const currentScopeDescription = computed(() => {
  const selected = scopeOptions.find((scope) => scope.value === form.tipo_ambito);
  return selected?.desc || 'Selecciona el nivel territorial de la asignación.';
});

// Obtencion de iniciales para avatar sintetico
const getInitials = (nombreCompleto) => {
  if (!nombreCompleto) return 'U';
  return nombreCompleto
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('');
};

// Mapeo visual de clases de estilo para badges de ambito
const getAmbitoBadgeClass = (ambito) => {
  switch (ambito) {
    case 'sede':
      return 'bg-indigo-50 text-indigo-700 border border-indigo-200/80';
    case 'edificio':
      return 'bg-blue-50 text-blue-700 border border-blue-200/80';
    case 'piso':
      return 'bg-teal-50 text-teal-700 border border-teal-200/80';
    case 'espacio':
      return 'bg-purple-50 text-purple-700 border border-purple-200/80';
    default:
      return 'bg-slate-100 text-slate-600 border border-slate-200';
  }
};

// Contenedor tonal de icono segun el ambito territorial
const getAmbitoIconContainerClass = (ambito) => {
  switch (ambito) {
    case 'sede':
      return 'bg-indigo-50 text-indigo-600';
    case 'edificio':
      return 'bg-blue-50 text-blue-600';
    case 'piso':
      return 'bg-teal-50 text-teal-600';
    case 'espacio':
      return 'bg-purple-50 text-purple-600';
    default:
      return 'bg-primary-50 text-primary-600';
  }
};

// Seleccion dinamica de icono de Lucide por ambito
const getAmbitoIcon = (ambito) => {
  switch (ambito) {
    case 'sede':
      return Landmark;
    case 'edificio':
      return Building2;
    case 'piso':
      return Layers;
    case 'espacio':
      return DoorClosed;
    default:
      return Building2;
  }
};

// Etiqueta de respaldo para nombres de ambito
const getAmbitoLabel = (ambito) => {
  switch (ambito) {
    case 'sede':
      return 'Sede';
    case 'edificio':
      return 'Pabellón';
    case 'piso':
      return 'Piso';
    case 'espacio':
      return 'Espacio';
    default:
      return 'Ámbito';
  }
};

// Estilo visual del badge segun el rol de responsabilidad
const getResponsabilidadBadgeClass = (rol) => {
  switch (rol) {
    case 'responsable':
      return 'bg-blue-50 text-blue-700 border border-blue-200/60';
    case 'tecnico':
      return 'bg-emerald-50 text-emerald-700 border border-emerald-200/60';
    case 'docente':
      return 'bg-amber-50 text-amber-700 border border-amber-200/60';
    default:
      return 'bg-violet-50 text-violet-700 border border-violet-200/60';
  }
};

// Icono segun el rol de responsabilidad
const getResponsabilidadIcon = (rol) => {
  switch (rol) {
    case 'responsable':
      return ShieldCheck;
    case 'tecnico':
      return Wrench;
    case 'docente':
      return GraduationCap;
    default:
      return ShieldCheck;
  }
};

// Formateo de etiqueta principal de ubicacion con resolucion defensiva ante nulos
const formatUbicacionPrincipal = (item) => {
  if (!item) return '—';
  if (item.ubicacion_display) return item.ubicacion_display;
  if (item.nombre_ambito) return item.nombre_ambito;

  const ambito = item.ambito || 'espacio';
  if (ambito === 'sede') return item.local?.nombre || 'Sede institucional';
  if (ambito === 'edificio') return item.edificio?.nombre || 'Pabellón / Edificio';
  if (ambito === 'piso') {
    const edif = item.edificio?.nombre || 'Pabellón';
    return item.piso ? `${edif} · Piso ${item.piso}` : edif;
  }
  if (ambito === 'espacio') {
    if (!item.espacio) return 'Espacio individual';
    const edif = item.edificio?.nombre || item.espacio.pabellon || '';
    return edif ? `${item.espacio.codigo_espacio} · ${edif}` : item.espacio.codigo_espacio;
  }
  return '—';
};

// Formateo de linea secundaria de ubicacion con contexto jerarquico
const formatUbicacionSecundaria = (item) => {
  if (!item) return '';
  const ambito = item.ambito || 'espacio';
  if (ambito === 'sede') {
    return item.local?.ciudad ? `Ciudad: ${item.local.ciudad}` : (item.local?.codigo ? `Código: ${item.local.codigo}` : 'Sede principal');
  }
  if (ambito === 'edificio') {
    return item.local?.nombre ? `Sede: ${item.local.nombre}` : (item.edificio?.codigo ? `Código: ${item.edificio.codigo}` : 'Edificio completo');
  }
  if (ambito === 'piso') {
    return item.local?.nombre ? `Sede: ${item.local.nombre}` : 'Nivel de planta';
  }
  if (ambito === 'espacio') {
    const subtipo = item.espacio?.tipo_display || '';
    const localNom = item.local?.nombre || '';
    return [subtipo, localNom].filter(Boolean).join(' · ');
  }
  return '';
};
</script>

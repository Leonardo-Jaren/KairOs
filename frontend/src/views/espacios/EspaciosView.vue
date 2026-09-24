<template>
  <div class="flex min-w-0 flex-col gap-5 sm:gap-6">
    <!-- Cabecera principal con alternancia de vistas y acciones contextuales -->
    <header class="flex flex-col gap-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-primary-600">
          Infraestructura territorial
        </p>
        <VistaEspaciosSwitch :active="currentView" @change="changeView" />
      </div>
      <div class="flex min-w-0 flex-col justify-between gap-3 lg:flex-row lg:items-end">
        <div>
          <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">
            Espacios y Sedes
          </h1>
          <p class="mt-1 max-w-2xl text-sm text-slate-500">
            Explora la jerarquía territorial de campus, pabellones y pisos o consulta el inventario general de ambientes.
          </p>
        </div>

        <!-- Controles superiores contextuales -->
        <div class="flex flex-wrap items-center gap-2.5">
        <BaseButton
          variant="secondary"
          size="sm"
          :full-width="false"
          @click="$router.push('/espacios/usuarios')"
        >
          <template #icon><Users :size="16" /></template>
          Usuarios por espacio
        </BaseButton>

        <!-- Botón de acción principal contextual -->
        <template v-if="canEdit">
          <BaseButton
            v-if="currentView === 'jerarquia' && !selectedSedeId"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="openCreateSede"
          >
            <template #icon><Plus :size="16" /></template>
             Nuevo local
          </BaseButton>

          <BaseButton
            v-else-if="currentView === 'jerarquia' && selectedSedeId && !selectedEdificioId"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="openCreateEdificio(selectedSedeId)"
          >
            <template #icon><Plus :size="16" /></template>
            Nuevo pabellón
          </BaseButton>

          <BaseButton
            v-else-if="currentView === 'jerarquia' && selectedEdificioId"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="openCreateEspacio({ sedeId: selectedSedeId, edificioId: selectedEdificioId })"
          >
            <template #icon><Plus :size="16" /></template>
            Agregar ambiente
          </BaseButton>

          <BaseButton
            v-else-if="currentView === 'inventario'"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="openCreateEspacio()"
          >
            <template #icon><Plus :size="16" /></template>
            Nuevo ambiente
          </BaseButton>
        </template>
        </div>
      </div>
    </header>

    <RutaEspacios v-if="currentView === 'jerarquia'" :items="locationItems" @navigate="navigateLocation" />

    <!-- Indicadores Estadísticos Superiores (Bento StatCards) -->
    <section class="order-3 grid grid-cols-2 gap-2 sm:gap-4 lg:order-none lg:grid-cols-4" aria-label="Resumen de infraestructura">
      <StatCard label="Espacios registrados" :value="stats.total" tone="blue">
        <template #icon><Building2 :size="20" /></template>
      </StatCard>
      <StatCard label="Espacios activos" :value="stats.activos" tone="emerald">
        <template #icon><Building2 :size="20" /></template>
      </StatCard>
      <StatCard label="Laboratorios activos" :value="stats.laboratorios" tone="violet">
        <template #icon><FlaskConical :size="20" /></template>
      </StatCard>
      <StatCard label="Equipos distribuidos" :value="stats.equipos" tone="amber">
        <template #icon><Monitor :size="20" /></template>
      </StatCard>
    </section>

    <!-- ================= CONTENIDO: VISTA JERÁRQUICA ================= -->
    <section v-if="currentView === 'jerarquia'" class="flex min-w-0 flex-col gap-6">
      <div v-if="!selectedSedeId" class="max-w-2xl">
        <EspaciosSearch id="search-sedes" v-model="searchQuery" :placeholder="selectedCity ? 'Buscar local' : 'Buscar ciudad o local'" />
      </div>
      <!-- Las ciudades son el primer nivel en ambas formas de exploración. -->
      <div v-if="!selectedCity && !selectedSedeId" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3" aria-label="Ciudades disponibles">
        <button v-for="item in filteredCityCards" :key="item.label" type="button" class="flex min-h-24 items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-xs transition-colors hover:border-primary-400 hover:bg-primary-50/40 focus-visible:outline-2 focus-visible:outline-primary-500" @click="selectCity(item.label)">
          <span class="min-w-0"><strong class="block text-base font-bold text-slate-900">{{ item.label }}</strong><span class="text-xs text-slate-600">{{ item.localCount }} {{ item.localCount === 1 ? 'local' : 'locales' }} · {{ item.buildingCount }} {{ item.buildingCount === 1 ? 'pabellón' : 'pabellones' }}</span></span>
          <ChevronRight :size="18" class="shrink-0 text-primary-600" aria-hidden="true" />
        </button>
        <p v-if="!filteredCityCards.length" class="text-sm text-slate-500">No hay ciudades que coincidan con la búsqueda.</p>
      </div>
      <!-- Nivel 1: Lista de Sedes -->
      <SedesBentoGrid
        v-else-if="!selectedSedeId"
        :sedes="citySedes"
        :loading="loading"
        :can-edit="canEdit"
        @select-sede="selectSede"
        @edit-sede="openEditSede"
        @delete-sede="askDeleteSede"
      />

      <!-- Nivel 2: Pabellones de la sede seleccionada -->
      <EdificiosBentoGrid
        v-else-if="selectedSedeId && !selectedEdificioId && selectedSede"
        :sede="selectedSede"
        :edificios="edificiosDeSede"
        :loading="loading"
        :can-edit="canEdit"
        @select-edificio="selectEdificio"
        @edit-edificio="openEditEdificio"
        @delete-edificio="askDeleteEdificio"
      />

      <!-- Nivel 3: Plantas Verticales / Acordeón de Pisos ordenados de arriba a abajo -->
      <PisosVerticalesView
        v-else-if="selectedEdificioId && selectedEdificio"
        :sede="selectedSede"
        :edificio="selectedEdificio"
        :pisos="pisosDeEdificio"
        :can-edit="canEdit"
        :loading="loading"
        :context-query="route.query"
        @back-to-edificios="resetToEdificios"
        @create-espacio="openCreateEspacio"
        @edit-espacio="openEditEspacio"
        @delete-espacio="askDeleteEspacio"
        @assign-technician="openAssignTechnicianModal"
      />
    </section>

    <!-- ================= CONTENIDO: VISTA INVENTARIO ================= -->
    <section v-else class="flex min-w-0 flex-col gap-5">
      <div v-if="inventoryScopeLabel" class="flex flex-wrap items-center gap-2 text-sm text-slate-700">
        <span>Ubicación: <strong>{{ inventoryScopeLabel }}</strong></span>
        <button type="button" class="min-h-11 rounded-lg px-3 font-semibold text-primary-700 hover:bg-primary-50 focus-visible:outline-2 focus-visible:outline-primary-500" @click="clearInventoryScope">Ver todos</button>
      </div>
      <!-- Barra de filtros de inventario -->
      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
        <form class="grid gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(240px,1fr)_190px_170px_auto]" @submit.prevent>
          <EspaciosSearch
            id="spaces-search"
            v-model="inventoryFilters.search"
            placeholder="Buscar por código, pabellón, piso o responsable"
          />
          <BaseSelect
            id="spaces-type"
            v-model="inventoryFilters.tipo"
            :options="typeOptions"
            placeholder="Todos los tipos"
          />
          <BaseSelect
            id="spaces-status"
            v-model="inventoryFilters.activo"
            :options="[{ value: 'true', label: 'Activos' }, { value: 'false', label: 'Inactivos' }]"
            placeholder="Todos los estados"
          />
          <BaseButton
            variant="ghost"
            :full-width="false"
            @click="clearInventoryFilters"
          >
            Limpiar
          </BaseButton>
        </form>
      </div>

      <!-- Tabla global de ambientes -->
      <div class="hidden min-w-0 md:block">
      <BaseTable
        :columns="inventoryColumns"
        :items="paginatedInventoryEspacios"
        :loading="loading"
        empty-message="No se encontraron espacios con los filtros actuales."
      >
        <template #cell-espacio="{ item }">
          <div class="flex items-center gap-3">
            <div class="grid size-10 place-items-center rounded-xl bg-primary-50 text-primary-600">
              <Building2 :size="19" />
            </div>
            <div>
              <p class="font-semibold text-slate-900">{{ item.codigo_espacio }}</p>
              <p class="text-xs text-slate-500">
                Actualizado {{ new Date(item.updated_at).toLocaleDateString() }}
              </p>
            </div>
          </div>
        </template>

        <template #cell-tipo="{ item }">
          <span class="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-700">
            {{ item.tipo_display || item.tipo }}
          </span>
        </template>

        <template #cell-ubicacion="{ item }">
          <p class="font-medium text-slate-700">{{ item.pabellon || item.edificio?.nombre }}</p>
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
          <span
            class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="item.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
          >
            <span class="size-1.5 rounded-full" :class="item.activo ? 'bg-success-500' : 'bg-slate-400'" />
            {{ item.activo ? 'Activo' : 'Inactivo' }}
          </span>
        </template>

        <template #cell-acciones="{ item }">
          <div class="flex justify-end gap-1">
            <RouterLink
              :to="`/espacios/${item.id}`"
              class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
              title="Plano interactivo de equipos"
              aria-label="Plano interactivo"
            >
              <Eye :size="17" />
            </RouterLink>
            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              aria-label="Ver espacio"
              @click="detailEspacio = item"
            >
              <Info :size="17" />
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
              aria-label="Editar espacio"
              @click="openEditEspacio(item)"
            >
              <Pencil :size="17" />
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
              aria-label="Desactivar espacio"
              @click="askDeleteEspacio(item)"
            >
              <Trash2 :size="17" />
            </button>
          </div>
        </template>
      </BaseTable>
      </div>

      <!-- En pantallas pequeñas, los datos se muestran sin desplazamiento horizontal. -->
      <div class="grid gap-3 md:hidden" aria-label="Espacios disponibles">
        <div v-if="loading && !paginatedInventoryEspacios.length" class="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500" role="status">Cargando espacios...</div>
        <div v-else-if="!paginatedInventoryEspacios.length" class="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">No se encontraron espacios con los filtros actuales.</div>
        <article v-for="item in paginatedInventoryEspacios" :key="item.id" class="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-xs">
          <div class="flex flex-wrap items-start justify-between gap-2">
            <div class="min-w-0">
              <h2 class="wrap-break-word text-base font-bold text-slate-900">{{ item.codigo_espacio }}</h2>
              <p class="text-xs text-slate-500">{{ item.tipo_display || item.tipo }} · {{ formatFloor(item.piso) }}</p>
            </div>
            <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="item.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-600'">{{ item.activo ? 'Activo' : 'Inactivo' }}</span>
          </div>
          <p class="mt-3 wrap-break-word text-sm text-slate-700">{{ item.pabellon || item.edificio?.nombre || 'Sin pabellón' }}</p>
          <p class="mt-1 wrap-break-word text-xs text-slate-500">Responsable: {{ item.responsable?.nombre_completo || 'Sin asignar' }}</p>
          <p class="mt-1 text-xs text-slate-500">{{ item.cantidad_equipos }} equipos</p>
          <div class="mt-3 grid grid-cols-2 gap-2 border-t border-slate-100 pt-3">
            <RouterLink :to="`/espacios/${item.id}`" class="inline-flex min-h-11 items-center justify-center gap-1 rounded-lg bg-primary-50 px-2 text-xs font-semibold text-primary-700 hover:bg-primary-100"><Eye :size="16" />Plano</RouterLink>
            <button type="button" class="min-h-11 rounded-lg bg-slate-50 px-2 text-xs font-semibold text-slate-700 hover:bg-slate-100" @click="detailEspacio = item">Ver espacio</button>
            <button v-if="canEdit" type="button" class="min-h-11 rounded-lg bg-slate-50 px-2 text-xs font-semibold text-primary-700 hover:bg-primary-50" @click="openEditEspacio(item)">Editar</button>
            <button v-if="canEdit" type="button" class="min-h-11 rounded-lg bg-danger-50 px-2 text-xs font-semibold text-danger-700 hover:bg-danger-100" @click="askDeleteEspacio(item)">Desactivar</button>
          </div>
        </article>
      </div>

      <BasePagination
        :page="inventoryFilters.page"
        :total-pages="inventoryPagination.totalPages"
        :total="inventoryPagination.total"
        :loading="loading"
        @change="changeInventoryPage"
      />
    </section>

    <!-- Modales Contextuales -->
    <SedeFormModal
      :open="sedeModalOpen"
      :is-editing="isEditingSede"
      :form="sedeForm"
      :errors="sedeErrors"
      :saving="saving"
      :type-options="sedeTipoOptions"
      @close="closeSedeModal"
      @submit="submitSede"
    />

    <EdificioFormModal
      :open="edificioModalOpen"
      :is-editing="isEditingEdificio"
      :form="edificioForm"
      :errors="edificioErrors"
      :saving="saving"
      :sedes-options="allLocalesOptions"
      @close="closeEdificioModal"
      @submit="submitEdificio"
    />

    <EspacioFormModal
      :open="espacioModalOpen"
      :is-editing="isEditingEspacio"
      :form="espacioForm"
      :errors="espacioErrors"
      :saving="saving"
      :sedes-options="allLocalesOptions"
      :edificios-options="edificiosOptionsForSede"
      :existing-floors="pisosExistentesEnEdificio"
      :type-options="typeOptions"
      @close="closeEspacioModal"
      @submit="submitEspacio"
    />

    <PisoTecnicoModal
      :open="technicianModalOpen"
      :target="technicianTarget"
      :form="technicianForm"
      :options="technicianOptions"
      :loading="technicianLoading"
      :saving="technicianSaving"
      @close="technicianModalOpen = false"
      @submit="submitTechnicianAssignment"
    />

    <!-- Modal de confirmación para desactivar Sede -->
    <BaseModal
      :open="deleteSedeModalOpen"
      title="Desactivar sede"
      size="sm"
      @close="deleteSedeModalOpen = false"
    >
      <p class="text-sm leading-6 text-slate-600">
        La sede <strong class="text-slate-900">{{ pendingDeleteSede?.nombre }}</strong> será desactivada.
        Sus pabellones y ambientes conservarán su historial de auditoría.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="deleteSedeModalOpen = false">
          Cancelar
        </BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDeleteSede">
          Desactivar
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de confirmación para desactivar Pabellón -->
    <BaseModal
      :open="deleteEdificioModalOpen"
      title="Desactivar pabellón"
      size="sm"
      @close="deleteEdificioModalOpen = false"
    >
      <p class="text-sm leading-6 text-slate-600">
        El pabellón <strong class="text-slate-900">{{ pendingDeleteEdificio?.nombre }}</strong> será desactivado.
        Los ambientes asociados se conservarán en el historial.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="deleteEdificioModalOpen = false">
          Cancelar
        </BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDeleteEdificio">
          Desactivar
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de confirmación para desactivar Ambiente -->
    <BaseModal
      :open="deleteEspacioModalOpen"
      title="Desactivar espacio"
      size="sm"
      @close="deleteEspacioModalOpen = false"
    >
      <p class="text-sm leading-6 text-slate-600">
        El espacio <strong class="text-slate-900">{{ pendingDeleteEspacio?.codigo_espacio }}</strong> dejará de estar
        disponible para nuevas asignaciones. Su historial se conservará.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="deleteEspacioModalOpen = false">
          Cancelar
        </BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDeleteEspacio">
          Desactivar
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de información detallada del espacio -->
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
                {{ detailEspacio?.tipo_display || detailEspacio?.tipo }}
              </span>
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Pabellón</dt>
            <dd class="mt-1 text-sm text-slate-700">{{ detailEspacio?.pabellon || detailEspacio?.edificio?.nombre }}</dd>
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
              <span
                class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="detailEspacio?.activo ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
              >
                <span
                  class="size-1.5 rounded-full"
                  :class="detailEspacio?.activo ? 'bg-success-500' : 'bg-slate-400'"
                />
                {{ detailEspacio?.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </dd>
          </div>
        </div>
      </template>
    </EntityDetailModal>

    <!-- Toast global para notificaciones -->
    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

<script setup>
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  Building2,
  ChevronRight,
  Eye,
  FlaskConical,
  Info,
  Monitor,
  Pencil,
  Plus,
  Trash2,
  Users,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import StatCard from '@/components/cards/StatCard.vue';
import EntityDetailModal from '@/components/shared/EntityDetailModal.vue';

import EdificioFormModal from '@/components/espacios/EdificioFormModal.vue';
import EdificiosBentoGrid from '@/components/espacios/EdificiosBentoGrid.vue';
import EspacioFormModal from '@/components/espacios/EspacioFormModal.vue';
import PisoTecnicoModal from '@/components/espacios/PisoTecnicoModal.vue';
import PisosVerticalesView from '@/components/espacios/PisosVerticalesView.vue';
import SedeFormModal from '@/components/espacios/SedeFormModal.vue';
import SedesBentoGrid from '@/components/espacios/SedesBentoGrid.vue';
import EspaciosSearch from '@/components/espacios/EspaciosSearch.vue';
import RutaEspacios from '@/components/espacios/RutaEspacios.vue';
import VistaEspaciosSwitch from '@/components/espacios/VistaEspaciosSwitch.vue';
import { viewLocation } from '@/composables/espacios/espaciosNavigation';

import { useEspaciosJerarquia } from '@/composables/espacios/useEspaciosJerarquia';
import { formatFloor } from '@/utils/formatters';

const inventoryColumns = [
  { key: 'espacio', label: 'Espacio' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'responsable', label: 'Responsable' },
  { key: 'equipos', label: 'Equipos' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const route = useRoute();
const router = useRouter();

const {
  loading, saving, currentView, searchQuery,
  selectedCity, selectedSedeId, selectedEdificioId, selectedSede, selectedEdificio,
  cityCards, sedesList, edificiosDeSede, pisosDeEdificio, stats,
  canEdit, typeOptions, sedeTipoOptions, allLocalesOptions,
  edificiosOptionsForSede, pisosExistentesEnEdificio,
  toast, detailEspacio,

  setVista, selectCity, selectSede, selectEdificio, resetToCities, resetToSedes, resetToEdificios,
  closeToast,

  sedeModalOpen, isEditingSede, sedeForm, sedeErrors, deleteSedeModalOpen, pendingDeleteSede,
  openCreateSede, openEditSede, closeSedeModal, submitSede, askDeleteSede, confirmDeleteSede,

  edificioModalOpen, isEditingEdificio, edificioForm, edificioErrors, deleteEdificioModalOpen, pendingDeleteEdificio,
  openCreateEdificio, openEditEdificio, closeEdificioModal, submitEdificio, askDeleteEdificio, confirmDeleteEdificio,

  espacioModalOpen, isEditingEspacio, espacioForm, espacioErrors, deleteEspacioModalOpen, pendingDeleteEspacio,
  openCreateEspacio, openEditEspacio, closeEspacioModal, submitEspacio, askDeleteEspacio, confirmDeleteEspacio,

  technicianModalOpen, technicianTarget, technicianForm, technicianOptions,
  technicianLoading, technicianSaving, openAssignTechnicianModal, submitTechnicianAssignment,

  inventoryFilters, paginatedInventoryEspacios, inventoryPagination,
  changeInventoryPage, clearInventoryFilters, clearInventoryScope,
} = useEspaciosJerarquia();

const filteredCityCards = computed(() => cityCards.value.filter((city) => (
  city.label.toLocaleLowerCase('es').includes(searchQuery.value.trim().toLocaleLowerCase('es'))
)));
const citySedes = computed(() => sedesList.value.filter((sede) => sede.ciudad === selectedCity.value));
const locationItems = computed(() => {
  const items = [{ label: 'Ciudades' }];
  if (selectedCity.value || selectedSede.value?.ciudad) items.push({ label: selectedCity.value || selectedSede.value.ciudad });
  if (selectedSede.value) items.push({ label: selectedSede.value.nombre });
  if (selectedEdificio.value) items.push({ label: selectedEdificio.value.nombre });
  if (selectedEdificio.value && route.query.piso) items.push({ label: formatFloor(route.query.piso) });
  return items;
});
const navigateLocation = (index) => {
  if (index === 0) resetToCities();
  else if (index === 1) resetToSedes();
  else if (index === 2) resetToEdificios();
  else if (index === 3) router.push({ query: { ...route.query, piso: undefined } });
};
const inventoryScopeLabel = computed(() => {
  if (currentView.value !== 'inventario') return '';
  return selectedEdificio.value?.nombre || selectedSede.value?.nombre || selectedCity.value;
});
watch(() => route.query, () => { inventoryFilters.page = 1; });
const changeView = (view) => {
  if (view === 'mapa') {
    router.push(viewLocation(view, route.query, selectedCity.value || selectedSede.value?.ciudad));
  } else if (view !== currentView.value) {
    setVista(view);
  }
};
</script>

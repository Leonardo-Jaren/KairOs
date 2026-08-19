<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <RouterLink to="/espacios/mapa"
        class="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-primary-600">
        <ArrowLeft :size="17" /> Volver al mapa de campus
      </RouterLink>
      <RouterLink to="/espacios" class="text-xs font-semibold text-slate-400 hover:text-primary-600">Inventario de
        espacios</RouterLink>
    </div>

    <div v-if="loading" class="grid gap-4" aria-label="Cargando plano">
      <div class="h-2 overflow-hidden rounded-full bg-slate-100"><span
          class="block h-full w-1/3 animate-pulse rounded-full bg-primary-400" /></div>
      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><span v-for="index in 4" :key="index"
          class="h-20 animate-pulse rounded-2xl bg-slate-100" /></div>
      <div class="h-72 animate-pulse rounded-3xl border border-slate-200 bg-white" />
    </div>
    <div v-else-if="error" class="rounded-2xl border border-danger-200 bg-danger-50 p-6 text-sm text-danger-700">{{
      error }}</div>
    <template v-else-if="espacio">
      <header
        class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end xl:grid-cols-[minmax(340px,1.15fr)_minmax(500px,1fr)_auto]">
        <div class="min-w-0 lg:col-start-1 lg:row-start-1">
          <div class="flex flex-wrap items-center gap-2"><span
              class="rounded-full bg-primary-50 px-3 py-1 text-[10px] font-extrabold uppercase tracking-[0.18em] text-primary-700">Plano
              interactivo</span><span
              class="rounded-full bg-slate-100 px-3 py-1 text-[10px] font-bold text-slate-500">{{
                formatBuildingName(espacio.pabellon) }} · {{ formatFloor(espacio.piso) }}</span></div>
          <h1 class="mt-3 text-3xl font-extrabold tracking-tight text-slate-950">{{ espacio.codigo_espacio }}</h1>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Selecciona una estación para consultar sus
            características o registrar una falla. Activa la edición para adaptar el plano a la distribución real del
            laboratorio.</p>
        </div>
        <div v-if="canEdit"
          class="grid shrink-0 gap-2 sm:flex sm:justify-end lg:col-start-2 lg:row-start-1 xl:col-start-3"
          :class="equipos.length ? 'grid-cols-2' : 'grid-cols-1'">
          <BaseButton size="sm" variant="secondary" :disabled="editing" :full-width="false" class="w-full sm:w-auto"
            @click="openCreateEquipment"><template #icon>
              <Plus :size="15" />
            </template>Nuevo
            equipo</BaseButton>
          <BaseButton v-if="equipos.length && !editing" size="sm" variant="accent" :full-width="false"
            class="w-full sm:w-auto" @click="startEditing"><template #icon>
              <Pencil :size="15" />
            </template>Editar distribución</BaseButton>
          <div v-else-if="editing"
            class="inline-flex min-h-9 items-center justify-center gap-2 rounded-lg border border-primary-200 bg-primary-50 px-3 text-xs font-bold text-primary-700">
            <LayoutGrid :size="15" />Edición activa
          </div>
        </div>
        <section
          class="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:col-span-2 lg:row-start-2 xl:col-span-1 xl:col-start-2 xl:row-start-1">
          <article
            class="flex min-w-0 items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 py-2 shadow-sm">
            <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-primary-50 text-primary-600">
              <MonitorCog :size="16" />
            </span>
            <div class="min-w-0">
              <p class="text-base font-extrabold leading-none text-slate-950">{{ equipos.length }}</p>
              <p class="mt-1 truncate text-[10px] leading-3 text-slate-500">Equipos ubicados</p>
            </div>
          </article>
          <article
            class="flex min-w-0 items-center gap-2 rounded-xl border border-success-200 bg-success-50/40 px-2.5 py-2 shadow-sm">
            <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-success-100 text-success-700">
              <Check :size="16" />
            </span>
            <div class="min-w-0">
              <p class="text-base font-extrabold leading-none text-success-800">{{ statusSummary.en_uso }}</p>
              <p class="mt-1 truncate text-[10px] leading-3 text-success-700">Operativos</p>
            </div>
          </article>
          <article
            class="flex min-w-0 items-center gap-2 rounded-xl border border-warning-200 bg-warning-50/40 px-2.5 py-2 shadow-sm">
            <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-warning-100 text-warning-700">
              <Wrench :size="16" />
            </span>
            <div class="min-w-0">
              <p class="text-base font-extrabold leading-none text-warning-800">{{ statusSummary.en_mantenimiento }}</p>
              <p class="mt-1 truncate text-[10px] leading-3 text-warning-700">En mantenimiento</p>
            </div>
          </article>
          <article
            class="flex min-w-0 items-center gap-2 rounded-xl border border-danger-200 bg-danger-50/40 px-2.5 py-2 shadow-sm">
            <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-danger-100 text-danger-700">
              <AlertTriangle :size="16" />
            </span>
            <div class="min-w-0">
              <p class="text-base font-extrabold leading-none text-danger-800">{{ statusSummary.dañado }}</p>
              <p class="mt-1 truncate text-[10px] leading-3 text-danger-700">Con falla</p>
            </div>
          </article>
        </section>
      </header>

      <section v-if="editing"
        class="sticky top-21 z-10 rounded-xl border border-primary-200 bg-primary-50/95 p-3 shadow-lg shadow-primary-950/8 backdrop-blur-xl sm:top-23 sm:rounded-2xl sm:p-4">
        <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex items-center gap-2.5">
            <span
              class="grid size-8 shrink-0 place-items-center rounded-lg bg-primary-500 text-white sm:size-10 sm:rounded-xl">
              <LayoutGrid :size="18" />
            </span>
            <div class="min-w-0">
              <p class="text-sm font-extrabold text-slate-900">Modo edición activo</p>
              <p class="truncate text-[11px] text-slate-500 sm:text-xs sm:leading-5">Elige un equipo y su nuevo puesto
                para
                moverlo.</p>
            </div>
          </div>
          <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-end">
            <div class="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-2 sm:contents">
              <div class="min-w-0 sm:w-42">
                <BaseSelect id="layout-columns" :model-value="columns" label="Ancho del laboratorio"
                  :options="columnOptions" @update:model-value="reflowPositions" />
              </div>
              <div>
                <p class="mb-1.5 text-xs font-semibold text-slate-600">Filas: {{ rows }}</p>
                <div class="flex overflow-hidden rounded-xl border border-slate-200 bg-white"><button type="button"
                    class="p-3 text-slate-500 hover:bg-slate-50 hover:text-primary-600" aria-label="Quitar fila"
                    @click="removeRow">
                    <ChevronDown :size="17" />
                  </button><button type="button"
                    class="border-l border-slate-200 p-3 text-slate-500 hover:bg-slate-50 hover:text-primary-600"
                    aria-label="Agregar fila" @click="addRow">
                    <ChevronUp :size="17" />
                  </button></div>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-2 sm:contents">
              <button type="button"
                class="flex min-h-10 min-w-0 items-center justify-center gap-1.5 rounded-xl border px-2 text-xs font-bold transition-colors sm:min-h-11 sm:justify-start sm:px-3"
                :class="selectedPosition?.es_docente ? 'border-primary-300 bg-primary-100 text-primary-700' : 'border-slate-200 bg-white text-slate-600 disabled:opacity-45'"
                :disabled="!selectedPosition" @click="toggleTeacher">
                <GraduationCap :size="16" class="shrink-0" /><span class="truncate sm:hidden">Docente</span><span
                  class="hidden sm:inline">{{ selectedPosition?.es_docente ? 'Quitar docente' : 'Marcar docente'
                  }}</span>
              </button>
              <BaseButton v-if="selectedLayoutEquipment" class="col-span-3 sm:col-span-1" variant="secondary" size="sm"
                :full-width="false" @click="manageSelectedEquipment"><template #icon>
                  <Settings2 :size="16" />
                </template>Gestionar equipo</BaseButton>
              <BaseButton variant="ghost" size="sm" :full-width="false" @click="cancelEditing"><template #icon>
                  <RotateCcw :size="16" />
                </template>Cancelar</BaseButton>
              <BaseButton variant="accent" size="sm" :loading="saving" :full-width="false" @click="saveLayout"><template
                  #icon>
                  <Save :size="16" />
                </template>Guardar</BaseButton>
            </div>
          </div>
        </div>
      </section>

      <section class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <header
          class="flex flex-col justify-between gap-4 border-b border-slate-100 bg-slate-50/70 px-5 py-4 sm:flex-row sm:items-center">
          <div class="flex items-center gap-3"><span
              class="grid size-10 place-items-center rounded-xl bg-secondary-950 text-primary-300">
              <Building2 :size="20" />
            </span>
            <div>
              <p class="text-sm font-extrabold text-slate-900">Distribución de {{ espacio.codigo_espacio }}</p>
              <p class="text-xs text-slate-500">Frente del aula en la parte superior</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-3 text-[10px] font-bold uppercase tracking-wide text-slate-500">
            <span class="inline-flex items-center gap-1.5">
              <CircleDot :size="13" class="text-success-500" />Operativo
            </span><span class="inline-flex items-center gap-1.5">
              <CircleDot :size="13" class="text-warning-500" />Mantenimiento
            </span><span class="inline-flex items-center gap-1.5">
              <CircleDot :size="13" class="text-danger-500" />Falla
            </span>
          </div>
        </header>

        <div v-if="equipos.length"
          class="overflow-x-auto bg-[linear-gradient(#f8fafc_1px,transparent_1px),linear-gradient(90deg,#f8fafc_1px,transparent_1px)] bg-[size:24px_24px] p-4 sm:p-6">
          <div
            class="mx-auto mb-5 flex min-w-160 max-w-4xl items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 bg-white/90 px-5 py-3 text-center shadow-sm">
            <GraduationCap :size="18" class="text-primary-600" />
            <div>
              <p class="text-xs font-extrabold uppercase tracking-[0.16em] text-slate-700">Frente del aula</p>
              <p class="text-[10px] text-slate-400">Pizarra y zona del docente<span v-if="teacherEquipment"> · {{
                teacherEquipment.codigo }} asignado</span></p>
            </div>
          </div>
          <div class="grid gap-3" :style="gridStyle()">
            <div v-for="cell in cells" :key="`${cell.row}-${cell.column}`"
              class="min-h-27 rounded-2xl p-1.5 text-left transition-colors"
              :class="[cell.isAisle ? 'border-x border-dashed border-slate-200 bg-slate-50/45' : editing ? 'border border-dashed border-slate-300 bg-white/55 hover:border-primary-300 hover:bg-primary-50/50' : cell.equipment ? 'bg-transparent' : 'bg-white/20', editing && selectedPositionId && !cell.equipment && !cell.isAisle ? 'cursor-cell' : '']"
              @dragover.prevent @drop.prevent="handleDrop($event, cell)">
              <PlanoEquipoCard v-if="cell.equipment" :equipment="cell.equipment" :editing="editing"
                :selected="selectedPositionId === cell.equipment.id" :teacher="cell.position.es_docente"
                @select="handleCellClick(cell)"
                @dragstart="$event.dataTransfer.setData('text/plain', String(cell.equipment.id))" />
              <button v-else-if="cell.isAisle" type="button"
                class="grid min-h-23 w-full place-items-center text-[9px] font-extrabold uppercase tracking-[0.2em] text-slate-300"
                :class="editing ? 'hover:text-primary-500' : 'cursor-default'"
                @click="editing && handleCellClick(cell)"><span v-if="cell.row === Math.ceil(rows / 2)"
                  class="-rotate-90">Pasillo</span></button>
              <button v-else-if="editing" type="button"
                class="grid min-h-23 w-full place-items-center text-[10px] font-bold uppercase tracking-wide text-slate-300 hover:text-primary-500"
                @click="handleCellClick(cell)">Puesto libre</button>
            </div>
          </div>
        </div>
        <div v-else class="px-6 py-20 text-center">
          <MonitorCog :size="38" class="mx-auto text-slate-300" />
          <p class="mt-4 font-semibold text-slate-700">Este espacio todavía no tiene equipos asignados.</p>
          <p class="mt-1 text-sm text-slate-400">Crea la primera PC sin salir del plano.</p>
          <BaseButton v-if="canEdit" class="mt-5" variant="accent" :full-width="false" @click="openCreateEquipment">
            <template #icon>
              <Plus :size="17" />
            </template>Agregar primera PC
          </BaseButton>
        </div>
      </section>
    </template>

    <EquipoPlanoPanel
      :equipment="equipmentDetailOpen || equipmentModalOpen || equipmentDeleteOpen ? null : selectedEquipo"
      :active-maintenances="activeMaintenances" :maintenance-loading="maintenanceLoading" :can-edit="canEdit"
      @close="selectedEquipo = null" @report="openReport" @edit="openEditEquipment" @delete="askDeleteEquipment"
      @manage="equipmentDetailOpen = true" />

    <EquipoFormModal :open="equipmentModalOpen" :form="equipmentForm" :errors="equipmentErrors"
      :saving="equipmentSaving" :editing="isEditingEquipment" :type-options="equipmentTypeOptions"
      :acquisition-options="acquisitionModeOptions" :status-options="equipmentStatusOptions" :lock-space="true"
      :space-name="espacio?.codigo_espacio ?? ''" @close="closeEquipmentModal" @submit="submitEquipment" />

    <BaseModal :open="equipmentDeleteOpen" title="Retirar equipo" size="sm" @close="cancelDeleteEquipment">
      <p class="text-sm leading-6 text-slate-600">La PC <strong class="text-slate-900">{{ pendingEquipmentDelete?.codigo
          }}</strong> se retirará del espacio y conservará su historial.</p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDeleteEquipment">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="equipmentSaving" :full-width="false" @click="confirmDeleteEquipment">
          Retirar</BaseButton>
      </template>
    </BaseModal>

    <EquipoDetailModal :open="equipmentDetailOpen" :equipo="selectedEquipo" :can-edit="canEdit"
      @close="equipmentDetailOpen = false" />

    <BaseModal :open="reportOpen" title="Registrar falla"
      :description="selectedEquipo ? `${selectedEquipo.codigo} · ${selectedEquipo.marca} ${selectedEquipo.modelo}` : ''"
      @close="closeReport">
      <form id="failure-form" class="flex flex-col gap-4" @submit.prevent="submitReport">
        <div class="rounded-xl border border-warning-200 bg-warning-50 p-4 text-sm leading-6 text-warning-800">
          <strong>Ticket correctivo:</strong> describe lo observado y define si el equipo debe ingresar a mantenimiento
          inmediatamente.
        </div>
        <BaseTextarea id="failure-description" v-model="reportForm.descripcion" appearance="light"
          label="Descripción de la falla" placeholder="Ej: El equipo enciende, pero no muestra imagen en el monitor..."
          :rows="4" :error="reportErrors.descripcion" />
        <BaseSelect id="failure-reporter" v-model="reportForm.reportado_por_id" label="Reportado por"
          :options="reporterOptions" :error="reportErrors.reportado_por_id" />
        <div class="grid gap-4 sm:grid-cols-2">
          <BaseSelect id="failure-attention" v-model="reportForm.atencion" label="Acción" :options="attentionOptions" />
          <BaseSelect id="failure-technician" v-model="reportForm.tecnico_id" label="Técnico responsable (opcional)"
            :options="technicianOptions" placeholder="Asignar después" />
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeReport">Cancelar</BaseButton>
        <BaseButton type="submit" form="failure-form" variant="accent" :loading="reportSaving" :full-width="false">
          <template #icon>
            <Wrench :size="17" />
          </template>Registrar
          falla
        </BaseButton>
      </template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>
<script setup>
import {
  AlertTriangle, ArrowLeft, Building2, Check, ChevronDown, ChevronUp,
  CircleDot, GraduationCap, LayoutGrid, MonitorCog, Pencil, Plus, RotateCcw, Save,
  Settings2, Wrench,
} from '@lucide/vue';
import { useRoute } from 'vue-router';

import BaseButton from '@/components/buttons/BaseButton.vue';
import EquipoDetailModal from '@/components/equipos/EquipoDetailModal.vue';
import EquipoFormModal from '@/components/equipos/EquipoFormModal.vue';
import EquipoPlanoPanel from '@/components/espacios/EquipoPlanoPanel.vue';
import PlanoEquipoCard from '@/components/espacios/PlanoEquipoCard.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { usePlanoEspacio } from '@/composables/espacios/usePlanoEspacio';
import { formatBuildingName, formatFloor } from '@/utils/formatters';

const route = useRoute();
const {
  espacio, equipos, loading, saving, error, editing, canEdit, columns, rows, cells,
  statusSummary, teacherEquipment, selectedPosition, selectedLayoutEquipment,
  selectedPositionId, selectedEquipo,
  equipmentDetailOpen, equipmentModalOpen, equipmentDeleteOpen, pendingEquipmentDelete,
  equipmentSaving, equipmentForm, equipmentErrors, isEditingEquipment,
  activeMaintenances, maintenanceLoading, reportOpen, reportSaving, reportForm,
  reportErrors, technicianOptions, reporterOptions, equipmentTypeOptions,
  acquisitionModeOptions, equipmentStatusOptions, toast,
  startEditing, cancelEditing, reflowPositions, addRow, removeRow, handleCellClick,
  handleDrop, toggleTeacher, saveLayout, openReport, closeReport, submitReport,
  openCreateEquipment, openEditEquipment, closeEquipmentModal, submitEquipment,
  askDeleteEquipment, cancelDeleteEquipment, confirmDeleteEquipment, closeToast,
  manageSelectedEquipment,
} = usePlanoEspacio(route.params.id);

const columnOptions = [3, 4, 5, 6, 7, 8].map((value) => ({ value, label: `${value} columnas` }));
const attentionOptions = [
  { value: 'en_proceso', label: 'Enviar ahora a mantenimiento' },
  { value: 'pendiente', label: 'Registrar como pendiente' },
];
const gridStyle = () => ({
  gridTemplateColumns: `repeat(${columns.value}, minmax(116px, 1fr))`,
  minWidth: `${columns.value * 132}px`,
});
</script>

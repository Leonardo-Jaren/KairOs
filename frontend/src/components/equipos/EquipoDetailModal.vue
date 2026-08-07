<script setup>
import { shallowRef, watch } from 'vue';
import { Pencil, Plus, Trash2 } from '@lucide/vue';

import AuditTimelineList from '@/components/historial/AuditTimelineList.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { TIPO_OPTIONS, getTipoIcon, useComponentes } from '@/composables/equipos/useComponentes';
import historialService from '@/services/historial.service';

const props = defineProps({
  open:     { type: Boolean, default: false },
  equipo:   { type: Object,  default: null },
  canEdit:  { type: Boolean, default: false },
});

defineEmits(['close']);

const activeTab        = shallowRef('info');
const timelineEvents   = shallowRef([]);
const timelineLoading  = shallowRef(false);
const timelineLoaded   = shallowRef(false);

const {
  componentes, loading: compLoading, saving, formOpen, deleteOpen, pendingDelete,
  form, formErrors, toast, isEditing,
  cargar, openCreate, openEdit, closeForm, submit,
  askDelete, cancelDelete, confirmDelete, closeToast, reset,
} = useComponentes();

const estadoClasses = {
  en_uso:           'bg-success-50 text-success-700',
  en_mantenimiento: 'bg-warning-50 text-warning-700',
  dañado:           'bg-danger-50 text-danger-700',
  de_baja:          'bg-slate-100 text-slate-600',
};
const estadoDotClasses = {
  en_uso:           'bg-success-500',
  en_mantenimiento: 'bg-warning-500',
  dañado:           'bg-danger-500',
  de_baja:          'bg-slate-400',
};

watch(() => props.equipo, (eq) => {
  activeTab.value      = 'info';
  timelineEvents.value = [];
  timelineLoaded.value = false;
  reset();
  if (eq) cargar(eq.id);
}, { immediate: true });

function switchTab(key) {
  if (activeTab.value !== key) closeForm();
  activeTab.value = key;
}

async function switchToTimeline() {
  if (activeTab.value !== 'timeline') closeForm();
  activeTab.value = 'timeline';
  if (timelineLoaded.value || !props.equipo) return;
  timelineLoading.value = true;
  try {
    const data = await historialService.listar({
      modulo: 'equipo',
      object_id: props.equipo.id,
      page_size: 50,
    });
    timelineEvents.value = data.results ?? data;
    timelineLoaded.value = true;
  } finally {
    timelineLoading.value = false;
  }
}

const tabs = [
  { key: 'info',       label: 'Información' },
  { key: 'componentes', label: 'Componentes' },
  { key: 'timeline',   label: 'Línea de Tiempo' },
];
</script>

<template>
  <BaseModal
    :open="open"
    :title="equipo?.codigo ?? ''"
    :description="`${equipo?.marca ?? ''} ${equipo?.modelo ?? ''} · ${equipo?.estado_display ?? ''}`"
    size="lg"
    @close="$emit('close')"
  >
    <div class="flex flex-col">

      <!-- Tab bar -->
      <div class="mb-5 flex border-b border-slate-200">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          class="-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === tab.key
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="tab.key === 'timeline' ? switchToTimeline() : switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Información -->
      <div v-if="activeTab === 'info'" class="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Código</dt>
          <dd class="mt-1 font-mono text-sm font-semibold text-slate-900">{{ equipo?.codigo }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Tipo</dt>
          <dd class="mt-1">
            <span class="rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700">
              {{ equipo?.tipo_equipo_display }}
            </span>
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Marca</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ equipo?.marca }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Modelo</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ equipo?.modelo }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">N° de serie</dt>
          <dd class="mt-1 font-mono text-xs text-slate-600">{{ equipo?.numero_serie }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Dirección MAC</dt>
          <dd class="mt-1 font-mono text-xs text-slate-600">{{ equipo?.numero_mac || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Espacio asignado</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ equipo?.espacio_nombre ?? 'Sin asignar' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Responsable</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ equipo?.responsable_usuario || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Adquisición</dt>
          <dd class="mt-1 text-sm text-slate-700">
            {{ equipo?.modo_adquisicion_display }} · {{ equipo?.fecha_adquisicion }}
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Estado</dt>
          <dd class="mt-1">
            <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="estadoClasses[equipo?.estado]">
              <span class="size-1.5 rounded-full" :class="estadoDotClasses[equipo?.estado]" />
              {{ equipo?.estado_display }}
            </span>
          </dd>
        </div>
      </div>

      <!-- Componentes -->
      <div v-else-if="activeTab === 'componentes'" class="flex flex-col gap-4">

        <!-- Formulario inline -->
        <Transition
          enter-from-class="opacity-0 -translate-y-2"
          enter-active-class="transition-all duration-200"
          leave-to-class="opacity-0 -translate-y-2"
          leave-active-class="transition-all duration-200"
        >
          <div v-if="formOpen" class="rounded-xl border border-primary-100 bg-primary-50/40 p-4">
            <p class="mb-3 text-sm font-semibold text-slate-800">
              {{ isEditing ? 'Editar componente' : 'Nuevo componente' }}
            </p>
            <form id="comp-form" class="grid gap-3 sm:grid-cols-2" @submit.prevent="submit(equipo?.id)">
              <BaseSelect
                id="comp-tipo"
                v-model="form.tipo"
                label="Tipo"
                :options="TIPO_OPTIONS"
                appearance="light"
                :error="formErrors.tipo"
              />
              <BaseInput
                id="comp-modelo"
                v-model="form.modelo"
                appearance="light"
                label="Modelo"
                placeholder="Ej: Ryzen 5 5600X"
                :error="formErrors.modelo"
              />
              <div class="sm:col-span-2">
                <BaseTextarea
                  id="comp-descripcion"
                  v-model="form.descripcion"
                  appearance="light"
                  label="Descripción (opcional)"
                  placeholder="Ej: 16 GB DDR4 3200 MHz"
                  :rows="2"
                />
              </div>
            </form>
            <div class="mt-3 flex justify-end gap-2">
              <BaseButton variant="ghost" :full-width="false" @click="closeForm">Cancelar</BaseButton>
              <BaseButton type="submit" form="comp-form" variant="accent" :loading="saving" :full-width="false">
                {{ isEditing ? 'Guardar' : 'Agregar' }}
              </BaseButton>
            </div>
          </div>
        </Transition>

        <!-- Botón agregar -->
        <div v-if="canEdit && !formOpen" class="flex justify-end">
          <BaseButton variant="accent" :full-width="false" @click="openCreate">
            <template #icon><Plus :size="16" /></template>
            Agregar componente
          </BaseButton>
        </div>

        <!-- Lista -->
        <div v-if="compLoading" class="py-8 text-center text-sm text-slate-400">Cargando componentes…</div>
        <div v-else-if="componentes.length === 0" class="py-8 text-center text-sm text-slate-400">
          Este equipo no tiene componentes registrados.
        </div>
        <ul v-else class="divide-y divide-slate-100">
          <li
            v-for="comp in componentes"
            :key="comp.id"
            class="flex items-center justify-between gap-3 py-3"
          >
            <div class="flex items-start gap-3">
              <span class="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                <component :is="getTipoIcon(comp.tipo)" :size="16" />
              </span>
              <div>
                <p class="text-sm font-semibold text-slate-900">
                  {{ comp.tipo_display }}
                  <span class="ml-1.5 font-normal text-slate-600">{{ comp.modelo }}</span>
                </p>
                <p v-if="comp.descripcion" class="text-xs text-slate-400">{{ comp.descripcion }}</p>
              </div>
            </div>
            <div v-if="canEdit" class="flex shrink-0 gap-1">
              <button type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
                @click="openEdit(comp)">
                <Pencil :size="15" />
              </button>
              <button type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
                @click="askDelete(comp)">
                <Trash2 :size="15" />
              </button>
            </div>
          </li>
        </ul>

        <!-- Confirmar eliminación -->
        <BaseModal :open="deleteOpen" title="Eliminar componente" size="sm" @close="cancelDelete">
          <p class="text-sm text-slate-600">
            ¿Eliminar el componente
            <strong class="text-slate-900">{{ pendingDelete?.tipo_display }} · {{ pendingDelete?.modelo }}</strong>?
            Esta acción no se puede deshacer.
          </p>
          <template #footer>
            <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
            <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete(equipo?.id)">
              Eliminar
            </BaseButton>
          </template>
        </BaseModal>
      </div>

      <!-- Línea de tiempo -->
      <div v-else>
        <AuditTimelineList :events="timelineEvents" :loading="timelineLoading" :inline="true" />
      </div>

    </div>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </BaseModal>
</template>

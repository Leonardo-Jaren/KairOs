<script setup>
import { Pencil, Plus, Trash2 } from '@lucide/vue';
import { shallowRef, watch } from 'vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useInstalaciones } from '@/composables/software/useInstalaciones';
import { formatCurrency, formatDate } from '@/utils/formatters';

const props = defineProps({
  open: { type: Boolean, default: false },
  producto: { type: Object, default: null },
  canEdit: { type: Boolean, default: false },
});

defineEmits(['close']);

const {
  instalaciones, loading: instalacionesLoading, saving, formOpen, deleteOpen, pendingDelete,
  form, formErrors, toast, isEditing, equipoSelectOptions,
  cargar, cargarOpciones, openCreate, openEdit, closeForm, submit,
  askDelete, cancelDelete, confirmDelete, closeToast, reset,
} = useInstalaciones();

const activeTab = shallowRef('info');

watch(() => props.producto, (producto) => {
  activeTab.value = 'info';
  reset();
  if (producto) {
    cargarOpciones();
    cargar({ producto_software_id: producto.id, page_size: 100 });
  }
}, { immediate: true });

function switchTab(key) {
  if (activeTab.value !== key) closeForm();
  activeTab.value = key;
}

function openCreateInstalacion() {
  openCreate({ producto_software: props.producto?.id });
}

const tabs = [
  { key: 'info', label: 'Información' },
  { key: 'instalaciones', label: 'Instalaciones' },
];
</script>

<template>
  <BaseModal
    :open="open"
    :title="producto ? `${producto.software} v${producto.version}` : ''"
    :description="producto?.tipo_licencia_display ?? ''"
    size="lg"
    @close="$emit('close')"
  >
    <div class="flex flex-col">

      <div class="mb-5 flex border-b border-slate-200">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          class="-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === tab.key
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Información -->
      <div v-if="activeTab === 'info'" class="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Software</dt>
          <dd class="mt-1 text-sm font-semibold text-slate-900">{{ producto?.software }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Versión</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ producto?.version }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Tipo de licencia</dt>
          <dd class="mt-1">
            <span class="rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700">
              {{ producto?.tipo_licencia_display }}
            </span>
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Costo anual</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ formatCurrency(producto?.costo_anual_total) }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Licencias totales</dt>
          <dd class="mt-1 text-sm font-semibold text-slate-900">{{ producto?.licencias_totales }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Usadas / Disponibles</dt>
          <dd class="mt-1 text-sm text-slate-700">
            {{ producto?.licencias_usadas }} / {{ producto?.licencias_disponibles }}
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Fecha de expiración</dt>
          <dd class="mt-1 text-sm text-slate-700">
            {{ producto?.fecha_expiracion ? formatDate(producto.fecha_expiracion) : 'Sin expiración' }}
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Estado de licencias</dt>
          <dd class="mt-1 flex gap-1.5">
            <span v-if="producto?.sobre_uso" class="rounded-full bg-danger-50 px-2.5 py-1 text-xs font-semibold text-danger-700">Sobre-uso</span>
            <span v-if="producto?.proxima_a_expirar" class="rounded-full bg-warning-50 px-2.5 py-1 text-xs font-semibold text-warning-700">Por expirar</span>
            <span v-if="!producto?.sobre_uso && !producto?.proxima_a_expirar" class="text-sm text-slate-400">Sin alertas</span>
          </dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="text-xs font-semibold uppercase tracking-wide text-slate-400">Descripción</dt>
          <dd class="mt-1 text-sm text-slate-700">{{ producto?.descripcion || '—' }}</dd>
        </div>
      </div>

      <!-- Instalaciones -->
      <div v-else-if="activeTab === 'instalaciones'" class="flex flex-col gap-4">

        <Transition
          enter-from-class="opacity-0 -translate-y-2"
          enter-active-class="transition-all duration-200"
          leave-to-class="opacity-0 -translate-y-2"
          leave-active-class="transition-all duration-200"
        >
          <div v-if="formOpen" class="rounded-xl border border-primary-100 bg-primary-50/40 p-4">
            <p class="mb-3 text-sm font-semibold text-slate-800">
              {{ isEditing ? 'Editar instalación' : 'Nueva instalación' }}
            </p>
            <form
              id="instalacion-form"
              class="grid gap-3 sm:grid-cols-2"
              @submit.prevent="submit({ producto_software_id: producto?.id, page_size: 100 })"
            >
              <BaseSelect
                v-if="!isEditing"
                id="inst-equipo"
                v-model="form.equipo"
                label="Equipo"
                :options="equipoSelectOptions"
                placeholder="Selecciona un equipo"
                appearance="light"
                :error="formErrors.equipo"
              />
              <BaseInput
                id="inst-licencia"
                v-model="form.numero_licencia_usado"
                appearance="light"
                label="Número de licencia (opcional)"
                placeholder="Ej: LIC-00123"
              />
              <BaseInput
                id="inst-fecha"
                v-model="form.fecha_instalacion"
                type="date"
                appearance="light"
                label="Fecha de instalación"
                :error="formErrors.fecha_instalacion"
              />
            </form>
            <div class="mt-3 flex justify-end gap-2">
              <BaseButton variant="ghost" :full-width="false" @click="closeForm">Cancelar</BaseButton>
              <BaseButton type="submit" form="instalacion-form" variant="accent" :loading="saving" :full-width="false">
                {{ isEditing ? 'Guardar' : 'Instalar' }}
              </BaseButton>
            </div>
          </div>
        </Transition>

        <div v-if="canEdit && !formOpen" class="flex justify-end">
          <BaseButton
            variant="accent"
            :full-width="false"
            :disabled="producto?.licencias_disponibles <= 0"
            @click="openCreateInstalacion"
          >
            <template #icon><Plus :size="16" /></template>
            Instalar en equipo
          </BaseButton>
        </div>
        <p v-if="canEdit && !formOpen && producto?.licencias_disponibles <= 0" class="text-right text-xs text-danger-600">
          No hay licencias disponibles para una nueva instalación.
        </p>

        <div v-if="instalacionesLoading" class="py-8 text-center text-sm text-slate-400">Cargando instalaciones…</div>
        <div v-else-if="instalaciones.length === 0" class="py-8 text-center text-sm text-slate-400">
          Este producto no está instalado en ningún equipo todavía.
        </div>
        <ul v-else class="divide-y divide-slate-100">
          <li
            v-for="inst in instalaciones"
            :key="inst.id"
            class="flex items-center justify-between gap-3 py-3"
          >
            <div>
              <p class="text-sm font-semibold text-slate-900">
                {{ inst.equipo_codigo }}
                <span class="ml-1.5 font-normal text-slate-500">{{ inst.espacio_nombre ?? 'Sin espacio' }}</span>
              </p>
              <p class="text-xs text-slate-400">
                Instalado el {{ formatDate(inst.fecha_instalacion) }}
                <span v-if="inst.numero_licencia_usado"> · Licencia {{ inst.numero_licencia_usado }}</span>
              </p>
            </div>
            <div v-if="canEdit" class="flex shrink-0 gap-1">
              <button type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
                aria-label="Editar instalación"
                @click="openEdit(inst)">
                <Pencil :size="15" />
              </button>
              <button type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
                aria-label="Eliminar instalación"
                @click="askDelete(inst)">
                <Trash2 :size="15" />
              </button>
            </div>
          </li>
        </ul>

        <BaseModal :open="deleteOpen" title="Eliminar instalación" size="sm" @close="cancelDelete">
          <p class="text-sm text-slate-600">
            ¿Eliminar la instalación en
            <strong class="text-slate-900">{{ pendingDelete?.equipo_codigo }}</strong>?
            Esto liberará una licencia disponible.
          </p>
          <template #footer>
            <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
            <BaseButton
              variant="danger"
              :loading="saving"
              :full-width="false"
              @click="confirmDelete({ producto_software_id: producto?.id, page_size: 100 })"
            >
              Eliminar
            </BaseButton>
          </template>
        </BaseModal>
      </div>

    </div>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </BaseModal>
</template>

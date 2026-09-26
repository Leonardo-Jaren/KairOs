<script setup>
import { computed } from 'vue';
import { AlertTriangle, CheckCircle2, ClipboardCheck } from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';

const props = defineProps({
  open: { type: Boolean, default: false },
  ticket: { type: Object, default: null },
  form: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
  resultadoOptions: { type: Array, default: () => [] },
});

const emit = defineEmits(['close', 'submit']);

const hasIncident = computed(() => Boolean(props.ticket?.incidencia_origen_id));
const closesIncident = computed(() => hasIncident.value && props.form.resultado_equipo === 'en_uso');
const submitLabel = computed(() => {
  if (closesIncident.value) return 'Finalizar y cerrar incidencia';
  if (props.form.resultado_equipo === 'dañado') return 'Finalizar como equipo dañado';
  if (props.form.resultado_equipo === 'de_baja') return 'Finalizar y dar de baja';
  return 'Finalizar mantenimiento';
});

const spaceLabel = computed(() => props.ticket?.equipo?.espacio_nombre || 'Sin espacio asignado');
const technicianLabel = computed(() => props.ticket?.tecnico_responsable || 'Sin asignar');
</script>

<template>
  <BaseModal
    :open="open"
    :title="`Finalizar mantenimiento #${ticket?.id ?? ''}`"
    description="Registra el trabajo realizado, prueba el equipo y define su resultado operativo."
    size="lg"
    @close="emit('close')"
  >
    <form id="finalizar-mantenimiento-form" class="grid gap-5" @submit.prevent="emit('submit')">
      <section class="grid gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:grid-cols-2" aria-label="Resumen de la orden">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Equipo</p>
          <p class="mt-1 text-sm font-bold text-slate-900">{{ ticket?.equipo?.codigo || '—' }}</p>
          <p class="text-xs text-slate-500">{{ ticket?.equipo?.marca }} {{ ticket?.equipo?.modelo }}</p>
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Espacio</p>
          <p class="mt-1 text-sm font-semibold text-slate-800">{{ spaceLabel }}</p>
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Tipo</p>
          <p class="mt-1 text-sm font-semibold text-slate-800">{{ ticket?.tipo_mantenimiento_display || ticket?.tipo_mantenimiento || '—' }}</p>
        </div>
        <div>
          <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Técnico responsable</p>
          <p class="mt-1 text-sm font-semibold text-slate-800">{{ technicianLabel }}</p>
        </div>
        <div v-if="hasIncident" class="sm:col-span-2">
          <p class="text-[10px] font-bold uppercase tracking-wide text-slate-400">Incidencia relacionada</p>
          <p class="mt-1 text-sm font-semibold text-warning-700">INC-{{ ticket.incidencia_origen_id }}</p>
        </div>
      </section>

      <div class="grid gap-4 sm:grid-cols-2">
        <BaseTextarea
          id="finalizar-diagnostico"
          v-model="form.diagnostico"
          appearance="light"
          label="Diagnóstico *"
          placeholder="Qué se encontró en el equipo"
          :rows="3"
          :error="errors.diagnostico"
        />
        <BaseTextarea
          id="finalizar-trabajo"
          v-model="form.trabajo_realizado"
          appearance="light"
          label="Trabajo realizado *"
          placeholder="Qué se hizo para atender la falla"
          :rows="3"
          :error="errors.trabajo_realizado"
        />
      </div>

      <section class="grid gap-3 rounded-2xl border border-slate-200 p-4">
        <div class="flex items-start gap-3">
          <span class="grid size-9 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600">
            <ClipboardCheck :size="18" aria-hidden="true" />
          </span>
          <div>
            <h3 class="text-sm font-bold text-slate-900">Verificación del equipo</h3>
            <p class="mt-0.5 text-xs leading-5 text-slate-500">Confirma que ejecutaste una prueba antes de finalizar la orden.</p>
          </div>
        </div>
        <label
          for="finalizar-prueba"
          class="flex min-h-11 cursor-pointer items-center gap-3 rounded-xl border px-3 py-2.5 transition-colors"
          :class="errors.prueba_realizada ? 'border-danger-300 bg-danger-50' : 'border-slate-200 hover:border-primary-300 hover:bg-primary-50/40'"
        >
          <input
            id="finalizar-prueba"
            v-model="form.prueba_realizada"
            type="checkbox"
            class="size-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
          />
          <span class="text-sm font-semibold text-slate-700">Prueba de funcionamiento realizada *</span>
        </label>
        <p v-if="errors.prueba_realizada" role="alert" class="text-xs text-danger-600">{{ errors.prueba_realizada }}</p>
        <BaseTextarea
          id="finalizar-observacion"
          v-model="form.observacion_prueba"
          appearance="light"
          label="Observación de la prueba (opcional)"
          placeholder="Ejemplo: inició el sistema y respondió el teclado"
          :rows="2"
          :error="errors.observacion_prueba"
        />
      </section>

      <BaseSelect
        id="finalizar-resultado"
        v-model="form.resultado_equipo"
        label="Resultado del equipo *"
        :options="resultadoOptions"
        placeholder="Selecciona el resultado"
        :error="errors.resultado_equipo"
      />

      <div v-if="closesIncident" class="flex items-start gap-3 rounded-xl border border-success-200 bg-success-50 px-3 py-3 text-sm text-success-800" role="status">
        <CheckCircle2 :size="18" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p>El equipo quedará funcional y la incidencia relacionada se cerrará automáticamente.</p>
      </div>
      <div v-else-if="form.resultado_equipo && form.resultado_equipo !== 'en_uso'" class="flex items-start gap-3 rounded-xl border border-warning-200 bg-warning-50 px-3 py-3 text-sm text-warning-800" role="status">
        <AlertTriangle :size="18" class="mt-0.5 shrink-0" aria-hidden="true" />
        <p>La orden terminará, pero la incidencia permanecerá abierta para otra intervención.</p>
      </div>
    </form>

    <template #footer>
      <BaseButton variant="ghost" :full-width="false" @click="emit('close')">Cancelar</BaseButton>
      <BaseButton type="submit" form="finalizar-mantenimiento-form" variant="accent" :loading="saving" :full-width="false">
        {{ submitLabel }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

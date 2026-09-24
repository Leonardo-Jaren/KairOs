<script setup>
import { Layers } from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

defineProps({
  open: { type: Boolean, default: false },
  target: { type: Object, default: () => null },
  form: { type: Object, required: true },
  options: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'submit']);
</script>

<template>
  <BaseModal
    :open="open"
    :title="form.assignment_id ? 'Cambiar técnico de piso' : 'Asignar técnico de piso'"
    :description="`Asigna el técnico referente operativo para el ${target?.piso ? 'Piso ' + target.piso : 'piso'} de ${target?.edificio_nombre || 'este pabellón'}.`"
    size="sm"
    @close="emit('close')"
  >
    <form id="piso-tecnico-form" class="space-y-4" @submit.prevent="emit('submit')">
      <div class="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5 text-xs">
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-500">Ámbito territorial</span>
          <span class="inline-flex items-center gap-1 rounded bg-primary-100 px-2 py-0.5 font-bold text-primary-800">
            <Layers :size="12" />
            Piso de Pabellón
          </span>
        </div>
        <p class="mt-1.5 font-bold text-slate-900">
          {{ target?.edificio_nombre }} · Piso {{ target?.piso }}
        </p>
      </div>

      <BaseSelect
        id="floor-technician-user"
        v-model="form.usuario_id"
        label="Técnico encargado"
        :options="options"
        placeholder="Seleccionar técnico..."
        required
      />

      <BaseSelect
        id="floor-technician-resp"
        v-model="form.tipo_responsabilidad"
        label="Rol de responsabilidad territorial"
        :options="[
          { value: 'tecnico', label: 'Soporte técnico de piso' },
          { value: 'responsable', label: 'Responsable operativo de piso' },
        ]"
      />
    </form>

    <template #footer>
      <BaseButton
        variant="ghost"
        :full-width="false"
        @click="emit('close')"
      >
        Cancelar
      </BaseButton>
      <BaseButton
        type="submit"
        form="piso-tecnico-form"
        variant="accent"
        :loading="saving"
        :full-width="false"
      >
        {{ form.assignment_id ? 'Actualizar asignación' : 'Asignar técnico' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';

const props = defineProps({
  open: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  creationMode: { type: String, default: 'sede' },
  city: { type: String, default: '' },
  cityLocked: { type: Boolean, default: false },
  cityOptions: { type: Array, default: () => [] },
  form: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
  typeOptions: { type: Array, required: true },
});

const emit = defineEmits(['close', 'submit']);

const modalTitle = computed(() => {
  if (props.isEditing) return 'Editar sede';
  return props.creationMode === 'city' ? 'Crear ciudad y primera sede' : 'Nueva sede';
});

const modalDescription = computed(() => {
  if (props.isEditing) return 'Actualiza los datos de esta sede.';
  if (props.creationMode === 'city') {
    return 'Crea la ciudad y su primera sede. Después podrás añadir otras sedes a la misma ciudad.';
  }
  if (props.city) return `La nueva sede se registrará en ${props.city}.`;
  return 'Registra una sede para organizar sus pabellones.';
});
</script>

<template>
  <BaseModal
    :open="open"
    :title="modalTitle"
    :description="modalDescription"
    @close="emit('close')"
  >
    <form id="sede-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="emit('submit')">
      <BaseInput
        id="sede-codigo"
        v-model="form.codigo"
        appearance="light"
        label="Código"
        placeholder="LOC-01"
        :error="errors.codigo"
      />
      <BaseInput
        id="sede-nombre"
        v-model="form.nombre"
        appearance="light"
        :label="creationMode === 'city' ? 'Nombre de la primera sede' : 'Nombre de la sede'"
        placeholder="Campus Central Huánuco"
        :error="errors.nombre"
      />
      <BaseInput
        v-if="creationMode === 'city' && !isEditing"
        id="sede-ciudad"
        v-model="form.ciudad_nombre"
        appearance="light"
        label="Nombre de la ciudad"
        placeholder="Huánuco"
        :error="errors.ciudad_nombre"
      />
      <BaseSelect
        v-else
        id="sede-ciudad"
        v-model="form.ciudad_id"
        label="Ciudad"
        :options="cityOptions"
        placeholder="Seleccionar ciudad"
        :disabled="cityLocked && !isEditing"
        :error="errors.ciudad_id"
      />
      <BaseSelect
        id="sede-tipo"
        v-model="form.tipo"
        label="Tipo de ubicación"
        :options="typeOptions"
        :error="errors.tipo"
      />
      <div class="sm:col-span-2">
        <BaseTextarea
          id="sede-descripcion"
          v-model="form.descripcion"
          appearance="light"
          label="Descripción (opcional)"
          placeholder="Información adicional sobre la sede y su infraestructura."
          :rows="2"
        />
      </div>
      <label class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <input
          v-model="form.activo"
          type="checkbox"
          class="size-4 accent-primary-500"
        />
        <span>
          <span class="block text-sm font-semibold text-slate-800">Local activo</span>
          <span class="block text-xs text-slate-500">Permite registrar y gestionar pabellones en esta ubicación.</span>
        </span>
      </label>
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
        form="sede-form"
        variant="accent"
        :loading="saving"
        :full-width="false"
      >
          {{ isEditing ? 'Guardar cambios' : creationMode === 'city' ? 'Crear ciudad y sede' : 'Crear sede' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

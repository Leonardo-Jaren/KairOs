<script setup>
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';

defineProps({
  open: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  form: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
  sedesOptions: { type: Array, required: true },
});

const emit = defineEmits(['close', 'submit']);
</script>

<template>
  <BaseModal
    :open="open"
    :title="isEditing ? 'Editar pabellón' : 'Nuevo pabellón'"
    description="Registra el bloque físico que agrupará pisos y ambientes tecnológicos."
    @close="emit('close')"
  >
    <form id="edificio-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="emit('submit')">
      <BaseInput
        id="edificio-codigo"
        v-model="form.codigo"
        appearance="light"
        label="Código"
        placeholder="PAB-01"
        :error="errors.codigo"
      />
      <BaseInput
        id="edificio-nombre"
        v-model="form.nombre"
        appearance="light"
        label="Nombre del pabellón"
        placeholder="Pabellón 1 - Ciencias e Ingeniería"
        :error="errors.nombre"
      />
      <div class="sm:col-span-2">
        <BaseSelect
          id="edificio-sede"
          v-model="form.local_id"
          label="Sede física correspondiente"
          :options="sedesOptions"
          placeholder="Seleccionar sede"
          :error="errors.local_id"
        />
      </div>
      <div class="sm:col-span-2">
        <BaseTextarea
          id="edificio-descripcion"
          v-model="form.descripcion"
          appearance="light"
          label="Descripción (opcional)"
          placeholder="Detalles sobre las facultades, especialidades o departamentos del bloque."
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
          <span class="block text-sm font-semibold text-slate-800">Pabellón activo</span>
          <span class="block text-xs text-slate-500">Permite registrar y gestionar pisos y ambientes en este pabellón.</span>
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
        form="edificio-form"
        variant="accent"
        :loading="saving"
        :full-width="false"
      >
        {{ isEditing ? 'Guardar cambios' : 'Crear pabellón' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

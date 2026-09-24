<script setup>
import { Layers } from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

defineProps({
  open: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  form: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
  sedesOptions: { type: Array, required: true },
  edificiosOptions: { type: Array, required: true },
  existingFloors: { type: Array, default: () => [] },
  typeOptions: { type: Array, required: true },
});

const emit = defineEmits(['close', 'submit']);
</script>

<template>
  <BaseModal
    :open="open"
    :title="isEditing ? 'Editar ambiente' : 'Nuevo ambiente'"
    description="Registra la ubicación física en un pabellón y piso; luego podrás diseñar su plano de equipos."
    @close="emit('close')"
  >
    <form id="espacio-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="emit('submit')">
      <BaseInput
        id="espacio-codigo"
        v-model="form.codigo_espacio"
        appearance="light"
        label="Código del ambiente"
        placeholder="LAB-203"
        :error="errors.codigo_espacio"
      />

      <BaseSelect
        id="espacio-tipo"
        v-model="form.tipo"
        label="Tipo de ambiente"
        :options="typeOptions"
        :error="errors.tipo"
      />

      <!-- Selector en cascada: Sede -->
      <BaseSelect
        id="espacio-sede"
        v-model="form.local_id"
        label="Sede (filtro)"
        :options="sedesOptions"
        placeholder="Todas las sedes"
      />

      <!-- Selector en cascada: Pabellón / Edificio -->
      <BaseSelect
        id="espacio-edificio"
        v-model="form.edificio_id"
        label="Pabellón / Edificio"
        :options="edificiosOptions"
        placeholder="Seleccionar pabellón"
        :error="errors.edificio_id"
      />

      <!-- Selector de piso inteligente asistido -->
      <div class="sm:col-span-2 flex flex-col gap-2 rounded-xl border border-slate-200/80 bg-slate-50/70 p-3.5">
        <div class="flex items-center justify-between">
          <label for="espacio-piso-input" class="text-xs font-bold text-slate-700 flex items-center gap-1.5">
            <Layers :size="14" class="text-primary-600" />
            Número de piso
          </label>
          <span v-if="existingFloors.length > 0" class="text-[11px] text-slate-400">
            Sugerencias de pisos existentes en este pabellón:
          </span>
        </div>

        <!-- Chips de pisos existentes -->
        <div v-if="existingFloors.length > 0" class="flex flex-wrap gap-1.5 pt-1">
          <button
            v-for="floorNum in existingFloors"
            :key="floorNum"
            type="button"
            class="rounded-lg px-3 py-1 text-xs font-bold transition-all"
            :class="String(form.piso) === String(floorNum)
              ? 'bg-primary-500 text-white shadow-xs'
              : 'border border-slate-200 bg-white text-slate-700 hover:border-primary-300 hover:bg-primary-50/50'"
            @click="form.piso = String(floorNum)"
          >
            Piso {{ floorNum }}
          </button>
        </div>

        <div class="mt-1">
          <BaseInput
            id="espacio-piso-input"
            v-model="form.piso"
            appearance="light"
            type="number"
            label="O escribe el número de piso directamente:"
            placeholder="Ej. 2"
            :error="errors.piso"
          />
        </div>
      </div>

      <label class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <input
          v-model="form.activo"
          type="checkbox"
          class="size-4 accent-primary-500"
        />
        <span>
          <span class="block text-sm font-semibold text-slate-800">Ambiente activo</span>
          <span class="block text-xs text-slate-500">Permite asignar usuarios, puestos y computadoras a este espacio.</span>
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
        form="espacio-form"
        variant="accent"
        :loading="saving"
        :full-width="false"
      >
        {{ isEditing ? 'Guardar cambios' : 'Crear ambiente' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

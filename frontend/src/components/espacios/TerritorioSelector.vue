<script setup>
import { Pencil, Plus, Trash2 } from "@lucide/vue";
import BaseButton from "@/components/buttons/BaseButton.vue";
import BaseSelect from "@/components/selects/BaseSelect.vue";

defineProps({
  city: { type: [String, Number], default: "" },
  cityOptions: { type: Array, default: () => [] },
  local: { type: [String, Number], default: "" },
  localOptions: { type: Array, default: () => [] },
  localIsReal: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});
const emit = defineEmits([
  "update:city",
  "update:local",
  "create-local",
  "edit-local",
  "delete-local",
]);
</script>

<template>
  <section
    class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
  >
    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
      <div class="min-w-0">
        <BaseSelect
          id="campus-city"
          :model-value="city"
          label="Ciudad"
          :options="cityOptions"
          :disabled="disabled"
          @update:model-value="emit('update:city', $event)"
        />
      </div>
      <div class="min-w-0">
        <BaseSelect
          id="campus-local"
          :model-value="local"
          label="Local"
          :options="localOptions"
          placeholder="Seleccionar local"
          :disabled="disabled"
          @update:model-value="emit('update:local', $event)"
        />
      </div>
      <div class="flex items-end gap-2 md:col-span-2 xl:col-span-1">
        <BaseButton
          v-if="canEdit"
          variant="accent"
          :full-width="false"
          :disabled="disabled"
          @click="emit('create-local')"
          ><template #icon><Plus :size="16" /></template>Nuevo local</BaseButton
        >
        <button
          v-if="canEdit && localIsReal"
          type="button"
          class="grid min-h-11 min-w-11 place-items-center rounded-xl border border-slate-200 text-slate-500 transition hover:border-primary-300 hover:text-primary-600 disabled:opacity-40"
          :disabled="disabled"
          aria-label="Editar local"
          @click="emit('edit-local')"
        >
          <Pencil :size="16" />
        </button>
        <button
          v-if="canEdit && localIsReal"
          type="button"
          class="grid min-h-11 min-w-11 place-items-center rounded-xl border border-slate-200 text-slate-500 transition hover:border-danger-300 hover:text-danger-600 disabled:opacity-40"
          :disabled="disabled"
          aria-label="Desactivar local"
          @click="emit('delete-local')"
        >
          <Trash2 :size="16" />
        </button>
      </div>
    </div>
    <p v-if="disabled" class="mt-3 text-xs font-medium text-warning-700" role="status">
      Guarda o cancela la edición del croquis para cambiar de territorio.
    </p>
  </section>
</template>

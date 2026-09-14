<script setup>
import { computed, useSlots } from 'vue';
import { CircleAlert } from '@lucide/vue';

const props = defineProps({
  modelValue:  { type: String,  default: '' },
  type:        { type: String,  default: 'text' },
  placeholder: { type: String,  default: '' },
  label:       { type: String,  default: '' },
  error:       { type: String,  default: '' },
  id:          { type: String,  required: true },
  disabled:    { type: Boolean, default: false },
  appearance:  { type: String,  default: 'dark' },
  autocomplete:{ type: String,  default: 'off' },
});

const emit  = defineEmits(['update:modelValue']);
const slots = useSlots();
const value = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full">

    <!-- Etiqueta superior del campo -->
    <label
      v-if="label"
      :for="id"
      class="text-xs font-semibold tracking-wide pl-0.5 select-none"
      :class="appearance === 'light' ? 'text-slate-600' : 'text-white/50'"
    >
      {{ label }}
    </label>

    <!-- Contenedor interactivo del input con soporte para iconos y acciones -->
    <div
      class="group relative flex items-center min-h-11 rounded-xl border overflow-hidden transition-all duration-200"
      :class="[
        error
          ? (appearance === 'light'
              ? 'bg-danger-50/50 border-danger-300 focus-within:border-danger-400 focus-within:ring-2 focus-within:ring-danger-100'
              : 'bg-danger-500/10 border-danger-500/40 focus-within:border-danger-400 focus-within:ring-2 focus-within:ring-danger-500/20')
          : (appearance === 'light'
              ? 'bg-white border-slate-200 hover:border-slate-300 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-500/20'
              : 'bg-white/[0.07] border-white/15 hover:bg-white/10 hover:border-white/25 focus-within:bg-white/10 focus-within:border-white/55 focus-within:ring-2 focus-within:ring-white/[0.07]')
      ]"
    >
      <!-- Icono contextual izquierdo -->
      <span
        v-if="slots.icon"
        class="absolute left-3.5 flex items-center transition-colors duration-200 pointer-events-none"
        :class="appearance === 'light' ? 'text-slate-400 group-focus-within:text-primary-600' : 'text-white/35 group-focus-within:text-white/75'"
        aria-hidden="true"
      >
        <slot name="icon" />
      </span>

      <!-- Elemento input con soporte para autofill nativo mediante clases Tailwind -->
      <input
        :id="id"
        :type="type"
        :disabled="disabled"
        :placeholder="placeholder"
        v-model="value"
        :autocomplete="autocomplete"
        spellcheck="false"
        class="w-full h-full rounded-xl bg-transparent outline-none text-sm py-2.5 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        :class="[
          slots.icon ? 'pl-10' : 'pl-3.5',
          slots.action ? 'pr-10' : 'pr-3.5',
          appearance === 'light'
            ? 'text-slate-800 placeholder-slate-400 autofill:rounded-xl autofill:shadow-[inset_0_0_0_1000px_#ffffff] autofill:[-webkit-text-fill-color:#0f172a]'
            : 'text-white placeholder-white/35 autofill:rounded-xl autofill:shadow-[inset_0_0_0_1000px_#1c2b3e] autofill:[-webkit-text-fill-color:#ffffff]'
        ]"
      />

      <!-- Accion interactiva derecha (ej. alternar visibilidad de contrasena) -->
      <span
        v-if="slots.action"
        class="absolute right-2.5 flex items-center transition-colors duration-200"
      >
        <slot name="action" />
      </span>
    </div>

    <!-- Mensaje de error accesible -->
    <Transition
      enter-from-class="opacity-0 -translate-y-1"
      enter-active-class="transition-all duration-200"
      leave-to-class="opacity-0 -translate-y-1"
      leave-active-class="transition-all duration-200"
    >
      <p
        v-if="error"
        role="alert"
        class="flex items-center gap-1.5 pl-0.5 text-[13px]"
        :class="appearance === 'light' ? 'text-danger-600' : 'text-danger-400'"
      >
        <CircleAlert :size="13" class="shrink-0" />
        {{ error }}
      </p>
    </Transition>

  </div>
</template>

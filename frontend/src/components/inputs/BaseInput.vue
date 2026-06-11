<script setup>
import { computed, useSlots } from 'vue';

const props = defineProps({
  modelValue:  { type: String,  default: '' },
  type:        { type: String,  default: 'text' },
  placeholder: { type: String,  default: '' },
  label:       { type: String,  default: '' },
  error:       { type: String,  default: '' },
  id:          { type: String,  required: true },
  disabled:    { type: Boolean, default: false },
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

    <label
      v-if="label"
      :for="id"
      class="text-xs font-medium text-white/50 tracking-wide pl-0.5 select-none"
    >
      {{ label }}
    </label>

    <div
      class="relative flex items-center rounded-[10px] border transition-all duration-200"
      :class="error
        ? 'bg-red-500/5 border-red-500/50 focus-within:border-red-500/80 focus-within:ring-2 focus-within:ring-red-500/10'
        : 'bg-white/[0.07] border-white/15 hover:bg-white/10 hover:border-white/25 focus-within:bg-white/10 focus-within:border-white/55 focus-within:ring-2 focus-within:ring-white/[0.07]'"
    >
      <span
        v-if="slots.icon"
        class="absolute left-3.5 flex items-center text-white/35 transition-colors duration-200 group-focus-within:text-white/70"
        aria-hidden="true"
      >
        <slot name="icon" />
      </span>

      <input
        :id="id"
        :type="type"
        :disabled="disabled"
        :placeholder="placeholder"
        v-model="value"
        autocomplete="off"
        spellcheck="false"
        class="w-full bg-transparent outline-none text-white placeholder-white/30 text-sm py-2.5 pr-4 disabled:opacity-40 disabled:cursor-not-allowed"
        :class="slots.icon ? 'pl-10' : 'pl-4'"
      />
    </div>

    <Transition
      enter-from-class="opacity-0 -translate-y-1"
      enter-active-class="transition-all duration-200"
      leave-to-class="opacity-0 -translate-y-1"
      leave-active-class="transition-all duration-200"
    >
      <p v-if="error" role="alert" class="flex items-center gap-1.5 text-[13px] text-red-300 pl-0.5">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true" class="shrink-0">
          <circle cx="6.5" cy="6.5" r="6" stroke="currentColor" stroke-opacity="0.6"/>
          <path d="M6.5 3.5V7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          <circle cx="6.5" cy="9.5" r="0.6" fill="currentColor"/>
        </svg>
        {{ error }}
      </p>
    </Transition>

  </div>
</template>
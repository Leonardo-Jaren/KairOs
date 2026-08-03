<script setup>
import { computed } from 'vue';
import { CircleAlert } from '@lucide/vue';

const props = defineProps({
  modelValue:  { type: String,  default: '' },
  placeholder: { type: String,  default: '' },
  label:       { type: String,  default: '' },
  error:       { type: String,  default: '' },
  id:          { type: String,  required: true },
  disabled:    { type: Boolean, default: false },
  appearance:  { type: String,  default: 'dark' },
  rows:        { type: Number,  default: 3 },
});

const emit = defineEmits(['update:modelValue']);
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
      class="text-xs font-semibold tracking-wide pl-0.5 select-none"
      :class="appearance === 'light' ? 'text-slate-600' : 'text-white/50'"
    >
      {{ label }}
    </label>

    <div
      class="relative flex items-center rounded-[10px] border transition-all duration-200"
      :class="error
        ? 'bg-danger-50 border-danger-300 focus-within:border-danger-400 focus-within:ring-4 focus-within:ring-danger-100'
        : appearance === 'light'
          ? 'bg-white border-slate-200 hover:border-slate-300 focus-within:border-primary-500 focus-within:ring-4 focus-within:ring-primary-100'
          : 'bg-white/[0.07] border-white/15 hover:bg-white/10 hover:border-white/25 focus-within:bg-white/10 focus-within:border-white/55 focus-within:ring-2 focus-within:ring-white/[0.07]'"
    >
      <textarea
        :id="id"
        :disabled="disabled"
        :placeholder="placeholder"
        :rows="rows"
        v-model="value"
        spellcheck="false"
        class="w-full resize-none bg-transparent outline-none text-sm py-2.5 px-4 disabled:opacity-40 disabled:cursor-not-allowed"
        :class="appearance === 'light' ? 'text-slate-800 placeholder-slate-400' : 'text-white placeholder-white/30'"
      />
    </div>

    <Transition
      enter-from-class="opacity-0 -translate-y-1"
      enter-active-class="transition-all duration-200"
      leave-to-class="opacity-0 -translate-y-1"
      leave-active-class="transition-all duration-200"
    >
      <p v-if="error" role="alert" class="flex items-center gap-1.5 pl-0.5 text-[13px] text-danger-600">
        <CircleAlert :size="13" class="shrink-0" />
        {{ error }}
      </p>
    </Transition>

  </div>
</template>

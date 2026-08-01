<script setup>
import { LoaderCircle } from '@lucide/vue';

defineProps({
  type: { type: String, default: 'button' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  fullWidth: { type: Boolean, default: true },
  id: { type: String, default: undefined },
});

const variants = {
  primary: 'bg-white text-secondary-900 hover:bg-slate-100 focus:ring-white/30',
  accent: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-200',
  secondary: 'border border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50 focus:ring-slate-200',
  danger: 'bg-red-50 text-red-700 hover:bg-red-100 focus:ring-red-100',
  ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus:ring-slate-100',
  google: 'border border-white/10 bg-secondary-800 text-white hover:bg-secondary-900 focus:ring-primary-200',
};

const sizes = {
  sm: 'min-h-9 px-3 py-1.5 text-sm rounded-lg',
  md: 'min-h-10 px-4 py-2 text-sm rounded-xl',
  lg: 'min-h-12 px-6 py-2.5 text-base rounded-xl',
};
</script>

<template>
  <button
    :id="id"
    :type="type"
    :disabled="loading || disabled"
    class="inline-flex items-center justify-center gap-2 font-semibold shadow-sm outline-none transition-all duration-200 focus:ring-4 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-55"
    :class="[variants[variant], sizes[size], fullWidth ? 'w-full' : 'w-auto']"
  >
    <LoaderCircle v-if="loading" :size="18" class="animate-spin" aria-hidden="true" />
    <slot name="icon" />
    <span><slot /></span>
  </button>
</template>

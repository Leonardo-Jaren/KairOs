<script setup>
import { computed } from 'vue';
import { FileSpreadsheet, Loader2 } from '@lucide/vue';

const props = defineProps({
  label: {
    type: String,
    default: 'Exportar Excel',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: 'sm',
    validator: (v) => ['xs', 'sm', 'md', 'lg'].includes(v),
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'outline', 'subtle'].includes(v),
  },
  tooltip: {
    type: String,
    default: 'Descargar datos filtrados en formato Excel (.xlsx)',
  },
});

const emit = defineEmits(['click', 'export']);

const handleExport = (event) => {
  emit('click', event);
  emit('export', event);
};

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'h-7 px-2.5 text-xs gap-1.5 rounded-lg';
    case 'md':
      return 'h-10 px-4 text-sm gap-2 rounded-xl';
    case 'lg':
      return 'h-11 px-5 text-base gap-2.5 rounded-xl';
    case 'sm':
    default:
      return 'h-8.5 px-3 text-xs font-bold gap-1.5 rounded-lg';
  }
});

const iconSize = computed(() => {
  switch (props.size) {
    case 'xs':
      return 13;
    case 'md':
    case 'lg':
      return 17;
    case 'sm':
    default:
      return 15;
  }
});

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'outline':
      return 'border border-emerald-300 bg-white text-emerald-700 hover:bg-emerald-50 hover:border-emerald-400 focus-visible:ring-emerald-500 shadow-xs';
    case 'subtle':
      return 'bg-emerald-50/80 text-emerald-800 hover:bg-emerald-100 border border-emerald-200/60 focus-visible:ring-emerald-500';
    case 'default':
    default:
      return 'border border-slate-200 bg-white text-slate-700 hover:border-emerald-300 hover:text-emerald-700 hover:bg-emerald-50/40 focus-visible:ring-emerald-500 shadow-xs';
  }
});
</script>

<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :title="tooltip"
    class="inline-flex items-center justify-center font-bold transition-all duration-150 select-none cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 disabled:pointer-events-none disabled:opacity-50"
    :class="[sizeClasses, variantClasses]"
    @click="handleExport"
  >
    <Loader2 v-if="loading" :size="iconSize" class="animate-spin text-emerald-600" />
    <FileSpreadsheet v-else :size="iconSize" class="text-emerald-600" />
    <span>{{ loading ? 'Generando...' : label }}</span>
  </button>
</template>

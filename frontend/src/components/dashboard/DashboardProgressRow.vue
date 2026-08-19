<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  tone: { type: String, default: 'blue' },
});

const percentage = computed(() => (
  props.total > 0 ? Math.round((props.value / props.total) * 100) : 0
));

const tones = {
  blue: 'bg-primary-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  danger: 'bg-danger-500',
  slate: 'bg-slate-400',
};
</script>

<template>
  <div>
    <div class="mb-2 flex items-center justify-between gap-4 text-sm">
      <span class="font-medium text-slate-600">{{ label }}</span>
      <span class="font-bold tabular-nums text-slate-900">
        {{ value }} <span class="font-medium text-slate-400">· {{ percentage }}%</span>
      </span>
    </div>
    <div class="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        class="h-full rounded-full transition-[width] duration-700 ease-out"
        :class="tones[tone]"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

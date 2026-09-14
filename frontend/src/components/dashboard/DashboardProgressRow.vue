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
  blue: {
    bar: 'bg-primary-500',
    dot: 'bg-primary-500',
  },
  success: {
    bar: 'bg-emerald-500',
    dot: 'bg-emerald-500',
  },
  warning: {
    bar: 'bg-amber-500',
    dot: 'bg-amber-500',
  },
  danger: {
    bar: 'bg-red-500',
    dot: 'bg-red-500',
  },
  slate: {
    bar: 'bg-slate-400',
    dot: 'bg-slate-400',
  },
};
</script>

<template>
  <div class="space-y-2 select-none">
    <div class="flex items-center justify-between gap-4 text-xs sm:text-sm">
      <div class="flex items-center gap-2">
        <span class="size-2 rounded-full" :class="tones[tone]?.dot ?? tones.blue.dot" />
        <span class="font-medium text-slate-700">{{ label }}</span>
      </div>
      <span class="font-bold tabular-nums text-slate-900">
        {{ value }} <span class="font-normal text-slate-400">({{ percentage }}%)</span>
      </span>
    </div>

    <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div
        class="h-full rounded-full transition-[width] duration-700 ease-out"
        :class="tones[tone]?.bar ?? tones.blue.bar"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

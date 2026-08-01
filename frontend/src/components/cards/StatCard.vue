<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  helper: { type: String, default: '' },
  tone: { type: String, default: 'blue' },
});

const tones = {
  blue: 'bg-primary-50 text-primary-600',
  emerald: 'bg-success-50 text-success-600',
  violet: 'bg-violet-50 text-violet-600',
  amber: 'bg-warning-50 text-warning-600',
};
</script>

<template>
  <article class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
    <div class="mb-4 flex items-center justify-between">
      <div class="grid size-10 place-items-center rounded-xl" :class="tones[tone]">
        <slot name="icon" />
      </div>
      <span v-if="helper" class="text-xs font-medium text-slate-400">{{ helper }}</span>
    </div>
    <p class="text-2xl font-extrabold text-slate-900">{{ value }}</p>
    <p class="mt-1 text-sm font-medium text-slate-500">{{ label }}</p>
  </article>
</template>

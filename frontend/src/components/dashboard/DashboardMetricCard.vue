<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  description: { type: String, default: '' },
  helper: { type: String, default: '' },
  icon: { type: [Object, Function], required: true },
  tone: { type: String, default: 'blue' },
  loading: { type: Boolean, default: false },
});

const tones = {
  blue: {
    icon: 'bg-primary-50 text-primary-600 ring-primary-100',
    accent: 'bg-primary-500',
  },
  emerald: {
    icon: 'bg-success-50 text-success-600 ring-success-100',
    accent: 'bg-success-500',
  },
  amber: {
    icon: 'bg-warning-50 text-warning-600 ring-warning-100',
    accent: 'bg-warning-500',
  },
  violet: {
    icon: 'bg-violet-50 text-violet-600 ring-violet-100',
    accent: 'bg-violet-500',
  },
};
</script>

<template>
  <article class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md">
    <span class="absolute inset-x-0 top-0 h-0.5" :class="tones[tone].accent" />

    <template v-if="loading">
      <div class="mb-5 flex items-center justify-between">
        <div class="size-11 animate-pulse rounded-xl bg-slate-100" />
        <div class="h-4 w-16 animate-pulse rounded bg-slate-100" />
      </div>
      <div class="h-8 w-20 animate-pulse rounded bg-slate-100" />
      <div class="mt-3 h-4 w-36 animate-pulse rounded bg-slate-100" />
    </template>

    <template v-else>
      <div class="mb-5 flex items-start justify-between gap-3">
        <div class="grid size-11 place-items-center rounded-xl ring-1 ring-inset" :class="tones[tone].icon">
          <component :is="icon" :size="21" :stroke-width="1.9" />
        </div>
        <span v-if="helper" class="rounded-full bg-slate-50 px-2.5 py-1 text-[11px] font-bold text-slate-500">
          {{ helper }}
        </span>
      </div>
      <p class="text-3xl font-extrabold tracking-tight text-slate-950">{{ value }}</p>
      <p class="mt-1 text-sm font-bold text-slate-700">{{ label }}</p>
      <p class="mt-1.5 text-xs leading-5 text-slate-400">{{ description }}</p>
    </template>
  </article>
</template>

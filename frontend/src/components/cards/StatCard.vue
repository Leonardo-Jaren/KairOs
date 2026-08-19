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
  <article class="group flex min-w-0 items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md sm:block sm:rounded-2xl sm:p-5">
    <div class="grid size-9 shrink-0 place-items-center rounded-lg sm:mb-4 sm:size-10 sm:rounded-xl" :class="tones[tone]">
      <slot name="icon" />
    </div>
    <div class="min-w-0 flex-1">
      <div class="flex items-baseline justify-between gap-2">
        <p class="text-xl font-extrabold leading-none text-slate-900 sm:text-2xl">{{ value }}</p>
        <span v-if="helper" class="hidden text-xs font-medium text-slate-400 sm:block">{{ helper }}</span>
      </div>
      <p class="mt-1 text-xs font-medium leading-4 text-slate-500 sm:text-sm">{{ label }}</p>
      <p v-if="helper" class="mt-0.5 truncate text-[10px] font-medium text-slate-400 sm:hidden">{{ helper }}</p>
    </div>
  </article>
</template>

<script setup>
import { ArrowUpRight } from '@lucide/vue';

defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  description: { type: String, default: '' },
  helper: { type: String, default: '' },
  icon: { type: [Object, Function], required: true },
  tone: { type: String, default: 'blue' },
  loading: { type: Boolean, default: false },
  to: { type: String, default: '' },
});

const tones = {
  blue: {
    icon: 'bg-primary-50 text-primary-600 ring-primary-200/60 group-hover:bg-primary-500 group-hover:text-white',
    helper: 'bg-primary-50 text-primary-700 border-primary-200/80',
    arrow: 'group-hover:text-primary-600',
  },
  emerald: {
    icon: 'bg-emerald-50 text-emerald-600 ring-emerald-200/60 group-hover:bg-emerald-500 group-hover:text-white',
    helper: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
    arrow: 'group-hover:text-emerald-600',
  },
  amber: {
    icon: 'bg-amber-50 text-amber-600 ring-amber-200/60 group-hover:bg-amber-500 group-hover:text-white',
    helper: 'bg-amber-50 text-amber-700 border-amber-200/80',
    arrow: 'group-hover:text-amber-600',
  },
  violet: {
    icon: 'bg-violet-50 text-violet-600 ring-violet-200/60 group-hover:bg-violet-500 group-hover:text-white',
    helper: 'bg-violet-50 text-violet-700 border-violet-200/80',
    arrow: 'group-hover:text-violet-600',
  },
};
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'article'"
    :to="to || undefined"
    class="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md select-none"
  >
    <!-- Estado de carga esqueleto -->
    <template v-if="loading">
      <div class="mb-5 flex items-center justify-between">
        <div class="size-11 animate-pulse rounded-xl bg-slate-100" />
        <div class="h-5 w-16 animate-pulse rounded-full bg-slate-100" />
      </div>
      <div>
        <div class="h-8 w-20 animate-pulse rounded bg-slate-100" />
        <div class="mt-2 h-4 w-32 animate-pulse rounded bg-slate-100" />
        <div class="mt-2 h-3 w-40 animate-pulse rounded bg-slate-100" />
      </div>
    </template>

    <!-- Estado activo -->
    <template v-else>
      <div>
        <div class="mb-4 flex items-start justify-between gap-3">
          <div
            class="grid size-11 place-items-center rounded-xl ring-1 ring-inset transition-colors duration-200"
            :class="tones[tone]?.icon ?? tones.blue.icon"
          >
            <component :is="icon" :size="20" :stroke-width="2" />
          </div>

          <div class="flex items-center gap-1.5">
            <span
              v-if="helper"
              class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-bold tracking-tight"
              :class="tones[tone]?.helper ?? tones.blue.helper"
            >
              {{ helper }}
            </span>
            <span
              v-if="to"
              class="grid size-6 place-items-center text-slate-300 transition-colors duration-200"
              :class="tones[tone]?.arrow ?? tones.blue.arrow"
              aria-hidden="true"
            >
              <ArrowUpRight :size="15" />
            </span>
          </div>
        </div>

        <p class="text-3xl font-extrabold tracking-tight text-slate-900 tabular-nums">
          {{ value }}
        </p>
        <p class="mt-1 text-sm font-bold text-slate-700">
          {{ label }}
        </p>
      </div>

      <p class="mt-3 border-t border-slate-100 pt-2.5 text-xs text-slate-500 leading-normal">
        {{ description }}
      </p>
    </template>
  </component>
</template>

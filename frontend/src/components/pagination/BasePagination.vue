<script setup>
import { ChevronLeft, ChevronRight } from '@lucide/vue';

defineProps({
  page: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  total: { type: Number, default: 0 },
});

defineEmits(['change']);
</script>

<template>
  <div class="flex flex-col items-center justify-between gap-3 sm:flex-row">
    <p class="text-sm text-slate-500">
      {{ total }} {{ total === 1 ? 'registro' : 'registros' }}
    </p>
    <div class="flex items-center gap-2">
      <button
        type="button"
        class="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 hover:border-slate-300 hover:text-slate-900 disabled:pointer-events-none disabled:opacity-40"
        :disabled="page <= 1"
        aria-label="Página anterior"
        @click="$emit('change', page - 1)"
      >
        <ChevronLeft :size="18" />
      </button>
      <span class="min-w-24 text-center text-sm font-semibold text-slate-700">
        Página {{ page }} de {{ totalPages }}
      </span>
      <button
        type="button"
        class="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 hover:border-slate-300 hover:text-slate-900 disabled:pointer-events-none disabled:opacity-40"
        :disabled="page >= totalPages"
        aria-label="Página siguiente"
        @click="$emit('change', page + 1)"
      >
        <ChevronRight :size="18" />
      </button>
    </div>
  </div>
</template>

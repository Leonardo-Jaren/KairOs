<script setup>
import { Inbox } from '@lucide/vue';

defineProps({
  columns: { type: Array, required: true },
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyMessage: { type: String, default: 'No hay registros para mostrar.' },
  rowKey: { type: String, default: 'id' },
});
</script>

<template>
  <div
    class="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
    :aria-busy="loading"
  >
    <div
      v-if="loading && items.length > 0"
      class="absolute inset-x-0 top-0 z-10 h-0.5 overflow-hidden bg-primary-100"
      role="status"
      aria-live="polite"
    >
      <div class="h-full w-full animate-pulse bg-primary-500" />
      <span class="sr-only">Actualizando registros...</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full min-w-[760px] border-collapse text-left">
        <thead class="bg-slate-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="border-b border-slate-200 px-5 py-3.5 text-[11px] font-bold uppercase tracking-wider text-slate-500"
              :class="column.class"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <template v-if="loading && items.length === 0">
            <tr v-for="index in 5" :key="index">
              <td v-for="column in columns" :key="column.key" class="px-5 py-4">
                <div class="h-4 animate-pulse rounded bg-slate-100" />
              </td>
            </tr>
          </template>
          <tr
            v-for="item in items"
            v-else
            :key="item[rowKey]"
            class="transition-colors duration-150 hover:bg-blue-50/40"
          >
            <td v-for="column in columns" :key="column.key" class="px-5 py-4 text-sm text-slate-600" :class="column.class">
              <slot :name="`cell-${column.key}`" :item="item">
                {{ item[column.key] ?? '—' }}
              </slot>
            </td>
          </tr>
          <tr v-if="!loading && items.length === 0">
            <td :colspan="columns.length" class="px-6 py-16 text-center">
              <Inbox :size="34" class="mx-auto mb-3 text-slate-300" />
              <p class="text-sm font-medium text-slate-500">{{ emptyMessage }}</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

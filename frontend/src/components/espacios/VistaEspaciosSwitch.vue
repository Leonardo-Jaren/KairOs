<script setup>
import { Layers, Map, Table } from '@lucide/vue';

defineProps({
  active: { type: String, required: true },
});
const emit = defineEmits(['change']);
const views = [
  { id: 'mapa', label: 'Mapa', icon: Map },
  { id: 'jerarquia', label: 'Tradicional', icon: Layers },
  { id: 'inventario', label: 'Lista', icon: Table },
];
</script>

<template>
  <nav class="ml-auto inline-flex max-w-full rounded-xl bg-slate-200/70 p-1 text-xs" aria-label="Vista de espacios">
    <button
      v-for="view in views"
      :key="view.id"
      type="button"
      class="inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg px-2 font-bold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 sm:px-3"
      :class="active === view.id ? 'bg-white text-primary-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
      :aria-current="active === view.id ? 'page' : undefined"
      @click="emit('change', view.id)"
    >
      <component :is="view.icon" :size="14" aria-hidden="true" />
      {{ view.label }}
    </button>
  </nav>
</template>

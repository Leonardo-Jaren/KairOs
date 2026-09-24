<script setup>
import { ChevronRight } from '@lucide/vue';

defineProps({ items: { type: Array, default: () => [] } });
const emit = defineEmits(['navigate']);
</script>

<template>
  <nav v-if="items.length > 1" class="flex min-w-0 flex-wrap items-center gap-1 text-xs font-semibold text-slate-500" aria-label="Ubicación actual">
    <template v-for="(item, index) in items" :key="`${index}-${item.label}`">
      <ChevronRight v-if="index" :size="14" class="shrink-0 text-slate-300" aria-hidden="true" />
      <span v-if="index === items.length - 1" class="max-w-full break-words rounded-lg px-2 py-2 font-bold text-slate-900" aria-current="location">{{ item.label }}</span>
      <button v-else type="button" class="min-h-11 max-w-full break-words rounded-lg px-2 text-left transition-colors hover:bg-slate-100 hover:text-primary-700 focus-visible:outline-2 focus-visible:outline-primary-500" @click="emit('navigate', index)">{{ item.label }}</button>
    </template>
  </nav>
</template>

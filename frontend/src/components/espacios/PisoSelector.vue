<script setup>
import { Check, Layers3 } from '@lucide/vue';

defineProps({
  floors: { type: Array, default: () => [] },
  selectedKey: { type: [String, Number], default: '' },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(['select']);
</script>

<template>
  <section class="min-w-0" aria-labelledby="floor-selector-title">
    <div class="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
      <div class="min-w-0">
        <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-primary-600">Pisos del pabellón</p>
        <h2 id="floor-selector-title" class="mt-1 text-lg font-extrabold text-slate-950 sm:text-xl">
          Elige el nivel que quieres recorrer
        </h2>
      </div>
      <p class="shrink-0 text-xs font-medium text-slate-400">
        {{ floors.length }} {{ floors.length === 1 ? 'piso disponible' : 'pisos disponibles' }}
      </p>
    </div>

    <div
      v-if="floors.length"
      class="mt-4 grid min-w-0 gap-2 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
      role="list"
      aria-label="Pisos del pabellón"
    >
      <button
        v-for="floor in floors"
        :key="floor.key"
        type="button"
        class="group grid min-h-20 min-w-0 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 rounded-2xl border p-3 text-left outline-none transition duration-200 focus-visible:ring-4 focus-visible:ring-primary-100"
        :class="String(selectedKey) === String(floor.key)
          ? 'border-primary-400 bg-primary-50 shadow-sm'
          : 'border-slate-200 bg-white hover:border-primary-200 hover:shadow-sm'"
        :aria-pressed="String(selectedKey) === String(floor.key)"
        :disabled="disabled"
        @click="emit('select', floor.key)"
      >
        <span
          class="grid size-10 shrink-0 place-items-center rounded-xl transition-colors"
          :class="String(selectedKey) === String(floor.key)
            ? 'bg-primary-500 text-white'
            : 'bg-slate-100 text-slate-500 group-hover:bg-primary-50 group-hover:text-primary-600'"
        >
          <Check v-if="String(selectedKey) === String(floor.key)" :size="17" aria-hidden="true" />
          <Layers3 v-else :size="17" aria-hidden="true" />
        </span>

        <span class="min-w-0">
          <strong class="block truncate text-sm font-extrabold text-slate-900">{{ floor.label }}</strong>
          <span class="mt-1 block truncate text-[10px] font-medium text-slate-500">
            {{ floor.aulas }} {{ floor.aulas === 1 ? 'aula' : 'aulas' }} ·
            {{ floor.labs }} {{ floor.labs === 1 ? 'tecnológico' : 'tecnológicos' }}
          </span>
        </span>

        <span class="rounded-full bg-white px-2 py-1 text-[9px] font-bold uppercase tracking-wide text-slate-400 shadow-sm">
          {{ floor.allSpaces.length }} amb.
        </span>
      </button>
    </div>
  </section>
</template>

<script setup>
import { ArrowRight, MapPin } from '@lucide/vue';

defineProps({
  ciudades: { type: Array, default: () => [] },
});

const emit = defineEmits(['select']);
</script>

<template>
  <section class="flex flex-col gap-4" aria-label="Ciudades disponibles">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-primary-600">Explorar por ciudad</p>
        <h2 class="mt-1 text-lg font-extrabold text-slate-950">Selecciona una ciudad</h2>
        <p class="mt-1 text-sm text-slate-500">Después podrás elegir una sede y recorrer sus pabellones y ambientes.</p>
      </div>
      <span class="rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 ring-1 ring-slate-200">
        {{ ciudades.length }} {{ ciudades.length === 1 ? 'ciudad' : 'ciudades' }}
      </span>
    </div>

    <ul class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="ciudad in ciudades" :key="ciudad.label">
        <button
          type="button"
          class="group flex min-h-36 w-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-xs transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
          @click="emit('select', ciudad.label)"
        >
          <span class="flex w-full items-center justify-between">
            <span class="grid size-10 place-items-center rounded-xl bg-primary-50 text-primary-600 transition-colors group-hover:bg-primary-500 group-hover:text-white">
              <MapPin :size="19" aria-hidden="true" />
            </span>
            <ArrowRight :size="17" class="text-slate-300 transition group-hover:translate-x-1 group-hover:text-primary-600 motion-reduce:transform-none" aria-hidden="true" />
          </span>
          <span class="mt-4 block min-w-0">
            <strong class="block truncate text-base font-extrabold text-slate-950 group-hover:text-primary-700">{{ ciudad.label }}</strong>
            <span class="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs font-medium text-slate-500">
              <span>{{ ciudad.localCount }} {{ ciudad.localCount === 1 ? 'local' : 'locales' }}</span>
              <span>{{ ciudad.buildingCount }} {{ ciudad.buildingCount === 1 ? 'pabellón' : 'pabellones' }}</span>
            </span>
          </span>
        </button>
      </li>
      <li v-if="!ciudades.length" class="rounded-2xl border border-dashed border-slate-300 bg-white p-5 text-sm text-slate-500 sm:col-span-2 xl:col-span-3">
        No hay ciudades que coincidan con la búsqueda.
      </li>
    </ul>
  </section>
</template>

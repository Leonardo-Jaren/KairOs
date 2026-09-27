<script setup>
import { computed, ref, watch } from 'vue';
import { Building2, ChevronLeft, ChevronRight, Network } from '@lucide/vue';
import AxonometricMassing from '@/components/espacios/AxonometricMassing.vue';

const props = defineProps({
  city: { type: [String, Number], default: '' },
  localCards: { type: Array, default: () => [] },
  totalLocalCount: { type: Number, default: 0 },
  totalBuildingCount: { type: Number, default: 0 },
  search: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(['select-local']);
const page = ref(1);
const pageSize = 3;

const cityName = computed(() => (
  String(props.city) === '__legacy__' ? 'Registros anteriores' : String(props.city ?? '')
));
const totalPages = computed(() => Math.max(1, Math.ceil(props.localCards.length / pageSize)));
const visibleLocals = computed(() => props.localCards.slice(
  (page.value - 1) * pageSize,
  page.value * pageSize,
));
const rootDetail = computed(() => (
  `${props.totalLocalCount} ${props.totalLocalCount === 1 ? 'sede' : 'sedes'} · ${props.totalBuildingCount} ${props.totalBuildingCount === 1 ? 'pabellón' : 'pabellones'}`
));
const emptyMessage = computed(() => {
  if (props.search.trim() && props.totalLocalCount) return 'No hay sedes que coincidan con la búsqueda.';
  return 'Esta ciudad todavía no tiene sedes registradas.';
});
const emptyHint = computed(() => (
  !props.search.trim() && !props.totalLocalCount
    ? 'Registra una sede para organizar sus pabellones y pisos.'
    : ''
));
const connectorPath = computed(() => {
  const count = visibleLocals.value.length;
  if (count <= 1) return 'M 500 0 V 60';

  const points = visibleLocals.value.map((_, index) => (
    ((index + 0.5) * 1000) / count
  ));
  return [
    'M 500 0 V 25',
    `M ${points[0]} 25 H ${points.at(-1)}`,
    ...points.map((point) => `M ${point} 25 V 60`),
  ].join(' ');
});

watch(() => `${props.city}|${props.search}`, () => {
  page.value = 1;
});
watch(totalPages, (pages) => {
  page.value = Math.min(page.value, pages);
});
</script>

<template>
  <section class="site-diagram relative flex min-h-[380px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-slate-50/80 p-3 sm:min-h-[420px] sm:p-5" :aria-busy="loading || disabled">
    <div class="relative z-10 flex items-center justify-between gap-2">
      <span class="inline-flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.14em] text-slate-500 sm:text-[10px]">
        <Network :size="15" class="text-primary-600" aria-hidden="true" />
        Esquema axonométrico
      </span>
      <span class="rounded-full border border-slate-200 bg-white/90 px-2.5 py-1.5 font-mono text-[8px] font-semibold uppercase tracking-wide text-slate-500 sm:text-[9px]">
        Jerarquía · no representa distancias
      </span>
    </div>

    <div class="relative z-10 mx-auto mt-4 flex w-fit max-w-full items-center gap-3 rounded-xl border border-slate-700 bg-secondary-950 px-3 py-2.5 text-white shadow-md sm:mt-5 sm:px-4 sm:py-3">
      <span class="grid size-10 shrink-0 place-items-center rounded-lg bg-white/10 text-primary-300 sm:size-11">
        <Network :size="20" aria-hidden="true" />
      </span>
      <span class="min-w-0">
        <strong class="block truncate text-sm font-bold sm:text-base">{{ cityName }}</strong>
        <span class="mt-0.5 block truncate font-mono text-[9px] text-slate-300 sm:text-[10px]">{{ rootDetail }}</span>
      </span>
      <span class="ml-1 size-2 shrink-0 rounded-full bg-accent-400" aria-hidden="true" />
    </div>

    <div v-if="loading && !visibleLocals.length" class="grid flex-1 place-items-center" role="status" aria-live="polite">
      <span class="text-sm font-semibold text-slate-500">Cargando sedes...</span>
    </div>

    <div v-else-if="visibleLocals.length" class="site-branches relative z-10 mt-1 flex-1">
      <svg
        class="branch-lines absolute inset-x-0 top-0 mx-auto h-[60px] w-full overflow-visible"
        viewBox="0 0 1000 60"
        preserveAspectRatio="none"
        aria-hidden="true"
        focusable="false"
      >
        <path :d="connectorPath" class="fill-none stroke-slate-300" stroke-width="1.5" vector-effect="non-scaling-stroke" />
      </svg>

      <ul class="site-grid relative grid h-full items-start gap-x-2 sm:gap-x-5" :style="{ '--site-count': visibleLocals.length }" aria-label="Locales disponibles">
        <li v-for="local in visibleLocals" :key="local.id" class="min-w-0">
          <button
            type="button"
            class="site-node group flex min-h-11 w-full flex-col items-center rounded-2xl px-1 pb-2 pt-2 text-center transition-colors duration-200 hover:bg-white/80 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 disabled:cursor-not-allowed disabled:opacity-50 sm:px-3 sm:pb-3"
            :disabled="disabled || loading"
            :aria-label="`Abrir croquis de ${local.nombre}. ${local.buildingCount} ${local.buildingCount === 1 ? 'pabellón' : 'pabellones'}`"
            @click="emit('select-local', local.id)"
          >
            <AxonometricMassing :count="local.buildingCount" />
            <span class="mt-1 block max-w-full truncate text-xs font-extrabold text-slate-900 transition-colors group-hover:text-primary-700 sm:text-sm" :title="local.nombre">
              {{ local.nombre }}
            </span>
            <span class="mt-1 block max-w-full truncate font-mono text-[9px] font-semibold uppercase tracking-wide text-slate-400">
              {{ local.codigo }}
            </span>
            <span class="mt-1.5 block text-[10px] text-slate-600">
              {{ local.buildingCount }} {{ local.buildingCount === 1 ? 'pabellón' : 'pabellones' }}
            </span>
            <span class="mt-2 inline-flex min-h-10 items-center gap-1 rounded-lg px-2 text-[10px] font-bold text-primary-700 transition-colors group-hover:bg-primary-50">
              Abrir croquis
              <span aria-hidden="true">→</span>
            </span>
          </button>
        </li>
      </ul>
    </div>

    <div v-else class="grid flex-1 place-items-center px-4 py-8 text-center" role="status">
      <div>
        <Building2 :size="30" class="mx-auto text-slate-300" aria-hidden="true" />
        <p class="mt-3 text-sm font-semibold text-slate-600">{{ emptyMessage }}</p>
        <p v-if="emptyHint" class="mt-1 text-xs text-slate-500">{{ emptyHint }}</p>
      </div>
    </div>

    <footer class="relative z-10 mt-2 flex flex-col gap-3 border-t border-slate-200 pt-3 sm:flex-row sm:items-center sm:justify-between">
      <span class="text-[9px] font-medium text-slate-500">Las formas representan grupos de pabellones, no su ubicación física.</span>
      <nav v-if="totalPages > 1" class="flex items-center justify-between gap-2 text-xs font-semibold text-slate-600" aria-label="Páginas de sedes">
        <button type="button" class="grid min-h-11 min-w-11 place-items-center rounded-lg transition-colors hover:bg-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 disabled:opacity-40" aria-label="Página anterior" :disabled="page <= 1 || disabled" @click="page -= 1">
          <ChevronLeft :size="17" aria-hidden="true" />
        </button>
        <span aria-live="polite">{{ page }} / {{ totalPages }}</span>
        <button type="button" class="grid min-h-11 min-w-11 place-items-center rounded-lg transition-colors hover:bg-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 disabled:opacity-40" aria-label="Página siguiente" :disabled="page >= totalPages || disabled" @click="page += 1">
          <ChevronRight :size="17" aria-hidden="true" />
        </button>
      </nav>
    </footer>
  </section>
</template>

<style scoped>
.site-diagram::before {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgb(148 163 184 / 28%) 0.7px, transparent 0.7px);
  background-size: 18px 18px;
  content: '';
  pointer-events: none;
}

.site-branches {
  min-height: 250px;
  padding-top: 54px;
}

.site-grid {
  grid-template-columns: repeat(var(--site-count), minmax(0, 1fr));
}

.site-node {
  -webkit-tap-highlight-color: transparent;
}

@media (max-width: 639px) {
  .site-branches {
    padding-top: 0;
  }

  .branch-lines {
    display: none;
  }

  .site-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.5rem;
  }

  .site-node {
    display: grid;
    grid-template-columns: minmax(6rem, 0.8fr) minmax(0, 1.2fr);
    grid-template-rows: auto auto auto;
    align-items: center;
    column-gap: 0.75rem;
    text-align: left;
  }

  .site-node :deep(.massing-art) {
    grid-row: 1 / 4;
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-node,
  .site-node * {
    transition-duration: 0.01ms !important;
  }
}
</style>

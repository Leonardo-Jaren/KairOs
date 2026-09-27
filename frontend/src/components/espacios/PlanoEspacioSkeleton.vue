<script setup>
import { computed } from 'vue';
import {
  AlertTriangle,
  Building2,
  Check,
  CircleDot,
  GraduationCap,
  Monitor,
  MonitorCog,
  Wrench,
} from '@lucide/vue';

const props = defineProps({
  columns: { type: Number, default: 6 },
  rows: { type: Number, default: 3 },
});

// Genera las celdas del plano simulado respetando pasillo central y puestos
const placeholderCells = computed(() => {
  const cells = [];
  const aisleCol = props.columns > 3 ? Math.ceil(props.columns / 2) : -1;
  for (let r = 1; r <= props.rows; r += 1) {
    for (let c = 1; c <= props.columns; c += 1) {
      cells.push({
        row: r,
        col: c,
        isAisle: c === aisleCol,
      });
    }
  }
  return cells;
});

const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${props.columns}, minmax(116px, 1fr))`,
  minWidth: `${props.columns * 132}px`,
}));
</script>

<template>
  <div
    class="flex flex-col gap-6"
    aria-busy="true"
    aria-label="Cargando plano interactivo del salón"
    role="status"
  >
    <!-- Encabezado con datos del espacio y métricas -->
    <header
      class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end xl:grid-cols-[minmax(340px,1.15fr)_minmax(500px,1fr)_auto]"
    >
      <div class="min-w-0 lg:col-start-1 lg:row-start-1">
        <div class="flex flex-wrap items-center gap-2">
          <span class="h-6 w-28 rounded-full bg-primary-100/70 animate-pulse" />
          <span class="h-6 w-32 rounded-full bg-slate-200/80 animate-pulse" />
        </div>
        <div class="mt-3 h-9 w-24 rounded-xl bg-slate-200 animate-pulse" />
        <div class="mt-3 max-w-2xl space-y-1.5">
          <div class="h-3.5 w-full rounded-md bg-slate-200/70 animate-pulse" />
          <div class="h-3.5 w-4/5 rounded-md bg-slate-200/55 animate-pulse" />
        </div>
      </div>

      <div class="hidden shrink-0 gap-2 sm:flex sm:justify-end lg:col-start-2 lg:row-start-1 xl:col-start-3">
        <div class="h-9 w-28 rounded-xl bg-slate-200/70 animate-pulse" />
        <div class="h-9 w-36 rounded-xl bg-slate-200/60 animate-pulse" />
      </div>

      <section
        class="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:col-span-2 lg:row-start-2 xl:col-span-1 xl:col-start-2 xl:row-start-1"
      >
        <!-- Equipos ubicados -->
        <article class="flex min-w-0 items-center gap-2 rounded-xl border border-slate-200/80 bg-white px-2.5 py-2 shadow-xs">
          <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-primary-50 text-primary-400">
            <MonitorCog :size="16" class="animate-pulse" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="h-4 w-6 rounded bg-slate-200 animate-pulse" />
            <div class="mt-1 h-2.5 w-16 rounded bg-slate-100 animate-pulse" />
          </div>
        </article>

        <!-- Operativos -->
        <article class="flex min-w-0 items-center gap-2 rounded-xl border border-success-200/70 bg-success-50/30 px-2.5 py-2 shadow-xs">
          <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-success-100/70 text-success-500">
            <Check :size="16" class="animate-pulse" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="h-4 w-6 rounded bg-success-200/80 animate-pulse" />
            <div class="mt-1 h-2.5 w-14 rounded bg-success-100/80 animate-pulse" />
          </div>
        </article>

        <!-- En mantenimiento -->
        <article class="flex min-w-0 items-center gap-2 rounded-xl border border-warning-200/70 bg-warning-50/30 px-2.5 py-2 shadow-xs">
          <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-warning-100/70 text-warning-500">
            <Wrench :size="16" class="animate-pulse" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="h-4 w-6 rounded bg-warning-200/80 animate-pulse" />
            <div class="mt-1 h-2.5 w-18 rounded bg-warning-100/80 animate-pulse" />
          </div>
        </article>

        <!-- Con falla -->
        <article class="flex min-w-0 items-center gap-2 rounded-xl border border-danger-200/70 bg-danger-50/30 px-2.5 py-2 shadow-xs">
          <span class="grid size-8 shrink-0 place-items-center rounded-lg bg-danger-100/70 text-danger-500">
            <AlertTriangle :size="16" class="animate-pulse" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="h-4 w-6 rounded bg-danger-200/80 animate-pulse" />
            <div class="mt-1 h-2.5 w-12 rounded bg-danger-100/80 animate-pulse" />
          </div>
        </article>
      </section>
    </header>

    <!-- Contenedor del plano interactivo -->
    <section class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <header
        class="flex flex-col justify-between gap-4 border-b border-slate-100 bg-slate-50/70 px-5 py-4 sm:flex-row sm:items-center"
      >
        <div class="flex items-center gap-3">
          <span class="grid size-10 place-items-center rounded-xl bg-secondary-950 text-slate-400">
            <Building2 :size="20" class="animate-pulse" />
          </span>
          <div>
            <div class="h-3.5 w-36 rounded bg-slate-200/90 animate-pulse" />
            <div class="mt-1.5 h-2.5 w-48 rounded bg-slate-200/60 animate-pulse" />
          </div>
        </div>

        <!-- Leyenda de estados -->
        <div class="flex flex-wrap items-center gap-3 text-[10px] font-bold uppercase tracking-wide text-slate-400">
          <span class="inline-flex items-center gap-1.5">
            <CircleDot :size="13" class="text-success-500/70 animate-pulse" />
            <span class="h-2 w-14 rounded bg-slate-200/80 animate-pulse" />
          </span>
          <span class="inline-flex items-center gap-1.5">
            <CircleDot :size="13" class="text-warning-500/70 animate-pulse" />
            <span class="h-2 w-18 rounded bg-slate-200/80 animate-pulse" />
          </span>
          <span class="inline-flex items-center gap-1.5">
            <CircleDot :size="13" class="text-danger-500/70 animate-pulse" />
            <span class="h-2 w-10 rounded bg-slate-200/80 animate-pulse" />
          </span>
        </div>
      </header>

      <div
        class="overflow-x-auto bg-[linear-gradient(#f8fafc_1px,transparent_1px),linear-gradient(90deg,#f8fafc_1px,transparent_1px)] bg-[size:24px_24px] p-4 sm:p-6"
      >
        <!-- Frente del aula / Pizarra docente -->
        <div
          class="mx-auto mb-5 flex min-w-160 max-w-4xl items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 bg-white/90 px-5 py-3 text-center shadow-xs"
          aria-label="Frente del aula"
        >
          <span class="sr-only">Frente del aula</span>
          <GraduationCap :size="18" class="text-primary-400 animate-pulse" />
          <div>
            <div class="h-3 w-28 rounded bg-slate-200/80 animate-pulse mx-auto" />
            <div class="mt-1.5 h-2 w-44 rounded bg-slate-100/90 animate-pulse mx-auto" />
          </div>
        </div>

        <!-- Matriz de puestos del salón -->
        <div class="grid gap-3" :style="gridStyle">
          <div
            v-for="cell in placeholderCells"
            :key="`${cell.row}-${cell.col}`"
            class="min-h-27 rounded-2xl p-1.5 text-left"
            :class="cell.isAisle ? 'border-x border-dashed border-slate-200 bg-slate-50/45' : 'bg-transparent'"
          >
            <!-- Pasillo central -->
            <div
              v-if="cell.isAisle"
              class="grid min-h-23 w-full place-items-center text-[9px] font-extrabold uppercase tracking-[0.2em] text-slate-300 select-none"
            >
              <span v-if="cell.row === Math.ceil(rows / 2)" class="-rotate-90">Pasillo</span>
              <span v-else class="h-8 w-px border-l border-dashed border-slate-200" />
            </div>

            <!-- Puesto de trabajo / Terminal de cómputo -->
            <div
              v-else
              class="relative flex min-h-25 w-full flex-col items-center justify-center rounded-xl border border-slate-200/80 bg-white p-2 text-center shadow-xs"
            >
              <!-- Distintivo docente en primera posición -->
              <span
                v-if="cell.row === 1 && cell.col === 1"
                class="absolute -top-2 left-1/2 -translate-x-1/2 rounded-full bg-primary-100 px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wide text-primary-600 animate-pulse"
              >
                Docente
              </span>

              <span class="grid size-9 place-items-center rounded-lg bg-slate-100/80 animate-pulse">
                <Monitor :size="20" class="text-slate-300" :stroke-width="1.8" />
              </span>
              <span class="mt-1.5 h-2.5 w-12 rounded bg-slate-200/80 animate-pulse" />
              <span class="mt-1.5 inline-flex items-center gap-1 animate-pulse">
                <span class="size-1.5 rounded-full bg-slate-300" />
                <span class="h-2 w-10 rounded bg-slate-100" />
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

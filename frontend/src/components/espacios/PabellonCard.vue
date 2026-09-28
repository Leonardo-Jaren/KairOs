<script setup>
import { computed } from 'vue';
import { Building2, ChevronRight, Layers3, MapPin, MonitorCog, Pencil, Trash2 } from '@lucide/vue';
import PabellonAxonometrico from '@/components/espacios/PabellonAxonometrico.vue';

const props = defineProps({
  building: { type: Object, required: true },
  index: { type: Number, default: 0 },
  selected: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(['select', 'edit', 'delete']);

const floorCount = computed(() => (
  Array.isArray(props.building.pisos) ? props.building.pisos.length : 0
));

const roomCount = computed(() => (
  Array.isArray(props.building.spaces) ? props.building.spaces.length : 0
));

const telemetry = computed(() => {
  const equipos = Number(props.building.equipos) || 0;
  const alertas = Number(props.building.alertas) || 0;
  const operativos = Math.max(0, equipos - alertas);

  return {
    equipos,
    alertas,
    porcentaje: equipos > 0 ? Math.round((operativos / equipos) * 100) : 100,
  };
});

const buildingLetter = computed(() => {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return letters[props.index % letters.length] || String(props.index + 1);
});
</script>

<template>
  <article
    class="group flex min-w-0 flex-col justify-between overflow-hidden rounded-2xl border bg-white p-4 shadow-xs transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md sm:p-5"
    :class="selected ? 'border-primary-500 ring-2 ring-primary-400/40 bg-primary-50/20' : 'border-slate-200/90'"
  >
    <div>
      <div class="flex items-start justify-between gap-3">
        <div class="flex min-w-0 items-center gap-3">
          <span
            class="grid size-11 shrink-0 place-items-center rounded-2xl shadow-xs transition-colors duration-200 group-hover:bg-primary-500 group-hover:text-white"
            :class="selected ? 'bg-primary-600 text-white' : 'bg-primary-50 text-primary-600'"
          >
            <Building2 :size="21" aria-hidden="true" />
          </span>
          <div class="min-w-0">
            <div class="flex min-w-0 items-center gap-1.5">
              <h4 class="truncate text-base font-extrabold text-slate-950 transition-colors group-hover:text-primary-600" :title="building.nombre">
                {{ building.nombre }}
              </h4>
              <span class="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-bold uppercase text-slate-500">
                Bloque {{ buildingLetter }}
              </span>
            </div>
            <p class="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
              {{ building.codigo }}
            </p>
          </div>
        </div>

        <div v-if="canEdit" class="flex shrink-0 items-center gap-1">
          <button
            type="button"
            class="grid size-11 place-items-center rounded-xl text-slate-400 transition hover:bg-slate-100 hover:text-primary-600 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="disabled"
            aria-label="Editar pabellón"
            @click.stop="emit('edit', building)"
          >
            <Pencil :size="16" aria-hidden="true" />
          </button>
          <button
            type="button"
            class="grid size-11 place-items-center rounded-xl text-slate-400 transition hover:bg-danger-50 hover:text-danger-600 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="disabled"
            aria-label="Desactivar pabellón"
            @click.stop="emit('delete', building)"
          >
            <Trash2 :size="16" aria-hidden="true" />
          </button>
        </div>
      </div>

      <p class="mt-3 line-clamp-2 min-h-10 text-xs leading-5 text-slate-500">
        {{ building.descripcion || 'Bloque físico con distribución de pisos, laboratorios y áreas de cómputo.' }}
      </p>

      <div class="mt-3 overflow-hidden rounded-xl border border-slate-100 bg-slate-50/50">
        <PabellonAxonometrico
          :name="building.nombre"
          :floors="floorCount"
          :selected="selected"
        />
      </div>

      <div class="mt-3 flex flex-wrap items-center gap-2">
        <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1.5 text-xs font-bold text-slate-700">
          <Layers3 :size="13" class="text-primary-500" aria-hidden="true" />
          {{ floorCount }} {{ floorCount === 1 ? 'piso' : 'pisos' }}
        </span>
        <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1.5 text-xs font-bold text-slate-700">
          <MapPin :size="13" class="text-emerald-500" aria-hidden="true" />
          {{ roomCount }} amb.
        </span>
        <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1.5 text-xs font-bold text-slate-700">
          <MonitorCog :size="13" class="text-amber-500" aria-hidden="true" />
          {{ telemetry.equipos }} {{ telemetry.equipos === 1 ? 'equipo' : 'equipos' }}
        </span>
      </div>

      <div v-if="telemetry.equipos > 0" class="mt-3 flex flex-col gap-1">
        <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500">
          <span>Operatividad hardware</span>
          <span class="font-bold text-slate-700">{{ telemetry.porcentaje }}%</span>
        </div>
        <div class="flex h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div class="bg-emerald-500 transition-all duration-300" :style="{ width: `${telemetry.porcentaje}%` }" />
          <div
            v-if="telemetry.alertas > 0"
            class="bg-amber-400 transition-all duration-300"
            :style="{ width: `${100 - telemetry.porcentaje}%` }"
          />
        </div>
      </div>
    </div>

    <div class="mt-4 border-t border-slate-100 pt-3">
      <button
        type="button"
        class="flex min-h-11 w-full items-center justify-between rounded-xl bg-slate-100 px-4 py-2 text-xs font-bold text-slate-800 transition hover:bg-primary-600 hover:text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="disabled"
        :aria-pressed="selected"
        @click="emit('select', building.id)"
      >
        <span>Recorrer pabellón</span>
        <ChevronRight :size="16" class="transition-transform group-hover:translate-x-1 motion-reduce:transform-none" aria-hidden="true" />
      </button>
    </div>
  </article>
</template>

<script setup>
import {
  Laptop,
  Monitor,
  Printer,
  Projector,
  Server,
} from '@lucide/vue';

const props = defineProps({
  equipment: { type: Object, required: true },
  editing: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
  teacher: { type: Boolean, default: false },
});

defineEmits(['select', 'dragstart']);

const icons = {
  desktop: Monitor,
  monitor: Monitor,
  laptop: Laptop,
  servidor: Server,
  impresora: Printer,
  proyector: Projector,
};

const statusClasses = {
  en_uso: 'border-success-200 bg-white text-success-700 shadow-success-100/70',
  en_mantenimiento: 'border-warning-300 bg-warning-50/40 text-warning-700 shadow-warning-100/70',
  dañado: 'border-danger-300 bg-danger-50/50 text-danger-700 shadow-danger-100/70',
  de_baja: 'border-slate-300 bg-slate-100 text-slate-500 shadow-slate-100',
};

const statusDots = {
  en_uso: 'bg-success-500',
  en_mantenimiento: 'bg-warning-500',
  dañado: 'bg-danger-500',
  de_baja: 'bg-slate-400',
};

const equipmentIcon = icons[props.equipment.tipo_equipo] ?? Monitor;
</script>

<template>
  <button
    type="button"
    :draggable="editing"
    class="group relative flex min-h-25 w-full flex-col items-center justify-center rounded-xl border p-2 text-center shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-primary-100"
    :class="[
      statusClasses[equipment.estado],
      selected ? 'ring-2 ring-primary-500 ring-offset-2' : '',
      editing ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer',
    ]"
    :aria-label="`${equipment.codigo}, ${equipment.estado_display}`"
    @click="$emit('select')"
    @dragstart="$emit('dragstart', $event)"
  >
    <span v-if="teacher" class="absolute -top-2 left-1/2 -translate-x-1/2 rounded-full bg-primary-600 px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wide text-white shadow-sm">
      Docente
    </span>
    <span class="grid size-9 place-items-center rounded-lg bg-current/10">
      <component :is="equipmentIcon" :size="21" :stroke-width="1.8" />
    </span>
    <span class="mt-1.5 max-w-full truncate font-mono text-[11px] font-extrabold text-slate-800">
      {{ equipment.codigo }}
    </span>
    <span class="mt-1 inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wide">
      <span class="size-1.5 rounded-full" :class="statusDots[equipment.estado]" />
      {{ equipment.estado_display }}
    </span>
  </button>
</template>

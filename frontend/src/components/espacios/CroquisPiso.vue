<script setup>
import {
  ArrowRight, DoorOpen, FlaskConical, Grid3X3, Minus, MonitorCog,
  Move, Pencil, Plus, Presentation, Route, Save, Trash2, X,
} from '@lucide/vue';
import { computed } from 'vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

const props = defineProps({
  floor: { type: Object, required: true },
  editing: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  selectedSpaceId: { type: [Number, String], default: null },
  tool: { type: String, default: 'move' },
});

const emit = defineEmits([
  'start-edit', 'save', 'cancel', 'select-space', 'cell-click', 'set-tool',
  'resize', 'update-columns', 'add-row', 'remove-row', 'create-space',
  'edit-space', 'delete-space',
]);

const columnOptions = [8, 10, 12, 14, 16].map((value) => ({
  value,
  label: `${value} columnas`,
}));

const roomIcon = (type) => ({
  laboratorio: FlaskConical,
  sala_computo: MonitorCog,
  aula: Presentation,
  oficina: DoorOpen,
}[type] ?? Grid3X3);

const spaceMap = computed(() => new Map(
  props.floor.allSpaces.map((space) => [Number(space.id), space]),
));
const visibleIds = computed(() => new Set(props.floor.spaces.map((space) => Number(space.id))));
const rooms = computed(() => props.floor.layout.ambientes
  .map((room) => ({ ...room, space: spaceMap.value.get(Number(room.espacio_id)) }))
  .filter((room) => room.space));
const selectedRoom = computed(() => rooms.value.find((room) => (
  Number(room.espacio_id) === Number(props.selectedSpaceId)
)));
const corridorKeys = computed(() => new Set(
  props.floor.layout.pasillos.map((cell) => `${cell.fila}-${cell.columna}`),
));
const cells = computed(() => {
  const result = [];
  for (let row = 1; row <= props.floor.layout.filas; row += 1) {
    for (let column = 1; column <= props.floor.layout.columnas; column += 1) {
      result.push({ row, column, key: `${row}-${column}` });
    }
  }
  return result;
});
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${props.floor.layout.columnas}, minmax(54px, 1fr))`,
  gridTemplateRows: `repeat(${props.floor.layout.filas}, 68px)`,
  minWidth: `${Math.max(680, props.floor.layout.columnas * 72)}px`,
}));
const roomStyle = (room) => ({
  gridColumn: `${room.columna} / span ${room.ancho}`,
  gridRow: `${room.fila} / span ${room.alto}`,
});
const cellStyle = (cell) => ({
  gridColumn: cell.column,
  gridRow: cell.row,
});
const isCorridorLabel = (cell) => (
  corridorKeys.value.has(cell.key)
  && cell.column === Math.ceil(props.floor.layout.columnas / 2)
);
const roomTone = (space) => {
  if (space.tipo === 'aula') return 'border-violet-200 bg-violet-50 text-violet-800';
  if (space.tipo === 'oficina') return 'border-sky-200 bg-sky-50 text-sky-800';
  if (['laboratorio', 'sala_computo'].includes(space.tipo)) {
    return 'border-primary-200 bg-primary-50 text-primary-800';
  }
  return 'border-slate-200 bg-white text-slate-800';
};
</script>

<template>
  <section class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
    <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/85 px-3 py-3 sm:px-4">
      <div class="flex items-center gap-3">
        <span class="grid size-10 place-items-center rounded-xl bg-secondary-950 text-xs font-black text-primary-300">{{ floor.key }}</span>
        <div>
          <h3 class="text-sm font-extrabold text-slate-900">{{ floor.label }}</h3>
          <p class="text-[10px] text-slate-400">{{ floor.allSpaces.length }} ambiente{{ floor.allSpaces.length === 1 ? '' : 's' }} · {{ floor.labs }} tecnológicos · {{ floor.aulas }} aulas</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <BaseButton v-if="canEdit && !editing" size="sm" variant="secondary" :full-width="false" @click="emit('start-edit')">
          <template #icon><Pencil :size="15" /></template>Diseñar piso
        </BaseButton>
        <BaseButton v-if="canEdit && !editing" size="sm" variant="accent" :full-width="false" @click="emit('create-space')">
          <template #icon><Plus :size="15" /></template>Ambiente
        </BaseButton>
      </div>
    </header>

    <div v-if="editing" class="sticky top-20 z-30 border-b border-primary-200 bg-primary-50/95 p-3 backdrop-blur-xl sm:p-4">
      <div class="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div class="flex min-w-0 flex-1 flex-wrap items-end gap-2">
          <div class="rounded-xl border border-primary-200 bg-white p-1">
            <button type="button" class="inline-flex min-h-9 items-center gap-2 rounded-lg px-3 text-xs font-bold" :class="tool === 'move' ? 'bg-primary-500 text-white' : 'text-slate-500 hover:bg-slate-50'" @click="emit('set-tool', 'move')"><Move :size="15" />Mover ambiente</button>
            <button type="button" class="inline-flex min-h-9 items-center gap-2 rounded-lg px-3 text-xs font-bold" :class="tool === 'corridor' ? 'bg-secondary-950 text-white' : 'text-slate-500 hover:bg-slate-50'" @click="emit('set-tool', 'corridor')"><Route :size="15" />Dibujar pasillo</button>
          </div>
          <div class="w-42"><BaseSelect :id="`floor-columns-${floor.key}`" :model-value="floor.layout.columnas" label="Ancho del piso" :options="columnOptions" @update:model-value="emit('update-columns', $event)" /></div>
          <div>
            <p class="mb-1.5 text-xs font-semibold text-slate-600">Filas: {{ floor.layout.filas }}</p>
            <div class="flex overflow-hidden rounded-xl border border-slate-200 bg-white">
              <button type="button" class="p-3 text-slate-500 hover:bg-slate-50 hover:text-primary-600" aria-label="Quitar fila" @click="emit('remove-row')"><Minus :size="16" /></button>
              <button type="button" class="border-l border-slate-200 p-3 text-slate-500 hover:bg-slate-50 hover:text-primary-600" aria-label="Agregar fila" @click="emit('add-row')"><Plus :size="16" /></button>
            </div>
          </div>
          <div v-if="selectedRoom" class="flex items-end gap-2 rounded-xl border border-primary-200 bg-white px-3 py-2">
            <div class="min-w-26"><p class="text-[9px] font-bold uppercase tracking-wide text-slate-400">Seleccionado</p><p class="truncate text-xs font-extrabold text-slate-800">{{ selectedRoom.space.codigo_espacio }}</p></div>
            <div class="flex items-center gap-1 text-xs text-slate-500"><span>Ancho</span><button type="button" class="rounded-md p-1 hover:bg-slate-100" @click="emit('resize', 'ancho', -1)"><Minus :size="14" /></button><strong>{{ selectedRoom.ancho }}</strong><button type="button" class="rounded-md p-1 hover:bg-slate-100" @click="emit('resize', 'ancho', 1)"><Plus :size="14" /></button></div>
            <div class="flex items-center gap-1 text-xs text-slate-500"><span>Fondo</span><button type="button" class="rounded-md p-1 hover:bg-slate-100" @click="emit('resize', 'alto', -1)"><Minus :size="14" /></button><strong>{{ selectedRoom.alto }}</strong><button type="button" class="rounded-md p-1 hover:bg-slate-100" @click="emit('resize', 'alto', 1)"><Plus :size="14" /></button></div>
          </div>
        </div>
        <div class="flex gap-2">
          <BaseButton size="sm" variant="ghost" :full-width="false" @click="emit('cancel')"><template #icon><X :size="16" /></template>Cancelar</BaseButton>
          <BaseButton size="sm" variant="accent" :loading="saving" :full-width="false" @click="emit('save')"><template #icon><Save :size="16" /></template>Guardar croquis</BaseButton>
        </div>
      </div>
      <p class="mt-2 text-[11px] text-primary-700">Selecciona un ambiente y toca una celda libre para moverlo. Cambia a “Dibujar pasillo” para marcar o borrar recorridos.</p>
    </div>

    <div class="border-b border-slate-100 px-3 py-2 sm:px-4">
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] font-bold uppercase tracking-wide text-slate-400">
        <span class="inline-flex items-center gap-1.5"><span class="size-2.5 rounded-sm bg-primary-200" />Laboratorio</span>
        <span class="inline-flex items-center gap-1.5"><span class="size-2.5 rounded-sm bg-violet-200" />Aula</span>
        <span class="inline-flex items-center gap-1.5"><span class="size-2.5 rounded-sm bg-slate-200" />Pasillo</span>
        <span class="ml-auto sm:hidden">Desliza para recorrer</span>
      </div>
    </div>

    <div class="scrollbar-hidden overflow-x-auto bg-slate-50/60 p-3 sm:p-4">
      <div class="relative grid gap-1 rounded-2xl border border-slate-200 bg-white p-2 shadow-inner" :style="gridStyle">
        <button
          v-for="cell in cells"
          :key="cell.key"
          type="button"
          :aria-label="corridorKeys.has(cell.key) ? 'Pasillo' : `Celda ${cell.row}, ${cell.column}`"
          class="relative z-0 min-h-0 rounded-md border transition-colors"
          :class="[
            corridorKeys.has(cell.key) ? 'border-slate-200 bg-slate-100' : 'border-dashed border-slate-100 bg-white',
            editing ? 'hover:border-primary-300 hover:bg-primary-50' : 'pointer-events-none',
          ]"
          :style="cellStyle(cell)"
          @click="emit('cell-click', cell)"
        >
          <span v-if="isCorridorLabel(cell)" class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-[8px] font-extrabold uppercase tracking-[0.18em] text-slate-400">Pasillo</span>
        </button>

        <article
          v-for="room in rooms"
          :key="room.espacio_id"
          class="group relative z-10 min-h-0 overflow-hidden rounded-xl border-2 shadow-sm transition-all"
          :class="[
            roomTone(room.space),
            editing ? 'cursor-pointer hover:-translate-y-0.5 hover:shadow-md' : 'hover:-translate-y-0.5 hover:shadow-md',
            Number(selectedSpaceId) === Number(room.espacio_id) ? 'ring-4 ring-primary-200' : '',
            visibleIds.has(Number(room.espacio_id)) ? '' : 'opacity-25',
          ]"
          :style="roomStyle(room)"
        >
          <button v-if="editing" type="button" class="flex size-full min-h-0 flex-col justify-between p-2 text-left" @click="emit('select-space', room.espacio_id)">
            <span class="flex items-start justify-between gap-2"><span class="grid size-8 shrink-0 place-items-center rounded-lg bg-white/75"><component :is="roomIcon(room.space.tipo)" :size="17" /></span><span class="rounded-full bg-white/75 px-2 py-0.5 text-[9px] font-bold">{{ room.space.cantidad_equipos }} PC</span></span>
            <span class="min-w-0"><strong class="block truncate font-mono text-xs">{{ room.space.codigo_espacio }}</strong><span v-if="room.ancho > 1" class="block truncate text-[10px] opacity-70">{{ room.space.tipo_display }}</span></span>
          </button>
          <template v-else>
            <RouterLink :to="`/espacios/${room.space.id}`" class="flex size-full min-h-0 flex-col justify-between p-2 pr-9">
              <span class="flex items-start justify-between gap-2"><span class="grid size-8 shrink-0 place-items-center rounded-lg bg-white/75"><component :is="roomIcon(room.space.tipo)" :size="17" /></span><span class="rounded-full bg-white/75 px-2 py-0.5 text-[9px] font-bold">{{ room.space.cantidad_equipos }} PC</span></span>
              <span class="min-w-0"><strong class="block truncate font-mono text-xs">{{ room.space.codigo_espacio }}</strong><span v-if="room.ancho > 1" class="block truncate text-[10px] opacity-70">{{ room.space.tipo_display }}</span><span v-if="room.alto > 1" class="mt-1 inline-flex items-center gap-1 text-[9px] font-bold">Abrir plano <ArrowRight :size="11" /></span></span>
            </RouterLink>
            <div v-if="canEdit" class="absolute right-1.5 top-1.5 flex flex-col gap-1 rounded-lg bg-white/90 p-0.5 opacity-0 shadow-sm transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
              <button type="button" class="rounded-md p-1 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar ambiente" @click="emit('edit-space', room.space)"><Pencil :size="12" /></button>
              <button type="button" class="rounded-md p-1 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Desactivar ambiente" @click="emit('delete-space', room.space)"><Trash2 :size="12" /></button>
            </div>
          </template>
        </article>
      </div>
    </div>
  </section>
</template>

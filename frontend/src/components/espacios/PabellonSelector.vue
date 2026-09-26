<script setup>
import { computed, ref } from 'vue';
import {
  Building2,
  ChevronRight,
  FolderOpen,
  Layers3,
  MapPin,
  MonitorCog,
  Pencil,
  Plus,
  Search,
  Trash2,
} from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';

const props = defineProps({
  buildings: { type: Array, default: () => [] },
  local: { type: Object, default: () => null },
  spaces: { type: Array, default: () => [] },
  selectedId: { type: [String, Number], default: '' },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(['select', 'edit', 'delete', 'create-building', 'select-space']);

const searchQuery = ref('');

const allSpaces = computed(() => {
  if (props.spaces && props.spaces.length > 0) return props.spaces;
  const list = [];
  props.buildings.forEach((b) => {
    if (Array.isArray(b.spaces)) {
      list.push(...b.spaces);
    }
  });
  return list;
});

const buildingMap = computed(() => {
  const map = new Map();
  props.buildings.forEach((b) => {
    map.set(Number(b.id), b.nombre);
  });
  return map;
});

const filteredSpaces = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return allSpaces.value;
  return allSpaces.value.filter((s) => (
    String(s.codigo_espacio || '').toLowerCase().includes(query)
    || String(s.tipo || '').toLowerCase().includes(query)
    || String(s.tipo_display || '').toLowerCase().includes(query)
    || String(s.piso || '').toLowerCase().includes(query)
  ));
});

const totalAmbientes = computed(() => (
  props.buildings.reduce((sum, b) => sum + (b.spaces?.length || 0), 0)
));

const totalPisos = computed(() => {
  const floorSet = new Set();
  props.buildings.forEach((b) => {
    (b.pisos || []).forEach((p) => floorSet.add(String(p)));
  });
  return floorSet.size || props.buildings.reduce((sum, b) => sum + (b.pisos?.length || 0), 0);
});

const totalEquipos = computed(() => (
  props.buildings.reduce((sum, b) => sum + (Number(b.equipos) || 0), 0)
));

function getBuildingLetter(index) {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return letters[index % letters.length] || String(index + 1);
}
</script>

<template>
  <div class="flex flex-col gap-6" :aria-busy="disabled">
    <!-- Banner de identidad del Campus / Local -->
    <section class="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-sm">
      <div class="relative overflow-hidden bg-secondary-950 px-5 py-6 text-white sm:px-8 sm:py-7">
        <div class="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full border-[28px] border-primary-500/15" />
        <div class="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-primary-500/25 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary-300 backdrop-blur">
                {{ local?.tipoLabel || 'Sede' }}
              </span>
              <span v-if="local?.codigo" class="rounded-full bg-white/10 px-2.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider text-white/80">
                {{ local.codigo }}
              </span>
              <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300">
                <span class="size-1.5 rounded-full bg-emerald-400" />
                Operativo
              </span>
            </div>

            <h2 class="mt-2 text-2xl font-extrabold tracking-tight sm:text-3xl">
              {{ local?.nombre || 'Sede seleccionada' }}
            </h2>
            <p class="mt-1 max-w-3xl text-sm leading-6 text-white/70">
              {{ local?.descripcion || 'Campus universitario con infraestructura tecnológica distribuida en pabellones y pisos.' }}
            </p>
          </div>
        </div>

        <!-- Fila de métricas territoriales del campus (Bento KPIs) -->
        <div class="mt-6 grid grid-cols-2 gap-3 border-t border-white/10 pt-5 sm:grid-cols-4 sm:gap-4">
          <div class="rounded-xl border border-white/10 bg-white/5 p-3.5 backdrop-blur">
            <div class="flex items-center gap-2 text-white/60">
              <Building2 :size="15" class="text-primary-400" aria-hidden="true" />
              <span class="text-[11px] font-semibold uppercase tracking-wider">Pabellones</span>
            </div>
            <p class="mt-1 text-xl font-extrabold text-white">
              {{ buildings.length }}
              <span class="text-xs font-normal text-white/60">{{ buildings.length === 1 ? 'bloque' : 'bloques' }}</span>
            </p>
          </div>

          <div class="rounded-xl border border-white/10 bg-white/5 p-3.5 backdrop-blur">
            <div class="flex items-center gap-2 text-white/60">
              <Layers3 :size="15" class="text-primary-400" aria-hidden="true" />
              <span class="text-[11px] font-semibold uppercase tracking-wider">Niveles físicos</span>
            </div>
            <p class="mt-1 text-xl font-extrabold text-white">
              {{ totalPisos }}
              <span class="text-xs font-normal text-white/60">{{ totalPisos === 1 ? 'piso' : 'pisos' }}</span>
            </p>
          </div>

          <div class="rounded-xl border border-white/10 bg-white/5 p-3.5 backdrop-blur">
            <div class="flex items-center gap-2 text-white/60">
              <MapPin :size="15" class="text-primary-400" aria-hidden="true" />
              <span class="text-[11px] font-semibold uppercase tracking-wider">Ambientes TI</span>
            </div>
            <p class="mt-1 text-xl font-extrabold text-white">
              {{ totalAmbientes }}
              <span class="text-xs font-normal text-white/60">{{ totalAmbientes === 1 ? 'espacio' : 'espacios' }}</span>
            </p>
          </div>

          <div class="rounded-xl border border-white/10 bg-white/5 p-3.5 backdrop-blur">
            <div class="flex items-center gap-2 text-white/60">
              <MonitorCog :size="15" class="text-primary-400" aria-hidden="true" />
              <span class="text-[11px] font-semibold uppercase tracking-wider">Equipamiento</span>
            </div>
            <p class="mt-1 text-xl font-extrabold text-white">
              {{ totalEquipos }}
              <span class="text-xs font-normal text-white/60">{{ totalEquipos === 1 ? 'equipo' : 'equipos' }}</span>
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Contenido principal: Pabellones (Columna izquierda) + Inteligencia de Campus (Columna derecha) -->
    <div class="grid gap-6 lg:grid-cols-12 lg:items-start">
      <!-- Columna izquierda: Cuadrícula de pabellones arquitectónicos -->
      <section class="lg:col-span-8 flex flex-col gap-4">
        <div class="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-primary-600">
              Pabellones del local
            </p>
            <h3 class="text-lg font-extrabold text-slate-950 sm:text-xl">
              Elige el bloque que quieres recorrer
            </h3>
          </div>
          <p class="text-xs font-semibold text-slate-400">
            {{ buildings.length }}
            {{ buildings.length === 1 ? 'pabellón disponible' : 'pabellones disponibles' }}
          </p>
        </div>

        <!-- Tarjetas arquitectónicas de pabellones cuando hay edificios -->
        <div v-if="buildings.length" class="grid gap-4 sm:grid-cols-2">
          <div
            v-for="(building, index) in buildings"
            :key="building.id"
            class="group relative flex flex-col justify-between overflow-hidden rounded-2xl border bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md"
            :class="String(selectedId) === String(building.id) ? 'border-primary-500 ring-2 ring-primary-400/40 bg-primary-50/20' : 'border-slate-200'"
          >
            <div>
              <!-- Encabezado de la tarjeta con avatar de bloque y botones de acción -->
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3">
                  <span
                    class="grid size-12 place-items-center rounded-xl font-extrabold text-base shadow-sm transition-transform duration-200 group-hover:scale-105"
                    :class="String(selectedId) === String(building.id)
                      ? 'bg-primary-600 text-white shadow-primary-500/30'
                      : 'bg-secondary-950 text-primary-300 shadow-slate-900/10'"
                  >
                    {{ getBuildingLetter(index) }}
                  </span>
                  <div>
                    <h4 class="text-base font-extrabold text-slate-950 group-hover:text-primary-600 transition-colors line-clamp-1" :title="building.nombre">
                      {{ building.nombre }}
                    </h4>
                    <p class="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                      {{ building.codigo }}
                    </p>
                  </div>
                </div>

                <!-- Botones de administración (Editar / Desactivar) -->
                <div v-if="canEdit" class="flex items-center gap-1">
                  <button
                    type="button"
                    class="grid size-8 place-items-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-primary-600 disabled:opacity-40"
                    :disabled="disabled"
                    aria-label="Editar pabellón"
                    @click.stop="emit('edit', building)"
                  >
                    <Pencil :size="15" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    class="grid size-8 place-items-center rounded-lg text-slate-400 transition hover:bg-danger-50 hover:text-danger-600 disabled:opacity-40"
                    :disabled="disabled"
                    aria-label="Desactivar pabellón"
                    @click.stop="emit('delete', building)"
                  >
                    <Trash2 :size="15" aria-hidden="true" />
                  </button>
                </div>
              </div>

              <!-- Descripción del pabellón -->
              <p class="mt-3 line-clamp-2 min-h-[2.5rem] text-xs leading-5 text-slate-500">
                {{ building.descripcion || 'Bloque físico con distribución de pisos, laboratorios y áreas de cómputo.' }}
              </p>

              <!-- Resumen estructural del pabellón -->
              <div class="mt-4 flex flex-col gap-2 rounded-xl border border-slate-100 bg-slate-50/70 p-3">
                <div class="flex items-center justify-between text-xs">
                  <span class="flex items-center gap-1.5 font-bold text-slate-800">
                    <Layers3 :size="14" class="text-primary-500" aria-hidden="true" />
                    {{ building.pisos.length }} {{ building.pisos.length === 1 ? 'piso' : 'pisos' }}
                  </span>
                  <span class="text-[11px] font-medium text-slate-400">
                    {{ building.pisos?.length ? building.pisos.map((p) => `Nivel ${p}`).join(' · ') : 'Sin pisos' }}
                  </span>
                </div>

                <div class="flex items-center justify-between border-t border-slate-200/60 pt-2 text-xs">
                  <span class="flex items-center gap-1.5 font-medium text-slate-600">
                    <MapPin :size="14" class="text-primary-500" aria-hidden="true" />
                    {{ building.spaces.length }} {{ building.spaces.length === 1 ? 'ambiente' : 'ambientes' }}
                  </span>
                  <span class="flex items-center gap-1.5 font-bold text-slate-800">
                    <MonitorCog :size="14" class="text-primary-500" aria-hidden="true" />
                    {{ building.equipos }} {{ Number(building.equipos) === 1 ? 'equipo' : 'equipos' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Parte inferior: Botón de entrada al pabellón -->
            <div class="mt-4 border-t border-slate-100 pt-3">
              <button
                type="button"
                class="flex w-full min-h-11 items-center justify-between rounded-xl bg-slate-100 px-4 py-2 text-xs font-bold text-slate-800 transition group-hover:bg-primary-600 group-hover:text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:opacity-50"
                :disabled="disabled"
                :aria-pressed="String(selectedId) === String(building.id)"
                @click="emit('select', building.id)"
              >
                <span>Recorrer pabellón</span>
                <ChevronRight :size="16" class="transition-transform group-hover:translate-x-1 motion-reduce:transform-none" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <!-- Estado vacío cuando el local no tiene pabellones -->
        <div
          v-else
          class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center sm:p-12 shadow-sm"
        >
          <div class="grid size-14 place-items-center rounded-2xl bg-slate-100 text-slate-400 shadow-sm">
            <Building2 :size="28" aria-hidden="true" />
          </div>
          <h4 class="mt-4 text-base font-extrabold text-slate-900">
            Este local aún no tiene pabellones registrados
          </h4>
          <p class="mt-1 max-w-md text-xs leading-5 text-slate-500">
            Organiza la infraestructura de esta sede registrando sus bloques o pabellones para luego ubicar los pisos y ambientes tecnológicos.
          </p>
          <BaseButton
            v-if="canEdit"
            class="mt-5"
            variant="accent"
            size="sm"
            :full-width="false"
            :disabled="disabled"
            @click="emit('create-building')"
          >
            <template #icon><Plus :size="15" aria-hidden="true" /></template>
            Registrar primer pabellón
          </BaseButton>
        </div>
      </section>

      <!-- Columna derecha: Inteligencia del Campus y Directorio de Ambientes -->
      <aside class="lg:col-span-4 flex flex-col gap-4">
        <!-- Directorio rápido de ambientes del campus -->
        <div class="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="grid size-7 place-items-center rounded-lg bg-primary-50 text-primary-600">
                <FolderOpen :size="15" aria-hidden="true" />
              </span>
              <h4 class="text-sm font-extrabold text-slate-900">Directorio de ambientes</h4>
            </div>
            <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">
              {{ allSpaces.length }}
            </span>
          </div>
          <p class="mt-1 text-[11px] text-slate-500">
            Acceso rápido a todos los espacios de esta sede.
          </p>

          <!-- Campo de búsqueda rápida de ambientes -->
          <div class="mt-3">
            <div class="relative">
              <Search :size="14" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" aria-hidden="true" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por código o tipo..."
                class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-8 pr-3 text-xs text-slate-800 placeholder-slate-400 transition focus:border-primary-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-100"
              />
            </div>
          </div>

          <!-- Lista con scroll de ambientes -->
          <ul
            v-if="filteredSpaces.length"
            class="mt-3 flex max-h-64 flex-col gap-1.5 overflow-y-auto pr-1 text-xs"
            aria-label="Directorio de ambientes en el local"
          >
            <li v-for="space in filteredSpaces" :key="space.id">
              <button
                type="button"
                class="group flex w-full items-center justify-between rounded-xl border border-slate-100 bg-slate-50/70 p-2.5 text-left transition hover:border-primary-200 hover:bg-white hover:shadow-xs disabled:opacity-50"
                :disabled="disabled"
                @click="emit('select-space', space)"
              >
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-1.5">
                    <strong class="font-mono text-xs font-extrabold text-slate-900 group-hover:text-primary-600">
                      {{ space.codigo_espacio }}
                    </strong>
                    <span class="rounded bg-slate-200/80 px-1.5 py-0.2 text-[9px] font-bold uppercase text-slate-600">
                      {{ space.tipo_display || space.tipo }}
                    </span>
                  </div>
                  <p class="mt-0.5 truncate text-[11px] text-slate-400">
                    {{ buildingMap.get(Number(space.edificio_id || space.edificio?.id)) || 'Pabellón' }} · Piso {{ space.piso }}
                  </p>
                </div>
                <span class="shrink-0 text-[11px] font-bold text-slate-500 group-hover:text-primary-600">
                  {{ space.cantidad_equipos || 0 }} eq.
                  <ChevronRight :size="14" class="inline text-slate-300 group-hover:text-primary-600" aria-hidden="true" />
                </span>
              </button>
            </li>
          </ul>

          <p v-else class="mt-4 text-center text-xs text-slate-400 py-3">
            No se encontraron ambientes coincidentes.
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import {
  ArrowLeft,
  Building2,
  ChevronRight,
  DoorOpen,
  FolderOpen,
  Layers3,
  MapPin,
  Monitor,
  MonitorCog,
  Pencil,
  Plus,
  Presentation,
  Search,
  ShieldCheck,
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
  canReturn: { type: Boolean, default: false },
  returnLabel: { type: String, default: 'Volver a ciudades' },
});

const emit = defineEmits(['select', 'edit', 'delete', 'create-building', 'select-space', 'back']);

const searchQuery = ref('');
const selectedTypeFilter = ref('todos');

const typeFilters = [
  { value: 'todos', label: 'Todos' },
  { value: 'laboratorio', label: 'Laboratorios' },
  { value: 'aula', label: 'Aulas' },
  { value: 'oficina', label: 'Oficinas' },
];

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
  return allSpaces.value.filter((s) => {
    const matchesQuery = !query || (
      String(s.codigo_espacio || '').toLowerCase().includes(query)
      || String(s.tipo || '').toLowerCase().includes(query)
      || String(s.tipo_display || '').toLowerCase().includes(query)
      || String(s.piso || '').toLowerCase().includes(query)
      || String(buildingMap.value.get(Number(s.edificio_id ?? s.edificio?.id)) || '').toLowerCase().includes(query)
    );
    const matchesType = selectedTypeFilter.value === 'todos' || (
      selectedTypeFilter.value === 'laboratorio'
        ? ['laboratorio', 'sala_computo'].includes(s.tipo)
        : s.tipo === selectedTypeFilter.value
    );
    return matchesQuery && matchesType;
  });
});

const totalAmbientes = computed(() => (
  props.buildings.reduce((sum, b) => sum + (b.spaces?.length || 0), 0)
));

const totalEquipos = computed(() => (
  props.buildings.reduce((sum, b) => sum + (Number(b.equipos) || 0), 0)
));

const totalLaboratorios = computed(() => (
  props.buildings.reduce((sum, b) => sum + (b.laboratorios?.length || 0), 0)
));

const totalAlertas = computed(() => (
  props.buildings.reduce((sum, b) => sum + (Number(b.alertas) || 0), 0)
));

const totalOperativos = computed(() => (
  Math.max(0, totalEquipos.value - totalAlertas.value)
));

const tasaOperatividad = computed(() => (
  totalEquipos.value > 0 ? Math.round((totalOperativos.value / totalEquipos.value) * 100) : 100
));

function getBuildingTelemetry(b) {
  const equipos = Number(b.equipos) || 0;
  const alertas = Number(b.alertas) || 0;
  const operativos = Math.max(0, equipos - alertas);
  const pct = equipos > 0 ? Math.round((operativos / equipos) * 100) : 100;
  return { equipos, alertas, operativos, pct };
}

function getSpaceIcon(tipo) {
  switch (tipo) {
    case 'laboratorio':
    case 'sala_computo':
      return Monitor;
    case 'aula':
      return Presentation;
    case 'oficina':
      return DoorOpen;
    default:
      return MapPin;
  }
}

function getBuildingLetter(index) {
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return letters[index % letters.length] || String(index + 1);
}
</script>

<template>
  <div class="flex flex-col gap-6" :aria-busy="disabled">
    <!-- Banner de identidad del Campus / Local con KPIs en pildoras y boton de retorno condicional -->
    <section class="overflow-hidden rounded-3xl border border-slate-800 bg-secondary-950 p-6 text-white shadow-xl sm:p-8">
      <div class="relative flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
        <div class="flex flex-col gap-3 min-w-0">
          <!-- Badges superiores de contexto -->
          <div class="flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-3 py-0.5 text-[11px] font-bold text-emerald-300">
              <span class="size-2 rounded-full bg-emerald-400 animate-pulse" />
              Operativo
            </span>
            <span v-if="local?.tipoLabel || local?.tipo" class="rounded-full bg-primary-500/25 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary-300 backdrop-blur">
              {{ local?.tipoLabel || 'Sede' }}
            </span>
            <span v-if="local?.codigo" class="rounded-full bg-white/10 px-2.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider text-white/80">
              {{ local.codigo }}
            </span>
          </div>

          <!-- Titulo y descripcion del campus -->
          <div>
            <h2 class="text-2xl font-extrabold tracking-tight sm:text-3xl text-white">
              {{ local?.nombre || 'Sede seleccionada' }}
            </h2>
            <p class="mt-1 max-w-2xl text-xs sm:text-sm leading-6 text-white/70">
              {{ local?.descripcion || 'Campus universitario con infraestructura tecnológica distribuida en pabellones y pisos.' }}
            </p>
          </div>

          <!-- Pildoras de KPIs compactas alineadas horizontalmente (estilo uniforme con PisoSelector) -->
          <div class="flex flex-wrap items-center gap-2.5 pt-2">
            <span class="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <Building2 :size="15" class="text-primary-300" />
              {{ buildings.length }} {{ buildings.length === 1 ? 'Pabellón' : 'Pabellones' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <MapPin :size="15" class="text-emerald-300" />
              {{ totalAmbientes }} {{ totalAmbientes === 1 ? 'Ambiente' : 'Ambientes' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <Monitor :size="15" class="text-cyan-300" />
              {{ totalLaboratorios }} {{ totalLaboratorios === 1 ? 'Laboratorio TI' : 'Laboratorios TI' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <MonitorCog :size="15" class="text-amber-300" />
              {{ totalEquipos }} {{ totalEquipos === 1 ? 'Equipo' : 'Equipos' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <ShieldCheck :size="15" class="text-emerald-400" />
              Salud Operativa: {{ tasaOperatividad }}%
            </span>
          </div>
        </div>

        <!-- Boton de retorno segun permisos de ambito territorial -->
        <div v-if="canReturn" class="flex shrink-0 items-center gap-2">
          <BaseButton
            variant="secondary"
            size="sm"
            :full-width="false"
            :disabled="disabled"
            @click="emit('back')"
          >
            <template #icon><ArrowLeft :size="15" /></template>
            {{ returnLabel }}
          </BaseButton>
        </div>
      </div>
    </section>

    <!-- Contenido principal: Pabellones y Directorio rapido -->
    <div class="grid gap-6 lg:grid-cols-12 lg:items-start">
      <!-- Columna izquierda: Pabellones arquitectonicos -->
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

        <!-- Tarjetas de pabellones -->
        <div v-if="buildings.length" class="grid gap-4 sm:grid-cols-2">
          <article
            v-for="(building, index) in buildings"
            :key="building.id"
            class="group relative flex flex-col justify-between overflow-hidden rounded-2xl border bg-white p-5 shadow-xs transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md"
            :class="String(selectedId) === String(building.id) ? 'border-primary-500 ring-2 ring-primary-400/40 bg-primary-50/20' : 'border-slate-200/90'"
          >
            <div>
              <!-- Encabezado con icono arquitectonico y acciones -->
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3">
                  <span
                    class="grid size-12 place-items-center rounded-2xl font-extrabold text-base shadow-xs transition-colors duration-200 group-hover:bg-primary-500 group-hover:text-white"
                    :class="String(selectedId) === String(building.id)
                      ? 'bg-primary-600 text-white shadow-primary-500/30'
                      : 'bg-primary-50 text-primary-600'"
                  >
                    <Building2 :size="22" aria-hidden="true" />
                  </span>
                  <div>
                    <div class="flex items-center gap-1.5">
                      <h4 class="text-base font-extrabold text-slate-950 group-hover:text-primary-600 transition-colors line-clamp-1" :title="building.nombre">
                        {{ building.nombre }}
                      </h4>
                      <span class="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-bold text-slate-500 uppercase">
                        Bloque {{ getBuildingLetter(index) }}
                      </span>
                    </div>
                    <p class="font-mono text-xs font-bold uppercase tracking-wider text-slate-400">
                      {{ building.codigo }}
                    </p>
                  </div>
                </div>

                <!-- Botones de edicion / eliminacion -->
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

              <!-- Descripcion del pabellon -->
              <p class="mt-3 line-clamp-2 min-h-[2.5rem] text-xs leading-5 text-slate-500">
                {{ building.descripcion || 'Bloque físico con distribución de pisos, laboratorios y áreas de cómputo.' }}
              </p>

              <!-- Resumen de infraestructura en chips -->
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-700">
                  <Layers3 :size="13" class="text-primary-500" />
                  {{ building.pisos?.length || 0 }} {{ (building.pisos?.length === 1) ? 'piso' : 'pisos' }}
                </span>
                <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-700">
                  <MapPin :size="13" class="text-emerald-500" />
                  {{ building.spaces?.length || 0 }} amb.
                </span>
                <span class="inline-flex items-center gap-1 rounded-xl bg-slate-100 px-2.5 py-1 text-xs font-bold text-slate-700">
                  <MonitorCog :size="13" class="text-amber-500" />
                  {{ building.equipos }} {{ Number(building.equipos) === 1 ? 'equipo' : 'equipos' }}
                </span>
              </div>

              <!-- Barra de telemetria por pabellon -->
              <div v-if="getBuildingTelemetry(building).equipos > 0" class="mt-3 flex flex-col gap-1">
                <div class="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                  <span>Operatividad hardware</span>
                  <span class="text-slate-700 font-bold">{{ getBuildingTelemetry(building).pct }}%</span>
                </div>
                <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100 flex">
                  <div
                    class="bg-emerald-500 transition-all duration-300"
                    :style="{ width: `${getBuildingTelemetry(building).pct}%` }"
                  />
                  <div
                    v-if="getBuildingTelemetry(building).alertas > 0"
                    class="bg-amber-400 transition-all duration-300"
                    :style="{ width: `${100 - getBuildingTelemetry(building).pct}%` }"
                  />
                </div>
              </div>
            </div>

            <!-- Boton de acceso al pabellon -->
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
          </article>
        </div>

        <!-- Estado vacio si el local no tiene pabellones -->
        <div
          v-else
          class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center sm:p-12 shadow-xs"
        >
          <div class="grid size-14 place-items-center rounded-2xl bg-primary-50 text-primary-500 shadow-xs">
            <Building2 :size="28" aria-hidden="true" />
          </div>
          <h4 class="mt-4 text-base font-extrabold text-slate-950">
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

      <!-- Columna derecha: Directorio interactivo de ambientes -->
      <aside class="lg:col-span-4 flex flex-col gap-4">
        <div class="rounded-2xl border border-slate-200/90 bg-white p-4 sm:p-5 shadow-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="grid size-8 place-items-center rounded-xl bg-primary-50 text-primary-600">
                <FolderOpen :size="16" aria-hidden="true" />
              </span>
              <div>
                <h4 class="text-sm font-extrabold text-slate-900">Directorio de ambientes</h4>
                <p class="text-[11px] text-slate-500">Acceso rápido a los espacios de la sede</p>
              </div>
            </div>
            <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">
              {{ allSpaces.length }}
            </span>
          </div>

          <!-- Filtros de tipo de ambiente -->
          <div class="mt-3 flex flex-wrap gap-1">
            <button
              v-for="filter in typeFilters"
              :key="filter.value"
              type="button"
              class="rounded-lg px-2.5 py-1 text-[11px] font-bold transition-colors"
              :class="selectedTypeFilter === filter.value
                ? 'bg-primary-500 text-white shadow-2xs'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
              @click="selectedTypeFilter = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Buscador rapido -->
          <div class="mt-3">
            <div class="relative">
              <Search :size="14" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" aria-hidden="true" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por código, tipo o piso..."
                class="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-8 pr-3 text-xs text-slate-800 placeholder-slate-400 transition focus:border-primary-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-100"
              />
            </div>
          </div>

          <!-- Listado de ambientes -->
          <ul
            v-if="filteredSpaces.length"
            class="mt-3 flex max-h-72 flex-col gap-1.5 overflow-y-auto pr-1 text-xs"
            aria-label="Directorio de ambientes en el local"
          >
            <li v-for="space in filteredSpaces" :key="space.id">
              <button
                type="button"
                class="group flex w-full items-center justify-between rounded-xl border border-slate-100 bg-slate-50/70 p-2.5 text-left transition hover:border-primary-200 hover:bg-white hover:shadow-2xs disabled:opacity-50"
                :disabled="disabled"
                @click="emit('select-space', space)"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <span class="grid size-7 shrink-0 place-items-center rounded-lg bg-white text-slate-600 shadow-2xs border border-slate-100">
                    <component :is="getSpaceIcon(space.tipo)" :size="14" />
                  </span>
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5">
                      <strong class="font-extrabold text-slate-900 group-hover:text-primary-600 transition-colors truncate">
                        {{ space.codigo_espacio }}
                      </strong>
                      <span class="rounded bg-slate-200/80 px-1 py-0.2 text-[9px] font-bold uppercase text-slate-600">
                        {{ space.tipo_display || space.tipo }}
                      </span>
                    </div>
                    <p class="text-[10px] text-slate-500 truncate">
                      {{ buildingMap.get(Number(space.edificio_id ?? space.edificio?.id)) || 'Pabellón' }} · Piso {{ space.piso }}
                    </p>
                  </div>
                </div>

                <div class="flex items-center gap-1 shrink-0 ml-2">
                  <span
                    class="rounded-full px-2 py-0.5 text-[10px] font-bold"
                    :class="Number(space.cantidad_equipos) > 0 ? 'bg-primary-50 text-primary-700' : 'bg-slate-100 text-slate-400'"
                  >
                    {{ space.cantidad_equipos || 0 }} eq.
                  </span>
                  <ChevronRight :size="13" class="text-slate-400 group-hover:text-primary-600 transition-transform group-hover:translate-x-0.5" />
                </div>
              </button>
            </li>
          </ul>

          <div v-else class="mt-4 rounded-xl border border-slate-100 bg-slate-50/60 p-4 text-center">
            <p class="text-xs font-semibold text-slate-500">No se encontraron ambientes coincidentes.</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

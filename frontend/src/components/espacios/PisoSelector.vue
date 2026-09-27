<script setup>
import { computed } from 'vue';
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  DoorOpen,
  Layers3,
  Monitor,
  Plus,
  Presentation,
  UserCheck,
} from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';

const props = defineProps({
  edificio: { type: Object, default: () => null },
  localName: { type: String, default: '' },
  floors: { type: Array, default: () => [] },
  selectedKey: { type: [String, Number], default: '' },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  sortDesc: { type: Boolean, default: true },
});

const emit = defineEmits([
  'select',
  'back',
  'create-space',
  'assign-technician',
]);

// Ordena los pisos de manera descendente para reflejar la altura física del edificio
const sortedFloors = computed(() => {
  const list = [...props.floors];
  if (!props.sortDesc) return list;
  return list.sort((a, b) => {
    const numA = Number(a.key ?? a.piso);
    const numB = Number(b.key ?? b.piso);
    if (!Number.isNaN(numA) && !Number.isNaN(numB)) {
      return numB - numA;
    }
    return String(b.label || b.key).localeCompare(String(a.label || a.key), 'es', { numeric: true });
  });
});

// Calcula la telemetria y estado del hardware por nivel
function getFloorTelemetry(floor) {
  if (floor.telemetria) return floor.telemetria;
  const spaces = floor.allSpaces || floor.spaces || [];
  const totalEquipos = spaces.reduce((sum, s) => sum + (Number(s.cantidad_equipos) || 0), 0);
  const enMantenimiento = spaces.reduce((sum, s) => sum + (Number(s.resumen_equipos?.en_mantenimiento) || 0), 0);
  const incidencias = spaces.reduce((sum, s) => sum + (Number(s.resumen_equipos?.dañado) || 0), 0);
  const operativos = Math.max(0, totalEquipos - enMantenimiento - incidencias);
  const pctOperativos = totalEquipos > 0 ? Math.round((operativos / totalEquipos) * 100) : 100;
  const pctMantenimiento = totalEquipos > 0 ? Math.round((enMantenimiento / totalEquipos) * 100) : 0;
  const pctIncidencias = totalEquipos > 0 ? Math.round((incidencias / totalEquipos) * 100) : 0;
  return {
    totalEquipos,
    operativos,
    enMantenimiento,
    incidencias,
    pctOperativos,
    pctMantenimiento,
    pctIncidencias,
  };
}

// Devuelve el icono de Lucide correspondiente segun el tipo de ambiente
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
      return Building2;
  }
}

// Metricas consolidadas del pabellon
const totalAmbientes = computed(() => {
  if (props.edificio?.spaces?.length) return props.edificio.spaces.length;
  return props.floors.reduce((sum, f) => sum + (f.allSpaces?.length || 0), 0);
});

const totalEquipos = computed(() => {
  if (props.edificio?.equipos != null) return Number(props.edificio.equipos);
  return props.floors.reduce((sum, f) => {
    const t = getFloorTelemetry(f);
    return sum + t.totalEquipos;
  }, 0);
});

const totalPisos = computed(() => {
  if (props.edificio?.pisos?.length) return props.edificio.pisos.length;
  return props.floors.length;
});
</script>

<template>
  <div class="flex flex-col gap-6" aria-labelledby="floor-selector-title">
    <!-- Banner Hero del Pabellon estilo corporativo dark navy -->
    <section
      v-if="edificio"
      class="overflow-hidden rounded-3xl border border-slate-800 bg-secondary-950 p-6 text-white shadow-xl sm:p-8"
      aria-label="Información del pabellón"
    >
      <div class="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
        <div class="flex flex-col gap-3 min-w-0">
          <div class="flex flex-wrap items-center gap-2.5">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-bold text-emerald-300">
              <span class="size-2 rounded-full bg-emerald-400 animate-pulse" />
              Operativo
            </span>
            <span v-if="localName" class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-white/80">
              {{ localName }}
            </span>
            <span v-if="edificio.codigo" class="rounded-full bg-primary-500/20 px-3 py-1 font-mono text-xs font-bold text-primary-300">
              {{ edificio.codigo }}
            </span>
          </div>

          <div>
            <h1 class="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              {{ edificio.nombre }}
            </h1>
            <p v-if="edificio.descripcion" class="mt-1 text-xs text-slate-300 max-w-xl">
              {{ edificio.descripcion }}
            </p>
          </div>

          <!-- Pildoras de metricas consolidadas -->
          <div class="flex flex-wrap items-center gap-3 pt-1">
            <span class="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <Layers3 :size="15" class="text-primary-300" />
              {{ totalPisos }} {{ totalPisos === 1 ? 'Piso' : 'Pisos' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <Building2 :size="15" class="text-emerald-300" />
              {{ totalAmbientes }} {{ totalAmbientes === 1 ? 'Ambiente' : 'Ambientes' }}
            </span>
            <span class="inline-flex items-center gap-2 rounded-2xl bg-white/10 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur">
              <Monitor :size="15" class="text-amber-300" />
              {{ totalEquipos }} {{ totalEquipos === 1 ? 'Equipo' : 'Equipos' }}
            </span>
          </div>
        </div>

        <!-- Botones de accion en el banner -->
        <div class="flex flex-wrap items-center gap-3">
          <BaseButton
            variant="secondary"
            size="sm"
            :full-width="false"
            @click="emit('back')"
          >
            <template #icon><ArrowLeft :size="15" /></template>
            Volver a pabellones
          </BaseButton>

          <BaseButton
            v-if="canEdit"
            variant="accent"
            size="sm"
            :full-width="false"
            @click="emit('create-space')"
          >
            <template #icon><Plus :size="16" /></template>
            Agregar ambiente
          </BaseButton>
        </div>
      </div>
    </section>

    <!-- Encabezado de seccion de plantas -->
    <section class="min-w-0">
      <div class="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div class="min-w-0">
          <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-primary-600">
            Plantas del pabellón
          </p>
          <h2 id="floor-selector-title" class="mt-1 text-lg font-extrabold text-slate-950 sm:text-xl">
            Estructura vertical del edificio y telemetría por nivel
          </h2>
        </div>
        <p class="shrink-0 text-xs font-semibold text-slate-400">
          {{ floors.length }} {{ floors.length === 1 ? 'piso disponible' : 'pisos disponibles' }}
        </p>
      </div>

      <!-- Lista vertical de plantas -->
      <div
        v-if="floors.length"
        class="mt-4 grid min-w-0 gap-4"
        role="list"
        aria-label="Pisos del pabellón"
      >
        <article
          v-for="floor in sortedFloors"
          :key="floor.key"
          class="group flex flex-col justify-between gap-5 rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs transition-all duration-200 hover:border-primary-300 hover:shadow-md lg:flex-row lg:items-center"
        >
          <!-- Lado Izquierdo: Identidad de Planta -->
          <div class="flex items-start gap-4 lg:w-52 lg:shrink-0">
            <span class="grid size-12 shrink-0 place-items-center rounded-2xl bg-primary-50 text-primary-600 transition-colors group-hover:bg-primary-500 group-hover:text-white">
              <Layers3 :size="22" aria-hidden="true" />
            </span>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="text-base font-extrabold text-slate-900 tracking-tight sm:text-lg">
                  {{ floor.label }}
                </h3>
                <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">
                  {{ floor.allSpaces?.length || 0 }} amb.
                </span>
              </div>
              <p class="mt-0.5 text-xs text-slate-500 font-medium">
                {{ floor.aulas || 0 }} {{ (floor.aulas === 1) ? 'aula' : 'aulas' }} ·
                {{ floor.labs || 0 }} {{ (floor.labs === 1) ? 'tecnológico' : 'tecnológicos' }}
              </p>
            </div>
          </div>

          <!-- Centro: Telemetria y Ambientes -->
          <div class="flex flex-1 flex-col gap-3 min-w-0">
            <!-- Barra de Telemetria -->
            <div v-if="getFloorTelemetry(floor).totalEquipos > 0" class="flex flex-col gap-1.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-slate-700">Salud del hardware</span>
                <span class="font-semibold text-slate-500">
                  {{ getFloorTelemetry(floor).totalEquipos }} equipos monitoreados
                </span>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-100 flex">
                <div
                  v-if="getFloorTelemetry(floor).pctOperativos > 0"
                  class="bg-emerald-500 transition-all duration-300"
                  :style="{ width: `${getFloorTelemetry(floor).pctOperativos}%` }"
                  :title="`${getFloorTelemetry(floor).operativos} equipos operativos`"
                />
                <div
                  v-if="getFloorTelemetry(floor).pctMantenimiento > 0"
                  class="bg-amber-400 transition-all duration-300"
                  :style="{ width: `${getFloorTelemetry(floor).pctMantenimiento}%` }"
                  :title="`${getFloorTelemetry(floor).enMantenimiento} equipos en mantenimiento`"
                />
                <div
                  v-if="getFloorTelemetry(floor).pctIncidencias > 0"
                  class="bg-danger-500 transition-all duration-300"
                  :style="{ width: `${getFloorTelemetry(floor).pctIncidencias}%` }"
                  :title="`${getFloorTelemetry(floor).incidencias} equipos con incidencia`"
                />
              </div>
              <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] font-semibold">
                <span class="inline-flex items-center gap-1 text-emerald-700">
                  <span class="size-1.5 rounded-full bg-emerald-500" />
                  {{ getFloorTelemetry(floor).operativos }} operativos
                </span>
                <span v-if="getFloorTelemetry(floor).enMantenimiento > 0" class="inline-flex items-center gap-1 text-amber-700">
                  <span class="size-1.5 rounded-full bg-amber-400" />
                  {{ getFloorTelemetry(floor).enMantenimiento }} en mantenimiento
                </span>
                <span v-if="getFloorTelemetry(floor).incidencias > 0" class="inline-flex items-center gap-1 text-danger-700">
                  <span class="size-1.5 rounded-full bg-danger-500" />
                  {{ getFloorTelemetry(floor).incidencias }} incidencias
                </span>
              </div>
            </div>
            <div v-else class="text-xs text-slate-400 italic">
              Sin equipos de cómputo registrados en esta planta.
            </div>

            <!-- Chips de Ambientes y Tecnico de Piso -->
            <div class="flex flex-wrap items-center gap-2 pt-0.5">
              <span
                v-for="space in (floor.allSpaces || []).slice(0, 4)"
                :key="space.id"
                class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-1 text-xs font-medium text-slate-700"
              >
                <component :is="getSpaceIcon(space.tipo)" :size="13" class="text-slate-500 shrink-0" />
                <strong class="font-bold text-slate-800">{{ space.codigo_espacio }}</strong>
                <span v-if="space.cantidad_equipos" class="text-slate-400 text-[10px]">
                  · {{ space.cantidad_equipos }} PCs
                </span>
              </span>

              <span
                v-if="(floor.allSpaces || []).length > 4"
                class="inline-flex items-center rounded-xl bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600"
              >
                +{{ (floor.allSpaces || []).length - 4 }} más
              </span>

              <!-- Ficha de Encargado de Piso -->
              <span
                v-if="floor.encargado"
                class="inline-flex items-center gap-1.5 rounded-xl border border-primary-200 bg-primary-50/70 px-2.5 py-1 text-xs font-medium text-primary-800"
              >
                <UserCheck :size="13" class="text-primary-600" />
                <span class="truncate max-w-[150px]">{{ floor.encargado.usuario_nombre }}</span>
                <span class="text-[10px] text-primary-600 font-bold">· Técnico</span>
              </span>
              <button
                v-else-if="canEdit"
                type="button"
                class="inline-flex items-center gap-1 rounded-xl border border-dashed border-slate-300 px-2.5 py-1 text-[11px] font-semibold text-slate-500 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50/40 transition-colors"
                @click="emit('assign-technician', { floor, piso: floor.key, edificio_id: edificio?.id, local_id: edificio?.local_id, edificio_nombre: edificio?.nombre, encargado: null })"
              >
                <Plus :size="12" />
                Asignar técnico
              </button>
            </div>
          </div>

          <!-- Lado Derecho: Boton de Accion Principal -->
          <div class="flex items-center justify-end lg:w-52 lg:shrink-0">
            <BaseButton
              variant="accent"
              size="sm"
              :full-width="false"
              class="w-full sm:w-auto"
              :disabled="disabled"
              @click="emit('select', floor.key)"
            >
              Ver croquis interactivo
              <template #icon><ArrowRight :size="15" /></template>
            </BaseButton>
          </div>
        </article>
      </div>

      <!-- Estado vacio si el pabellon no tiene pisos -->
      <div
        v-else
        class="mt-4 flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center"
      >
        <Layers3 :size="40" class="text-slate-300 mb-3" />
        <h3 class="text-base font-bold text-slate-900">No hay pisos registrados en este pabellón</h3>
        <p class="mt-1 text-xs text-slate-500 max-w-sm">
          Registra ambientes para comenzar a estructurar los pisos y planos de este edificio.
        </p>
        <BaseButton
          v-if="canEdit"
          variant="accent"
          size="sm"
          class="mt-4"
          :full-width="false"
          @click="emit('create-space')"
        >
          <template #icon><Plus :size="16" /></template>
          Registrar ambiente en Piso 1
        </BaseButton>
      </div>
    </section>
  </div>
</template>

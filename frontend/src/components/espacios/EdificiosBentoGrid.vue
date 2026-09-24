<script setup>
import {
  ArrowRight,
  Building2,
  ChevronRight,
  DoorOpen,
  Landmark,
  Layers,
  MapPin,
  Monitor,
  Pencil,
  Trash2,
} from '@lucide/vue';

defineProps({
  sede: { type: Object, required: true },
  edificios: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
});

const emit = defineEmits([
  'select-edificio',
  'edit-edificio',
  'delete-edificio',
]);
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Banner de contexto de la Sede seleccionada -->
    <section class="overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-sm">
      <div class="flex flex-col justify-between gap-4 p-5 sm:p-6 lg:flex-row lg:items-center">
         <div class="flex min-w-0 items-start gap-4">
          <span class="grid size-12 shrink-0 place-items-center rounded-2xl bg-primary-50 text-primary-600">
            <Landmark :size="24" aria-hidden="true" />
          </span>
           <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                {{ sede.tipo || 'Sede' }}
              </span>
              <span class="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-0.5 text-[10px] font-bold text-primary-700">
                <MapPin :size="10" />
                {{ sede.ciudad }}
              </span>
              <span class="font-mono text-xs font-bold text-slate-400">
                {{ sede.codigo }}
              </span>
            </div>
             <h2 class="mt-1 wrap-break-word text-xl font-extrabold text-slate-950 sm:text-2xl">
              {{ sede.nombre }}
            </h2>
            <p v-if="sede.descripcion" class="mt-1 text-xs text-slate-500 max-w-2xl">
              {{ sede.descripcion }}
            </p>
          </div>
        </div>

      </div>

      <!-- Barra de contadores globales de la sede -->
      <div class="grid grid-cols-2 divide-x divide-y divide-slate-100 border-t border-slate-100 bg-slate-50/60 sm:grid-cols-4 sm:divide-y-0 text-center">
        <div class="p-3">
          <span class="block text-lg font-extrabold text-slate-900">{{ edificios.length }}</span>
          <span class="block text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Pabellones</span>
        </div>
        <div class="p-3">
          <span class="block text-lg font-extrabold text-slate-900">{{ sede.ambientesCount ?? 0 }}</span>
          <span class="block text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Ambientes</span>
        </div>
        <div class="p-3">
          <span class="block text-lg font-extrabold text-slate-900">{{ sede.equiposCount ?? 0 }}</span>
          <span class="block text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Equipos</span>
        </div>
        <div class="p-3">
          <span class="block text-lg font-extrabold text-emerald-600">{{ sede.telemetria?.operativos ?? 0 }}</span>
          <span class="block text-[11px] font-semibold text-slate-500 uppercase tracking-tight">Operativos</span>
        </div>
      </div>
    </section>

    <!-- Lista de Pabellones / Edificios -->
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="item in 3"
        :key="item"
        class="h-44 animate-pulse rounded-2xl border border-slate-100 bg-slate-100/60"
      />
    </div>

    <div
      v-else-if="edificios.length > 0"
      class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
      aria-label="Lista de pabellones"
    >
      <div
        v-for="edificio in edificios"
        :key="edificio.id"
        role="button"
        tabindex="0"
         class="group relative flex min-w-0 flex-col justify-between rounded-2xl border border-slate-200/90 bg-white p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 cursor-pointer sm:p-5"
        @click="emit('select-edificio', edificio.id)"
        @keydown.enter="emit('select-edificio', edificio.id)"
      >
        <div>
          <!-- Cabecera de la tarjeta del pabellon -->
          <div class="flex items-start justify-between gap-3">
            <span
              class="grid size-11 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600 transition-colors group-hover:bg-primary-500 group-hover:text-white"
            >
              <Building2 :size="20" aria-hidden="true" />
            </span>
            <span class="font-mono text-xs font-bold text-slate-400">
              {{ edificio.codigo }}
            </span>
          </div>

          <div class="mt-3">
             <h3 class="wrap-break-word text-base font-bold text-slate-900 group-hover:text-primary-600 transition-colors">
              {{ edificio.nombre }}
            </h3>
            <p v-if="edificio.descripcion" class="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
              {{ edificio.descripcion }}
            </p>
          </div>

          <!-- Badges de pisos, ambientes y equipos -->
          <div class="mt-4 flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              <Layers :size="13" class="text-slate-400" />
              {{ edificio.pisosCount }} {{ edificio.pisosCount === 1 ? 'piso' : 'pisos' }}
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              <DoorOpen :size="13" class="text-slate-400" />
              {{ edificio.ambientesCount }} {{ edificio.ambientesCount === 1 ? 'ambiente' : 'ambientes' }}
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              <Monitor :size="13" class="text-slate-400" />
              {{ edificio.equiposCount }} {{ edificio.equiposCount === 1 ? 'equipo' : 'equipos' }}
            </span>
          </div>
        </div>

        <!-- Pie: Salud y navegacion -->
         <div class="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
          <div class="flex items-center gap-1.5 text-xs font-semibold">
            <template v-if="edificio.salud === 'incidencia'">
              <span class="size-2 rounded-full bg-danger-500" />
              <span class="text-danger-700">{{ edificio.telemetria.incidencias }} incidencias</span>
            </template>
            <template v-else-if="edificio.salud === 'mantenimiento'">
              <span class="size-2 rounded-full bg-amber-500" />
              <span class="text-amber-700">{{ edificio.telemetria.mantenimiento }} en mant.</span>
            </template>
            <template v-else-if="edificio.equiposCount > 0">
              <span class="size-2 rounded-full bg-emerald-500" />
              <span class="text-emerald-700">Operativo</span>
            </template>
            <template v-else>
              <span class="size-2 rounded-full bg-slate-400" />
              <span class="text-slate-500">Sin equipos</span>
            </template>
          </div>

          <div class="flex items-center gap-1">
            <button
              v-if="canEdit"
              type="button"
              class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-primary-600"
              title="Editar pabellón"
              aria-label="Editar pabellón"
              @click.stop="emit('edit-edificio', edificio)"
            >
              <Pencil :size="15" />
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="rounded-lg p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
              title="Desactivar pabellón"
              aria-label="Desactivar pabellón"
              @click.stop="emit('delete-edificio', edificio)"
            >
              <Trash2 :size="15" />
            </button>
            <span class="ml-1 inline-flex items-center gap-1 text-xs font-bold text-primary-600 group-hover:underline">
              Ver pisos
              <ChevronRight :size="15" />
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado vacio de pabellones -->
    <div
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center"
    >
      <Building2 :size="40" class="text-slate-300 mb-3" />
      <h3 class="text-base font-bold text-slate-900">No hay pabellones en esta sede</h3>
      <p class="mt-1 text-xs text-slate-500 max-w-sm">
        Registra el primer pabellón o edificio para organizar sus pisos y ambientes tecnológicos.
      </p>
    </div>
  </div>
</template>

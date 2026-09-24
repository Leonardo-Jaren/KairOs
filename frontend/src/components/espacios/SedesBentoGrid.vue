<script setup>
import {
  ArrowRight,
  Building2,
  Landmark,
  MapPin,
  Pencil,
  Trash2,
} from '@lucide/vue';

defineProps({
  sedes: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
});

const emit = defineEmits([
  'select-sede',
  'edit-sede',
  'delete-sede',
]);
</script>

<template>
  <div class="flex flex-col gap-5">
    <div class="flex items-center justify-end">
       <div class="flex items-center gap-3">
         <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">
           {{ sedes.length }} {{ sedes.length === 1 ? 'local registrado' : 'locales registrados' }}
         </span>
       </div>
    </div>

    <!-- Skeleton loading -->
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="item in 3"
        :key="item"
        class="h-48 animate-pulse rounded-2xl border border-slate-100 bg-slate-100/60"
      />
    </div>

    <!-- Lista de Sedes en tarjetas Bento -->
    <div
      v-else-if="sedes.length > 0"
      class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
       aria-label="Lista de locales"
    >
      <div
        v-for="sede in sedes"
        :key="sede.id"
        role="button"
        tabindex="0"
         class="group relative flex min-w-0 flex-col justify-between rounded-2xl border border-slate-200/90 bg-white p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 cursor-pointer sm:p-5"
        @click="emit('select-sede', sede.id)"
        @keydown.enter="emit('select-sede', sede.id)"
      >
        <div>
          <!-- Cabecera de la tarjeta: Icono + Badges -->
          <div class="flex items-start justify-between gap-3">
            <span
              class="grid size-12 shrink-0 place-items-center rounded-2xl bg-primary-50 text-primary-600 transition-colors group-hover:bg-primary-500 group-hover:text-white"
            >
              <Landmark :size="22" aria-hidden="true" />
            </span>
            <div class="flex flex-wrap items-center justify-end gap-1.5">
              <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-600">
                {{ sede.tipo || 'Sede' }}
              </span>
              <span class="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-0.5 text-[10px] font-bold text-primary-700">
                <MapPin :size="10" />
                {{ sede.ciudad }}
              </span>
            </div>
          </div>

          <!-- Nombre y código de la sede -->
          <div class="mt-3.5">
            <span class="block font-mono text-[11px] font-bold uppercase tracking-wider text-slate-400">
              {{ sede.codigo }}
            </span>
             <h3 class="mt-0.5 wrap-break-word text-lg font-bold text-slate-900 group-hover:text-primary-600 transition-colors">
              {{ sede.nombre }}
            </h3>
            <p v-if="sede.descripcion" class="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
              {{ sede.descripcion }}
            </p>
          </div>

          <!-- Metricas Bento compactas -->
           <div class="mt-4 grid grid-cols-3 gap-1 rounded-xl border border-slate-100 bg-slate-50/70 p-2 text-center sm:gap-2 sm:p-2.5">
            <div>
              <span class="block text-base font-extrabold text-slate-900">{{ sede.edificiosCount }}</span>
               <span class="block text-[10px] font-semibold text-slate-500 uppercase tracking-tight max-[360px]:text-[9px]">Pabellones</span>
            </div>
            <div>
              <span class="block text-base font-extrabold text-slate-900">{{ sede.ambientesCount }}</span>
              <span class="block text-[10px] font-semibold text-slate-500 uppercase tracking-tight">Ambientes</span>
            </div>
            <div>
              <span class="block text-base font-extrabold text-slate-900">{{ sede.equiposCount }}</span>
              <span class="block text-[10px] font-semibold text-slate-500 uppercase tracking-tight">Equipos</span>
            </div>
          </div>
        </div>

        <!-- Pie de tarjeta: Estado de salud y accion -->
         <div class="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
          <div class="flex items-center gap-1.5 text-xs font-semibold">
            <template v-if="sede.salud === 'incidencia'">
              <span class="size-2 rounded-full bg-danger-500" />
              <span class="text-danger-700">{{ sede.telemetria.incidencias }} incidencias</span>
            </template>
            <template v-else-if="sede.salud === 'mantenimiento'">
              <span class="size-2 rounded-full bg-amber-500" />
              <span class="text-amber-700">{{ sede.telemetria.mantenimiento }} en mant.</span>
            </template>
            <template v-else-if="sede.equiposCount > 0">
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
               title="Editar local"
               aria-label="Editar local"
              @click.stop="emit('edit-sede', sede)"
            >
              <Pencil :size="15" />
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="rounded-lg p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
               title="Desactivar local"
               aria-label="Desactivar local"
              @click.stop="emit('delete-sede', sede)"
            >
              <Trash2 :size="15" />
            </button>
            <span class="ml-1 inline-flex items-center gap-1 text-xs font-bold text-primary-600 group-hover:underline">
              Explorar
              <ArrowRight :size="14" />
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado vacio -->
    <div
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center"
    >
      <Building2 :size="40" class="text-slate-300 mb-3" />
       <h3 class="text-base font-bold text-slate-900">No se encontraron locales</h3>
      <p class="mt-1 text-xs text-slate-500 max-w-sm">
         No hay registros que coincidan con la búsqueda.
       </p>
    </div>
  </div>
</template>

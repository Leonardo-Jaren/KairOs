<script setup>
import { ArrowLeft, Building2, Layers, MapPin, Plus } from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import CroquisPiso from '@/components/espacios/CroquisPiso.vue';
import { viewLocation } from '@/composables/espacios/espaciosNavigation';

defineProps({
  sede: { type: Object, default: () => null },
  edificio: { type: Object, required: true },
  pisos: { type: Array, default: () => [] },
  canEdit: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  contextQuery: { type: Object, default: () => ({}) },
});

const emit = defineEmits([
  'back-to-edificios',
  'create-espacio',
  'edit-espacio',
  'delete-espacio',
  'assign-technician',
]);
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Cabecera del Pabellón seleccionado -->
    <section class="overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-sm">
      <div class="flex flex-col justify-between gap-4 p-5 sm:p-6 lg:flex-row lg:items-center">
         <div class="flex min-w-0 items-start gap-4">
          <span class="grid size-12 shrink-0 place-items-center rounded-2xl bg-primary-50 text-primary-600">
            <Building2 :size="24" aria-hidden="true" />
          </span>
           <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span v-if="sede" class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold text-slate-600">
                <MapPin :size="10" />
                {{ sede.nombre }}
              </span>
              <span class="font-mono text-xs font-bold text-slate-400">
                {{ edificio.codigo }}
              </span>
            </div>
             <h2 class="mt-1 wrap-break-word text-xl font-extrabold text-slate-950 sm:text-2xl">
              {{ edificio.nombre }}
            </h2>
            <p class="mt-1 text-xs text-slate-500">
              Plantas verticales y distribución física de ambientes y hardware.
            </p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <BaseButton
            variant="ghost"
            size="sm"
            :full-width="false"
            @click="emit('back-to-edificios')"
          >
            <template #icon>
              <ArrowLeft :size="16" />
            </template>
            Volver a pabellones
          </BaseButton>
        </div>
      </div>
    </section>

    <!-- Lista de Plantas Verticales / Pisos (ordenados de arriba hacia abajo: Piso 3, Piso 2, Piso 1) -->
    <div v-if="loading" class="flex flex-col gap-5">
      <div
        v-for="item in 2"
        :key="item"
        class="h-64 animate-pulse rounded-2xl border border-slate-100 bg-slate-100/60"
      />
    </div>

    <div v-else-if="pisos.length > 0" class="flex flex-col gap-6" aria-label="Plantas verticales">
      <section
        v-for="floor in pisos"
        :key="floor.key"
        class="overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-sm transition-all duration-200"
      >
        <CroquisPiso
          :floor="floor"
          :can-edit="canEdit"
          :layout-editable="false"
          embedded
          :context-query="contextQuery"
          @create-space="emit('create-espacio', { sedeId: edificio.local_id, edificioId: edificio.id, piso: floor.piso })"
          @edit-space="emit('edit-espacio', $event)"
          @delete-space="emit('delete-espacio', $event)"
          @assign-technician="emit('assign-technician', $event)"
        />
        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 bg-slate-50/60 px-4 py-3">
          <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-semibold">
            <span class="text-emerald-700">{{ floor.telemetria.operativos }} operativos</span>
            <span class="text-amber-700">{{ floor.telemetria.mantenimiento }} en mantenimiento</span>
            <span class="text-danger-700">{{ floor.telemetria.incidencias }} incidencias</span>
          </div>
          <RouterLink
            v-if="canEdit"
            :to="viewLocation('mapa', { ...contextQuery, sede: edificio.local_id, edificio: edificio.id, piso: floor.piso }, sede?.ciudad)"
            class="inline-flex min-h-11 items-center rounded-lg px-3 text-xs font-bold text-primary-700 transition-colors hover:bg-primary-50 focus-visible:outline-2 focus-visible:outline-primary-500"
          >Editar distribución en Mapa</RouterLink>
        </div>
      </section>
    </div>

    <!-- Estado vacio de pisos -->
    <div
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center"
    >
      <Layers :size="40" class="text-slate-300 mb-3" />
      <h3 class="text-base font-bold text-slate-900">No hay pisos registrados</h3>
      <p class="mt-1 text-xs text-slate-500 max-w-sm">
        Registra ambientes para comenzar a estructurar los pisos de este pabellón.
      </p>
      <BaseButton
        v-if="canEdit"
        variant="accent"
        size="sm"
        class="mt-4"
        :full-width="false"
        @click="emit('create-espacio', { sedeId: edificio.local_id, edificioId: edificio.id, piso: '1' })"
      >
        <template #icon>
          <Plus :size="16" />
        </template>
        Registrar ambiente en Piso 1
      </BaseButton>
    </div>
  </div>
</template>

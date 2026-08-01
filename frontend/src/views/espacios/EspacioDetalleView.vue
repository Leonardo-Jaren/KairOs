<template>
  <div class="flex flex-col gap-6">
    <RouterLink to="/espacios"
      class="inline-flex w-fit items-center gap-2 text-sm font-semibold text-slate-500 hover:text-primary-600">
      <ArrowLeft :size="17" />
      Volver a espacios
    </RouterLink>

    <div v-if="loading" class="h-72 animate-pulse rounded-2xl bg-slate-200" />
    <div v-else-if="error" class="rounded-2xl border border-danger-200 bg-danger-50 p-6 text-sm text-danger-700">{{
      error }}</div>
    <template v-else-if="espacio">
      <section class="grid gap-4 sm:grid-cols-3">
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <Building2 :size="22" class="mb-3 text-primary-600" />
          <p class="text-2xl font-extrabold text-slate-950">{{ espacio.codigo_espacio }}</p>
          <p class="text-sm text-slate-500">{{ espacio.tipo_display }} · {{ espacio.pabellon }} · Piso {{ espacio.piso}}</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <Monitor :size="22" class="mb-3 text-success-600" />
          <p class="text-2xl font-extrabold text-slate-950">{{ equipos.length }}</p>
          <p class="text-sm text-slate-500">Equipos asignados</p>
        </article>
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <UserRound :size="22" class="mb-3 text-violet-600" />
          <p class="truncate text-lg font-bold text-slate-950">
            {{ espacio.responsable?.nombre_completo || 'Sin responsable' }}</p>
          <p class="truncate text-sm text-slate-500">{{ espacio.responsable?.correo || 'Pendiente de asignación' }}</p>
        </article>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-8 text-center">
          <p class="text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Distribución tecnológica</p>
          <h1 class="mt-1 text-2xl font-extrabold text-slate-950">Diagrama de {{ espacio.codigo_espacio }}</h1>
          <p class="mt-2 text-sm text-slate-500">Consulta el inventario asignado actualmente a este ambiente.</p>
        </div>

        <div v-if="equipos.length"
          class="mx-auto grid max-w-5xl grid-cols-2 gap-x-6 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          <article v-for="equipo in equipos" :key="equipo.id" class="group text-center">
            <div
              class="mx-auto grid size-16 place-items-center rounded-full bg-primary-600 text-white shadow-lg shadow-primary-200 transition-transform group-hover:-translate-y-1">
              <Monitor :size="28" :stroke-width="1.7" />
            </div>
            <p class="mt-2 truncate text-sm font-bold text-slate-800">{{ equipo.codigo }}</p>
            <p class="truncate text-xs text-slate-400">{{ equipo.tipo_display }}</p>
            <span class="mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold"
              :class="equipo.estado === 'en_uso' ? 'bg-success-50 text-success-700' : 'bg-warning-50 text-warning-700'">
              {{ equipo.estado_display }}
            </span>
          </article>
        </div>
        <div v-else class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
          <Monitor :size="34" class="mx-auto mb-3 text-slate-300" />
          <p class="font-semibold text-slate-600">Este espacio todavía no tiene equipos asignados.</p>
        </div>
      </section>
    </template>
  </div>
</template>
<script setup>
import { ArrowLeft, Building2, Monitor, UserRound } from '@lucide/vue';
import { useRoute } from 'vue-router';

import { useEspacioDetalle } from '@/composables/espacios/useEspacioDetalle';

const route = useRoute();
const { espacio, equipos, loading, error } = useEspacioDetalle(route.params.id);
</script>

<script setup>
import { AlertTriangle, ArrowRight, Building2, Layers3, Map, MapPin, MonitorCog, Search } from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import { useCampusTecnologico } from '@/composables/espacios/useCampusTecnologico';
import { formatFloor } from '@/utils/formatters';

const {
  loading, error, search, edificios, selectedBuilding, edificioActivo,
  laboratoriosVisibles, stats, loadCampus,
} = useCampusTecnologico();

const floorLabel = (floors) => `${floors.length} ${floors.length === 1 ? 'piso' : 'pisos'}`;
const laboratoryLabel = (count) => `${count} ${count === 1 ? 'laboratorio' : 'laboratorios'}`;
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Infraestructura visual</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Mapa tecnológico del campus</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">Recorre los edificios, ubica cada laboratorio y consulta su distribución de equipos como si estuvieras dentro del ambiente.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <BaseButton variant="secondary" :full-width="false" @click="loadCampus">Actualizar mapa</BaseButton>
        <BaseButton variant="accent" :full-width="false" @click="$router.push('/espacios')">Ver inventario</BaseButton>
      </div>
    </header>

    <section class="relative overflow-hidden rounded-3xl bg-secondary-950 px-6 py-7 text-white shadow-xl shadow-secondary-950/10 sm:px-8">
      <div class="absolute -right-16 -top-16 size-72 rounded-full bg-primary-500/15 blur-3xl" />
      <div class="absolute bottom-0 right-12 hidden h-36 w-72 items-end gap-3 opacity-35 lg:flex" aria-hidden="true">
        <span v-for="height in [55, 90, 72, 110, 82]" :key="height" class="flex-1 rounded-t-lg border border-primary-300/40 bg-primary-500/20" :style="{ height: `${height}%` }" />
      </div>
      <div class="relative grid gap-7 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-primary-200"><Map :size="15" /> Vista operativa del campus</span>
          <h2 class="mt-5 max-w-2xl text-2xl font-extrabold leading-tight sm:text-3xl">De la vista general al puesto exacto en pocos clics.</h2>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-white/55">Los bloques representan los edificios registrados; dentro encontrarás sus laboratorios y el estado actual de cada estación.</p>
        </div>
        <dl class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-2">
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3"><dt class="text-[10px] font-bold uppercase tracking-wider text-white/40">Edificios</dt><dd class="mt-1 text-2xl font-extrabold">{{ stats.edificios }}</dd></div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3"><dt class="text-[10px] font-bold uppercase tracking-wider text-white/40">Laboratorios</dt><dd class="mt-1 text-2xl font-extrabold">{{ stats.laboratorios }}</dd></div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3"><dt class="text-[10px] font-bold uppercase tracking-wider text-white/40">Equipos</dt><dd class="mt-1 text-2xl font-extrabold">{{ stats.equipos }}</dd></div>
          <div class="rounded-2xl border border-warning-300/20 bg-warning-400/10 px-4 py-3"><dt class="text-[10px] font-bold uppercase tracking-wider text-warning-200">Por revisar</dt><dd class="mt-1 text-2xl font-extrabold text-warning-200">{{ stats.alertas }}</dd></div>
        </dl>
      </div>
    </section>

    <div v-if="loading" class="grid gap-4 md:grid-cols-3"><div v-for="item in 6" :key="item" class="h-40 animate-pulse rounded-2xl bg-slate-200" /></div>
    <div v-else-if="error" class="rounded-2xl border border-danger-200 bg-danger-50 p-6 text-sm text-danger-700">{{ error }}</div>
    <template v-else>
      <section>
        <div class="mb-3 flex items-center justify-between gap-4">
          <div><p class="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Selecciona un bloque</p><h2 class="mt-1 text-xl font-extrabold text-slate-950">Edificios del campus</h2></div>
          <p class="hidden text-xs text-slate-400 sm:block">{{ edificios.length }} ubicaciones registradas</p>
        </div>
        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          <button v-for="(building, index) in edificios" :key="building.name" type="button" class="group relative overflow-hidden rounded-2xl border p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md" :class="selectedBuilding === building.name ? 'border-primary-400 bg-primary-50 ring-2 ring-primary-100' : 'border-slate-200 bg-white hover:border-primary-200'" @click="selectedBuilding = building.name">
            <span class="absolute right-3 top-2 font-mono text-5xl font-black text-slate-100 group-hover:text-primary-100">{{ String(index + 1).padStart(2, '0') }}</span>
            <span class="relative grid size-11 place-items-center rounded-xl" :class="selectedBuilding === building.name ? 'bg-primary-500 text-white' : 'bg-secondary-950 text-primary-300'"><Building2 :size="22" /></span>
            <p class="relative mt-4 text-base font-extrabold text-slate-900">{{ building.name }}</p>
            <div class="relative mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500"><span>{{ floorLabel(building.pisos) }}</span><span>{{ laboratoryLabel(building.laboratorios.length) }}</span><span>{{ building.equipos }} equipos</span></div>
            <span v-if="building.alertas" class="relative mt-3 inline-flex items-center gap-1 rounded-full bg-warning-100 px-2 py-1 text-[10px] font-bold text-warning-700"><AlertTriangle :size="12" /> {{ building.alertas }} por revisar</span>
          </button>
        </div>
      </section>

      <section v-if="edificioActivo" class="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
        <aside class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm xl:sticky xl:top-26 xl:h-fit">
          <span class="grid size-12 place-items-center rounded-2xl bg-primary-50 text-primary-600"><Building2 :size="24" /></span>
          <p class="mt-4 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Edificio seleccionado</p><h2 class="mt-1 text-xl font-extrabold text-slate-950">{{ edificioActivo.name }}</h2>
          <dl class="mt-5 divide-y divide-slate-100">
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><Layers3 :size="16" /> Pisos</dt><dd class="font-bold text-slate-800">{{ edificioActivo.pisos.length }}</dd></div>
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><MapPin :size="16" /> Ambientes</dt><dd class="font-bold text-slate-800">{{ edificioActivo.spaces.length }}</dd></div>
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><MonitorCog :size="16" /> Equipos</dt><dd class="font-bold text-slate-800">{{ edificioActivo.equipos }}</dd></div>
          </dl>
          <p class="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-500">Selecciona un laboratorio para abrir su distribución y trabajar directamente con cada equipo.</p>
        </aside>

        <div class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p class="text-xs font-bold uppercase tracking-[0.18em] text-primary-600">Ambientes tecnológicos</p><h2 class="mt-1 text-xl font-extrabold text-slate-950">Laboratorios en {{ edificioActivo.name }}</h2></div><div class="w-full sm:max-w-xs"><BaseInput id="campus-search" v-model="search" appearance="light" placeholder="Buscar laboratorio o piso"><template #icon><Search :size="16" /></template></BaseInput></div></div>
          <div v-if="laboratoriosVisibles.length" class="mt-5 grid gap-3 lg:grid-cols-2">
            <RouterLink v-for="lab in laboratoriosVisibles" :key="lab.id" :to="`/espacios/${lab.id}`" class="group rounded-2xl border border-slate-200 p-4 transition-all duration-200 hover:border-primary-300 hover:bg-primary-50/40 hover:shadow-md">
              <div class="flex items-start justify-between gap-4"><div class="flex min-w-0 items-center gap-3"><span class="grid size-11 shrink-0 place-items-center rounded-xl bg-secondary-950 text-primary-300"><MonitorCog :size="21" /></span><div class="min-w-0"><p class="truncate font-mono text-base font-extrabold text-slate-900">{{ lab.codigo_espacio }}</p><p class="mt-0.5 text-xs text-slate-500">{{ formatFloor(lab.piso) }} · {{ lab.tipo_display }}</p></div></div><ArrowRight :size="18" class="shrink-0 text-slate-300 transition-transform group-hover:translate-x-1 group-hover:text-primary-600" /></div>
              <div class="mt-4 grid grid-cols-3 gap-2"><div class="rounded-lg bg-slate-50 px-2.5 py-2"><p class="text-[9px] font-bold uppercase text-slate-400">Equipos</p><p class="text-sm font-extrabold text-slate-800">{{ lab.cantidad_equipos }}</p></div><div class="rounded-lg bg-success-50 px-2.5 py-2"><p class="text-[9px] font-bold uppercase text-success-600">Operativos</p><p class="text-sm font-extrabold text-success-700">{{ lab.resumen_equipos?.en_uso ?? 0 }}</p></div><div class="rounded-lg bg-warning-50 px-2.5 py-2"><p class="text-[9px] font-bold uppercase text-warning-600">Atención</p><p class="text-sm font-extrabold text-warning-700">{{ (lab.resumen_equipos?.en_mantenimiento ?? 0) + (lab.resumen_equipos?.dañado ?? 0) }}</p></div></div>
            </RouterLink>
          </div>
          <div v-else class="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center"><MapPin :size="30" class="mx-auto text-slate-300" /><p class="mt-3 text-sm font-semibold text-slate-600">No hay laboratorios que coincidan con la búsqueda.</p></div>
        </div>
      </section>
    </template>
  </div>
</template>

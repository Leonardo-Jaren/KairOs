<script setup>
import { computed, ref, watch } from 'vue';
import {
  Building2,
  ChevronRight,
  Compass,
  Landmark,
  MapPin,
} from '@lucide/vue';
import EspaciosSearch from '@/components/espacios/EspaciosSearch.vue';
import {
  HUANUCO_PROVINCES,
  CITY_COORDINATES,
} from '@/components/espacios/huanucoMapData.js';

const props = defineProps({
  city: { type: [String, Number], default: '' },
  cityCards: { type: Array, default: () => [] },
  localCards: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  search: { type: String, default: '' },
});

const emit = defineEmits(['select-city', 'select-local', 'update:search']);

const hoveredCity = ref(null);

const huanucoCard = computed(() => (
  props.cityCards.find((c) => {
    const text = `${c.value ?? ''} ${c.label ?? ''}`.toLowerCase();
    return text.includes('huánuco') || text.includes('huanuco');
  }) || null
));

const tingoCard = computed(() => (
  props.cityCards.find((c) => {
    const text = `${c.value ?? ''} ${c.label ?? ''}`.toLowerCase();
    return text.includes('tingo') || text.includes('maría') || text.includes('maria') || text.includes('leoncio');
  }) || null
));

const amboCard = computed(() => (
  props.cityCards.find((c) => {
    const text = `${c.value ?? ''} ${c.label ?? ''}`.toLowerCase();
    return text.includes('ambo');
  }) || null
));

function getProvinceCard(provId) {
  if (provId === 'HUANUCO') return huanucoCard.value;
  if (provId === 'LEONCIO_PRADO') return tingoCard.value;
  if (provId === 'AMBO') return amboCard.value;
  const prov = HUANUCO_PROVINCES.find((p) => p.id === provId);
  if (!prov) return null;
  return props.cityCards.find((c) => {
    const text = `${c.value ?? ''} ${c.label ?? ''}`.toLowerCase();
    return text.includes(prov.name.toLowerCase());
  }) || null;
}

function isProvActive(provId) {
  return Boolean(getProvinceCard(provId));
}

function isCityHovered(cityName) {
  if (!hoveredCity.value || !cityName) return false;
  return String(hoveredCity.value).toLowerCase() === String(cityName).toLowerCase();
}

function isProvHovered(provId) {
  if (!hoveredCity.value) return false;
  const card = getProvinceCard(provId);
  if (card && isCityHovered(card.value)) return true;
  return false;
}

function onProvinceClick(prov) {
  if (props.disabled) return;
  const card = getProvinceCard(prov.id);
  if (card) {
    emit('select-city', card.value);
  }
}

const citiesPage = ref(1);
const citiesPerPage = 4;
const filteredCities = computed(() => props.cityCards.filter((card) => (
  `${card.label} ${card.value}`.toLocaleLowerCase('es').includes(props.search.trim().toLocaleLowerCase('es'))
)));
const filteredLocals = computed(() => props.localCards.filter((local) => (
  `${local.nombre} ${local.codigo}`.toLocaleLowerCase('es').includes(props.search.trim().toLocaleLowerCase('es'))
)));
const totalCityPages = computed(() => Math.max(1, Math.ceil(filteredCities.value.length / citiesPerPage)));
const visibleCityCards = computed(() => filteredCities.value.slice(
  (citiesPage.value - 1) * citiesPerPage,
  citiesPage.value * citiesPerPage,
));
watch(totalCityPages, (pages) => {
  citiesPage.value = Math.min(citiesPage.value, pages);
});

const totalLocalesCount = computed(() => (
  props.cityCards.reduce((acc, c) => acc + (c.localCount || 0), 0)
));

const totalPabellonesCount = computed(() => (
  props.cityCards.reduce((acc, c) => acc + (c.buildingCount || 0), 0)
));
</script>

<template>
  <section
    class="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-sm flex flex-col flex-1 min-h-0"
    :aria-busy="disabled"
  >
    <!-- Nivel 1: Selección de ciudad con Hero Canvas y panel de sedes -->
    <div v-if="!city" class="p-3 sm:p-5 flex-1 flex flex-col min-h-0">
      <div class="grid gap-4 lg:grid-cols-12 lg:items-stretch flex-1 min-h-0">
        <!-- Hero Canvas: Mapa cartográfico oficial a escala equilibrada -->
        <div class="flex min-w-0 flex-col justify-between rounded-2xl border border-slate-200/90 bg-linear-to-b from-slate-50 via-slate-50/50 to-white p-3 sm:p-5 lg:col-span-7 xl:col-span-7 shadow-xs">
          <!-- Barra superior del Hero Canvas -->
          <div class="mb-2 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/60 pb-3 shrink-0">
            <div class="flex flex-wrap items-center gap-1.5">
              <Compass :size="16" class="text-primary-600" aria-hidden="true" />
              <span class="text-xs font-bold uppercase tracking-wider text-slate-700">Departamento de Huánuco</span>
              <span class="text-slate-300">·</span>
              <span class="text-xs text-slate-500">11 Provincias</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] font-semibold">
              <span class="inline-flex items-center gap-1.5 text-primary-700">
                <span class="size-2 rounded-full bg-primary-500" />
                 Ciudades con locales
              </span>
              <span class="inline-flex items-center gap-1.5 text-slate-500">
                <span class="size-2 rounded-full bg-slate-300" />
                Provincias
              </span>
            </div>
          </div>

          <!-- Canvas SVG interactivo -->
          <div class="relative flex flex-1 items-center justify-center w-full min-h-[260px] py-2 select-none">
            <svg
              viewBox="0 0 360 280"
              class="h-auto max-h-[310px] w-full max-w-[400px] drop-shadow-sm"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              role="img"
              aria-label="Mapa cartográfico oficial del departamento de Huánuco con sedes universitarias"
            >
              <defs>
                <filter id="mapDropShadow" x="-5%" y="-5%" width="110%" height="110%">
                  <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.08" />
                </filter>
                <filter id="glowHuanuco" x="-30%" y="-30%" width="160%" height="160%">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#2563eb" flood-opacity="0.35" />
                </filter>
                <filter id="glowTingo" x="-30%" y="-30%" width="160%" height="160%">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0284c7" flood-opacity="0.3" />
                </filter>
                <filter id="glowAmbo" x="-30%" y="-30%" width="160%" height="160%">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#4f46e5" flood-opacity="0.3" />
                </filter>
              </defs>

              <!-- Silueta cartográfica oficial de las 11 provincias de Huánuco -->
              <g filter="url(#mapDropShadow)">
                <path
                  v-for="prov in HUANUCO_PROVINCES"
                  :key="prov.id"
                  :d="prov.path"
                  stroke-linejoin="round"
                  stroke-linecap="round"
                  class="transition-colors duration-200"
                  :class="[
                    isProvActive(prov.id) ? 'cursor-pointer' : 'cursor-default',
                    isProvHovered(prov.id)
                      ? prov.id === 'LEONCIO_PRADO'
                        ? 'fill-sky-500/35 stroke-sky-600 stroke-[2]'
                        : prov.id === 'AMBO'
                          ? 'fill-indigo-500/35 stroke-indigo-600 stroke-[2]'
                          : 'fill-primary-500/35 stroke-primary-600 stroke-[2]'
                      : prov.id === 'HUANUCO' && huanucoCard
                        ? 'fill-primary-500/20 stroke-primary-600 stroke-[1.6] hover:fill-primary-500/35 hover:stroke-primary-700'
                        : prov.id === 'LEONCIO_PRADO' && tingoCard
                          ? 'fill-sky-500/20 stroke-sky-600 stroke-[1.4] hover:fill-sky-500/35 hover:stroke-sky-700'
                          : prov.id === 'AMBO' && amboCard
                            ? 'fill-indigo-500/20 stroke-indigo-600 stroke-[1.4] hover:fill-indigo-500/35 hover:stroke-indigo-700'
                            : 'fill-slate-100/90 stroke-slate-300 stroke-[1] hover:fill-slate-200/70'
                  ]"
                  @mouseenter="getProvinceCard(prov.id) && (hoveredCity = getProvinceCard(prov.id).value)"
                  @mouseleave="hoveredCity = null"
                  @click="onProvinceClick(prov)"
                >
                  <title>{{ prov.name }}{{ getProvinceCard(prov.id) ? ` (${getProvinceCard(prov.id).label})` : '' }}</title>
                </path>
              </g>

              <!-- SEDE REGIONAL: TINGO MARÍA (Leoncio Prado) -->
              <g
                v-if="tingoCard"
                class="group/tingo cursor-pointer"
                :filter="isCityHovered(tingoCard.value) ? 'url(#glowTingo)' : undefined"
                @mouseenter="hoveredCity = tingoCard.value"
                @mouseleave="hoveredCity = null"
                @click="emit('select-city', tingoCard.value)"
              >
                <!-- Pulso animado para Tingo María -->
                <circle :cx="CITY_COORDINATES.tingoMaria.x" :cy="CITY_COORDINATES.tingoMaria.y" r="8" class="fill-sky-500/25 animate-pulse" />
                <!-- Punto interactivo para Tingo María -->
                <circle :cx="CITY_COORDINATES.tingoMaria.x" :cy="CITY_COORDINATES.tingoMaria.y" r="5" class="fill-white stroke-sky-600 transition-colors group-hover/tingo:stroke-sky-500" stroke-width="2" />
                <circle :cx="CITY_COORDINATES.tingoMaria.x" :cy="CITY_COORDINATES.tingoMaria.y" r="2.2" class="fill-sky-600" />

                <!-- Etiqueta flotante de Tingo María -->
                <rect
                  :x="CITY_COORDINATES.tingoMaria.x + 8"
                  :y="CITY_COORDINATES.tingoMaria.y - 10"
                  width="80"
                  height="20"
                  rx="10"
                  class="fill-white/95 stroke-sky-400 shadow-sm transition-colors group-hover/tingo:stroke-sky-600 group-hover/tingo:fill-sky-50/70"
                  stroke-width="1.2"
                />
                <text
                  :x="CITY_COORDINATES.tingoMaria.x + 48"
                  :y="CITY_COORDINATES.tingoMaria.y + 4"
                  text-anchor="middle"
                  class="fill-sky-900 font-sans text-[9px] font-extrabold transition-colors group-hover/tingo:fill-sky-950"
                >
                  Tingo María
                </text>
              </g>

              <!-- SEDE REGIONAL: AMBO -->
              <g
                v-if="amboCard"
                class="group/ambo cursor-pointer"
                :filter="isCityHovered(amboCard.value) ? 'url(#glowAmbo)' : undefined"
                @mouseenter="hoveredCity = amboCard.value"
                @mouseleave="hoveredCity = null"
                @click="emit('select-city', amboCard.value)"
              >
                <!-- Pulso animado para Ambo -->
                <circle :cx="CITY_COORDINATES.ambo.x" :cy="CITY_COORDINATES.ambo.y" r="7" class="fill-indigo-500/25 animate-pulse" />
                <!-- Punto interactivo para Ambo -->
                <circle :cx="CITY_COORDINATES.ambo.x" :cy="CITY_COORDINATES.ambo.y" r="5" class="fill-white stroke-indigo-600 transition-colors group-hover/ambo:stroke-indigo-500" stroke-width="2" />
                <circle :cx="CITY_COORDINATES.ambo.x" :cy="CITY_COORDINATES.ambo.y" r="2.2" class="fill-indigo-600" />

                <!-- Etiqueta flotante de Ambo -->
                <rect
                  :x="CITY_COORDINATES.ambo.x + 8"
                  :y="CITY_COORDINATES.ambo.y - 9"
                  width="62"
                  height="18"
                  rx="9"
                  class="fill-white/95 stroke-indigo-400 shadow-sm transition-colors group-hover/ambo:stroke-indigo-600 group-hover/ambo:fill-indigo-50/70"
                  stroke-width="1.2"
                />
                <text
                  :x="CITY_COORDINATES.ambo.x + 39"
                  :y="CITY_COORDINATES.ambo.y + 3"
                  text-anchor="middle"
                  class="fill-indigo-900 font-sans text-[9px] font-extrabold transition-colors group-hover/ambo:fill-indigo-950"
                >
                  Ambo
                </text>
              </g>

              <!-- SEDE PRINCIPAL: HUÁNUCO (Capital provincial, Campus Central y La Esperanza) -->
              <g
                v-if="huanucoCard"
                class="group/huanuco cursor-pointer"
                :filter="isCityHovered(huanucoCard.value) ? 'url(#glowHuanuco)' : undefined"
                @mouseenter="hoveredCity = huanucoCard.value"
                @mouseleave="hoveredCity = null"
                @click="emit('select-city', huanucoCard.value)"
              >
                <!-- Pulso animado para Huánuco -->
                <circle :cx="CITY_COORDINATES.huanuco.x" :cy="CITY_COORDINATES.huanuco.y" r="10" class="fill-primary-500/25 animate-pulse" />
                <!-- Punto de la sede activa -->
                <circle :cx="CITY_COORDINATES.huanuco.x" :cy="CITY_COORDINATES.huanuco.y" r="6" class="fill-white stroke-primary-600 transition-colors group-hover/huanuco:stroke-primary-400" stroke-width="2.5" />
                <circle :cx="CITY_COORDINATES.huanuco.x" :cy="CITY_COORDINATES.huanuco.y" r="2.8" class="fill-primary-600" />

                <!-- Badge institucional de Huánuco -->
                <rect
                  :x="CITY_COORDINATES.huanuco.x - 48"
                  :y="CITY_COORDINATES.huanuco.y - 30"
                  width="96"
                  height="20"
                  rx="10"
                  class="fill-secondary-950 stroke-primary-400 shadow-md transition-colors group-hover/huanuco:stroke-primary-300 group-hover/huanuco:fill-secondary-900"
                  stroke-width="1.2"
                />
                <text
                  :x="CITY_COORDINATES.huanuco.x"
                  :y="CITY_COORDINATES.huanuco.y - 16"
                  text-anchor="middle"
                  class="fill-white font-sans text-[10px] font-extrabold tracking-wide"
                >
                  Huánuco
                </text>
              </g>
            </svg>
          </div>

        </div>

        <!-- Panel lateral integrado de sedes disponibles -->
        <div class="flex min-w-0 flex-col justify-between gap-3 lg:col-span-5 xl:col-span-5 min-h-0">
          <div class="flex flex-col gap-3 min-h-0">
            <div class="flex flex-wrap items-center justify-between gap-2 shrink-0">
              <div>
                 <p class="text-xs font-bold uppercase tracking-wider text-primary-600">Ciudades disponibles</p>
                 <h3 class="text-base font-extrabold text-slate-900">Selecciona una ciudad</h3>
              </div>
              <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold text-slate-600">
                 {{ cityCards.length }} {{ cityCards.length === 1 ? 'ciudad' : 'ciudades' }}
              </span>
            </div>

            <EspaciosSearch id="map-city-search" :model-value="search" placeholder="Buscar ciudad" @update:model-value="emit('update:search', $event)" />

            <ul class="flex flex-col gap-2.5" aria-label="Ciudades disponibles">
              <template v-if="loading && visibleCityCards.length === 0">
                <li v-for="n in 3" :key="n" class="h-[72px] animate-pulse rounded-xl bg-slate-100 border border-slate-200/60" />
              </template>
              <li v-for="option in visibleCityCards" :key="option.value">
                <!-- Todas las sedes comparten la misma presentación. -->
                <button
                  type="button"
                  class="group flex w-full items-center gap-3.5 rounded-xl border border-slate-200 bg-white p-3.5 text-left text-slate-900 shadow-xs transition-colors duration-200 hover:border-primary-400 hover:bg-primary-50/40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 disabled:opacity-50"
                  :class="isCityHovered(option.value) ? 'border-primary-500 bg-primary-50/40' : ''"
                  :disabled="disabled"
                  @mouseenter="hoveredCity = option.value"
                  @mouseleave="hoveredCity = null"
                  @focus="hoveredCity = option.value"
                  @blur="hoveredCity = null"
                  @click="emit('select-city', option.value)"
                >
                  <span class="grid size-11 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600">
                    <Landmark v-if="!option.legacy" :size="20" aria-hidden="true" />
                    <MapPin v-else :size="20" aria-hidden="true" />
                  </span>
                  <span class="min-w-0 flex-1">
                    <strong class="block truncate text-sm font-extrabold text-slate-950">{{ option.label }}</strong>
                    <span class="block text-xs leading-5 text-slate-600">
                      {{ option.localCount }} {{ option.localCount === 1 ? 'local' : 'locales' }} · {{ option.buildingCount }} {{ option.buildingCount === 1 ? 'pabellón' : 'pabellones' }}
                    </span>
                  </span>
                  <ChevronRight :size="18" class="shrink-0 text-slate-400 group-hover:text-primary-600" aria-hidden="true" />
                </button>
              </li>
              <li v-if="!loading && !filteredCities.length" class="rounded-xl border border-dashed border-slate-200 p-4 text-sm text-slate-600">No hay ciudades que coincidan con la búsqueda.</li>
            </ul>

             <nav v-if="totalCityPages > 1" class="flex items-center justify-between gap-2 text-xs font-semibold text-slate-600 shrink-0" aria-label="Páginas de ciudades">
              <button type="button" class="min-h-11 rounded-lg px-3 hover:bg-slate-100 disabled:opacity-40" :disabled="citiesPage <= 1" @click="citiesPage--">Anterior</button>
              <span aria-live="polite">{{ citiesPage }} / {{ totalCityPages }}</span>
              <button type="button" class="min-h-11 rounded-lg px-3 hover:bg-slate-100 disabled:opacity-40" :disabled="citiesPage >= totalCityPages" @click="citiesPage++">Siguiente</button>
            </nav>
          </div>

          <!-- Resumen de infraestructura total -->
          <div class="flex flex-wrap items-center justify-between gap-1 rounded-xl border border-slate-200 bg-slate-50/70 p-3 text-xs text-slate-600 shrink-0">
            <div class="flex items-center gap-2">
              <Building2 :size="16" class="text-primary-600" aria-hidden="true" />
              <span class="font-semibold text-slate-700">Infraestructura total:</span>
            </div>
            <span class="font-bold text-slate-900">
              {{ totalLocalesCount }} locales · {{ totalPabellonesCount }} pabellones
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Nivel 2: Selección de locales de la ciudad elegida -->
    <div v-else class="p-4 sm:p-7">
      <h2 class="mb-4 text-lg font-extrabold text-slate-950">Locales en {{ city === '__legacy__' ? 'registros anteriores' : city }}</h2>

      <div class="mb-4 max-w-2xl">
        <EspaciosSearch id="map-local-search" :model-value="search" placeholder="Buscar local" @update:model-value="emit('update:search', $event)" />
      </div>
      <ul v-if="filteredLocals.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-label="Locales disponibles">
        <li v-for="local in filteredLocals" :key="local.id" class="flex flex-col h-full">
          <button
            type="button"
            class="group flex flex-1 h-full w-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:opacity-50 motion-reduce:transform-none"
            :disabled="disabled"
            @click="emit('select-local', local.id)"
          >
            <div class="flex flex-1 flex-col">
              <div class="flex w-full items-start justify-between gap-3">
                <span class="grid size-11 shrink-0 place-items-center rounded-xl bg-secondary-950 text-primary-300 shadow-sm">
                  <Building2 :size="20" aria-hidden="true" />
                </span>
                <span class="rounded-full bg-primary-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-primary-700">
                  {{ local.tipoLabel }}
                </span>
              </div>
              <strong class="mt-3 block truncate text-base font-extrabold text-slate-950 group-hover:text-primary-600 transition-colors" :title="local.nombre">
                {{ local.nombre }}
              </strong>
              <span class="mt-0.5 block font-mono text-[11px] font-bold uppercase tracking-wide text-slate-400">
                {{ local.codigo }}
              </span>
              <p class="mt-2 line-clamp-2 min-h-[2.5rem] text-xs leading-5 text-slate-500">
                {{ (local.descripcion && local.descripcion.trim()) || `${local.tipoLabel || 'Sede'} con infraestructura tecnológica distribuida en pabellones y pisos.` }}
              </p>
            </div>

            <div class="mt-4 flex w-full items-center justify-between border-t border-slate-100 pt-3 text-xs font-semibold text-slate-600 shrink-0">
              <span class="flex items-center gap-1.5">
                <span class="size-2 rounded-full bg-primary-500" />
                {{ local.buildingCount }} {{ local.buildingCount === 1 ? 'pabellón' : 'pabellones' }}
              </span>
              <span class="flex items-center gap-1 font-bold text-primary-600 group-hover:underline">
                Explorar local
                <ChevronRight :size="16" class="transition-transform group-hover:translate-x-1 motion-reduce:transform-none" aria-hidden="true" />
              </span>
            </div>
          </button>
        </li>
      </ul>

      <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
        <Building2 :size="32" class="mx-auto text-slate-300" aria-hidden="true" />
        <p class="mt-3 text-sm font-semibold text-slate-600">{{ localCards.length ? 'No hay locales que coincidan con la búsqueda.' : 'Esta ciudad todavía no tiene locales registrados.' }}</p>
        <p v-if="!localCards.length" class="mt-1 text-xs text-slate-400">Agrega un local para clasificar y organizar sus pabellones.</p>
      </div>
    </div>

    <!-- Alerta cuando la edición del croquis está en curso -->
    <p
      v-if="disabled"
      class="border-t border-warning-200 bg-warning-50 px-5 py-3 text-xs font-semibold text-warning-800"
      role="status"
    >
      Guarda o cancela la edición del croquis para cambiar de ubicación.
    </p>
  </section>
</template>

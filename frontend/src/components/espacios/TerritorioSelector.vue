<script setup>
import { computed } from 'vue';
import {
  ArrowLeft,
  Building2,
  CheckCircle2,
  ChevronRight,
  Landmark,
  MapPin,
  MapPinned,
  Plus,
  Sparkles,
} from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import {
  HUANUCO_PROVINCES,
  CITY_COORDINATES,
} from '@/components/espacios/huanucoMapData.js';

const props = defineProps({
  city: { type: [String, Number], default: '' },
  cityCards: { type: Array, default: () => [] },
  localCards: { type: Array, default: () => [] },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(['select-city', 'select-local', 'create-local']);

const huanucoCard = computed(() => (
  props.cityCards.find((c) => String(c.value).toLowerCase().includes('huánuco') || String(c.value).toLowerCase().includes('huanuco'))
  || props.cityCards[0]
  || null
));

const tingoCard = computed(() => (
  props.cityCards.find((c) => String(c.value).toLowerCase().includes('tingo') || String(c.value).toLowerCase().includes('maría') || String(c.value).toLowerCase().includes('maria'))
  || null
));
</script>

<template>
  <section
    class="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-sm"
    :aria-busy="disabled"
  >
    <!-- Encabezado territorial -->
    <div class="relative overflow-hidden bg-secondary-950 px-5 py-5 text-white sm:px-7 sm:py-6">
      <div class="pointer-events-none absolute -right-12 -top-16 size-48 rounded-full border-[28px] border-primary-500/15" />
      <div class="relative flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-primary-500/20 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary-300">
              <Sparkles :size="12" aria-hidden="true" />
              {{ city ? 'Sedes y campus' : 'Mapa territorial' }}
            </span>
          </div>
          <h2 class="mt-2 text-xl font-extrabold tracking-tight sm:text-2xl">
            {{ city ? `¿A dónde vamos en ${city === '__legacy__' ? 'los registros anteriores' : city}?` : 'Infraestructura territorial' }}
          </h2>
          <p class="mt-1 max-w-2xl text-sm leading-6 text-white/70">
            {{ city ? 'Selecciona una sede o campus para consultar sus pabellones, pisos y equipamiento.' : 'Explora el mapa del territorio y selecciona una sede central para desplegar sus locales operativos.' }}
          </p>
        </div>
        <div class="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-2 text-xs font-semibold text-white/80 backdrop-blur">
          <MapPinned :size="16" class="text-primary-400" aria-hidden="true" />
          {{ city ? `${localCards.length} ${localCards.length === 1 ? 'local' : 'locales'}` : `${cityCards.length} ${cityCards.length === 1 ? 'ciudad' : 'ciudades'}` }}
        </div>
      </div>
    </div>

    <!-- Nivel 1: Selección de ciudad con mapa territorial -->
    <div v-if="!city" class="p-4 sm:p-7">
      <div class="grid gap-6 lg:grid-cols-12 lg:items-start">
        <!-- Lista y tarjetas de ciudades disponibles (garantiza aria-label y compatibilidad con tests) -->
        <div class="lg:col-span-7">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-primary-600">Zonas disponibles</p>
              <h3 class="text-base font-extrabold text-slate-900">Selecciona la sede que deseas explorar</h3>
            </div>
            <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold text-slate-600">
              {{ cityCards.length }} {{ cityCards.length === 1 ? 'región' : 'regiones' }}
            </span>
          </div>

          <ul class="grid gap-3.5" aria-label="Ciudades disponibles">
            <li v-for="(option, index) in cityCards" :key="option.value">
              <!-- Tarjeta destacada de Huánuco o sede principal (sobresale visualmente) -->
              <button
                type="button"
                class="group relative flex w-full flex-col overflow-hidden rounded-2xl border text-left transition duration-200 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-200 disabled:opacity-50 motion-reduce:transform-none"
                :class="option.localCount > 1 || index === 0
                  ? 'border-primary-400 bg-gradient-to-br from-primary-600 to-primary-700 p-5 text-white shadow-lg shadow-primary-500/25 ring-2 ring-primary-400/40'
                  : 'border-slate-200 bg-white p-4 text-slate-900 shadow-sm hover:border-primary-300 hover:shadow-md'"
                :disabled="disabled"
                @click="emit('select-city', option.value)"
              >
                <!-- Badge superior en la tarjeta destacada -->
                <div v-if="option.localCount > 1 || index === 0" class="mb-3 flex items-center justify-between">
                  <span class="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white backdrop-blur">
                    <span class="size-1.5 rounded-full bg-emerald-400" />
                    {{ option.value === 'Huánuco' ? 'Sede Central' : 'Sede Activa' }}
                  </span>
                  <span class="text-[11px] font-medium text-white/80">{{ option.value }}, Perú</span>
                </div>

                <div class="flex items-center gap-4">
                  <span
                    class="grid size-12 shrink-0 place-items-center rounded-2xl shadow-md"
                    :class="option.localCount > 1 || index === 0 ? 'bg-white/15 text-white shadow-primary-900/10 ring-1 ring-white/30' : 'bg-primary-50 text-primary-600'"
                  >
                    <Landmark v-if="!option.legacy" :size="22" aria-hidden="true" />
                    <MapPin v-else :size="22" aria-hidden="true" />
                  </span>

                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2">
                      <strong class="block text-base font-extrabold" :class="option.localCount > 1 || index === 0 ? 'text-white' : 'text-slate-950'">
                        {{ option.label }}
                      </strong>
                      <span v-if="option.localCount > 1 || index === 0" class="rounded bg-white/20 px-1.5 py-0.5 text-[9px] font-extrabold uppercase text-white">
                        Núcleo
                      </span>
                    </div>
                    <p class="mt-1 text-xs leading-5" :class="option.localCount > 1 || index === 0 ? 'text-white/85' : 'text-slate-500'">
                      {{ option.localCount }} {{ option.localCount === 1 ? 'local' : 'locales' }} · {{ option.buildingCount }} {{ option.buildingCount === 1 ? 'pabellón' : 'pabellones' }}
                    </p>
                  </div>

                  <span
                    class="grid size-9 shrink-0 place-items-center rounded-xl transition duration-200 group-hover:translate-x-1 motion-reduce:transform-none"
                    :class="option.localCount > 1 || index === 0 ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-400 group-hover:bg-primary-50 group-hover:text-primary-600'"
                  >
                    <ChevronRight :size="18" aria-hidden="true" />
                  </span>
                </div>

                <!-- Barra inferior de acción rápida en tarjeta destacada -->
                <div
                  v-if="option.localCount > 1 || index === 0"
                  class="mt-4 flex items-center justify-between border-t border-white/15 pt-3 text-xs font-semibold text-white"
                >
                  <span class="flex items-center gap-1.5">
                    <CheckCircle2 :size="14" class="text-emerald-300" aria-hidden="true" />
                    {{ option.localCount }} {{ option.localCount === 1 ? 'sede operativa disponible' : 'sedes operativas disponibles' }}
                  </span>
                  <span class="flex items-center gap-1 text-[11px] font-bold text-white group-hover:underline">
                    Ver locales
                    <ChevronRight :size="14" aria-hidden="true" />
                  </span>
                </div>
              </button>
            </li>
          </ul>
        </div>

        <!-- Columna derecha: Mapa cartográfico oficial del departamento de Huánuco -->
        <div class="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:p-6 lg:col-span-5">
          <div class="mb-3 flex w-full items-center justify-between">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Cartografía territorial</span>
            <span class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
              <span class="size-1.5 rounded-full bg-emerald-500" />
              Sede activa
            </span>
          </div>

          <!-- Representación vectorial cartográfica oficial del departamento de Huánuco -->
          <div class="relative w-full max-w-[320px] select-none py-1">
            <svg
              viewBox="0 0 360 280"
              class="h-auto w-full drop-shadow-sm"
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
              </defs>

              <!-- Silueta cartográfica oficial de las 11 provincias de Huánuco -->
              <g filter="url(#mapDropShadow)">
                <path
                  v-for="prov in HUANUCO_PROVINCES"
                  :key="prov.id"
                  :d="prov.path"
                  stroke-linejoin="round"
                  stroke-linecap="round"
                  class="transition-all duration-200"
                  :class="[
                    prov.id === 'HUANUCO' && huanucoCard
                      ? 'cursor-pointer fill-primary-500/25 stroke-primary-600 stroke-[1.6] hover:fill-primary-500/40 hover:stroke-primary-700'
                      : prov.id === 'LEONCIO_PRADO' && tingoCard
                        ? 'cursor-pointer fill-sky-500/20 stroke-sky-600 stroke-[1.4] hover:fill-sky-500/35 hover:stroke-sky-700'
                        : 'fill-slate-100/90 stroke-slate-300 stroke-[1]'
                  ]"
                  @click="prov.id === 'HUANUCO' && huanucoCard ? emit('select-city', huanucoCard.value) : (prov.id === 'LEONCIO_PRADO' && tingoCard ? emit('select-city', tingoCard.value) : null)"
                >
                  <title>{{ prov.name }}</title>
                </path>
              </g>

              <!-- SEDE REGIONAL: TINGO MARÍA (Provincia de Leoncio Prado) -->
              <g
                v-if="tingoCard"
                class="group/tingo cursor-pointer"
                @click="emit('select-city', tingoCard.value)"
              >
                <!-- Punto interactivo para Tingo María -->
                <circle :cx="CITY_COORDINATES.tingoMaria.x" :cy="CITY_COORDINATES.tingoMaria.y" r="5" class="fill-white stroke-sky-600 transition-colors group-hover/tingo:stroke-sky-500" stroke-width="2" />
                <circle :cx="CITY_COORDINATES.tingoMaria.x" :cy="CITY_COORDINATES.tingoMaria.y" r="2.2" class="fill-sky-600" />

                <!-- Etiqueta de Tingo María -->
                <rect
                  :x="CITY_COORDINATES.tingoMaria.x + 8"
                  :y="CITY_COORDINATES.tingoMaria.y - 10"
                  width="78"
                  height="20"
                  rx="10"
                  class="fill-white/95 stroke-sky-400 shadow-sm transition-all group-hover/tingo:stroke-sky-600 group-hover/tingo:fill-sky-50/50"
                  stroke-width="1.2"
                />
                <text
                  :x="CITY_COORDINATES.tingoMaria.x + 47"
                  :y="CITY_COORDINATES.tingoMaria.y + 3"
                  text-anchor="middle"
                  class="fill-sky-900 font-sans text-[9px] font-extrabold transition-colors group-hover/tingo:fill-sky-950"
                >
                  Tingo María
                </text>
              </g>

              <!-- SEDE PRINCIPAL: HUÁNUCO (Capital provincial, Campus Central y La Esperanza) -->
              <g
                v-if="huanucoCard"
                class="group/huanuco cursor-pointer"
                filter="url(#glowHuanuco)"
                @click="emit('select-city', huanucoCard.value)"
              >
                <!-- Punto de la sede activa -->
                <circle :cx="CITY_COORDINATES.huanuco.x" :cy="CITY_COORDINATES.huanuco.y" r="6" class="fill-white stroke-primary-600 transition-colors group-hover/huanuco:stroke-primary-400" stroke-width="2" />
                <circle :cx="CITY_COORDINATES.huanuco.x" :cy="CITY_COORDINATES.huanuco.y" r="2.5" class="fill-primary-600" />

                <!-- Badge institucional de Huánuco -->
                <rect
                  :x="CITY_COORDINATES.huanuco.x - 55"
                  :y="CITY_COORDINATES.huanuco.y - 32"
                  width="110"
                  height="22"
                  rx="11"
                  class="fill-secondary-950 stroke-primary-400 shadow-md transition-all group-hover/huanuco:stroke-primary-300 group-hover/huanuco:fill-secondary-900"
                  stroke-width="1.2"
                />
                <text
                  :x="CITY_COORDINATES.huanuco.x"
                  :y="CITY_COORDINATES.huanuco.y - 17"
                  text-anchor="middle"
                  class="fill-white font-sans text-[10px] font-extrabold tracking-wide"
                >
                  📍 HUÁNUCO
                </text>
              </g>
            </svg>
          </div>

          <div class="mt-2 text-center">
            <p class="text-xs font-bold text-slate-900">Región Huánuco destacada</p>
            <p class="mt-0.5 text-[11px] text-slate-500">Haz clic en la tarjeta o en el mapa para acceder a sus locales.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Nivel 2: Selección de locales de la ciudad elegida -->
    <div v-else class="p-4 sm:p-7">
      <div class="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div class="flex items-center gap-3">
          <span class="grid size-11 place-items-center rounded-2xl bg-primary-50 text-primary-600 shadow-sm">
            <Landmark :size="20" aria-hidden="true" />
          </span>
          <div>
            <div class="flex items-center gap-2">
              <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-primary-600">Ciudad seleccionada</p>
              <button
                type="button"
                class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-bold text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                :disabled="disabled"
                @click="emit('select-city', '')"
              >
                <ArrowLeft :size="11" aria-hidden="true" />
                Cambiar ciudad
              </button>
            </div>
            <p class="text-lg font-extrabold text-slate-950">{{ city === '__legacy__' ? 'Registros anteriores' : city }}</p>
          </div>
        </div>

        <BaseButton
          v-if="canEdit"
          size="sm"
          variant="ghost"
          :full-width="false"
          :disabled="disabled"
          @click="emit('create-local')"
        >
          <template #icon><Plus :size="15" aria-hidden="true" /></template>
          Nuevo local
        </BaseButton>
      </div>

      <ul v-if="localCards.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-label="Locales disponibles">
        <li v-for="local in localCards" :key="local.id">
          <button
            type="button"
            class="group flex min-h-36 w-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-md focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:opacity-50 motion-reduce:transform-none"
            :disabled="disabled"
            @click="emit('select-local', local.id)"
          >
            <div>
              <div class="flex w-full items-start justify-between gap-3">
                <span class="grid size-11 shrink-0 place-items-center rounded-xl bg-secondary-950 text-primary-300 shadow-sm">
                  <Building2 :size="20" aria-hidden="true" />
                </span>
                <span class="rounded-full bg-primary-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-primary-700">
                  {{ local.tipoLabel }}
                </span>
              </div>
              <strong class="mt-3 block text-base font-extrabold text-slate-950 group-hover:text-primary-600 transition-colors">
                {{ local.nombre }}
              </strong>
              <span class="mt-0.5 block font-mono text-[11px] font-bold uppercase tracking-wide text-slate-400">
                {{ local.codigo }}
              </span>
              <p v-if="local.descripcion" class="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
                {{ local.descripcion }}
              </p>
            </div>

            <div class="mt-4 flex w-full items-center justify-between border-t border-slate-100 pt-3 text-xs font-semibold text-slate-600">
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
        <p class="mt-3 text-sm font-semibold text-slate-600">Esta ciudad todavía no tiene locales registrados.</p>
        <p class="mt-1 text-xs text-slate-400">Agrega un local para clasificar y organizar sus pabellones.</p>
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

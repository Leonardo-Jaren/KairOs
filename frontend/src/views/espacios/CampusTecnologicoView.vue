<script setup>
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  DoorOpen,
  FlaskConical,
  Layers3,
  MapPin,
  MonitorCog,
  Pencil,
  Plus,
  Presentation,
  Search,
  Trash2,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseTextarea from '@/components/inputs/BaseTextarea.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import { useCampusTecnologico } from '@/composables/espacios/useCampusTecnologico';

const {
  loading, saving, error, search, edificios, selectedBuildingId, edificioActivo,
  pisosVisibles, stats, canEdit, buildingOptions, typeOptions, buildingModalOpen,
  buildingDeleteOpen, pendingBuildingDelete, buildingForm, buildingErrors,
  isEditingBuilding, spaceModalOpen, spaceDeleteOpen, pendingSpaceDelete, spaceForm,
  spaceErrors, isEditingSpace, toast, openCreateBuilding, openEditBuilding,
  closeBuildingModal, submitBuilding, askDeleteBuilding, cancelDeleteBuilding,
  confirmDeleteBuilding, openCreateSpace, openEditSpace, closeSpaceModal, submitSpace,
  askDeleteSpace, cancelDeleteSpace, confirmDeleteSpace, closeToast,
} = useCampusTecnologico();

const floorLabel = (count) => `${count} ${count === 1 ? 'piso' : 'pisos'}`;
const environmentLabel = (count) => `${count} ${count === 1 ? 'ambiente' : 'ambientes'}`;
const iconForType = (type) => ({
  laboratorio: FlaskConical,
  sala_computo: MonitorCog,
  aula: Presentation,
  oficina: DoorOpen,
}[type] ?? MapPin);
</script>

<template>
  <div class="flex flex-col gap-6">
    <header class="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
      <div>
        <p class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Infraestructura del campus</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-slate-950">Campus tecnológico</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">Ubica edificios, pisos y ambientes; desde cada espacio puedes abrir su distribución y trabajar con los equipos.</p>
      </div>
      <BaseButton v-if="canEdit" variant="accent" :full-width="false" @click="openCreateBuilding">
        <template #icon><Plus :size="18" /></template>
        Agregar edificio
      </BaseButton>
    </header>

    <section class="grid overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm sm:grid-cols-3 xl:grid-cols-6">
      <div v-for="metric in [
        ['Edificios', stats.edificios],
        ['Pisos activos', edificios.reduce((total, item) => total + item.pisos.length, 0)],
        ['Ambientes', stats.ambientes],
        ['Laboratorios', stats.laboratorios],
        ['Aulas', stats.aulas],
        ['Por revisar', stats.alertas],
      ]" :key="metric[0]" class="border-b border-slate-100 px-4 py-3 last:border-b-0 sm:border-r sm:last:border-r-0 xl:border-b-0">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">{{ metric[0] }}</p>
        <p class="mt-1 text-xl font-extrabold" :class="metric[0] === 'Por revisar' && metric[1] ? 'text-warning-700' : 'text-slate-900'">{{ metric[1] }}</p>
      </div>
    </section>

    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"><div v-for="item in 7" :key="item" class="h-40 animate-pulse rounded-2xl bg-slate-100" /></div>
    <div v-else-if="error" class="rounded-2xl border border-danger-200 bg-danger-50 p-6 text-sm text-danger-700">{{ error }}</div>
    <template v-else>
      <section>
        <div class="mb-3 flex flex-wrap items-end justify-between gap-3">
          <div><p class="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Selecciona un bloque</p><h2 class="mt-1 text-xl font-extrabold text-slate-950">Edificios del campus</h2></div>
          <p class="text-xs text-slate-400">El diseño se adapta automáticamente a {{ edificios.length }} edificio{{ edificios.length === 1 ? '' : 's' }}</p>
        </div>

        <div v-if="edificios.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          <article v-for="(building, index) in edificios" :key="building.id" class="group relative overflow-hidden rounded-2xl border shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md" :class="String(selectedBuildingId) === String(building.id) ? 'border-primary-400 bg-primary-50 ring-2 ring-primary-100' : 'border-slate-200 bg-white hover:border-primary-200'">
            <button type="button" class="block w-full p-4 text-left" @click="selectedBuildingId = building.id">
              <span class="absolute right-3 top-2 font-mono text-5xl font-black text-slate-100 group-hover:text-primary-100">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="relative grid size-11 place-items-center rounded-xl" :class="String(selectedBuildingId) === String(building.id) ? 'bg-primary-500 text-white' : 'bg-secondary-950 text-primary-300'"><Building2 :size="22" /></span>
              <p class="relative mt-4 truncate text-base font-extrabold text-slate-900">{{ building.nombre }}</p>
              <p class="relative mt-0.5 font-mono text-[10px] font-bold uppercase tracking-wide text-slate-400">{{ building.codigo }}</p>
              <div class="relative mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500"><span>{{ floorLabel(building.pisos.length) }}</span><span>{{ environmentLabel(building.spaces.length) }}</span><span>{{ building.equipos }} equipos</span></div>
              <span v-if="building.alertas" class="relative mt-3 inline-flex items-center gap-1 rounded-full bg-warning-100 px-2 py-1 text-[10px] font-bold text-warning-700"><AlertTriangle :size="12" />{{ building.alertas }} por revisar</span>
            </button>
            <div v-if="canEdit" class="absolute bottom-3 right-3 flex gap-1 rounded-xl border border-slate-200 bg-white/95 p-1 shadow-sm backdrop-blur">
              <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar edificio" @click.stop="openEditBuilding(building)"><Pencil :size="15" /></button>
              <button type="button" class="rounded-lg p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Desactivar edificio" @click.stop="askDeleteBuilding(building)"><Trash2 :size="15" /></button>
            </div>
          </article>
        </div>
        <div v-else class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-14 text-center"><Building2 :size="34" class="mx-auto text-slate-300" /><p class="mt-3 text-sm font-semibold text-slate-600">Aún no hay edificios registrados.</p><BaseButton v-if="canEdit" class="mt-4" variant="accent" :full-width="false" @click="openCreateBuilding">Agregar el primero</BaseButton></div>
      </section>

      <section v-if="edificioActivo" class="grid min-w-0 gap-5 xl:grid-cols-[270px_minmax(0,1fr)]">
        <aside class="h-fit rounded-2xl border border-slate-200 bg-white p-5 shadow-sm xl:sticky xl:top-24">
          <div class="flex items-start justify-between gap-3"><span class="grid size-12 place-items-center rounded-2xl bg-primary-50 text-primary-600"><Building2 :size="24" /></span><button v-if="canEdit" type="button" class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar edificio seleccionado" @click="openEditBuilding(edificioActivo)"><Pencil :size="16" /></button></div>
          <p class="mt-4 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Edificio seleccionado</p>
          <h2 class="mt-1 text-xl font-extrabold text-slate-950">{{ edificioActivo.nombre }}</h2>
          <p v-if="edificioActivo.descripcion" class="mt-2 text-xs leading-5 text-slate-500">{{ edificioActivo.descripcion }}</p>
          <dl class="mt-4 divide-y divide-slate-100">
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><Layers3 :size="16" />Pisos</dt><dd class="font-bold text-slate-800">{{ edificioActivo.pisos.length }}</dd></div>
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><MapPin :size="16" />Ambientes</dt><dd class="font-bold text-slate-800">{{ edificioActivo.spaces.length }}</dd></div>
            <div class="flex items-center justify-between py-3 text-sm"><dt class="flex items-center gap-2 text-slate-500"><MonitorCog :size="16" />Equipos</dt><dd class="font-bold text-slate-800">{{ edificioActivo.equipos }}</dd></div>
          </dl>
          <BaseButton v-if="canEdit" class="mt-4" variant="accent" @click="openCreateSpace()"><template #icon><Plus :size="16" /></template>Agregar ambiente</BaseButton>
        </aside>

        <div class="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div><p class="text-xs font-bold uppercase tracking-[0.18em] text-primary-600">Distribución vertical</p><h2 class="mt-1 text-xl font-extrabold text-slate-950">Pisos y ambientes</h2><p class="mt-1 text-xs text-slate-500">Cada piso puede contener varios laboratorios, aulas u oficinas.</p></div>
            <div class="w-full lg:max-w-xs"><BaseInput id="campus-search" v-model="search" appearance="light" placeholder="Buscar ambiente, tipo o piso"><template #icon><Search :size="16" /></template></BaseInput></div>
          </div>

          <div v-if="pisosVisibles.length" class="mt-6 flex flex-col gap-5">
            <section v-for="floor in pisosVisibles" :key="floor.key" class="overflow-hidden rounded-2xl border border-slate-200">
              <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/80 px-4 py-3">
                <div class="flex items-center gap-3"><span class="grid size-9 place-items-center rounded-xl bg-secondary-950 text-xs font-black text-primary-300">{{ floor.key }}</span><div><h3 class="text-sm font-extrabold text-slate-900">{{ floor.label }}</h3><p class="text-[10px] text-slate-400">{{ environmentLabel(floor.spaces.length) }} · {{ floor.labs }} tecnológicos · {{ floor.aulas }} aulas</p></div></div>
                <BaseButton v-if="canEdit" size="sm" variant="secondary" :full-width="false" @click="openCreateSpace(floor.key)"><template #icon><Plus :size="15" /></template>Agregar aquí</BaseButton>
              </header>
              <div class="grid gap-3 p-3 sm:grid-cols-2 2xl:grid-cols-3">
                <article v-for="space in floor.spaces" :key="space.id" class="group relative rounded-xl border border-slate-200 bg-white p-4 transition-all duration-200 hover:border-primary-300 hover:bg-primary-50/30 hover:shadow-sm">
                  <RouterLink :to="`/espacios/${space.id}`" class="block pr-12">
                    <div class="flex items-start gap-3"><span class="grid size-10 shrink-0 place-items-center rounded-xl bg-secondary-950 text-primary-300"><component :is="iconForType(space.tipo)" :size="19" /></span><div class="min-w-0"><p class="truncate font-mono text-sm font-extrabold text-slate-900">{{ space.codigo_espacio }}</p><p class="mt-0.5 text-xs text-slate-500">{{ space.tipo_display }}</p></div></div>
                    <div class="mt-4 flex items-center justify-between text-xs"><span class="text-slate-400">{{ space.cantidad_equipos }} equipos</span><span class="inline-flex items-center gap-1 font-bold text-primary-600">Abrir <ArrowRight :size="14" /></span></div>
                  </RouterLink>
                  <div v-if="canEdit" class="absolute right-2 top-2 flex gap-0.5 rounded-lg bg-white/95 p-0.5 shadow-sm">
                    <button type="button" class="rounded-md p-1.5 text-slate-400 hover:bg-primary-50 hover:text-primary-600" aria-label="Editar ambiente" @click="openEditSpace(space)"><Pencil :size="14" /></button>
                    <button type="button" class="rounded-md p-1.5 text-slate-400 hover:bg-danger-50 hover:text-danger-600" aria-label="Desactivar ambiente" @click="askDeleteSpace(space)"><Trash2 :size="14" /></button>
                  </div>
                </article>
              </div>
            </section>
          </div>
          <div v-else class="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center"><MapPin :size="30" class="mx-auto text-slate-300" /><p class="mt-3 text-sm font-semibold text-slate-600">{{ search ? 'No hay ambientes que coincidan con la búsqueda.' : 'Este edificio todavía no tiene ambientes.' }}</p><BaseButton v-if="canEdit && !search" class="mt-4" variant="accent" :full-width="false" @click="openCreateSpace()">Agregar ambiente</BaseButton></div>
        </div>
      </section>
    </template>

    <BaseModal :open="buildingModalOpen" :title="isEditingBuilding ? 'Editar edificio' : 'Nuevo edificio'" description="Registra el bloque físico que agrupará pisos y ambientes." @close="closeBuildingModal">
      <form id="building-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submitBuilding">
        <BaseInput id="building-code" v-model="buildingForm.codigo" appearance="light" label="Código" placeholder="EDIF-01" :error="buildingErrors.codigo" />
        <BaseInput id="building-name" v-model="buildingForm.nombre" appearance="light" label="Nombre" placeholder="Edificio 1" :error="buildingErrors.nombre" />
        <div class="sm:col-span-2"><BaseTextarea id="building-description" v-model="buildingForm.descripcion" appearance="light" label="Descripción (opcional)" placeholder="Facultad o referencia de ubicación" :rows="3" /></div>
        <label class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"><input v-model="buildingForm.activo" type="checkbox" class="size-4 accent-primary-500" /><span><span class="block text-sm font-semibold text-slate-800">Edificio activo</span><span class="block text-xs text-slate-500">Permite agregar y consultar sus espacios.</span></span></label>
      </form>
      <template #footer><BaseButton variant="ghost" :full-width="false" @click="closeBuildingModal">Cancelar</BaseButton><BaseButton type="submit" form="building-form" variant="accent" :loading="saving" :full-width="false">{{ isEditingBuilding ? 'Guardar cambios' : 'Crear edificio' }}</BaseButton></template>
    </BaseModal>

    <BaseModal :open="buildingDeleteOpen" title="Desactivar edificio" size="sm" @close="cancelDeleteBuilding">
      <p class="text-sm leading-6 text-slate-600">Se desactivará <strong class="text-slate-900">{{ pendingBuildingDelete?.nombre }}</strong>. Sus ambientes e historial se conservarán y podrán reasignarse.</p>
      <template #footer><BaseButton variant="ghost" :full-width="false" @click="cancelDeleteBuilding">Cancelar</BaseButton><BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDeleteBuilding">Desactivar</BaseButton></template>
    </BaseModal>

    <BaseModal :open="spaceModalOpen" :title="isEditingSpace ? 'Editar ambiente' : 'Nuevo ambiente'" description="Ubícalo en un edificio y piso; luego podrás construir su plano." @close="closeSpaceModal">
      <form id="campus-space-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="submitSpace">
        <BaseInput id="campus-space-code" v-model="spaceForm.codigo_espacio" appearance="light" label="Código" placeholder="LAB-203" :error="spaceErrors.codigo_espacio" />
        <BaseSelect id="campus-space-type" v-model="spaceForm.tipo" label="Tipo" :options="typeOptions" :error="spaceErrors.tipo" />
        <BaseSelect id="campus-space-building" v-model="spaceForm.edificio_id" label="Edificio" :options="buildingOptions" :error="spaceErrors.edificio_id" />
        <BaseInput id="campus-space-floor" v-model="spaceForm.piso" appearance="light" label="Piso" placeholder="2" :error="spaceErrors.piso" />
        <label class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"><input v-model="spaceForm.activo" type="checkbox" class="size-4 accent-primary-500" /><span><span class="block text-sm font-semibold text-slate-800">Ambiente activo</span><span class="block text-xs text-slate-500">Permite asignar equipos y usuarios.</span></span></label>
      </form>
      <template #footer><BaseButton variant="ghost" :full-width="false" @click="closeSpaceModal">Cancelar</BaseButton><BaseButton type="submit" form="campus-space-form" variant="accent" :loading="saving" :full-width="false">{{ isEditingSpace ? 'Guardar cambios' : 'Crear ambiente' }}</BaseButton></template>
    </BaseModal>

    <BaseModal :open="spaceDeleteOpen" title="Desactivar ambiente" size="sm" @close="cancelDeleteSpace">
      <p class="text-sm leading-6 text-slate-600">El ambiente <strong class="text-slate-900">{{ pendingSpaceDelete?.codigo_espacio }}</strong> dejará de estar disponible. Su historial se conservará.</p>
      <template #footer><BaseButton variant="ghost" :full-width="false" @click="cancelDeleteSpace">Cancelar</BaseButton><BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDeleteSpace">Desactivar</BaseButton></template>
    </BaseModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

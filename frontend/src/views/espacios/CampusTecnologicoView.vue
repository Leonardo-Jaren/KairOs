<template>
  <div class="flex flex-col gap-5">
    <header
      class="flex flex-col justify-between gap-4 xl:flex-row xl:items-end"
    >
      <div>
        <p
          class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-primary-600"
        >
          Gestión territorial
        </p>
        <h1
          class="text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl"
        >
          Mapa de infraestructura
        </h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
          Explora cada ciudad y entra en sus locales, pabellones y pisos sin mezclar ubicaciones.
        </p>
      </div>
      <div class="flex gap-2">
        <BaseButton
          v-if="explorerLevel !== 'cities'"
          variant="ghost"
          :full-width="false"
          :disabled="Boolean(editingFloor || floorSaving)"
          @click="goBack"
        ><template #icon><ArrowLeft :size="18" /></template>Volver</BaseButton>
        <button
          v-if="canEdit && explorerLevel === 'buildings' && localActivo"
          type="button"
          class="grid size-11 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:border-primary-300 hover:text-primary-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
          aria-label="Editar local"
          @click="openEditLocal(localActivo)"
        ><Pencil :size="17" /></button>
        <button
          v-if="canEdit && explorerLevel === 'buildings' && localActivo"
          type="button"
          class="grid size-11 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:border-danger-300 hover:text-danger-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-danger-500"
          aria-label="Desactivar local"
          @click="askDeleteLocal(localActivo)"
        ><Trash2 :size="17" /></button>
        <BaseButton
          v-if="canEdit && explorerLevel === 'buildings'"
          variant="accent"
          :full-width="false"
          :disabled="Boolean(editingFloor || floorSaving)"
          @click="openCreateBuilding"
          ><template #icon><Plus :size="18" /></template>Agregar
          pabellón</BaseButton
        >
      </div>
    </header>
    <nav
      class="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-400"
      aria-label="Ubicación actual"
    >
      <button type="button" class="min-h-11 rounded-lg px-2 hover:bg-slate-100 hover:text-primary-700 disabled:pointer-events-none" :disabled="explorerLevel === 'cities'" @click="showCities">Infraestructura</button>
      <template v-if="selectedCity">
        <ChevronRight :size="14" aria-hidden="true" />
        <button type="button" class="min-h-11 rounded-lg px-2 hover:bg-slate-100 hover:text-primary-700 disabled:pointer-events-none disabled:text-slate-700" :disabled="explorerLevel === 'locals'" @click="showLocals">{{ selectedCity === '__legacy__' ? 'Registros anteriores' : selectedCity }}</button>
      </template>
      <template v-if="selectedLocalId">
        <ChevronRight :size="14" aria-hidden="true" />
        <button type="button" class="min-h-11 rounded-lg px-2 hover:bg-slate-100 hover:text-primary-700 disabled:pointer-events-none disabled:text-slate-700" :disabled="explorerLevel === 'buildings'" @click="showBuildings">{{ selectedLocalName }}</button>
      </template>
      <template v-if="selectedBuildingId">
        <ChevronRight :size="14" aria-hidden="true" />
        <button type="button" class="min-h-11 rounded-lg px-2 hover:bg-slate-100 hover:text-primary-700 disabled:pointer-events-none disabled:text-slate-700" :disabled="explorerLevel === 'floors'" @click="showFloors">{{ edificioActivo?.nombre }}</button>
      </template>
      <template v-if="activeFloor">
        <ChevronRight :size="14" aria-hidden="true" />
        <span class="px-2 font-bold text-slate-700" aria-current="page">{{ activeFloor.label }}</span>
      </template>
    </nav>
    <TerritorioSelector
      v-if="!selectedLocalId"
      :city="selectedCity"
      :city-cards="cityCards"
      :local-cards="cityLocalCards"
      :can-edit="canEdit"
      :disabled="Boolean(editingFloor || floorSaving)"
      @select-city="selectCity"
      @select-local="selectLocalCard"
      @create-local="openCreateLocal"
    />
    <div v-if="loading" class="grid gap-3 sm:grid-cols-3">
      <div
        v-for="item in 3"
        :key="item"
        class="h-24 animate-pulse rounded-2xl bg-slate-100"
      />
    </div>
    <div
      v-else-if="error"
      class="rounded-2xl border border-danger-200 bg-danger-50 p-5 text-sm text-danger-700"
    >
      <p>{{ error }}</p>
      <BaseButton
        class="mt-3"
        variant="danger"
        :full-width="false"
        @click="loadCampus"
        >Reintentar</BaseButton
      >
    </div>
    <template v-else>
      <PabellonSelector
        v-if="explorerLevel === 'buildings'"
        :local="localActivo"
        :buildings="edificios"
        :spaces="currentSpaces"
        :selected-id="selectedBuildingId"
        :can-edit="canEdit"
        :disabled="Boolean(editingFloor || floorSaving)"
        @select="selectBuilding"
        @edit="openEditBuilding"
        @delete="askDeleteBuilding"
        @create-building="openCreateBuilding"
        @select-space="goToSpace"
      />
      <section
        v-if="explorerLevel === 'floors' && edificioActivo"
        class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6"
      >
        <div class="mb-6 flex flex-col justify-between gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center">
          <div class="flex items-center gap-4">
            <span class="grid size-12 shrink-0 place-items-center rounded-2xl bg-primary-50 text-primary-600"><Building2 :size="24" aria-hidden="true" /></span>
            <div>
              <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-primary-600">{{ selectedLocalName }}</p>
              <h2 class="mt-1 text-xl font-extrabold text-slate-950">{{ edificioActivo.nombre }}</h2>
              <p class="mt-1 text-xs text-slate-500">{{ edificioActivo.spaces.length }} ambientes distribuidos en {{ edificioActivo.pisos.length }} {{ edificioActivo.pisos.length === 1 ? 'piso' : 'pisos' }}.</p>
            </div>
          </div>
          <BaseButton v-if="canEdit" variant="accent" :full-width="false" @click="openCreateSpace()"><template #icon><Plus :size="16" /></template>Agregar ambiente</BaseButton>
        </div>
        <PisoSelector
          :floors="pisosVisibles"
          :selected-key="activeFloorKey"
          :disabled="Boolean(editingFloor)"
          @select="selectFloor"
        />
      </section>
      <section
        v-else-if="explorerLevel === 'floor-plan' && edificioActivo"
        class="grid min-w-0 gap-5 xl:grid-cols-[270px_minmax(0,1fr)]"
      >
        <aside
          class="hidden h-fit rounded-2xl border border-slate-200 bg-white p-5 shadow-sm xl:sticky xl:top-24 xl:block"
        >
          <span
            class="grid size-12 place-items-center rounded-2xl bg-primary-50 text-primary-600"
            ><Building2 :size="24"
          /></span>
          <p
            class="mt-4 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400"
          >
            Pabellón seleccionado
          </p>
          <h2 class="mt-1 text-xl font-extrabold text-slate-950">
            {{ edificioActivo.nombre }}
          </h2>
          <p
            v-if="edificioActivo.descripcion"
            class="mt-2 text-xs leading-5 text-slate-500"
          >
            {{ edificioActivo.descripcion }}
          </p>
          <dl class="mt-4 divide-y divide-slate-100">
            <div class="flex items-center justify-between py-3 text-sm">
              <dt class="flex items-center gap-2 text-slate-500">
                <Layers3 :size="16" />Pisos
              </dt>
              <dd class="font-bold text-slate-800">
                {{ edificioActivo.pisos.length }}
              </dd>
            </div>
            <div class="flex items-center justify-between py-3 text-sm">
              <dt class="flex items-center gap-2 text-slate-500">
                <MapPin :size="16" />Ambientes
              </dt>
              <dd class="font-bold text-slate-800">
                {{ edificioActivo.spaces.length }}
              </dd>
            </div>
            <div class="flex items-center justify-between py-3 text-sm">
              <dt class="flex items-center gap-2 text-slate-500">
                <MonitorCog :size="16" />Equipos
              </dt>
              <dd class="font-bold text-slate-800">
                {{ edificioActivo.equipos }}
              </dd>
            </div>
          </dl>
          <BaseButton
            v-if="canEdit"
            class="mt-4"
            variant="accent"
            @click="openCreateSpace()"
            ><template #icon><Plus :size="16" /></template>Agregar
            ambiente</BaseButton
          >
        </aside>
        <div
          class="min-w-0 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm sm:p-6"
        >
          <div
            class="flex flex-col justify-between gap-3 lg:flex-row lg:items-end"
          >
            <div class="flex items-end justify-between gap-3">
              <div>
                <p
                  class="text-[10px] font-bold uppercase tracking-[0.18em] text-primary-600 sm:text-xs"
                >
                  {{ edificioActivo.nombre }}
                </p>
                <div class="mt-1 flex flex-wrap items-center gap-3">
                  <h2 class="text-lg font-extrabold text-slate-950 sm:text-xl">
                    Pisos y ambientes
                  </h2>
                  <span v-if="activeFloor" class="rounded-full bg-primary-50 px-3 py-1 text-xs font-bold text-primary-700">{{ activeFloor.label }}</span>
                </div>
                <p class="mt-1 hidden text-xs text-slate-500 sm:block">
                  Navega entre pisos para consultar o editar su distribución.
                </p>
              </div>
              <BaseButton
                v-if="canEdit"
                class="xl:hidden"
                size="sm"
                variant="accent"
                :full-width="false"
                @click="openCreateSpace(activeFloor?.key)"
                ><template #icon><Plus :size="15" /></template
                >Ambiente</BaseButton
              >
            </div>
            <div
              class="sticky top-20 z-10 -mx-3 border-y border-slate-100 bg-white/95 px-3 py-3 backdrop-blur lg:static lg:mx-0 lg:w-full lg:max-w-xs lg:border-0 lg:bg-transparent lg:p-0"
            >
              <BaseInput
                id="campus-search"
                v-model="search"
                appearance="light"
                placeholder="Buscar ambiente, tipo o piso"
                ><template #icon><Search :size="16" /></template
              ></BaseInput>
            </div>
          </div>
          <div class="mt-3 sm:mt-6">
            <CroquisPiso
              :key="activeFloor.key"
              :floor="activeFloor"
              :editing="editingFloor === activeFloor.key"
              :can-edit="
                canEdit && (!editingFloor || editingFloor === activeFloor.key)
              "
              :saving="floorSaving"
              :selected-space-id="selectedFloorSpaceId"
              :tool="floorTool"
              :context-query="route.query"
              @start-edit="startFloorEditing(activeFloor)"
              @save="saveFloorLayout"
              @cancel="cancelFloorEditing"
              @select-space="selectFloorSpace"
              @cell-click="handleFloorCell"
              @set-tool="setFloorTool"
              @resize="resizeSelectedFloorSpace"
              @update-columns="updateFloorColumns"
              @add-row="addFloorRow"
              @remove-row="removeFloorRow"
              @create-space="openCreateSpace(activeFloor.key)"
              @edit-space="openEditSpace"
              @delete-space="askDeleteSpace"
            />
          </div>
        </div>
      </section>
    </template>

    <BaseModal
      :open="localModalOpen"
      :title="isEditingLocal ? 'Editar local' : 'Nuevo local'"
      description="Registra una sede territorial para organizar sus pabellones."
      @close="closeLocalModal"
      ><form
        id="local-form"
        class="grid gap-4 sm:grid-cols-2"
        @submit.prevent="submitLocal"
      >
        <BaseInput
          id="local-code"
          v-model="localForm.codigo"
          appearance="light"
          label="Código"
          placeholder="LOC-01"
          :error="localErrors.codigo"
        /><BaseInput
          id="local-name"
          v-model="localForm.nombre"
          appearance="light"
          label="Nombre"
          placeholder="Local central"
          :error="localErrors.nombre"
        /><BaseInput
          id="local-city"
          v-model="localForm.ciudad"
          appearance="light"
          label="Ciudad"
          placeholder="Huánuco"
          :error="localErrors.ciudad"
        />
        <BaseSelect
          id="local-type"
          v-model="localForm.tipo"
          label="Tipo de ubicación"
          :options="[
            { value: 'campus', label: 'Campus' },
            { value: 'sede', label: 'Sede' },
            { value: 'anexo', label: 'Anexo' },
            { value: 'otro', label: 'Otro' },
          ]"
          :error="localErrors.tipo"
        />
        <div class="sm:col-span-2">
          <BaseTextarea
            id="local-description"
            v-model="localForm.descripcion"
            appearance="light"
            label="Descripción (opcional)"
            :rows="3"
          />
        </div>
        <label
          class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
          ><input
            v-model="localForm.activo"
            type="checkbox"
            class="size-4 accent-primary-500"
          /><span
            ><span class="block text-sm font-semibold text-slate-800"
              >Local activo</span
            ><span class="block text-xs text-slate-500"
              >Permite organizar nuevos pabellones.</span
            ></span
          ></label
        >
      </form>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="closeLocalModal"
          >Cancelar</BaseButton
        ><BaseButton
          type="submit"
          form="local-form"
          variant="accent"
          :loading="saving"
          :full-width="false"
          >{{ isEditingLocal ? "Guardar cambios" : "Crear local" }}</BaseButton
        ></template
      ></BaseModal
    >
    <BaseModal
      :open="localDeleteOpen"
      title="Desactivar local"
      size="sm"
      @close="cancelDeleteLocal"
      ><p class="text-sm leading-6 text-slate-600">
        Se desactivará
        <strong class="text-slate-900">{{ pendingLocalDelete?.nombre }}</strong
        >. Primero debes reasignar o retirar todos sus pabellones. El historial se conservará.
      </p>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="cancelDeleteLocal"
          >Cancelar</BaseButton
        ><BaseButton
          variant="danger"
          :loading="saving"
          :full-width="false"
          @click="confirmDeleteLocal"
          >Desactivar</BaseButton
        ></template
      ></BaseModal
    >
    <BaseModal
      :open="buildingModalOpen"
      :title="isEditingBuilding ? 'Editar pabellón' : 'Nuevo pabellón'"
      description="Registra el bloque físico que agrupará pisos y ambientes."
      @close="closeBuildingModal"
      ><form
        id="building-form"
        class="grid gap-4 sm:grid-cols-2"
        @submit.prevent="submitBuilding"
      >
        <BaseInput
          id="building-code"
          v-model="buildingForm.codigo"
          appearance="light"
          label="Código"
          placeholder="PAB-01"
          :error="buildingErrors.codigo"
        /><BaseInput
          id="building-name"
          v-model="buildingForm.nombre"
          appearance="light"
          label="Nombre"
          placeholder="Pabellón principal"
          :error="buildingErrors.nombre"
        />
        <div class="sm:col-span-2">
          <BaseSelect
            id="building-local"
            v-model="buildingForm.local_id"
            label="Local"
            :options="allLocalOptions"
            placeholder="Sin local asignado"
            :error="buildingErrors.local_id"
          />
        </div>
        <div class="sm:col-span-2">
          <BaseTextarea
            id="building-description"
            v-model="buildingForm.descripcion"
            appearance="light"
            label="Descripción (opcional)"
            :rows="3"
          />
        </div>
        <label
          class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
          ><input
            v-model="buildingForm.activo"
            type="checkbox"
            class="size-4 accent-primary-500"
          /><span
            ><span class="block text-sm font-semibold text-slate-800"
              >Pabellón activo</span
            ><span class="block text-xs text-slate-500"
              >Permite consultar y organizar sus ambientes.</span
            ></span
          ></label
        >
      </form>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="closeBuildingModal"
          >Cancelar</BaseButton
        ><BaseButton
          type="submit"
          form="building-form"
          variant="accent"
          :loading="saving"
          :full-width="false"
          >{{
            isEditingBuilding ? "Guardar cambios" : "Crear pabellón"
          }}</BaseButton
        ></template
      ></BaseModal
    >
    <BaseModal
      :open="buildingDeleteOpen"
      title="Desactivar pabellón"
      size="sm"
      @close="cancelDeleteBuilding"
      ><p class="text-sm leading-6 text-slate-600">
        Se desactivará
        <strong class="text-slate-900">{{
          pendingBuildingDelete?.nombre
        }}</strong
        >. Sus ambientes e historial se conservarán.
      </p>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="cancelDeleteBuilding"
          >Cancelar</BaseButton
        ><BaseButton
          variant="danger"
          :loading="saving"
          :full-width="false"
          @click="confirmDeleteBuilding"
          >Desactivar</BaseButton
        ></template
      ></BaseModal
    >
    <BaseModal
      :open="spaceModalOpen"
      :title="isEditingSpace ? 'Editar ambiente' : 'Nuevo ambiente'"
      description="Ubícalo en un pabellón y piso; luego podrás construir su plano."
      @close="closeSpaceModal"
      ><form
        id="campus-space-form"
        class="grid gap-4 sm:grid-cols-2"
        @submit.prevent="submitSpace"
      >
        <BaseInput
          id="campus-space-code"
          v-model="spaceForm.codigo_espacio"
          appearance="light"
          label="Código"
          placeholder="LAB-203"
          :error="spaceErrors.codigo_espacio"
        /><BaseSelect
          id="campus-space-type"
          v-model="spaceForm.tipo"
          label="Tipo"
          :options="typeOptions"
          :error="spaceErrors.tipo"
        /><BaseSelect
          id="campus-space-building"
          v-model="spaceForm.edificio_id"
          label="Pabellón"
          :options="buildingOptions"
          :error="spaceErrors.edificio_id"
        /><BaseInput
          id="campus-space-floor"
          v-model="spaceForm.piso"
          appearance="light"
          type="number"
          label="Número de piso"
          placeholder="Ej. 2"
          :error="spaceErrors.piso"
        /><label
          class="sm:col-span-2 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
          ><input
            v-model="spaceForm.activo"
            type="checkbox"
            class="size-4 accent-primary-500"
          /><span
            ><span class="block text-sm font-semibold text-slate-800"
              >Ambiente activo</span
            ><span class="block text-xs text-slate-500"
              >Permite asignar equipos y usuarios.</span
            ></span
          ></label
        >
      </form>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="closeSpaceModal"
          >Cancelar</BaseButton
        ><BaseButton
          type="submit"
          form="campus-space-form"
          variant="accent"
          :loading="saving"
          :full-width="false"
          >{{
            isEditingSpace ? "Guardar cambios" : "Crear ambiente"
          }}</BaseButton
        ></template
      ></BaseModal
    >
    <BaseModal
      :open="spaceDeleteOpen"
      title="Desactivar ambiente"
      size="sm"
      @close="cancelDeleteSpace"
      ><p class="text-sm leading-6 text-slate-600">
        El ambiente
        <strong class="text-slate-900">{{
          pendingSpaceDelete?.codigo_espacio
        }}</strong>
        dejará de estar disponible.
      </p>
      <template #footer
        ><BaseButton
          variant="ghost"
          :full-width="false"
          @click="cancelDeleteSpace"
          >Cancelar</BaseButton
        ><BaseButton
          variant="danger"
          :loading="saving"
          :full-width="false"
          @click="confirmDeleteSpace"
          >Desactivar</BaseButton
        ></template
      ></BaseModal
    >
    <BaseToast
      :show="toast.show"
      :message="toast.message"
      :type="toast.type"
      @close="closeToast"
    />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeft,
  Building2,
  ChevronRight,
  Layers3,
  MapPin,
  MonitorCog,
  Pencil,
  Plus,
  Search,
  Trash2,
} from "@lucide/vue";
import BaseButton from "@/components/buttons/BaseButton.vue";
import CroquisPiso from "@/components/espacios/CroquisPiso.vue";
import PabellonSelector from "@/components/espacios/PabellonSelector.vue";
import PisoSelector from "@/components/espacios/PisoSelector.vue";
import TerritorioSelector from "@/components/espacios/TerritorioSelector.vue";
import BaseInput from "@/components/inputs/BaseInput.vue";
import BaseTextarea from "@/components/inputs/BaseTextarea.vue";
import BaseModal from "@/components/modals/BaseModal.vue";
import BaseSelect from "@/components/selects/BaseSelect.vue";
import BaseToast from "@/components/toasts/BaseToast.vue";
import edificiosService from "@/services/edificios.service";
import espaciosService from "@/services/espacios.service";
import localesService from "@/services/locales.service";
import { useCampusTecnologico } from "@/composables/espacios/useCampusTecnologico";

const route = useRoute();
const router = useRouter();
const state = useCampusTecnologico(
  espaciosService,
  edificiosService,
  localesService,
  { route, router },
);
const {
  loading,
  saving,
  error,
  search,
  cityCards,
  cityLocalCards,
  selectedCity,
  allLocalOptions,
  localActivo,
  selectedLocalId,
  selectedLocalName,
  edificios,
  currentSpaces,
  selectedBuildingId,
  edificioActivo,
  pisosVisibles,
  activeFloor,
  activeFloorKey,
  stats,
  explorerLevel,
  canEdit,
  buildingOptions,
  typeOptions,
  localModalOpen,
  localDeleteOpen,
  pendingLocalDelete,
  localForm,
  localErrors,
  isEditingLocal,
  buildingModalOpen,
  buildingDeleteOpen,
  pendingBuildingDelete,
  buildingForm,
  buildingErrors,
  isEditingBuilding,
  spaceModalOpen,
  spaceDeleteOpen,
  pendingSpaceDelete,
  spaceForm,
  spaceErrors,
  isEditingSpace,
  toast,
  loadCampus,
  selectCity,
  selectLocalCard,
  selectBuilding,
  openCreateLocal,
  openEditLocal,
  closeLocalModal,
  submitLocal,
  askDeleteLocal,
  cancelDeleteLocal,
  confirmDeleteLocal,
  openCreateBuilding,
  openEditBuilding,
  closeBuildingModal,
  submitBuilding,
  askDeleteBuilding,
  cancelDeleteBuilding,
  confirmDeleteBuilding,
  openCreateSpace,
  openEditSpace,
  closeSpaceModal,
  submitSpace,
  askDeleteSpace,
  cancelDeleteSpace,
  confirmDeleteSpace,
  closeToast,
  editingFloor,
  floorTool,
  selectedFloorSpaceId,
  floorSaving,
  startFloorEditing,
  cancelFloorEditing,
  selectFloorSpace,
  handleFloorCell,
  setFloorTool,
  resizeSelectedFloorSpace,
  updateFloorColumns,
  addFloorRow,
  removeFloorRow,
  saveFloorLayout,
  selectFloor,
  showCities,
  showLocals,
  showBuildings,
  showFloors,
  goBack,
} = state;

const goToSpace = (space) => {
  const buildingId = space?.edificio_id ?? space?.edificio?.id;
  if (buildingId) {
    selectBuilding(buildingId);
    if (space.piso) {
      selectFloor(space.piso);
    }
  }
};
</script>

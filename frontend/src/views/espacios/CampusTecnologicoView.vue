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
          Selecciona una ciudad y un local para consultar sus pabellones, pisos
          y ambientes.
        </p>
      </div>
      <div class="flex gap-2">
        <BaseButton
          v-if="canEdit"
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
      <span>Infraestructura</span><ChevronRight :size="14" /><span>{{
        selectedCity === "__legacy__"
          ? "Registros anteriores"
          : selectedCity || "Sin ciudad"
      }}</span
      ><ChevronRight :size="14" /><span>{{
        selectedLocalName || "Selecciona un local"
      }}</span
      ><ChevronRight :size="14" /><span class="text-slate-700">{{
        edificioActivo?.nombre || "Selecciona un pabellón"
      }}</span>
    </nav>
    <TerritorioSelector
      :city="selectedCity"
      :city-options="cityOptions"
      :local="selectedLocalId"
      :local-options="localOptions"
      :local-is-real="Boolean(localActivo)"
      :can-edit="canEdit"
      :disabled="Boolean(editingFloor || floorSaving)"
      @update:city="selectCity"
      @update:local="selectLocal"
      @create-local="openCreateLocal"
      @edit-local="openEditLocal(localActivo)"
      @delete-local="askDeleteLocal(localActivo)"
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
      <section
        class="grid grid-cols-3 gap-2 sm:grid-cols-6 sm:gap-0 sm:overflow-hidden sm:rounded-2xl sm:border sm:border-slate-200 sm:bg-white sm:shadow-sm"
      >
        <div
          v-for="metric in [
            ['Pabellones', stats.edificios],
            ['Pisos activos', stats.pisos],
            ['Ambientes', stats.ambientes],
            ['Laboratorios', stats.laboratorios],
            ['Aulas', stats.aulas],
            ['Por revisar', stats.alertas],
          ]"
          :key="metric[0]"
          class="min-w-0 rounded-xl border border-slate-200 bg-white px-3 py-2.5 shadow-sm sm:rounded-none sm:border-0 sm:border-r sm:border-slate-100 sm:px-4 sm:py-3 sm:shadow-none sm:last:border-r-0"
        >
          <p
            class="truncate text-[9px] font-bold uppercase tracking-wide text-slate-400 sm:text-[10px]"
          >
            {{ metric[0] }}
          </p>
          <p
            class="mt-0.5 text-lg font-extrabold sm:mt-1 sm:text-xl"
            :class="
              metric[0] === 'Por revisar' && metric[1]
                ? 'text-warning-700'
                : 'text-slate-900'
            "
          >
            {{ metric[1] }}
          </p>
        </div>
      </section>
      <PabellonSelector
        :buildings="edificios"
        :selected-id="selectedBuildingId"
        :can-edit="canEdit"
        :disabled="Boolean(editingFloor || floorSaving)"
        @select="selectBuilding"
        @edit="openEditBuilding"
        @delete="askDeleteBuilding"
      />
      <section
        v-if="edificioActivo"
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
                  <div
                    v-if="activeFloor"
                    class="inline-flex items-center rounded-xl border border-slate-200 bg-slate-50 p-1 shadow-sm"
                  >
                    <button
                      type="button"
                      class="grid size-8 place-items-center rounded-lg text-slate-500 transition-colors hover:bg-white hover:text-primary-600 disabled:cursor-not-allowed disabled:opacity-35"
                      :disabled="activeFloorIndex <= 0 || Boolean(editingFloor)"
                      aria-label="Piso anterior"
                      @click="showPreviousFloor"
                    >
                      <ChevronLeft :size="17" />
                    </button>
                    <div class="min-w-24 px-2 text-center">
                      <p class="text-xs font-extrabold text-slate-800">
                        {{ activeFloor.label }}
                      </p>
                      <p class="text-[9px] font-semibold text-slate-400">
                        {{ activeFloorIndex + 1 }} de {{ pisosVisibles.length }}
                      </p>
                    </div>
                    <button
                      type="button"
                      class="grid size-8 place-items-center rounded-lg text-slate-500 transition-colors hover:bg-white hover:text-primary-600 disabled:cursor-not-allowed disabled:opacity-35"
                      :disabled="
                        activeFloorIndex >= pisosVisibles.length - 1 ||
                        Boolean(editingFloor)
                      "
                      aria-label="Piso siguiente"
                      @click="showNextFloor"
                    >
                      <ChevronRight :size="17" />
                    </button>
                  </div>
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
          <div v-if="activeFloor" class="mt-3 sm:mt-6">
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
          <div
            v-else
            class="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center"
          >
            <MapPin :size="30" class="mx-auto text-slate-300" />
            <p class="mt-3 text-sm font-semibold text-slate-600">
              {{
                search
                  ? "No hay ambientes que coincidan con la búsqueda."
                  : "Este pabellón todavía no tiene ambientes."
              }}
            </p>
            <BaseButton
              v-if="canEdit && !search"
              class="mt-4"
              variant="accent"
              :full-width="false"
              @click="openCreateSpace()"
              >Agregar ambiente</BaseButton
            >
          </div>
        </div>
      </section>
      <div
        v-else
        class="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center"
      >
        <Building2 :size="32" class="mx-auto text-slate-300" />
        <p class="mt-3 text-sm font-semibold text-slate-600">
          Selecciona un pabellón para ver pisos y ambientes.
        </p>
      </div>
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
  Building2,
  ChevronLeft,
  ChevronRight,
  Layers3,
  MapPin,
  MonitorCog,
  Plus,
  Search,
} from "@lucide/vue";
import BaseButton from "@/components/buttons/BaseButton.vue";
import CroquisPiso from "@/components/espacios/CroquisPiso.vue";
import PabellonSelector from "@/components/espacios/PabellonSelector.vue";
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
  cityOptions,
  selectedCity,
  localOptions,
  allLocalOptions,
  localActivo,
  selectedLocalId,
  selectedLocalName,
  edificios,
  selectedBuildingId,
  edificioActivo,
  pisosVisibles,
  activeFloor,
  activeFloorIndex,
  stats,
  canEdit,
  buildingOptions,
  typeOptions,
  localModalOpen,
  localDeleteOpen,
  editingLocal,
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
  selectLocal,
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
  showPreviousFloor,
  showNextFloor,
} = state;
</script>

<template>
  <div
    data-testid="org-chart"
    class="relative h-[min(740px,calc(100svh-7rem))] min-h-[620px] w-full select-none overflow-hidden rounded-2xl border border-slate-200 bg-slate-50/70 touch-none md:h-[740px] md:rounded-3xl"
    :class="isDragging ? 'cursor-grabbing' : 'cursor-grab'"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
    @wheel.prevent="onWheel"
    @touchstart="onTouchStart"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
    @touchcancel="onTouchEnd"
    @click.capture="handleClickCapture"
  >
    <!-- Fondo decorativo tipo lienzo con cuadricula sutil -->
    <div
      class="absolute inset-0 pointer-events-none opacity-40"
      style="background-image: radial-gradient(#94a3b8 1px, transparent 1px); background-size: 24px 24px;"
    />

    <!-- Herramientas del organigrama distribuidas en grupos estables para cada ancho -->
    <div class="absolute inset-x-3 top-3 z-20 flex flex-col gap-2 md:inset-x-4 md:top-4 min-[1360px]:flex-row min-[1360px]:items-center min-[1360px]:justify-between">
      <div class="flex min-w-0 flex-col gap-2 min-[1360px]:flex-row min-[1360px]:items-center">
        <!-- Indicador de sede -->
        <div
          v-if="sedeInfo"
          class="flex min-h-10 min-w-0 items-center gap-1.5 self-start rounded-xl border border-slate-200/80 bg-white/95 px-3 py-1.5 shadow-2xs backdrop-blur-md min-[1360px]:self-auto"
        >
          <MapPin :size="14" class="text-primary-600" />
          <span class="truncate text-xs font-bold text-slate-800">{{ sedeInfo.nombre }}</span>
          <span class="hidden text-[11px] font-mono text-slate-400 sm:inline">({{ sedeInfo.ciudad }})</span>
        </div>

        <!-- Selector de vistas: cuatro opciones del mismo ancho, sin desplazamiento horizontal -->
        <div class="grid w-full grid-cols-4 gap-1 rounded-xl border border-slate-200/80 bg-white/95 p-1 shadow-2xs backdrop-blur-md md:flex md:w-fit md:items-center">
        <button
          type="button"
          class="flex min-h-11 min-w-0 items-center justify-center gap-1 rounded-lg px-1.5 text-[10px] font-semibold transition-all sm:text-xs md:min-h-9 md:px-2.5"
          :class="
            activeView === 'mando'
              ? 'bg-primary-600 text-white shadow-2xs'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          "
          title="Ver linea de mando jerarquica (arbol activo)"
          @click="selectView('mando')"
        >
          <Network :size="13" />
          <span class="truncate sm:hidden">Mando</span>
          <span class="hidden truncate sm:inline">Línea de mando</span>
          <span
            class="hidden rounded-full px-1.5 py-0.5 text-[10px] font-bold min-[420px]:inline-flex"
            :class="activeView === 'mando' ? 'bg-primary-700/80 text-white' : 'bg-slate-200 text-slate-700'"
          >
            {{ effectiveMeta.total_mando ?? totalNodos }}
          </span>
        </button>

        <button
          type="button"
          class="flex min-h-11 min-w-0 items-center justify-center gap-1 rounded-lg px-1.5 text-[10px] font-semibold transition-all sm:text-xs md:min-h-9 md:px-2.5"
          :class="
            isDockOpen && currentDockTab === 'sin_supervisor'
              ? 'bg-amber-100 text-amber-900 ring-1 ring-amber-300'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          "
          title="Ver personal huerfano y asignar supervisor directo"
          @click="handleOpenDock('sin_supervisor')"
        >
          <AlertCircle
            :size="13"
            :class="effectiveMeta.total_sin_supervisor > 0 ? 'text-amber-500' : 'text-slate-400'"
          />
          <span class="truncate sm:hidden">Pendientes</span>
          <span class="hidden truncate sm:inline">Sin supervisor</span>
          <span
            class="hidden rounded-full px-1.5 py-0.5 text-[10px] font-bold min-[420px]:inline-flex"
            :class="
              effectiveMeta.total_sin_supervisor > 0
                ? 'bg-amber-500 text-white'
                : 'bg-slate-200 text-slate-700'
            "
          >
            {{ effectiveMeta.total_sin_supervisor }}
          </span>
        </button>

        <button
          type="button"
          class="flex min-h-11 min-w-0 items-center justify-center gap-1 rounded-lg px-1.5 text-[10px] font-semibold transition-all sm:text-xs md:min-h-9 md:px-2.5"
          :class="
            isDockOpen && currentDockTab === 'docentes'
              ? 'bg-sky-100 text-sky-900 ring-1 ring-sky-300'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          "
          title="Ver claustro docente independiente"
          @click="handleOpenDock('docentes')"
        >
          <GraduationCap :size="13" class="text-sky-600" />
          <span class="truncate">Docentes</span>
          <span class="hidden rounded-full bg-sky-100 px-1.5 py-0.5 text-[10px] font-bold text-sky-800 min-[420px]:inline-flex">
            {{ effectiveMeta.total_docentes }}
          </span>
        </button>

        <button
          type="button"
          class="flex min-h-11 min-w-0 items-center justify-center gap-1 rounded-lg px-1.5 text-[10px] font-semibold transition-all sm:text-xs md:min-h-9 md:px-2.5"
          :class="
            activeView === 'todos'
              ? 'bg-slate-800 text-white shadow-2xs'
              : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          "
          title="Ver todos los nodos en lienzo panoramico completo"
          @click="selectView('todos')"
        >
          <Globe :size="13" />
          <span class="truncate">Todos</span>
          <span
            class="hidden rounded-full px-1.5 py-0.5 text-[10px] font-bold min-[420px]:inline-flex"
            :class="activeView === 'todos' ? 'bg-slate-700 text-white' : 'bg-slate-200 text-slate-700'"
          >
            {{ effectiveMeta.total ?? totalNodos }}
          </span>
        </button>
        </div>
      </div>

      <!-- Acciones del lienzo: zoom separado y cuatro acciones principales equivalentes -->
      <div class="flex min-h-12 w-full items-center gap-1 rounded-xl border border-slate-200/80 bg-white/95 p-1 shadow-sm backdrop-blur-md md:w-fit md:self-end md:px-1.5 min-[1360px]:self-auto">
        <div class="hidden shrink-0 items-center gap-0.5 border-r border-slate-200 pr-1 md:flex">
          <button type="button" class="grid size-10 place-items-center rounded-lg text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900" title="Acercar (+)" aria-label="Acercar organigrama" @click="zoomIn">
            <ZoomIn :size="17" />
          </button>
          <button type="button" class="grid size-10 place-items-center rounded-lg text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900" title="Alejar (-)" aria-label="Alejar organigrama" @click="zoomOut">
            <ZoomOut :size="17" />
          </button>
          <button type="button" class="hidden min-h-10 rounded-lg px-2 font-mono text-[11px] font-bold text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 min-[1450px]:block" title="Restablecer vista" @click="resetView">
            {{ Math.round(zoom * 100) }}%
          </button>
        </div>

        <div class="grid min-w-0 flex-1 grid-cols-4 gap-1 md:flex md:flex-none">
          <button type="button" class="flex min-h-10 min-w-0 items-center justify-center gap-1 rounded-lg px-1 text-[10px] font-semibold text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 sm:text-xs md:min-h-9 md:px-2.5" title="Expandir todas las ramas" @click="expandAll">
            <Maximize2 :size="14" />
            <span class="truncate">Expandir</span>
          </button>
          <button type="button" class="flex min-h-10 min-w-0 items-center justify-center gap-1 rounded-lg px-1 text-[10px] font-semibold text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 sm:text-xs md:min-h-9 md:px-2.5" title="Colapsar ramas secundarias" @click="collapseAll">
            <Minimize2 :size="14" />
            <span class="truncate">Contraer</span>
          </button>
          <button type="button" class="flex min-h-10 min-w-0 items-center justify-center gap-1 rounded-lg px-1 text-[10px] font-semibold text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 disabled:opacity-50 sm:text-xs md:min-h-9 md:px-2.5" :disabled="isExporting" title="Exportar organigrama como imagen PNG en alta resolución" @click="exportToPng">
            <Loader2 v-if="isExporting" :size="14" class="animate-spin text-primary-600" />
            <Download v-else :size="14" />
            <span class="truncate">{{ isExporting ? 'Procesando' : 'PNG' }}</span>
          </button>
          <button
            type="button"
            class="relative flex min-h-10 min-w-0 items-center justify-center gap-1 rounded-lg px-1 text-[10px] font-semibold transition-colors sm:text-xs md:min-h-9 md:px-2.5"
            :class="isDockOpen ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-200' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'"
            title="Alternar panel lateral de accion rapida"
            @click="toggleDock"
          >
            <PanelRightClose v-if="isDockOpen" :size="14" />
            <PanelRightOpen v-else :size="14" />
            <span class="truncate">Panel</span>
            <span v-if="effectiveMeta.total_sin_supervisor > 0" class="hidden size-4 items-center justify-center rounded-full bg-amber-500 text-[10px] font-bold text-white min-[420px]:flex">
              {{ effectiveMeta.total_sin_supervisor }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Indicador de ayuda al usuario para arrastre -->
    <div class="pointer-events-none absolute bottom-4 left-4 z-20 hidden rounded-xl bg-slate-900/60 px-3 py-1 text-[11px] font-medium text-white/90 backdrop-blur-xs md:block">
      Arrastra el lienzo para mover · Clic en un usuario para ver detalles
    </div>

    <!-- Estado de carga -->
    <div v-if="loading" class="absolute inset-0 z-30 flex flex-col items-center justify-center bg-white/75 backdrop-blur-xs">
      <div class="size-9 animate-spin rounded-full border-3 border-primary-200 border-t-primary-600" />
      <p class="mt-3 text-sm font-semibold text-slate-700">Cargando jerarquia del organigrama...</p>
    </div>

    <!-- Estado vacio -->
    <div v-else-if="!displayNodes || displayNodes.length === 0" class="absolute inset-0 z-10 flex flex-col items-center justify-center p-8 text-center">
      <div class="grid size-16 place-items-center rounded-2xl bg-slate-100 text-slate-400 mb-4">
        <Users :size="28" />
      </div>
      <h3 class="text-base font-bold text-slate-900">No hay usuarios en esta vista</h3>
      <p class="mt-1 max-w-sm text-xs text-slate-500">
        No se encontraron cuentas activas o con asignacion para la sede seleccionada.
      </p>
    </div>

    <!-- Capa transformable que recibe Zoom y Paneo -->
    <div
      v-else
      ref="treeCanvasRef"
      data-testid="org-chart-canvas"
      class="absolute min-w-full origin-top-left px-8 pb-16 md:px-16"
      :class="[
        isDragging ? 'transition-none' : 'transition-transform duration-100 ease-out',
        sedeInfo ? 'pt-52' : 'pt-40',
      ]"
      :style="canvasStyle"
    >
      <!-- Disposicion para vista 'Todos': arboles jerarquicos arriba y colaboradores en columnas balanceadas -->
      <div
        v-if="activeView === 'todos'"
        class="mx-auto flex w-full max-w-7xl flex-col items-center gap-8 md:min-w-max md:gap-10"
      >
        <!-- Cadenas de mando / Arboles jerarquicos con subordinados -->
        <div
          v-if="arbolesJerarquicos.length > 0"
          class="flex w-full flex-row flex-wrap items-start justify-center gap-8 md:gap-12"
        >
          <OrgChartNode
            v-for="rootNode in arbolesJerarquicos"
            :key="rootNode.id"
            :node="rootNode"
            :collapsed-set="collapsedNodes"
            :selected-id="selectedId"
            @select="$emit('select', $event)"
            @toggle-collapse="toggleCollapse"
            @manage-permisos="$emit('manage-permisos', $event)"
          />
        </div>

        <!-- Separador de colaboradores independientes cuando conviven con arboles -->
        <div
          v-if="arbolesJerarquicos.length > 0 && nodosIndependientes.length > 0"
          class="w-full flex items-center gap-3 my-2"
        >
          <div class="h-px flex-1 bg-slate-300/80" />
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider bg-white/90 px-3 py-1 rounded-full border border-slate-200 shadow-2xs backdrop-blur-xs">
            Colaboradores Independientes ({{ nodosIndependientes.length }})
          </span>
          <div class="h-px flex-1 bg-slate-300/80" />
        </div>

        <!-- Cuadricula en columnas para colaboradores independientes -->
        <div
          v-if="nodosIndependientes.length > 0"
          class="grid w-full grid-cols-1 justify-items-center gap-5 md:grid-cols-2 md:gap-8 lg:grid-cols-3 xl:grid-cols-4"
        >
          <OrgChartNode
            v-for="rootNode in nodosIndependientes"
            :key="rootNode.id"
            :node="rootNode"
            :collapsed-set="collapsedNodes"
            :selected-id="selectedId"
            @select="$emit('select', $event)"
            @toggle-collapse="toggleCollapse"
            @manage-permisos="$emit('manage-permisos', $event)"
          />
        </div>
      </div>

      <!-- Nivel raiz tradicional centrado para 'Linea de Mando' -->
      <div
        v-if="activeView !== 'todos'"
        class="mx-auto flex w-max items-start justify-center gap-16"
      >
        <OrgChartNode
          v-for="rootNode in displayNodes"
          :key="rootNode.id"
          :node="rootNode"
          :collapsed-set="collapsedNodes"
          :selected-id="selectedId"
          @select="$emit('select', $event)"
          @toggle-collapse="toggleCollapse"
          @manage-permisos="$emit('manage-permisos', $event)"
        />
      </div>
    </div>

    <!-- Panel lateral deslizante de accion rapida (slide-over dock) -->
    <OrgActionDock
      :open="isDockOpen"
      :active-tab="currentDockTab"
      :sin-supervisor="grupos.sin_supervisor"
      :docentes="grupos.docentes"
      :supervisores="supervisores"
      :all-nodes="rawArbol && rawArbol.length > 0 ? rawArbol : arbol"
      :assigning-user-id="assigningUserId"
      @close="handleCloseDock"
      @update:active-tab="handleTabChange"
      @assign-supervisor="handleAssignSupervisor"
      @select="$emit('select', $event)"
      @manage-permisos="$emit('manage-permisos', $event)"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import {
  AlertCircle,
  Download,
  Globe,
  GraduationCap,
  Loader2,
  MapPin,
  Maximize2,
  Minimize2,
  Network,
  PanelRightClose,
  PanelRightOpen,
  Users,
  ZoomIn,
  ZoomOut,
} from '@lucide/vue';
import { toPng } from 'html-to-image';

import OrgActionDock from '@/components/organigrama/OrgActionDock.vue';
import OrgChartNode from '@/components/organigrama/OrgChartNode.vue';

const props = defineProps({
  arbol: {
    type: Array,
    default: () => [],
  },
  rawArbol: {
    type: Array,
    default: () => [],
  },
  grupos: {
    type: Object,
    default: () => ({
      arbol_mando: [],
      sin_supervisor: [],
      docentes: [],
      sin_sede: [],
    }),
  },
  meta: {
    type: Object,
    default: () => ({
      total: 0,
      total_mando: 0,
      total_sin_supervisor: 0,
      total_docentes: 0,
      total_sin_sede: 0,
    }),
  },
  activeView: {
    type: String,
    default: 'mando',
  },
  dockOpen: {
    type: Boolean,
    default: undefined,
  },
  dockTab: {
    type: String,
    default: 'sin_supervisor',
  },
  supervisores: {
    type: Array,
    default: () => [],
  },
  totalNodos: {
    type: Number,
    default: 0,
  },
  sedeInfo: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  selectedId: {
    type: [Number, String],
    default: null,
  },
  zoom: {
    type: Number,
    default: 1,
  },
  pan: {
    type: Object,
    default: () => ({ x: 0, y: 0 }),
  },
  isDragging: {
    type: Boolean,
    default: false,
  },
  hasDragged: {
    type: Boolean,
    default: false,
  },
  collapsedNodes: {
    type: Set,
    default: () => new Set(),
  },
  zoomIn: {
    type: Function,
    required: true,
  },
  zoomOut: {
    type: Function,
    required: true,
  },
  resetView: {
    type: Function,
    required: true,
  },
  expandAll: {
    type: Function,
    required: true,
  },
  collapseAll: {
    type: Function,
    required: true,
  },
  toggleCollapse: {
    type: Function,
    required: true,
  },
  onMouseDown: {
    type: Function,
    required: true,
  },
  onMouseMove: {
    type: Function,
    required: true,
  },
  onMouseUp: {
    type: Function,
    required: true,
  },
  onWheel: {
    type: Function,
    default: () => {},
  },
  onTouchStart: {
    type: Function,
    default: () => {},
  },
  onTouchMove: {
    type: Function,
    default: () => {},
  },
  onTouchEnd: {
    type: Function,
    default: () => {},
  },
  assigningUserId: {
    type: [Number, String],
    default: null,
  },
});

const emit = defineEmits([
  'select',
  'manage-permisos',
  'change-view',
  'open-dock',
  'close-dock',
  'update:dock-tab',
  'assign-supervisor',
  'export-success',
  'export-error',
]);

// Referencias y estado reactivo para exportacion de imagen PNG
const treeCanvasRef = ref(null);
const isExporting = ref(false);

const canvasStyle = computed(() => ({
  transform: `translate(${props.pan.x}px, ${props.pan.y}px) scale(${props.zoom})`,
}));

// Suprime eventos click en tarjetas de usuario cuando la interaccion fue un arrastre del lienzo
const handleClickCapture = (event) => {
  if (props.hasDragged) {
    event.stopPropagation();
    event.preventDefault();
  }
};

// Estado local fallback del dock si el padre no controla el dock
const localDockOpen = ref(false);
const localDockTab = ref('sin_supervisor');

const isDockOpen = computed(() => {
  return props.dockOpen !== undefined ? props.dockOpen : localDockOpen.value;
});

const currentDockTab = computed(() => {
  return props.dockTab || localDockTab.value;
});

// Metadatos con fallback reactivo
const effectiveMeta = computed(() => {
  return {
    total: props.meta?.total ?? props.totalNodos ?? 0,
    total_mando: props.meta?.total_mando ?? (props.grupos?.arbol_mando?.length ? props.totalNodos : 0),
    total_sin_supervisor: props.meta?.total_sin_supervisor ?? props.grupos?.sin_supervisor?.length ?? 0,
    total_docentes: props.meta?.total_docentes ?? props.grupos?.docentes?.length ?? 0,
    total_sin_sede: props.meta?.total_sin_sede ?? 0,
  };
});

// Nodos a mostrar en el lienzo segun el modo de vista activo
const displayNodes = computed(() => {
  if (props.activeView === 'mando' && props.grupos?.arbol_mando && props.grupos.arbol_mando.length > 0) {
    return props.grupos.arbol_mando;
  }
  return props.arbol;
});

// Separa arboles jerarquicos con subordinados de nodos individuales para la vista 'Todos'
const arbolesJerarquicos = computed(() => {
  return displayNodes.value.filter(
    (n) => n.children && n.children.length > 0
  );
});

const nodosIndependientes = computed(() => {
  return displayNodes.value.filter(
    (n) => !n.children || n.children.length === 0
  );
});

const selectView = (view) => {
  emit('change-view', view);
  props.resetView?.();
};

const handleOpenDock = (tab) => {
  if (isDockOpen.value && currentDockTab.value === tab) {
    handleCloseDock();
    return;
  }
  localDockTab.value = tab;
  localDockOpen.value = true;
  emit('open-dock', tab);
  emit('update:dock-tab', tab);
};

const handleCloseDock = () => {
  localDockOpen.value = false;
  emit('close-dock');
};

const toggleDock = () => {
  if (isDockOpen.value) {
    handleCloseDock();
  } else {
    handleOpenDock(currentDockTab.value);
  }
};

const handleTabChange = (tab) => {
  localDockTab.value = tab;
  emit('update:dock-tab', tab);
};

const handleAssignSupervisor = (payload) => {
  emit('assign-supervisor', payload);
};

// Exporta el organigrama actual a una imagen PNG de alta resolucion (2x)
const exportToPng = async () => {
  if (!treeCanvasRef.value || isExporting.value) return;
  isExporting.value = true;

  try {
    const dataUrl = await toPng(treeCanvasRef.value, {
      pixelRatio: 2,
      backgroundColor: '#f8fafc',
      cacheBust: true,
      style: {
        transform: 'none',
        position: 'static',
        width: 'max-content',
        height: 'max-content',
        margin: '0 auto',
        padding: '56px',
      },
    });

    const sedeTag = props.sedeInfo?.nombre
      ? props.sedeInfo.nombre.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      : 'global';
    const fecha = new Date().toISOString().split('T')[0];
    const filename = `organigrama-kairos-${sedeTag}-${fecha}.png`;

    const link = document.createElement('a');
    link.download = filename;
    link.href = dataUrl;
    link.click();

    emit('export-success', { filename });
  } catch (error) {
    console.error('Error al exportar organigrama a PNG:', error);
    emit('export-error', error);
  } finally {
    isExporting.value = false;
  }
};

defineExpose({
  exportToPng,
  isExporting,
});
</script>

<template>
  <Transition
    enter-active-class="transform transition duration-300 ease-out"
    enter-from-class="translate-x-full opacity-0"
    enter-to-class="translate-x-0 opacity-100"
    leave-active-class="transform transition duration-200 ease-in"
    leave-from-class="translate-x-0 opacity-100"
    leave-to-class="translate-x-full opacity-0"
  >
    <aside
      v-if="open"
      class="absolute inset-0 z-30 flex h-full max-h-screen w-full cursor-default select-auto flex-col bg-white/95 shadow-2xl backdrop-blur-lg sm:inset-y-0 sm:left-auto sm:right-0 sm:max-w-lg sm:border-l sm:border-slate-200/90"
      role="dialog"
      aria-modal="true"
      aria-label="Panel de accion rapida del organigrama"
      @wheel.stop
      @mousedown.stop
      @pointerdown.stop
      @touchstart.stop
    >
      <!-- Cabecera del panel -->
      <header class="flex shrink-0 items-center justify-between gap-3 border-b border-slate-200/80 px-4 py-4 sm:px-5">
        <div>
          <div class="flex items-center gap-2">
            <span class="grid size-7 place-items-center rounded-lg bg-primary-100 text-primary-700">
              <Users :size="16" />
            </span>
            <h2 class="text-sm font-bold text-slate-900">Panel de Accion Rapida</h2>
          </div>
          <p class="mt-0.5 text-xs text-slate-500">
            Gestion y asignacion directa sobre el organigrama
          </p>
        </div>

        <button
          type="button"
          class="grid size-10 shrink-0 place-items-center rounded-xl text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
          title="Cerrar panel lateral"
          @click="$emit('close')"
        >
          <X :size="18" />
        </button>
      </header>

      <!-- Selector de pestanas -->
      <div class="shrink-0 border-b border-slate-200/80 bg-slate-50/70 p-3">
        <div class="grid grid-cols-2 gap-1 rounded-xl bg-slate-200/70 p-1">
          <button
            type="button"
            class="relative flex min-h-10 items-center justify-center gap-1.5 rounded-lg px-1 py-2 text-xs font-bold transition-all"
            :class="
              currentTab === 'sin_supervisor'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            "
            @click="setTab('sin_supervisor')"
          >
            <AlertCircle :size="14" :class="currentTab === 'sin_supervisor' ? 'text-amber-500' : 'text-slate-400'" />
            <span>Por Asignar</span>
            <span
              class="rounded-full px-1.5 py-0.5 text-[10px] font-bold"
              :class="
                currentTab === 'sin_supervisor'
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-slate-300/80 text-slate-700'
              "
            >
              {{ sinSupervisor.length }}
            </span>
          </button>

          <button
            type="button"
            class="relative flex min-h-10 items-center justify-center gap-1.5 rounded-lg px-1 py-2 text-xs font-bold transition-all"
            :class="
              currentTab === 'docentes'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            "
            @click="setTab('docentes')"
          >
            <GraduationCap :size="14" :class="currentTab === 'docentes' ? 'text-sky-600' : 'text-slate-400'" />
            <span>Docentes</span>
            <span
              class="rounded-full px-1.5 py-0.5 text-[10px] font-bold"
              :class="
                currentTab === 'docentes'
                  ? 'bg-sky-100 text-sky-800'
                  : 'bg-slate-300/80 text-slate-700'
              "
            >
              {{ docentes.length }}
            </span>
          </button>
        </div>

        <!-- Buscador rapido dentro del panel -->
        <div class="relative mt-2.5">
          <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Filtrar por nombre o sede..."
            class="min-h-10 w-full rounded-xl border border-slate-200 bg-white py-2 pl-8 pr-8 text-xs text-slate-800 placeholder-slate-400 shadow-2xs focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            @click="searchQuery = ''"
          >
            <X :size="13" />
          </button>
        </div>
      </div>

      <!-- Contenido scrolleable -->
      <div data-testid="org-action-dock-scroll" class="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain p-4 pb-8 dock-scrollbar">
        <!-- PESTANA 1: PERSONAL POR ASIGNAR -->
        <template v-if="currentTab === 'sin_supervisor'">
          <!-- Estado vacio: Todo asignado -->
          <div
            v-if="filteredSinSupervisor.length === 0"
            class="flex flex-col items-center justify-center py-12 px-4 text-center"
          >
            <div class="grid size-12 place-items-center rounded-2xl bg-emerald-50 text-emerald-600 mb-3">
              <CheckCircle2 :size="24" />
            </div>
            <h3 class="text-sm font-bold text-slate-900">
              {{ searchQuery ? 'Sin resultados para la búsqueda' : '¡Todo el personal asignado!' }}
            </h3>
            <p class="mt-1 max-w-xs text-xs text-slate-500">
              {{
                searchQuery
                  ? 'Intenta con otro término de búsqueda.'
                  : 'No existen técnicos o usuarios huérfanos pendientes de supervisor en esta sede.'
              }}
            </p>
          </div>

          <!-- Listado de tarjetas de usuarios huerfanos -->
          <article
            v-for="user in filteredSinSupervisor"
            :key="user.id"
            class="group rounded-2xl border border-slate-200 bg-white p-3.5 shadow-2xs hover:border-slate-300 hover:shadow-xs transition-all text-left"
          >
            <!-- Cabecera de la tarjeta -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-2.5 min-w-0">
                <div
                  class="grid size-9 shrink-0 place-items-center rounded-xl text-xs font-bold"
                  :class="avatarClasses[user.rol] || 'bg-slate-100 text-slate-700'"
                >
                  {{ getInitials(user.nombre, user.apellido) }}
                </div>
                <div class="min-w-0">
                  <h4 class="truncate text-xs font-bold text-slate-900">
                    {{ user.nombre_completo || [user.nombre, user.apellido].filter(Boolean).join(' ') || user.nombre }}
                  </h4>
                  <p class="truncate text-[11px] text-slate-500">
                    {{ user.correo || `@${user.username}` }}
                  </p>
                </div>
              </div>

              <!-- Boton ver ficha -->
              <button
                type="button"
                class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
                title="Ver ficha completa"
                @click="$emit('select', user)"
              >
                <Eye :size="14" />
              </button>
            </div>

            <!-- Metadatos de rol y sede -->
            <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
              <span
                class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-semibold ring-1 ring-inset"
                :class="roleBadgeClasses[user.rol] || 'bg-slate-100 text-slate-700 ring-slate-200'"
              >
                <Crown v-if="user.rol === 'superadmin'" :size="10" />
                <Shield v-else-if="user.rol === 'admin'" :size="10" />
                <Building2 v-else-if="user.rol === 'responsable'" :size="10" />
                <Wrench v-else-if="user.rol === 'tecnico'" :size="10" />
                <User v-else :size="10" />
                {{ roleLabels[user.rol] || user.rol }}
              </span>

              <!-- Badge de sede -->
              <span
                v-if="user.sedes && user.sedes.length > 0"
                class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600"
                :title="user.sedes.map(s => s.nombre).join(', ')"
              >
                <MapPin :size="9" class="text-slate-400" />
                <span class="max-w-[120px] truncate">{{ user.sedes[0].nombre }}</span>
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1 rounded-md bg-amber-50 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700 border border-amber-200"
              >
                Sin sede
              </span>
            </div>

            <!-- Formulario rapido de asignacion en 1 clic -->
            <div class="mt-3 flex flex-col gap-2 border-t border-slate-100 pt-2.5 min-[420px]:flex-row min-[420px]:items-center">
              <div class="relative flex-1 min-w-0">
                <BaseSelect
                  :id="`supervisor-select-${user.id}`"
                  v-model="selectedSupervisors[user.id]"
                  :options="getSupervisorOptions(user)"
                  placeholder="Seleccionar supervisor..."
                  size="sm"
                  :disabled="isAssigning(user.id) || !!assigningUserId"
                />
              </div>

              <button
                type="button"
                class="inline-flex min-h-10 w-full shrink-0 items-center justify-center gap-1.5 rounded-xl bg-primary-600 px-3.5 text-xs font-bold text-white shadow-xs transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50 min-[420px]:w-auto"
                :disabled="!selectedSupervisors[user.id] || isAssigning(user.id) || !!assigningUserId"
                @click="onAssign(user.id)"
              >
                <Loader2 v-if="isAssigning(user.id)" :size="13" class="animate-spin" />
                <UserCheck v-else :size="13" />
                <span>Asignar</span>
              </button>
            </div>
          </article>
        </template>

        <!-- PESTANA 2: CLAUSTRO DOCENTE -->
        <template v-else>
          <!-- Estado vacio docentes -->
          <div
            v-if="filteredDocentes.length === 0"
            class="flex flex-col items-center justify-center py-12 px-4 text-center"
          >
            <div class="grid size-12 place-items-center rounded-2xl bg-sky-50 text-sky-600 mb-3">
              <GraduationCap :size="24" />
            </div>
            <h3 class="text-sm font-bold text-slate-900">
              {{ searchQuery ? 'Sin resultados' : 'No hay docentes registrados' }}
            </h3>
            <p class="mt-1 max-w-xs text-xs text-slate-500">
              Los docentes se mantienen como claustro independiente fuera de la cadena de mando operativa.
            </p>
          </div>

          <div v-else class="space-y-3">
            <p class="text-[11px] text-slate-500 px-1">
              Claustro docente independiente de supervisión jerárquica directa.
            </p>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <article
                v-for="docente in filteredDocentes"
                :key="docente.id"
                class="group flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-3 shadow-2xs hover:border-slate-300 hover:shadow-xs transition-all text-left"
              >
                <!-- Cabecera de la tarjeta con avatar, nombre e informacion basica -->
                <div>
                  <div class="flex items-start justify-between gap-1.5">
                    <div class="flex items-center gap-2 min-w-0">
                      <div class="grid size-8 shrink-0 place-items-center rounded-xl bg-sky-100 text-sky-700 text-xs font-bold">
                        {{ getInitials(docente.nombre, docente.apellido) }}
                      </div>
                      <div class="min-w-0">
                        <h4 class="truncate text-xs font-bold text-slate-900 group-hover:text-primary-600 transition-colors" :title="docente.nombre_completo || docente.nombre">
                          {{ docente.nombre_completo || [docente.nombre, docente.apellido].filter(Boolean).join(' ') || docente.nombre }}
                        </h4>
                        <p class="truncate text-[10px] text-slate-500" :title="docente.correo || `@${docente.username}`">
                          {{ docente.correo || `@${docente.username}` }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- Badges de rol y sede -->
                  <div class="mt-2 flex flex-wrap items-center gap-1">
                    <span
                      class="inline-flex items-center gap-0.5 rounded-md bg-sky-50 px-1.5 py-0.5 text-[9px] font-semibold text-sky-700 border border-sky-200"
                    >
                      <GraduationCap :size="9" />
                      Docente
                    </span>

                    <span
                      v-for="sede in (docente.sedes || []).slice(0, 1)"
                      :key="sede.id"
                      class="inline-flex items-center gap-0.5 rounded-md bg-slate-100 px-1.5 py-0.5 text-[9px] font-medium text-slate-600"
                      :title="sede.nombre"
                    >
                      <MapPin :size="8" class="text-slate-400" />
                      <span class="max-w-[75px] truncate">{{ sede.nombre }}</span>
                    </span>
                    <span
                      v-if="(docente.sedes || []).length > 1"
                      class="rounded-md bg-slate-100 px-1 py-0.5 text-[9px] font-medium text-slate-500"
                    >
                      +{{ docente.sedes.length - 1 }}
                    </span>
                    <span
                      v-if="!docente.sedes || docente.sedes.length === 0"
                      class="rounded-md bg-amber-50 px-1 py-0.5 text-[9px] font-semibold text-amber-700 border border-amber-200"
                    >
                      Sin sede
                    </span>
                  </div>
                </div>

                <!-- Barra inferior de acciones compactas -->
                <div class="mt-2.5 flex items-center justify-end gap-1 border-t border-slate-100 pt-2">
                  <button
                    type="button"
                    class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                    title="Ver ficha técnica"
                    @click="$emit('select', docente)"
                  >
                    <Eye :size="12" />
                    <span>Ficha</span>
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-primary-700 bg-primary-50 hover:bg-primary-100 transition-colors"
                    title="Configurar permisos"
                    @click="$emit('manage-permisos', docente)"
                  >
                    <KeyRound :size="12" />
                    <span>Permisos</span>
                  </button>
                </div>
              </article>
            </div>
          </div>
        </template>
      </div>
    </aside>
  </Transition>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Crown,
  Eye,
  GraduationCap,
  KeyRound,
  Loader2,
  MapPin,
  Search,
  Shield,
  User,
  UserCheck,
  Users,
  Wrench,
  X,
} from '@lucide/vue';

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  activeTab: {
    type: String,
    default: 'sin_supervisor',
  },
  sinSupervisor: {
    type: Array,
    default: () => [],
  },
  docentes: {
    type: Array,
    default: () => [],
  },
  supervisores: {
    type: Array,
    default: () => [],
  },
  allNodes: {
    type: Array,
    default: () => [],
  },
  assigningUserId: {
    type: [Number, String],
    default: null,
  },
});

const emit = defineEmits([
  'close',
  'update:activeTab',
  'assign-supervisor',
  'select',
  'manage-permisos',
]);

let scrollLockSnapshot = null;

// Mantiene un único contexto de desplazamiento mientras el panel está abierto.
const lockPageScroll = () => {
  if (typeof document === 'undefined' || scrollLockSnapshot) return;

  scrollLockSnapshot = {
    htmlOverflow: document.documentElement.style.overflow,
    bodyOverflow: document.body.style.overflow,
    bodyPaddingRight: document.body.style.paddingRight,
  };

  const scrollbarWidth = Math.max(0, window.innerWidth - document.documentElement.clientWidth);
  const currentPaddingRight = Number.parseFloat(window.getComputedStyle(document.body).paddingRight) || 0;

  document.documentElement.style.overflow = 'hidden';
  document.body.style.overflow = 'hidden';
  if (scrollbarWidth > 0) {
    document.body.style.paddingRight = `${currentPaddingRight + scrollbarWidth}px`;
  }
};

const unlockPageScroll = () => {
  if (typeof document === 'undefined' || !scrollLockSnapshot) return;

  document.documentElement.style.overflow = scrollLockSnapshot.htmlOverflow;
  document.body.style.overflow = scrollLockSnapshot.bodyOverflow;
  document.body.style.paddingRight = scrollLockSnapshot.bodyPaddingRight;
  scrollLockSnapshot = null;
};

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      lockPageScroll();
    } else {
      unlockPageScroll();
    }
  },
  { immediate: true }
);

onBeforeUnmount(unlockPageScroll);

const currentTab = computed({
  get: () => props.activeTab || 'sin_supervisor',
  set: (val) => emit('update:activeTab', val),
});

const setTab = (tab) => {
  currentTab.value = tab;
};

const searchQuery = ref('');
const selectedSupervisors = reactive({});
const assigningIds = reactive(new Set());

const isAssigning = (id) => props.assigningUserId === id || assigningIds.has(id);

// Limpiar opciones seleccionadas cuando el usuario ya no esté en la lista de huérfanos
watch(
  () => props.sinSupervisor,
  (newVal) => {
    const currentIds = new Set((newVal || []).map((u) => u.id));
    for (const id in selectedSupervisors) {
      if (!currentIds.has(Number(id))) {
        delete selectedSupervisors[id];
      }
    }
  },
  { deep: true }
);

// Filtrado de personal sin supervisor
const filteredSinSupervisor = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return props.sinSupervisor;
  return props.sinSupervisor.filter((user) => {
    const nombre = (user.nombre_completo || `${user.nombre} ${user.apellido || ''}`).toLowerCase();
    const correo = (user.correo || '').toLowerCase();
    const username = (user.username || '').toLowerCase();
    const sedes = (user.sedes || []).map((s) => s.nombre.toLowerCase()).join(' ');
    return nombre.includes(q) || correo.includes(q) || username.includes(q) || sedes.includes(q);
  });
});

// Filtrado de claustro docente
const filteredDocentes = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return props.docentes;
  return props.docentes.filter((docente) => {
    const nombre = (docente.nombre_completo || `${docente.nombre} ${docente.apellido || ''}`).toLowerCase();
    const correo = (docente.correo || '').toLowerCase();
    const username = (docente.username || '').toLowerCase();
    const sedes = (docente.sedes || []).map((s) => s.nombre.toLowerCase()).join(' ');
    return nombre.includes(q) || correo.includes(q) || username.includes(q) || sedes.includes(q);
  });
});

// Extraer supervisores elegibles de props o arbol completo
const eligibleSupervisors = computed(() => {
  const map = new Map();

  // 1. Extraer del árbol completo del organigrama (todos los administradores y responsables activos)
  const extractFromNodes = (nodes) => {
    for (const node of nodes) {
      if (['superadmin', 'admin', 'responsable'].includes(node.rol) && node.is_active !== false) {
        if (!map.has(node.id)) {
          map.set(node.id, {
            id: node.id,
            nombre: node.nombre_completo || `${node.nombre} ${node.apellido || ''}`.trim() || node.nombre,
            rol: node.rol,
          });
        }
      }
      if (node.children && node.children.length > 0) {
        extractFromNodes(node.children);
      }
    }
  };
  extractFromNodes(props.allNodes || []);

  // 2. Normalizar e incorporar props.supervisores (compatible con formato value/label y directo id/nombre/rol)
  if (Array.isArray(props.supervisores)) {
    for (const s of props.supervisores) {
      const id = s.id ?? s.value;
      if (id === undefined || id === null) continue;

      if (!map.has(id)) {
        const roleMatch = s.label?.match(/\(([^)]+)\)$/);
        const extractedRole = s.rol || (roleMatch ? roleMatch[1] : '');
        const cleanNombre = s.nombre || s.nombre_completo || (s.label ? s.label.replace(/\s*\([^)]*\)$/, '').trim() : '');

        map.set(id, {
          id,
          nombre: cleanNombre || `Supervisor #${id}`,
          rol: extractedRole,
        });
      }
    }
  }

  return Array.from(map.values()).sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''));
});

const getSupervisorsFor = (user) => {
  return eligibleSupervisors.value.filter((s) => s.id !== user.id);
};

const getSupervisorOptions = (user) => {
  return getSupervisorsFor(user).map((sup) => ({
    value: sup.id,
    label: `${sup.nombre}${sup.rol ? ` (${roleLabels[sup.rol] || sup.rol})` : ''}`,
  }));
};

const onAssign = async (userId) => {
  const supervisorId = selectedSupervisors[userId];
  if (!supervisorId) return;

  assigningIds.add(userId);
  try {
    emit('assign-supervisor', { usuarioId: userId, supervisorId: Number(supervisorId) });
  } finally {
    setTimeout(() => {
      assigningIds.delete(userId);
    }, 400);
  }
};

const getInitials = (nombre = '', apellido = '') => {
  const n = (nombre || '').trim().charAt(0).toUpperCase();
  const a = (apellido || '').trim().charAt(0).toUpperCase();
  return (n + a) || 'U';
};

const roleLabels = {
  superadmin: 'Superadmin',
  admin: 'Administrador',
  responsable: 'Responsable',
  tecnico: 'Técnico',
  docente: 'Docente',
  usuario: 'Usuario',
};

const avatarClasses = {
  superadmin: 'bg-amber-100 text-amber-800',
  admin: 'bg-primary-100 text-primary-700',
  responsable: 'bg-purple-100 text-purple-700',
  tecnico: 'bg-emerald-100 text-emerald-700',
  docente: 'bg-sky-100 text-sky-700',
  usuario: 'bg-slate-100 text-slate-700',
};

const roleBadgeClasses = {
  superadmin: 'bg-amber-50 text-amber-800 ring-amber-200',
  admin: 'bg-primary-50 text-primary-700 ring-primary-200',
  responsable: 'bg-purple-50 text-purple-700 ring-purple-200',
  tecnico: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  docente: 'bg-sky-50 text-sky-700 ring-sky-200',
  usuario: 'bg-slate-50 text-slate-700 ring-slate-200',
};
</script>

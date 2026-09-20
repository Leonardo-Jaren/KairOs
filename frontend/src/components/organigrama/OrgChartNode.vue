<template>
  <div class="flex flex-col items-center">
    <!-- Tarjeta del usuario -->
    <div
      class="group relative w-72 cursor-pointer select-none rounded-2xl border bg-white p-4 text-left transition-all duration-200"
      :class="[
        selected
          ? 'border-primary-500 shadow-lg ring-2 ring-primary-500/20'
          : 'border-slate-200/90 shadow-sm hover:border-slate-300 hover:shadow-md',
        !node.is_active ? 'opacity-70 bg-slate-50' : '',
      ]"
      @click="$emit('select', node)"
    >
      <!-- Cabecera: Avatar, Nombre e Indicador de Estado -->
      <div class="flex items-start gap-3">
        <div class="relative grid size-11 shrink-0 place-items-center rounded-xl font-bold text-sm"
          :class="avatarClasses[node.rol] || 'bg-slate-100 text-slate-700'">
          {{ getInitials(node.nombre, node.apellido) }}
          <span
            class="absolute -bottom-0.5 -right-0.5 size-3 rounded-full border-2 border-white ring-1 ring-black/5"
            :class="node.is_active ? 'bg-success-500' : 'bg-slate-400'"
            :title="node.is_active ? 'Cuenta activa' : 'Cuenta inactiva'"
          />
        </div>

        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between gap-1">
            <h3 class="truncate text-sm font-bold text-slate-900 group-hover:text-primary-600 transition-colors">
              {{ node.nombre_completo || node.nombre }}
            </h3>
          </div>
          <p class="truncate text-xs text-slate-500 font-mono">
            @{{ node.username }}
          </p>
        </div>
      </div>

      <!-- Rol y Sedes -->
      <div class="mt-3 flex flex-wrap items-center gap-1.5">
        <span
          class="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold ring-1 ring-inset"
          :class="roleBadgeClasses[node.rol] || 'bg-slate-100 text-slate-700 ring-slate-300'"
        >
          <Crown v-if="node.rol === 'superadmin'" :size="12" class="text-amber-600" />
          <Shield v-else-if="node.rol === 'admin'" :size="12" class="text-primary-600" />
          <Building2 v-else-if="node.rol === 'responsable'" :size="12" class="text-purple-600" />
          <Wrench v-else-if="node.rol === 'tecnico'" :size="12" class="text-emerald-600" />
          <GraduationCap v-else-if="node.rol === 'docente'" :size="12" class="text-sky-600" />
          <User v-else :size="12" class="text-slate-500" />
          {{ roleLabels[node.rol] || node.rol }}
        </span>

        <!-- Badge de Sede física -->
        <span
          v-for="sede in (node.sedes || []).slice(0, 2)"
          :key="sede.id"
          class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-600"
          :title="sede.nombre"
        >
          <MapPin :size="10" class="text-slate-400" />
          <span class="max-w-[80px] truncate">{{ sede.nombre }}</span>
        </span>
        <span
          v-if="(node.sedes || []).length > 2"
          class="rounded-md bg-slate-100 px-1 py-0.5 text-[10px] font-medium text-slate-500"
        >
          +{{ node.sedes.length - 2 }}
        </span>
      </div>

      <!-- Pie de la tarjeta: Botón para gestionar permisos y subordinados -->
      <div class="mt-3 flex items-center justify-between border-t border-slate-100 pt-2.5 text-xs text-slate-500">
        <div class="flex items-center gap-1.5 font-medium">
          <Users :size="13" class="text-slate-400" />
          <span>{{ totalSubordinados }} {{ totalSubordinados === 1 ? 'subordinado' : 'subordinados' }}</span>
        </div>

        <div class="flex items-center gap-1" @click.stop>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 hover:bg-primary-50 hover:text-primary-600 transition-colors"
            title="Gestionar permisos"
            @click="$emit('manage-permisos', node)"
          >
            <KeyRound :size="14" />
          </button>
          <button
            v-if="hasChildren"
            type="button"
            class="flex items-center gap-1 rounded-lg px-2 py-1 font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
            :title="isCollapsed ? 'Expandir rama' : 'Colapsar rama'"
            @click="$emit('toggle-collapse', node.id)"
          >
            <ChevronDown
              :size="14"
              class="transition-transform duration-200 text-slate-500"
              :class="{ '-rotate-90': isCollapsed }"
            />
            <span>{{ node.children.length }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Ramas y Conectores de subordinados (Recursivo) -->
    <template v-if="hasChildren && !isCollapsed">
      <!-- Línea vertical del tronco superior -->
      <div class="h-6 w-0.5 bg-slate-300 shrink-0" />

      <!-- Fila horizontal de columnas de hijos -->
      <div class="flex flex-row items-start justify-center">
        <div
          v-for="(child, index) in node.children"
          :key="child.id"
          class="relative flex flex-col items-center px-4"
        >
          <!-- Segmentos de la barra horizontal de bifurcación -->
          <div
            v-if="node.children.length > 1 && index === 0"
            class="absolute top-0 right-0 left-1/2 h-0.5 bg-slate-300"
          />
          <div
            v-else-if="node.children.length > 1 && index === node.children.length - 1"
            class="absolute top-0 left-0 right-1/2 h-0.5 bg-slate-300"
          />
          <div
            v-else-if="node.children.length > 1"
            class="absolute top-0 left-0 right-0 h-0.5 bg-slate-300"
          />

          <!-- Línea vertical individual que desciende hacia cada hijo -->
          <div class="h-6 w-0.5 bg-slate-300 shrink-0" />

          <!-- Llamada recursiva -->
          <OrgChartNode
            :node="child"
            :collapsed-set="collapsedSet"
            :selected-id="selectedId"
            @select="$emit('select', $event)"
            @toggle-collapse="$emit('toggle-collapse', $event)"
            @manage-permisos="$emit('manage-permisos', $event)"
          />
        </div>
      </div>
    </template>
  </div>
</template>


<script setup>
import { computed } from 'vue';
import {
  Building2,
  ChevronDown,
  Crown,
  GraduationCap,
  KeyRound,
  MapPin,
  Shield,
  User,
  Users,
  Wrench,
} from '@lucide/vue';

defineOptions({
  name: 'OrgChartNode',
});

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  collapsedSet: {
    type: Set,
    default: () => new Set(),
  },
  selectedId: {
    type: [Number, String],
    default: null,
  },
});

defineEmits(['select', 'toggle-collapse', 'manage-permisos']);

const isCollapsed = computed(() => props.collapsedSet.has(props.node.id));
const hasChildren = computed(() => Array.isArray(props.node.children) && props.node.children.length > 0);
const selected = computed(() => props.selectedId === props.node.id);
const totalSubordinados = computed(() => props.node.subordinados_count ?? props.node.children?.length ?? 0);


const getInitials = (nombre = '', apellido = '') => {
  const n = (nombre || '').trim().charAt(0);
  const a = (apellido || '').trim().charAt(0);
  return (n + a).toUpperCase() || 'U';
};

const roleLabels = {
  superadmin: 'Superadmin',
  admin: 'Administrador',
  responsable: 'Responsable',
  tecnico: 'Técnico',
  docente: 'Docente',
  usuario: 'Usuario',
};

const roleBadgeClasses = {
  superadmin: 'bg-amber-50 text-amber-800 ring-amber-400/40',
  admin: 'bg-primary-50 text-primary-700 ring-primary-600/20',
  responsable: 'bg-purple-50 text-purple-700 ring-purple-600/20',
  tecnico: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  docente: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  usuario: 'bg-slate-100 text-slate-700 ring-slate-300',
};

const avatarClasses = {
  superadmin: 'bg-amber-100 text-amber-800',
  admin: 'bg-primary-100 text-primary-800',
  responsable: 'bg-purple-100 text-purple-800',
  tecnico: 'bg-emerald-100 text-emerald-800',
  docente: 'bg-sky-100 text-sky-800',
  usuario: 'bg-slate-100 text-slate-700',
};
</script>

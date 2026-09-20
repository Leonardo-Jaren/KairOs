<template>
  <Teleport to="body">
    <div>
    <!-- Backdrop oscuro con transición de opacidad -->
    <transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-xs"
        @click="$emit('close')"
      />
    </transition>

    <!-- Ficha de usuario como modal centrado -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="scale-95 opacity-0"
      enter-to-class="scale-100 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="scale-100 opacity-100"
      leave-to-class="scale-95 opacity-0"
    >
      <aside
        v-if="open && user"
        class="fixed left-1/2 top-1/2 z-50 flex w-[calc(100%-1.5rem)] max-w-xl -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-2xl max-h-[calc(100dvh-2rem)] sm:max-h-[min(640px,calc(100dvh-3rem))] sm:w-[calc(100%-2rem)]"
        role="dialog"
        aria-modal="true"
        :aria-label="`Ficha de ${user.nombre_completo || user.nombre}`"
        tabindex="-1"
        @keydown.esc="$emit('close')"
      >
        <!-- Encabezado de la ficha -->
        <header class="flex shrink-0 items-start justify-between border-b border-slate-200 p-4 sm:p-6">
          <div class="flex items-center gap-3">
            <div class="relative grid size-12 place-items-center rounded-2xl font-bold text-base"
              :class="avatarClasses[user.rol] || 'bg-slate-100 text-slate-700'">
              {{ getInitials(user.nombre, user.apellido) }}
              <span
                class="absolute -bottom-0.5 -right-0.5 size-3.5 rounded-full border-2 border-white ring-1 ring-black/5"
                :class="user.is_active ? 'bg-success-500' : 'bg-slate-400'"
              />
            </div>
            <div>
              <h2 class="text-base font-extrabold text-slate-900 leading-tight">
                {{ user.nombre_completo || user.nombre }}
              </h2>
              <p class="text-xs text-slate-500 font-mono">@{{ user.username }}</p>
            </div>
          </div>

          <button
            type="button"
            class="grid size-10 shrink-0 place-items-center rounded-xl text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            aria-label="Cerrar ficha"
            @click="$emit('close')"
          >
            <X :size="18" />
          </button>
        </header>

        <!-- Selector de pestañas internas -->
        <nav class="surface-scrollbar flex shrink-0 overflow-x-auto border-b border-slate-200 bg-slate-50/70 px-2 text-xs font-semibold sm:px-4">
          <button
            type="button"
            class="flex min-h-11 shrink-0 items-center gap-2 border-b-2 px-3 py-3 transition-colors"
            :class="activeTab === 'detalles' ? 'border-primary-600 text-primary-600 bg-white' : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="activeTab = 'detalles'"
          >
            <Info :size="14" />
            <span>Ficha Técnica</span>
          </button>
          <button
            type="button"
            class="flex min-h-11 shrink-0 items-center gap-2 border-b-2 px-3 py-3 transition-colors"
            :class="activeTab === 'equipo' ? 'border-primary-600 text-primary-600 bg-white' : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="cargarEquipo"
          >
            <Users :size="14" />
            <span>A su cargo</span>
            <span v-if="subordinadosCount" class="rounded-full bg-slate-200 px-1.5 py-0.2 text-[10px] text-slate-700">
              {{ subordinadosCount }}
            </span>
          </button>
          <button
            v-if="canViewActividad"
            type="button"
            class="flex min-h-11 shrink-0 items-center gap-2 border-b-2 px-3 py-3 transition-colors"
            :class="activeTab === 'actividad' ? 'border-primary-600 text-primary-600 bg-white' : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="cargarActividad"
          >
            <Clock :size="14" />
            <span>Actividad</span>
          </button>
        </nav>

        <!-- Contenido de las pestañas -->
        <div class="dock-scrollbar min-h-0 flex-1 space-y-5 overflow-y-auto p-4 sm:p-5">
          <!-- Pestaña 1: Detalles -->
          <section v-if="activeTab === 'detalles'" class="space-y-5">
            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Rol Institucional</p>
              <div class="mt-1 flex items-center gap-2">
                <span class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-bold ring-1 ring-inset"
                  :class="roleBadgeClasses[user.rol]">
                  {{ roleLabels[user.rol] || user.rol }}
                </span>
                <span class="text-xs text-slate-500">
                  {{ user.is_active ? 'Cuenta operativa' : 'Cuenta suspendida / inactiva' }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-3 min-[360px]:grid-cols-2 sm:gap-4">
              <div class="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3">
                <p class="text-[11px] font-semibold text-slate-400 uppercase">DNI</p>
                <p class="mt-1 font-mono text-sm font-bold text-slate-800">{{ user.dni || 'Sin registrar' }}</p>
              </div>
              <div class="rounded-xl border border-slate-200/80 bg-slate-50/50 p-3">
                <p class="text-[11px] font-semibold text-slate-400 uppercase">Subordinados</p>
                <p class="mt-1 text-sm font-bold text-slate-800">{{ user.subordinados_count ?? 0 }} directos</p>
              </div>
            </div>

            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Correo Electrónico</p>
              <p class="mt-1 flex items-start gap-2 break-all text-sm font-medium text-slate-800">
                <Mail :size="14" class="text-slate-400" />
                {{ user.correo }}
              </p>
            </div>

            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Supervisor Directo</p>
              <div v-if="user.supervisor_nombre || user.supervisor" class="mt-2 flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-xs">
                <div class="grid size-8 place-items-center rounded-lg bg-slate-100 font-bold text-xs text-slate-700">
                  {{ (user.supervisor_nombre || user.supervisor?.nombre_completo || 'S').charAt(0) }}
                </div>
                <div class="min-w-0 flex-1">
                  <p class="truncate text-xs font-bold text-slate-800">
                    {{ user.supervisor_nombre || user.supervisor?.nombre_completo }}
                  </p>
                  <p class="text-[11px] text-slate-400 font-mono">
                    {{ user.supervisor?.rol || 'Supervisor jerárquico' }}
                  </p>
                </div>
              </div>
              <p v-else class="mt-1 text-xs text-slate-500 italic">
                Sin supervisor directo asignado (Nodo principal o de máxima autoridad).
              </p>
            </div>

            <div>
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Sedes Asignadas</p>
              <div v-if="(user.sedes || []).length" class="mt-2 flex flex-wrap gap-2">
                <div
                  v-for="sede in user.sedes"
                  :key="sede.id"
                  class="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-1.5 text-xs font-medium text-slate-700"
                >
                  <Building2 :size="13" class="text-primary-600" />
                  <span>{{ sede.nombre }}</span>
                  <span v-if="sede.es_sede_principal" class="rounded bg-primary-100 px-1 text-[10px] font-bold text-primary-700">
                    Principal
                  </span>
                </div>
              </div>
              <p v-else class="mt-1 text-xs text-slate-500 italic">
                Sin sedes físicas asociadas actualmente.
              </p>
            </div>
          </section>

          <!-- Pestaña 2: Equipo a su cargo -->
          <section v-else-if="activeTab === 'equipo'" class="space-y-4">
            <div class="flex flex-col items-start gap-2 min-[420px]:flex-row min-[420px]:items-center min-[420px]:justify-between">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Personal subordinado</p>
              <button
                v-if="canAddSubordinate"
                type="button"
                class="inline-flex items-center gap-1.5 rounded-xl bg-primary-50 px-3 py-1.5 text-xs font-bold text-primary-700 hover:bg-primary-100 hover:text-primary-800 transition-colors shadow-xs"
                title="Crear un nuevo usuario subordinado a esta persona"
                @click="$emit('add-subordinate', user)"
              >
                <UserPlus :size="14" />
                <span>Añadir a su cargo</span>
              </button>
            </div>

            <div v-if="loadingEquipo" class="flex justify-center py-8">
              <div class="size-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
            </div>

            <div v-else-if="subordinados.length === 0" class="py-8 text-center rounded-2xl border border-dashed border-slate-200 p-6">
              <Users :size="28" class="mx-auto text-slate-300" />
              <p class="mt-2 text-xs font-semibold text-slate-700">No tiene personas a su cargo</p>
              <p class="mt-0.5 text-[11px] text-slate-400">No se encontraron subordinados directos registrados.</p>
              <button
                v-if="canAddSubordinate"
                type="button"
                class="mt-3 inline-flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-700 underline"
                @click="$emit('add-subordinate', user)"
              >
                <UserPlus :size="13" />
                <span>Asignar primer usuario a su cargo</span>
              </button>
            </div>

            <ul v-else class="space-y-2">
              <li
                v-for="sub in subordinados"
                :key="sub.id"
                class="flex items-center justify-between rounded-xl border border-slate-200/80 bg-white p-3 shadow-xs hover:border-primary-300 transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div class="grid size-8 place-items-center rounded-lg bg-slate-100 font-bold text-xs text-slate-700">
                    {{ sub.nombre?.charAt(0) }}{{ sub.apellido?.charAt(0) }}
                  </div>
                  <div>
                    <p class="text-xs font-bold text-slate-900">{{ sub.nombre_completo }}</p>
                    <p class="text-[11px] text-slate-400">@{{ sub.username }} · {{ roleLabels[sub.rol] || sub.rol }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-1">
                  <span
                    class="size-2 rounded-full"
                    :class="sub.is_active ? 'bg-success-500' : 'bg-slate-300'"
                    :title="sub.is_active ? 'Activo' : 'Inactivo'"
                  />
                  <button
                    v-if="canEditTarget(sub)"
                    type="button"
                    class="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                    title="Editar usuario"
                    :aria-label="`Editar a ${sub.nombre_completo || sub.nombre}`"
                    @click="$emit('edit', sub)"
                  >
                    <Pencil :size="14" />
                  </button>
                  <button
                    v-if="canDeleteTarget(sub)"
                    type="button"
                    class="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-danger-50 hover:text-danger-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-danger-500"
                    title="Desactivar usuario"
                    :aria-label="`Desactivar a ${sub.nombre_completo || sub.nombre}`"
                    @click="$emit('delete', sub)"
                  >
                    <UserX :size="14" />
                  </button>
                </div>
              </li>
            </ul>
          </section>

          <!-- Pestaña 3: Actividad reciente (Auditoría) -->
          <section v-else-if="activeTab === 'actividad'" class="space-y-4">
            <div v-if="loadingActividad" class="flex justify-center py-8">
              <div class="size-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
            </div>

            <div v-else-if="actividad.length === 0" class="py-8 text-center">
              <Clock :size="28" class="mx-auto text-slate-300" />
              <p class="mt-2 text-xs font-semibold text-slate-700">Sin actividad reciente registrada</p>
              <p class="mt-0.5 text-[11px] text-slate-400">No se encontraron eventos de auditoría para este usuario.</p>
            </div>

            <ol v-else class="relative border-l border-slate-200 space-y-6 ml-3">
              <li v-for="evento in actividad" :key="evento.id" class="ml-4">
                <div class="absolute -left-1.5 mt-1.5 size-3 rounded-full border-2 border-white bg-primary-500 ring-2 ring-primary-100" />
                <time class="text-[11px] font-mono font-medium text-slate-400">
                  {{ formatDate(evento.fecha) }}
                </time>
                <h4 class="text-xs font-bold text-slate-800 mt-0.5">
                  {{ evento.tipo_evento }}
                </h4>
                <p class="text-xs text-slate-600 mt-0.5 leading-relaxed">
                  {{ evento.descripcion }}
                </p>
              </li>
            </ol>
          </section>
        </div>

        <!-- Pie con acciones de gestión adaptado responsivamente -->
        <footer class="flex shrink-0 flex-col gap-2 border-t border-slate-100 bg-slate-50/80 p-3 sm:flex-row sm:items-center sm:justify-between sm:px-5 sm:py-3.5">
          <div>
            <BaseButton
              v-if="canDeleteUser"
              variant="danger"
              :full-width="true"
              class="sm:w-auto!"
              @click="$emit('delete', user)"
            >
              <template #icon>
                <UserX :size="15" />
              </template>
              Desactivar usuario
            </BaseButton>
          </div>

          <div class="flex flex-col-reverse gap-2 sm:flex-row sm:items-center sm:justify-end sm:gap-2.5">
            <BaseButton
              variant="ghost"
              :full-width="true"
              class="sm:w-auto!"
              @click="$emit('close')"
            >
              Cerrar ficha
            </BaseButton>

            <BaseButton
              v-if="canManagePermisos"
              variant="accent"
              :full-width="true"
              class="sm:w-auto!"
              @click="$emit('manage-permisos', user)"
            >
              <template #icon>
                <KeyRound :size="15" />
              </template>
              Permisos CRUD
            </BaseButton>

            <BaseButton
              v-if="canEditUser"
              variant="secondary"
              :full-width="true"
              class="sm:w-auto!"
              @click="$emit('edit', user)"
            >
              <template #icon>
                <Pencil :size="15" />
              </template>
              Editar datos
            </BaseButton>
          </div>
        </footer>
      </aside>
    </transition>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import {
  Building2,
  Clock,
  Info,
  KeyRound,
  Mail,
  Pencil,
  UserPlus,
  Users,
  X,
  UserX,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import permisosService from '@/services/permisos.service';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  user: {
    type: Object,
    default: null,
  },
});

defineEmits(['close', 'edit', 'delete', 'manage-permisos', 'add-subordinate']);

const authStore = useAuthStore();

const activeSedeIds = (user) => new Set((user?.sedes || []).map((sede) => Number(sede.id)));

const sharesSede = (target) => {
  const actorSedes = activeSedeIds(authStore.user);
  if (!actorSedes.size) return true;
  const targetSedes = activeSedeIds(target);
  return !targetSedes.size || [...targetSedes].some((id) => actorSedes.has(id));
};

const canManageTarget = (target) => {
  const actor = authStore.user;
  if (!actor || !target) return false;
  if (actor.rol === 'superadmin' || actor.is_superuser) return true;
  if (actor.rol === 'admin') {
    return target.id === actor.id
      ? target.rol === 'admin'
      : ['responsable', 'tecnico', 'docente', 'usuario'].includes(target.rol) && sharesSede(target);
  }
  if (actor.rol === 'responsable') {
    return ['tecnico', 'docente', 'usuario'].includes(target.rol)
      && target.supervisor_id === actor.id
      && sharesSede(target);
  }
  return false;
};

const canAddSubordinate = computed(() => {
  if (!authStore.user || !props.user) return false;
  if (['docente', 'tecnico', 'usuario'].includes(props.user.rol)) return false;
  if (authStore.isSuperAdmin || authStore.isAdmin) return true;
  if (authStore.isResponsable) {
    return props.user.id === authStore.user.id && props.user.rol === 'responsable';
  }
  return false;
});

const canManagePermisos = computed(() => {
  return (authStore.isSuperAdmin || authStore.isAdmin)
    && authStore.hasPermission('usuarios', 'editar')
    && props.user?.id !== authStore.user?.id
    && canManageTarget(props.user);
});

const canEditUser = computed(() => {
  return authStore.hasPermission('usuarios', 'editar') && canManageTarget(props.user);
});

const canDeleteUser = computed(() => (
  authStore.hasPermission('usuarios', 'eliminar')
  && props.user?.id !== authStore.user?.id
  && canManageTarget(props.user)
));

const canEditTarget = (target) => authStore.hasPermission('usuarios', 'editar') && canManageTarget(target);

const canDeleteTarget = (target) => (
  authStore.hasPermission('usuarios', 'eliminar')
  && target?.id !== authStore.user?.id
  && canManageTarget(target)
);

const canViewActividad = computed(() => {
  if (!authStore.user || !props.user) return false;
  if (authStore.isSuperAdmin || authStore.isAdmin || authStore.isResponsable) return true;
  return props.user.id === authStore.user.id;
});

const subordinadosCount = computed(() => subordinados.value.length || props.user?.subordinados_count || 0);

const activeTab = ref('detalles');
const subordinados = ref([]);
const actividad = ref([]);
const loadingEquipo = ref(false);
const loadingActividad = ref(false);

const getInitials = (nombre = '', apellido = '') => {
  const n = (nombre || '').trim().charAt(0);
  const a = (apellido || '').trim().charAt(0);
  return (n + a).toUpperCase() || 'U';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('es-PE', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};

const cargarEquipo = async () => {
  activeTab.value = 'equipo';
  if (!props.user?.id) return;
  loadingEquipo.value = true;
  try {
    subordinados.value = await permisosService.obtenerSubordinados(props.user.id);
  } catch {
    if (!subordinados.value.length && props.user?.children?.length) {
      subordinados.value = props.user.children;
    }
  } finally {
    loadingEquipo.value = false;
  }
};

const cargarActividad = async () => {
  activeTab.value = 'actividad';
  if (!props.user?.id) return;
  loadingActividad.value = true;
  try {
    actividad.value = await permisosService.obtenerActividad(props.user.id, { limit: 15 });
  } catch {
    actividad.value = [];
  } finally {
    loadingActividad.value = false;
  }
};

watch(
  () => props.user,
  (newUser) => {
    activeTab.value = 'detalles';
    subordinados.value = [];
    actividad.value = [];
    if (newUser) {
      // Precarga previa si está disponible en el objeto
      if (newUser.children) {
        subordinados.value = newUser.children;
      }
    }
  },
);

const roleLabels = {
  superadmin: 'Superadministrador',
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

<script setup>
import {
  Boxes,
  Building2,
  Clock3,
  Gauge,
  LogOut,
  Menu,
  MonitorCog,
  PanelLeftClose,
  ShieldAlert,
  UserRoundCog,
  UsersRound,
  Wrench,
} from '@lucide/vue';
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const sidebarOpen = ref(false);

const user = computed(() => authStore.user);
const pageTitle = computed(() => route.meta.title ?? 'Panel de control');
const initials = computed(() => {
  const names = `${user.value?.nombre ?? ''} ${user.value?.apellido ?? ''}`.trim().split(/\s+/);
  return names.filter(Boolean).slice(0, 2).map((name) => name[0]).join('').toUpperCase() || 'KR';
});

const menuItems = computed(() => [
  { name: 'Dashboard', path: '/dashboard', icon: Gauge },
  { name: 'Usuarios', path: '/usuarios', icon: UsersRound, roles: ['admin', 'tecnico'] },
  { name: 'Espacios', path: '/espacios', icon: Building2, roles: ['admin', 'tecnico'] },
  { name: 'Usuarios por espacio', path: '/espacios/usuarios', icon: UserRoundCog, roles: ['admin', 'tecnico'] },
  { name: 'Equipos', path: '/equipos', icon: MonitorCog },
  { name: 'Componentes', path: '/componentes', icon: Boxes },
  { name: 'Software', path: '/software', icon: PanelLeftClose },
  { name: 'Mantenimiento', path: '/mantenimiento', icon: Wrench },
  { name: 'Incidencias', path: '/incidencias', icon: ShieldAlert },
  { name: 'Historial', path: '/historial', icon: Clock3 },
].filter((item) => !item.roles || item.roles.includes(user.value?.rol)));

const handleLogout = async () => {
  authStore.logout();
  await router.push('/auth/login');
};

watch(() => route.fullPath, () => {
  sidebarOpen.value = false;
});
</script>

<template>
  <div class="flex min-h-screen bg-slate-50 text-slate-900">
    <Transition enter-active-class="transition-opacity" enter-from-class="opacity-0" leave-active-class="transition-opacity" leave-to-class="opacity-0">
      <button
        v-if="sidebarOpen"
        type="button"
        class="fixed inset-0 z-30 bg-secondary-950/55 backdrop-blur-sm lg:hidden"
        aria-label="Cerrar menú"
        @click="sidebarOpen = false"
      />
    </Transition>

    <aside
      class="fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-secondary-950 text-white shadow-2xl transition-transform duration-300 lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 lg:shadow-none"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex h-20 items-center justify-between border-b border-white/8 px-6">
        <div>
          <p class="text-xl font-extrabold tracking-[0.16em] text-white">KairOs</p>
          <p class="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.2em] text-primary-300">Gestión tecnológica</p>
        </div>
        <span class="rounded-md bg-primary-500/15 px-2 py-1 text-[10px] font-bold text-primary-300">v1.0</span>
      </div>

      <nav class="flex-1 overflow-y-auto px-4 py-6" aria-label="Navegación principal">
        <p class="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-white/35">Módulos</p>
        <div class="flex flex-col gap-1">
          <RouterLink
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="group flex items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-medium text-white/60 transition-all duration-200 hover:bg-white/6 hover:text-white"
            active-class="bg-primary-500! text-white! shadow-lg shadow-primary-950/20"
          >
            <component :is="item.icon" :size="19" :stroke-width="1.8" class="shrink-0" />
            <span>{{ item.name }}</span>
          </RouterLink>
        </div>
      </nav>

      <div class="border-t border-white/8 p-4">
        <div class="flex items-center gap-3 rounded-xl bg-white/5 p-3">
          <div class="grid size-10 shrink-0 place-items-center rounded-xl bg-primary-500 text-sm font-bold text-white">
            {{ initials }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-white">{{ user?.nombre }} {{ user?.apellido }}</p>
            <p class="truncate text-[11px] font-medium uppercase tracking-wider text-white/40">{{ user?.rol }}</p>
          </div>
          <button type="button" class="rounded-lg p-2 text-white/40 hover:bg-white/8 hover:text-danger-300" title="Cerrar sesión" aria-label="Cerrar sesión" @click="handleLogout">
            <LogOut :size="18" />
          </button>
        </div>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
        <div class="flex items-center gap-3">
          <button type="button" class="rounded-xl border border-slate-200 p-2.5 text-slate-600 hover:bg-slate-50 lg:hidden" aria-label="Abrir menú" @click="sidebarOpen = true">
            <Menu :size="20" />
          </button>
          <div>
            <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">KairOs / Administración</p>
            <h2 class="mt-0.5 text-lg font-bold text-slate-900">{{ pageTitle }}</h2>
          </div>
        </div>
        <div class="hidden items-center gap-2 rounded-full border border-success-200 bg-success-50 px-3 py-1.5 sm:flex">
          <span class="size-2 rounded-full bg-success-500" />
          <span class="text-xs font-semibold text-success-700">Sistema operativo</span>
        </div>
      </header>

      <main class="flex-1 p-4 sm:p-6 lg:p-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>

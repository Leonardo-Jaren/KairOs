<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// Obtener el perfil del usuario activo desde el store
const user = computed(() => authStore.user);

// Cierra la sesion del usuario y lo redirige al login
const handleLogout = () => {
  authStore.logout();
  router.push('/auth/login');
};

// Menu de navegacion lateral segun el rol del usuario (Filtrado para el futuro)
const menuItems = computed(() => {
  const items = [
    { name: 'Dashboard', path: '/dashboard', icon: 'M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z' },
    { name: 'Usuarios', path: '/usuarios', icon: 'M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.109A11.386 11.386 0 0 1 10.089 20.8c-1.802 0-3.54-.388-5.118-1.085a4.125 4.125 0 0 1 3.754-5.736A11.579 11.579 0 0 1 12 12.75c2.97 0 5.679 1.11 7.763 2.934m0 0a11.39 11.39 0 0 1 1.196 2.443m-1.2-2.443a9.07 9.07 0 0 0-2.316-1.57m3.516 4.013a8.908 8.908 0 0 0 1.376-2.553M14.25 7.5a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0ZM16.5 7.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0ZM6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z', roles: ['admin'] },
    { name: 'Espacios', path: '/espacios', icon: 'M2.25 21h19.5m-18-18v18m16.5-18v18m-13.5-18h10.5a.75.75 0 0 1 .75.75v16.5a.75.75 0 0 1-.75.75H5.25a.75.75 0 0 1-.75-.75V3.75a.75.75 0 0 1 .75-.75Z' },
    { name: 'Equipos', path: '/equipos', icon: 'M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25' },
    { name: 'Software', path: '/software', icon: 'M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z' },
    { name: 'Mantenimiento', path: '/mantenimiento', icon: 'M11.42 15.17L17.25 21A2.67 2.67 0 0021 17.25l-5.83-5.83m-3.75 3.75a2.25 2.25 0 11-3.18-3.18 2.25 2.25 0 013.18 3.18zm-3.75-3.75L3 3.75A2.67 2.67 0 006.75 7.5l4.67 4.67' },
    { name: 'Incidencias', path: '/incidencias', icon: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z' },
    { name: 'Historial', path: '/historial', icon: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z' }
  ];

  // Si no hay usuario activo, vacio
  if (!user.value) return [];
  
  // Filtrar en base al rol
  return items.filter(item => !item.roles || item.roles.includes(user.value.rol));
});
</script>

<template>
  <div class="flex h-screen w-screen bg-kairos-navy-dark text-white overflow-hidden">
    
    <!-- Sidebar - Navegacion Lateral -->
    <aside class="w-64 bg-kairos-navy border-r border-white/5 flex flex-col z-20 shrink-0">
      
      <!-- Encabezado de la App con Logo de KairOs -->
      <div class="h-16 px-6 border-b border-white/5 flex items-center justify-between">
        <span class="text-xl font-bold uppercase tracking-wider text-kairos-blue">
          KairOs
        </span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-kairos-blue/10 text-kairos-blue uppercase">
          v1.0
        </span>
      </div>

      <!-- Listado de Opciones del Menu -->
      <nav class="flex-grow py-4 px-4 overflow-y-auto flex flex-col gap-1">
        <router-link
          v-for="item in menuItems"
          :key="item.name"
          :to="item.path"
          class="flex items-center gap-3.5 px-4 py-3 rounded-lg text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 transition-all duration-200 cursor-pointer"
          active-class="bg-kairos-blue! text-white! font-semibold"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke-width="1.5" 
            stroke="currentColor" 
            class="w-5 h-5 shrink-0"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
          </svg>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- Pie de Pagina de Sidebar -->
      <div class="p-4 border-t border-white/5">
        <div class="flex items-center gap-3 bg-white/5 p-3 rounded-lg text-xs">
          <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
          <span class="text-white/60">Servidor en línea</span>
        </div>
      </div>

    </aside>

    <!-- Area Principal de Contenido -->
    <div class="flex-grow flex flex-col min-w-0 h-full overflow-hidden">
      
      <!-- Navbar - Barra Superior -->
      <header class="h-16 bg-kairos-navy border-b border-white/5 flex items-center justify-between px-6 z-10 shrink-0">
        
        <!-- Titulo de la Seccion Activa -->
        <h2 class="text-lg font-semibold tracking-wide text-white uppercase">
          Panel de Control
        </h2>

        <!-- Perfil y Acciones del Usuario -->
        <div class="flex items-center gap-4">
          
          <!-- Informacion del Usuario Activo -->
          <div v-if="user" class="text-right hidden sm:flex flex-col">
            <span class="text-sm font-semibold text-white leading-tight">
              {{ user.nombre }}
            </span>
            <span class="text-[11px] text-white/50 leading-none uppercase tracking-wider font-bold">
              {{ user.rol }}
            </span>
          </div>

          <!-- Divisor Vertical -->
          <div class="h-8 w-[1px] bg-white/10 hidden sm:block"></div>

          <!-- Boton de Salida / Logout -->
          <button
            @click="handleLogout"
            class="flex items-center justify-center p-2.5 rounded-lg text-white/70 hover:text-white hover:bg-white/5 hover:text-red-400 transition-all duration-200 cursor-pointer outline-none border border-transparent"
            title="Cerrar sesión"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke-width="1.5" 
              stroke="currentColor" 
              class="w-5.5 h-5.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
            </svg>
          </button>

        </div>

      </header>

      <!-- Panel de Contenido Dinamico (Vista inyectada) -->
      <main class="flex-grow overflow-y-auto p-6 md:p-8 bg-kairos-navy-dark">
        <router-view />
      </main>

    </div>

  </div>
</template>

<style scoped>
/* Los estilos se resuelven completamente con clases de Tailwind CSS */
</style>

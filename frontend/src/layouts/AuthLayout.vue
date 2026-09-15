<script setup>
import {
  Cpu,
  ShieldCheck,
} from '@lucide/vue';
</script>

<template>
  <div class="h-screen max-h-screen w-full flex flex-col justify-between bg-slate-50 text-slate-900 selection:bg-primary-500 selection:text-white relative overflow-y-auto sm:overflow-hidden">

    <!-- Fondo arquitectonico sutil y profesional para entorno de administracion TI -->
    <div 
      class="absolute inset-0 opacity-40 pointer-events-none select-none"
      style="background-image: radial-gradient(#cbd5e1 1px, transparent 1px); background-size: 24px 24px;"
    />

    <!-- Barra superior: Encabezado institucional de marca -->
    <header class="relative z-10 w-full max-w-6xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between shrink-0">
      <!-- Logotipo y denominacion del sistema -->
      <div class="flex items-center gap-2.5 select-none">
        <div class="size-9 rounded-xl bg-secondary-950 flex items-center justify-center text-white shadow-xs border border-secondary-800">
          <Cpu :size="18" :stroke-width="2.2" class="text-primary-400" />
        </div>
        <div>
          <div class="flex items-center gap-1.5 leading-none">
            <span class="text-lg font-extrabold tracking-tight text-slate-900">Kair<span class="text-primary-600">Os</span></span>
            <span class="text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-secondary-900/5 text-secondary-700 border border-secondary-200">
              Campus TI
            </span>
          </div>
          <span class="block text-[11px] text-slate-500 font-medium mt-0.5">
            Sistema de Gestión de Laboratorios e Infraestructura
          </span>
        </div>
      </div>

      <!-- Indicador de red institucional segura -->
      <div class="hidden sm:inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-xs text-xs text-slate-600 select-none">
        <span class="size-2 rounded-full bg-emerald-500"></span>
        <span class="font-medium text-slate-700">Red Institucional Segura</span>
      </div>
    </header>

    <!-- Contenedor central: Tarjeta interactiva de autenticacion (Login / Password Reset) -->
    <main class="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-2 sm:py-3 my-auto shrink-0">
      <div class="w-full max-w-[430px]">
        <router-view />
      </div>

      <!-- Aviso legal y de confidencialidad institucional -->
      <div class="w-full max-w-[430px] mt-2.5 px-2 text-center">
        <p class="text-[11px] text-slate-400 leading-tight select-none">
          Acceso exclusivo para personal autorizado • Actividad registrada para auditoría institucional
        </p>
      </div>
    </main>

    <!-- Barra inferior: Pie de soporte y versionado institucional -->
    <footer class="relative z-10 w-full max-w-6xl mx-auto px-4 sm:px-6 py-2.5 sm:py-3 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500 border-t border-slate-200/80 shrink-0 select-none">
      <div class="flex items-center gap-2">
        <span>&copy; {{ new Date().getFullYear() }} KairOs Campus & Labs</span>
        <span>•</span>
        <span class="text-slate-600 font-medium">Dirección de Tecnologías de Información</span>
      </div>

      <div class="flex items-center gap-3 text-slate-500">
        <span class="hover:text-slate-800 transition-colors cursor-pointer">Mesa de Ayuda TI</span>
        <span>•</span>
        <span class="hover:text-slate-800 transition-colors cursor-pointer">Soporte Técnico</span>
        <span>•</span>
        <span class="font-mono text-[11px] text-slate-400">v2.4</span>
      </div>
    </footer>

  </div>
</template>

<style scoped>
/* Estilos resueltos de forma nativa con Tailwind CSS v4 */
</style>

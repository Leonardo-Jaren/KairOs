<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

// Obtener detalles del usuario autenticado
const user = computed(() => authStore.user);

// Tarjetas de resumen conceptuales del sistema
const stats = [
  { title: 'Total Equipos', value: '48', desc: 'Hardware registrado en el sistema', color: 'border-l-4 border-kairos-blue bg-white/5' },
  { title: 'Incidencias Activas', value: '5', desc: 'Pendientes por resolver', color: 'border-l-4 border-red-500 bg-white/5' },
  { title: 'Espacios Habilitados', value: '12', desc: 'Aulas, pabellones y laboratorios', color: 'border-l-4 border-emerald-500 bg-white/5' },
  { title: 'Licencias de Software', value: '18', desc: 'Productos vigentes registrados', color: 'border-l-4 border-amber-500 bg-white/5' }
];
</script>

<template>
  <div class="w-full flex flex-col gap-8">
    
    <!-- Bienvenida Personalizada -->
    <section class="flex flex-col gap-2">
      <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-wide">
        Bienvenido, {{ user ? user.nombre : 'Usuario' }}
      </h1>
      <p class="text-white/60 text-sm md:text-base">
        Este es tu panel central de KairOs. Desde aquí puedes gestionar los equipos de hardware, espacios de campus, incidencias y control de software.
      </p>
    </section>

    <!-- Tarjetas de Resumen Estadistico con micro-animaciones -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div 
        v-for="stat in stats" 
        :key="stat.title"
        :class="[stat.color]"
        class="p-6 rounded-r-xl shadow transition-all duration-300 hover:scale-[1.02] hover:bg-white/10"
      >
        <span class="text-xs font-bold text-white/50 uppercase tracking-widest block mb-1">
          {{ stat.title }}
        </span>
        <span class="text-3xl font-extrabold text-white block mb-2">
          {{ stat.value }}
        </span>
        <span class="text-xs text-white/60">
          {{ stat.desc }}
        </span>
      </div>
    </section>

    <!-- Seccion de Actividad Reciente Conceptual -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Panel de Incidencias -->
      <div class="lg:col-span-2 bg-kairos-navy p-6 rounded-xl border border-white/5 flex flex-col gap-4">
        <h3 class="text-lg font-semibold text-white uppercase tracking-wider border-b border-white/5 pb-3">
          Incidencias Críticas Recientes
        </h3>
        
        <div class="flex flex-col gap-3">
          <!-- Incidencia 1 -->
          <div class="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors duration-200">
            <div class="flex flex-col">
              <span class="text-sm font-semibold text-white">Falla en proyector de Aula Magna 301</span>
              <span class="text-xs text-white/50">Reportado hace 2 horas por Técnico</span>
            </div>
            <span class="px-2.5 py-1 rounded text-xs font-bold bg-red-500/10 text-red-400 uppercase">Alta</span>
          </div>

          <!-- Incidencia 2 -->
          <div class="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors duration-200">
            <div class="flex flex-col">
              <span class="text-sm font-semibold text-white">Actualización de RAM requerida en Servidor Principal</span>
              <span class="text-xs text-white/50">Reportado hace 1 día por Admin</span>
            </div>
            <span class="px-2.5 py-1 rounded text-xs font-bold bg-amber-500/10 text-amber-400 uppercase">Media</span>
          </div>
        </div>
      </div>

      <!-- Panel de Licencias Expirando -->
      <div class="bg-kairos-navy p-6 rounded-xl border border-white/5 flex flex-col gap-4">
        <h3 class="text-lg font-semibold text-white uppercase tracking-wider border-b border-white/5 pb-3">
          Alertas de Licencias
        </h3>
        
        <div class="flex flex-col gap-3">
          <div class="p-4 rounded-lg bg-amber-500/5 border border-amber-500/15 flex flex-col">
            <span class="text-sm font-semibold text-amber-400">Licencia MATLAB expira pronto</span>
            <span class="text-xs text-white/60 mt-1">Vence en 5 días (Quedan 3 puestos activos)</span>
          </div>

          <div class="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/15 flex flex-col">
            <span class="text-sm font-semibold text-emerald-400">Licencia JetBrains renovada</span>
            <span class="text-xs text-white/60 mt-1">Renovación exitosa para 50 puestos técnicos</span>
          </div>
        </div>
      </div>

    </section>

  </div>
</template>

<style scoped>
/* Los estilos se resuelven completamente con clases de Tailwind CSS */
</style>

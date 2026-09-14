<script setup>
import {
  Activity,
  ArrowRight,
  Building2,
  CalendarDays,
  CheckCircle2,
  Clock3,
  MonitorCog,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UsersRound,
  Wrench,
  Zap,
} from '@lucide/vue';

import DashboardMetricCard from '@/components/dashboard/DashboardMetricCard.vue';
import DashboardProgressRow from '@/components/dashboard/DashboardProgressRow.vue';
import { useDashboard } from '@/composables/dashboard/useDashboard';

const {
  loading,
  error,
  warning,
  canViewOperations,
  firstName,
  roleLabel,
  todayLabel,
  lastUpdatedLabel,
  equipmentStats,
  spaceStats,
  userStats,
  maintenanceStats,
  equipmentOperationalRate,
  activeSpacesRate,
  activeUsersRate,
  openMaintenance,
  maintenanceResolutionRate,
  equipmentDistribution,
  maintenanceDistribution,
  recentMaintenance,
  topSpaces,
  formatDate,
  getDateParts,
  loadDashboard,
} = useDashboard();

const maintenanceStateClasses = {
  pendiente: 'bg-amber-50 text-amber-800 border border-amber-200/80',
  en_proceso: 'bg-primary-50 text-primary-800 border border-primary-200/80',
  resuelto: 'bg-emerald-50 text-emerald-800 border border-emerald-200/80',
  cancelado: 'bg-slate-100 text-slate-700 border border-slate-200',
};

// Obtener el valor maximo de equipos entre los espacios destacados para calcular las barras de capacidad relativa
const maxEquipmentInSpaces = () => {
  if (!topSpaces.value.length) return 1;
  return Math.max(...topSpaces.value.map((s) => s.cantidad_equipos || 1));
};
</script>

<template>
  <div class="flex w-full flex-col gap-6">

    <!-- 1. Cabecera de mando operativo institucional -->
    <section class="relative overflow-hidden rounded-2xl bg-secondary-950 px-6 py-6 text-white shadow-md border border-secondary-800/90 sm:px-8 sm:py-7 select-none">
      <!-- Trama arquitectonica sutil sin neones de IA -->
      <div
        class="absolute inset-0 opacity-[0.06] pointer-events-none"
        style="background-image: radial-gradient(#ffffff 1px, transparent 1px); background-size: 22px 22px;"
      />

      <div class="relative z-10 flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
        <div>
          <!-- Insignias superiores de contexto institucional -->
          <div class="mb-3.5 flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold text-primary-200 backdrop-blur-xs">
              <ShieldCheck :size="14" class="text-primary-400" />
              {{ roleLabel }} • Campus Central
            </span>
            <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400">
              <CalendarDays :size="13" />
              {{ todayLabel }}
            </span>
          </div>

          <p class="text-xs font-bold uppercase tracking-wider text-primary-400">
            Centro de Control Operativo
          </p>
          <h1 class="mt-1 text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Bienvenido, {{ firstName }}.
          </h1>
          <p class="mt-2 max-w-2xl text-xs sm:text-sm text-slate-300 leading-relaxed">
            Supervisión integral de laboratorios, disponibilidad de hardware y órdenes de servicio técnico.
          </p>
        </div>

        <!-- Panel lateral de sincronizacion e indicador de red en vivo -->
        <div v-if="canViewOperations" class="flex shrink-0 items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur-xs">
          <div class="grid size-10 place-items-center rounded-lg bg-emerald-500/15 text-emerald-300">
            <Activity :size="20" />
          </div>
          <div class="pr-2">
            <div class="flex items-center gap-1.5">
              <span class="size-2 rounded-full bg-emerald-400 animate-pulse" />
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-300">Red Operativa</span>
            </div>
            <p class="mt-0.5 text-xs font-semibold text-white">Sincronizado: {{ lastUpdatedLabel }}</p>
          </div>
          <button
            type="button"
            class="grid size-9 place-items-center rounded-lg border border-white/10 text-slate-300 transition-colors hover:bg-white/10 hover:text-white disabled:cursor-wait disabled:opacity-50 cursor-pointer"
            :disabled="loading"
            aria-label="Actualizar indicadores"
            title="Actualizar indicadores"
            @click="loadDashboard"
          >
            <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </section>

    <!-- Alerta accesible en caso de fallo o advertencia de conexion -->
    <div
      v-if="error || warning"
      class="flex items-start gap-3 rounded-xl border px-4 py-3 text-xs sm:text-sm"
      :class="error ? 'border-danger-200 bg-danger-50 text-danger-800' : 'border-warning-200 bg-warning-50 text-warning-800'"
      role="status"
    >
      <Activity :size="18" class="mt-0.5 shrink-0" />
      <span>{{ error || warning }}</span>
    </div>

    <!-- 2. Bloque principal para roles con permisos de gestion (Admin y Tecnico) -->
    <template v-if="canViewOperations">

      <!-- Cuadricula de 4 indicadores KPI clave con enlaces directos -->
      <section aria-labelledby="dashboard-metrics-title">
        <div class="mb-3.5 flex items-end justify-between gap-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-primary-600">Telemetría Principal</p>
            <h2 id="dashboard-metrics-title" class="text-lg font-extrabold text-slate-900">Estado general de infraestructura</h2>
          </div>
          <p class="hidden text-xs text-slate-400 sm:block">Métricas consolidadas de la institución</p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <DashboardMetricCard
            label="Equipos registrados"
            :value="equipmentStats.total"
            :description="`${equipmentStats.en_uso} terminales disponibles para uso docente y libre`"
            :helper="`${equipmentOperationalRate}% operativos`"
            :icon="MonitorCog"
            tone="blue"
            to="/equipos"
            :loading="loading && !equipmentStats.total"
          />
          <DashboardMetricCard
            label="Espacios activos"
            :value="spaceStats.activos"
            :description="`${spaceStats.laboratorios} laboratorios especializados en ${spaceStats.total} salas`"
            :helper="`${activeSpacesRate}% habilitados`"
            :icon="Building2"
            tone="emerald"
            to="/espacios"
            :loading="loading && !spaceStats.total"
          />
          <DashboardMetricCard
            label="Mantenimientos abiertos"
            :value="openMaintenance"
            :description="`${maintenanceStats.pendientes} pendientes de atención y ${maintenanceStats.en_proceso} en curso`"
            :helper="`${maintenanceResolutionRate}% resueltos`"
            :icon="Wrench"
            tone="amber"
            to="/mantenimiento"
            :loading="loading && !maintenanceStats.total"
          />
          <DashboardMetricCard
            label="Usuarios del sistema"
            :value="userStats.activos"
            :description="`${userStats.tecnicos} técnicos asignados y ${userStats.docentes} docentes acreditados`"
            :helper="`${activeUsersRate}% habilitados`"
            :icon="UsersRound"
            tone="violet"
            to="/usuarios"
            :loading="loading && !userStats.total"
          />
        </div>
      </section>

      <!-- 3. Signature Element & Health Bento Grid -->
      <section class="grid grid-cols-1 gap-5 xl:grid-cols-5">

        <!-- Card A: Salud del parque informatico con barra segmentada (Signature) -->
        <article class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs sm:p-6 xl:col-span-3 flex flex-col justify-between">
          <div>
            <!-- Encabezado de la tarjeta -->
            <div class="mb-5 flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Parque Tecnológico</p>
                <h2 class="mt-0.5 text-lg font-extrabold text-slate-900">Salud del Inventario de Hardware</h2>
                <p class="mt-1 text-xs text-slate-500">Distribución de los {{ equipmentStats.total }} dispositivos de laboratorio según su condición operativa.</p>
              </div>
              <div class="rounded-xl bg-emerald-50 border border-emerald-200/80 px-3.5 py-2 text-right shrink-0">
                <p class="text-xl font-extrabold text-emerald-700 tabular-nums">{{ equipmentOperationalRate }}%</p>
                <p class="text-[10px] font-bold uppercase tracking-wide text-emerald-600">Operatividad</p>
              </div>
            </div>

            <!-- Signature Element: Barra Macro Segmentada Proporcional -->
            <div class="mb-6 space-y-2 select-none">
              <div class="flex items-center justify-between text-xs text-slate-500 font-medium">
                <span>Composición global del parque</span>
                <span>Total: {{ equipmentStats.total }} equipos</span>
              </div>
              <div class="h-3.5 w-full overflow-hidden rounded-full bg-slate-100 flex shadow-inner">
                <div
                  v-if="equipmentStats.en_uso"
                  class="h-full bg-emerald-500 transition-all duration-500 hover:opacity-90"
                  :style="{ width: `${equipmentStats.total > 0 ? (equipmentStats.en_uso / equipmentStats.total) * 100 : 0}%` }"
                  :title="`En uso: ${equipmentStats.en_uso}`"
                />
                <div
                  v-if="equipmentStats.en_mantenimiento"
                  class="h-full bg-amber-500 transition-all duration-500 hover:opacity-90"
                  :style="{ width: `${equipmentStats.total > 0 ? (equipmentStats.en_mantenimiento / equipmentStats.total) * 100 : 0}%` }"
                  :title="`En mantenimiento: ${equipmentStats.en_mantenimiento}`"
                />
                <div
                  v-if="equipmentDistribution.find(d => d.tone === 'danger')?.value"
                  class="h-full bg-red-500 transition-all duration-500 hover:opacity-90"
                  :style="{ width: `${equipmentStats.total > 0 ? ((equipmentDistribution.find(d => d.tone === 'danger')?.value || 0) / equipmentStats.total) * 100 : 0}%` }"
                  :title="`Dañados: ${equipmentDistribution.find(d => d.tone === 'danger')?.value}`"
                />
                <div
                  v-if="equipmentStats.de_baja"
                  class="h-full bg-slate-400 transition-all duration-500 hover:opacity-90"
                  :style="{ width: `${equipmentStats.total > 0 ? (equipmentStats.de_baja / equipmentStats.total) * 100 : 0}%` }"
                  :title="`De baja: ${equipmentStats.de_baja}`"
                />
              </div>
            </div>

            <!-- Desglose cuantitativo por estado -->
            <div class="grid gap-4 sm:grid-cols-2">
              <DashboardProgressRow
                v-for="item in equipmentDistribution"
                :key="item.label"
                :label="item.label"
                :value="item.value"
                :total="equipmentStats.total"
                :tone="item.tone"
              />
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs text-slate-400">Ver componentes, marcas y números de serie</span>
            <RouterLink to="/equipos" class="inline-flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-700 transition-colors">
              Explorar inventario completo
              <ArrowRight :size="14" />
            </RouterLink>
          </div>
        </article>

        <!-- Card B: Triage y Mantenimiento Tecnico -->
        <article class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs sm:p-6 xl:col-span-2 flex flex-col justify-between">
          <div>
            <div class="mb-5 flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Mesa de Soporte</p>
                <h2 class="mt-0.5 text-lg font-extrabold text-slate-900">Flujo de Mantenimiento</h2>
                <p class="mt-1 text-xs text-slate-500">{{ maintenanceStats.total }} órdenes de trabajo registradas.</p>
              </div>
              <div class="grid size-10 place-items-center rounded-xl bg-amber-50 text-amber-600 border border-amber-200/80 shrink-0">
                <Zap :size="19" />
              </div>
            </div>

            <!-- Resumen de resolucion -->
            <div class="mb-5 flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <div class="text-left">
                <p class="text-xs text-slate-500 font-medium">Tasa de resolución</p>
                <p class="text-lg font-extrabold text-slate-900 tabular-nums">{{ maintenanceResolutionRate }}%</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-slate-500 font-medium">Cola activa</p>
                <p class="text-lg font-extrabold text-amber-700 tabular-nums">{{ openMaintenance }} tickets</p>
              </div>
            </div>

            <!-- Desglose de estados de mantenimiento -->
            <div class="flex flex-col gap-3.5">
              <DashboardProgressRow
                v-for="item in maintenanceDistribution"
                :key="item.label"
                :label="item.label"
                :value="item.value"
                :total="maintenanceStats.total"
                :tone="item.tone"
              />
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span class="text-xs text-slate-400">Gestión de tickets y técnicos</span>
            <RouterLink to="/mantenimiento" class="inline-flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-700 transition-colors">
              Gestionar órdenes
              <ArrowRight :size="14" />
            </RouterLink>
          </div>
        </article>

      </section>

      <!-- 4. Actividad reciente de tickets y ranking de capacidad de laboratorios -->
      <section class="grid grid-cols-1 gap-5 xl:grid-cols-3">

        <!-- Card C: Bitacora de mantenimientos recientes (2 columnas) -->
        <article class="overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-xs xl:col-span-2 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4 sm:px-6">
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Seguimiento Operativo</p>
                <h2 class="mt-0.5 text-base sm:text-lg font-extrabold text-slate-900">Actividad de Mantenimiento Reciente</h2>
              </div>
              <div class="flex items-center gap-2">
                <Clock3 :size="18" class="text-slate-400" />
              </div>
            </div>

            <!-- Skeleton loader -->
            <div v-if="loading && !recentMaintenance.length" class="divide-y divide-slate-100">
              <div v-for="index in 4" :key="index" class="flex items-center gap-4 px-5 py-4 sm:px-6">
                <div class="size-10 animate-pulse rounded-xl bg-slate-100 shrink-0" />
                <div class="flex-1">
                  <div class="h-4 w-1/3 animate-pulse rounded bg-slate-100" />
                  <div class="mt-2 h-3 w-2/3 animate-pulse rounded bg-slate-100" />
                </div>
              </div>
            </div>

            <!-- Listado de tickets -->
            <div v-else-if="recentMaintenance.length" class="divide-y divide-slate-100">
              <div
                v-for="ticket in recentMaintenance"
                :key="ticket.id"
                class="group flex flex-col gap-3 px-5 py-3.5 transition-colors hover:bg-slate-50/80 sm:flex-row sm:items-center sm:px-6"
              >
                <!-- Fecha estilizada tipo calendario perfectamente centrada -->
                <div class="flex flex-col items-center justify-center size-11 shrink-0 rounded-xl bg-slate-100 border border-slate-200/70 leading-none select-none group-hover:bg-primary-50 group-hover:border-primary-200 transition-colors">
                  <span class="text-sm font-extrabold text-slate-800 tabular-nums group-hover:text-primary-700">
                    {{ getDateParts(ticket.fecha).day }}
                  </span>
                  <span class="text-[9px] font-bold uppercase tracking-wider text-slate-500 mt-0.5 group-hover:text-primary-600">
                    {{ getDateParts(ticket.fecha).month }}
                  </span>
                </div>

                <!-- Informacion del equipo e incidencia -->
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-bold text-slate-900 text-sm">{{ ticket.equipo?.codigo }}</p>
                    <span class="text-xs text-slate-400 font-medium">{{ ticket.tipo_mantenimiento_display }}</span>
                  </div>
                  <p class="mt-0.5 truncate text-xs text-slate-500">{{ ticket.descripcion }}</p>
                </div>

                <!-- Estado del ticket y tecnico asignado -->
                <div class="flex items-center justify-between gap-3 sm:flex-col sm:items-end shrink-0">
                  <span
                    class="rounded-full px-2.5 py-0.5 text-[11px] font-bold"
                    :class="maintenanceStateClasses[ticket.estado] ?? 'bg-slate-100 text-slate-700 border border-slate-200'"
                  >
                    {{ ticket.estado_display }}
                  </span>
                  <span class="text-[11px] text-slate-400">{{ ticket.tecnico_responsable }}</span>
                </div>
              </div>
            </div>

            <!-- Estado vacio si no hay tickets -->
            <div v-else class="px-6 py-12 text-center select-none">
              <CheckCircle2 :size="32" class="mx-auto text-emerald-500" />
              <p class="mt-2 text-sm font-semibold text-slate-700">Sin mantenimientos pendientes</p>
              <p class="text-xs text-slate-400">Todos los equipos registrados se encuentran en servicio regular.</p>
            </div>
          </div>

          <div class="p-4 sm:px-6 border-t border-slate-100 text-right">
            <RouterLink to="/mantenimiento" class="inline-flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-700 transition-colors">
              Historial completo de mantenimiento
              <ArrowRight :size="14" />
            </RouterLink>
          </div>
        </article>

        <!-- Card D: Top espacios tecnologicos con barra relativa de capacidad (1 columna) -->
        <article class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs sm:p-6 flex flex-col justify-between">
          <div>
            <div class="mb-4 flex items-start justify-between">
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Capacidad Instalada</p>
                <h2 class="mt-0.5 text-base sm:text-lg font-extrabold text-slate-900">Equipos por Espacio</h2>
              </div>
              <Building2 :size="18" class="text-slate-400" />
            </div>

            <!-- Lista de espacios destacados -->
            <div v-if="topSpaces.length" class="flex flex-col gap-2.5 select-none">
              <div
                v-for="(space, index) in topSpaces"
                :key="space.id"
                class="flex flex-col gap-1.5 rounded-xl border border-slate-100 p-3 hover:bg-slate-50/60 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2.5 min-w-0">
                    <span class="grid size-6 shrink-0 place-items-center rounded-md bg-slate-100 text-[11px] font-extrabold text-slate-600">
                      {{ index + 1 }}
                    </span>
                    <div class="min-w-0">
                      <p class="truncate text-xs font-bold text-slate-900">{{ space.codigo_espacio }}</p>
                      <p class="truncate text-[11px] text-slate-400">{{ space.pabellon }} • {{ space.tipo_display }}</p>
                    </div>
                  </div>
                  <div class="text-right shrink-0">
                    <span class="text-sm font-extrabold text-slate-900 tabular-nums">{{ space.cantidad_equipos }}</span>
                    <span class="text-[10px] text-slate-400 ml-1">equipos</span>
                  </div>
                </div>

                <!-- Barra de proporcion de capacidad relativa -->
                <div class="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full bg-primary-500 transition-all duration-500"
                    :style="{ width: `${(space.cantidad_equipos / maxEquipmentInSpaces()) * 100}%` }"
                  />
                </div>
              </div>
            </div>

            <div v-else-if="loading" class="flex flex-col gap-3">
              <div v-for="index in 4" :key="index" class="h-14 animate-pulse rounded-xl bg-slate-100" />
            </div>

            <p v-else class="py-8 text-center text-xs text-slate-400">No hay espacios disponibles.</p>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 text-right">
            <RouterLink to="/espacios" class="inline-flex items-center gap-1.5 text-xs font-bold text-primary-600 hover:text-primary-700 transition-colors">
              Ver todos los espacios
              <ArrowRight :size="14" />
            </RouterLink>
          </div>
        </article>

      </section>

      <!-- 5. Hub de accesos directos -->
      <section class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-xs sm:p-6 select-none">
        <div class="mb-4">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Flujos de Trabajo</p>
          <h2 class="mt-0.5 text-base sm:text-lg font-extrabold text-slate-900">Accesos Rápidos al Sistema</h2>
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <RouterLink
            to="/equipos"
            class="group flex items-center gap-3.5 rounded-xl border border-slate-200/90 p-4 transition-all duration-200 hover:border-primary-300 hover:bg-primary-50/40 hover:shadow-xs"
          >
            <div class="grid size-11 place-items-center rounded-xl bg-primary-50 text-primary-600 transition-colors group-hover:bg-primary-500 group-hover:text-white">
              <MonitorCog :size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-slate-900 group-hover:text-primary-700 transition-colors">Inventario</p>
              <p class="text-xs text-slate-500">Terminales y hardware</p>
            </div>
            <ArrowRight :size="15" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-primary-600 transition-all" />
          </RouterLink>

          <RouterLink
            to="/mantenimiento"
            class="group flex items-center gap-3.5 rounded-xl border border-slate-200/90 p-4 transition-all duration-200 hover:border-amber-300 hover:bg-amber-50/40 hover:shadow-xs"
          >
            <div class="grid size-11 place-items-center rounded-xl bg-amber-50 text-amber-600 transition-colors group-hover:bg-amber-500 group-hover:text-white">
              <Wrench :size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-slate-900 group-hover:text-amber-700 transition-colors">Mantenimiento</p>
              <p class="text-xs text-slate-500">Atender y resolver tickets</p>
            </div>
            <ArrowRight :size="15" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-amber-600 transition-all" />
          </RouterLink>

          <RouterLink
            to="/espacios"
            class="group flex items-center gap-3.5 rounded-xl border border-slate-200/90 p-4 transition-all duration-200 hover:border-emerald-300 hover:bg-emerald-50/40 hover:shadow-xs"
          >
            <div class="grid size-11 place-items-center rounded-xl bg-emerald-50 text-emerald-600 transition-colors group-hover:bg-emerald-500 group-hover:text-white">
              <Building2 :size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">Espacios</p>
              <p class="text-xs text-slate-500">Salas, aulas y croquis</p>
            </div>
            <ArrowRight :size="15" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-emerald-600 transition-all" />
          </RouterLink>

          <RouterLink
            to="/usuarios"
            class="group flex items-center gap-3.5 rounded-xl border border-slate-200/90 p-4 transition-all duration-200 hover:border-violet-300 hover:bg-violet-50/40 hover:shadow-xs"
          >
            <div class="grid size-11 place-items-center rounded-xl bg-violet-50 text-violet-600 transition-colors group-hover:bg-violet-500 group-hover:text-white">
              <UsersRound :size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-slate-900 group-hover:text-violet-700 transition-colors">Usuarios</p>
              <p class="text-xs text-slate-500">Acreditaciones y permisos</p>
            </div>
            <ArrowRight :size="15" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-violet-600 transition-all" />
          </RouterLink>
        </div>
      </section>

    </template>

    <!-- 6. Vista simplificada para roles sin permisos de administracion tecnica (ej. Docente / Usuario) -->
    <section v-else class="grid min-h-80 place-items-center rounded-2xl border border-slate-200/90 bg-white p-8 text-center shadow-xs select-none">
      <div class="max-w-md">
        <div class="mx-auto grid size-14 place-items-center rounded-2xl bg-primary-50 text-primary-600 border border-primary-200/80">
          <ShieldCheck :size="28" />
        </div>
        <h2 class="mt-4 text-xl font-extrabold text-slate-900">Sesión Institucional Activa</h2>
        <p class="mt-2 text-xs sm:text-sm leading-relaxed text-slate-500">
          Tu cuenta tiene perfil de {{ roleLabel }}. Las métricas avanzadas y gestión técnica de salas están reservadas para administradores y técnicos de soporte.
        </p>
        <div class="mt-6 flex justify-center gap-3">
          <RouterLink
            to="/software"
            class="inline-flex items-center gap-2 rounded-xl bg-primary-500 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-primary-600 transition-colors cursor-pointer"
          >
            Consultar Software Institucional
            <ArrowRight :size="14" />
          </RouterLink>
        </div>
      </div>
    </section>

  </div>
</template>

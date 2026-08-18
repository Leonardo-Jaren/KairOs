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
  loadDashboard,
} = useDashboard();

const maintenanceStateClasses = {
  pendiente: 'bg-warning-50 text-warning-700 ring-warning-600/10',
  en_proceso: 'bg-primary-50 text-primary-700 ring-primary-600/10',
  resuelto: 'bg-success-50 text-success-700 ring-success-600/10',
  cancelado: 'bg-slate-100 text-slate-600 ring-slate-500/10',
};
</script>

<template>
  <div class="flex w-full flex-col gap-6">
    <section class="relative overflow-hidden rounded-3xl bg-secondary-950 px-5 py-6 text-white shadow-xl shadow-secondary-950/10 sm:px-7 sm:py-7 lg:px-8">
      <div class="pointer-events-none absolute -right-20 -top-24 size-72 rounded-full bg-primary-500/15 blur-3xl" />
      <div class="pointer-events-none absolute -bottom-24 left-1/3 size-56 rounded-full bg-success-500/10 blur-3xl" />

      <div class="relative flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
        <div>
          <div class="mb-4 flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-primary-200">
              <ShieldCheck :size="15" />
              {{ roleLabel }}
            </span>
            <span class="inline-flex items-center gap-2 text-xs font-medium text-white/45">
              <CalendarDays :size="14" />
              {{ todayLabel }}
            </span>
          </div>
          <p class="text-sm font-semibold text-primary-300">Resumen operativo</p>
          <h1 class="mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl">
            Hola, {{ firstName }}. Todo bajo control.
          </h1>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-white/55 sm:text-base">
            Supervisa la disponibilidad tecnológica, los espacios y la atención de mantenimiento desde una sola vista.
          </p>
        </div>

        <div v-if="canViewOperations" class="flex shrink-0 items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-3 backdrop-blur-sm">
          <div class="grid size-11 place-items-center rounded-xl bg-success-500/15 text-success-300">
            <Activity :size="21" />
          </div>
          <div class="pr-2">
            <p class="text-[10px] font-bold uppercase tracking-[0.16em] text-white/35">Última actualización</p>
            <p class="mt-0.5 text-sm font-semibold text-white">Hoy, {{ lastUpdatedLabel }}</p>
          </div>
          <button
            type="button"
            class="grid size-10 place-items-center rounded-xl border border-white/10 text-white/60 transition-colors hover:bg-white/10 hover:text-white disabled:cursor-wait disabled:opacity-50"
            :disabled="loading"
            aria-label="Actualizar indicadores"
            title="Actualizar indicadores"
            @click="loadDashboard"
          >
            <RefreshCw :size="18" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </section>

    <div
      v-if="error || warning"
      class="flex items-start gap-3 rounded-2xl border px-4 py-3 text-sm"
      :class="error ? 'border-danger-200 bg-danger-50 text-danger-700' : 'border-warning-200 bg-warning-50 text-warning-700'"
      role="status"
    >
      <Activity :size="18" class="mt-0.5 shrink-0" />
      <span>{{ error || warning }}</span>
    </div>

    <template v-if="canViewOperations">
      <section aria-labelledby="dashboard-metrics-title">
        <div class="mb-4 flex items-end justify-between gap-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-[0.18em] text-primary-600">Indicadores clave</p>
            <h2 id="dashboard-metrics-title" class="mt-1 text-xl font-extrabold text-slate-950">Estado general de la operación</h2>
          </div>
          <p class="hidden text-xs text-slate-400 sm:block">Datos consolidados del sistema</p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <DashboardMetricCard
            label="Equipos registrados"
            :value="equipmentStats.total"
            :description="`${equipmentStats.en_uso} dispositivos disponibles para operación`"
            :helper="`${equipmentOperationalRate}% operativos`"
            :icon="MonitorCog"
            tone="blue"
            :loading="loading && !equipmentStats.total"
          />
          <DashboardMetricCard
            label="Espacios activos"
            :value="spaceStats.activos"
            :description="`${spaceStats.laboratorios} laboratorios dentro de ${spaceStats.total} espacios`"
            :helper="`${activeSpacesRate}% habilitados`"
            :icon="Building2"
            tone="emerald"
            :loading="loading && !spaceStats.total"
          />
          <DashboardMetricCard
            label="Mantenimientos abiertos"
            :value="openMaintenance"
            :description="`${maintenanceStats.pendientes} pendientes y ${maintenanceStats.en_proceso} en proceso`"
            :helper="`${maintenanceResolutionRate}% resueltos`"
            :icon="Wrench"
            tone="amber"
            :loading="loading && !maintenanceStats.total"
          />
          <DashboardMetricCard
            label="Usuarios activos"
            :value="userStats.activos"
            :description="`${userStats.tecnicos} técnicos y ${userStats.docentes} docentes registrados`"
            :helper="`${activeUsersRate}% habilitados`"
            :icon="UsersRound"
            tone="violet"
            :loading="loading && !userStats.total"
          />
        </div>
      </section>

      <section class="grid grid-cols-1 gap-5 xl:grid-cols-5">
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 xl:col-span-3">
          <div class="mb-6 flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Inventario</p>
              <h2 class="mt-1 text-lg font-extrabold text-slate-950">Salud de los equipos</h2>
              <p class="mt-1 text-sm text-slate-500">Distribución por estado operativo actual.</p>
            </div>
            <div class="rounded-xl bg-success-50 px-3 py-2 text-right">
              <p class="text-2xl font-extrabold text-success-700">{{ equipmentOperationalRate }}%</p>
              <p class="text-[10px] font-bold uppercase tracking-wide text-success-600">Disponibilidad</p>
            </div>
          </div>

          <div class="grid gap-5 sm:grid-cols-2">
            <DashboardProgressRow
              v-for="item in equipmentDistribution"
              :key="item.label"
              :label="item.label"
              :value="item.value"
              :total="equipmentStats.total"
              :tone="item.tone"
            />
          </div>

          <RouterLink to="/equipos" class="mt-6 inline-flex items-center gap-2 text-sm font-bold text-primary-600 hover:text-primary-700">
            Revisar inventario
            <ArrowRight :size="16" />
          </RouterLink>
        </article>

        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 xl:col-span-2">
          <div class="mb-6 flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Atención técnica</p>
              <h2 class="mt-1 text-lg font-extrabold text-slate-950">Flujo de mantenimiento</h2>
              <p class="mt-1 text-sm text-slate-500">{{ maintenanceStats.total }} tickets registrados.</p>
            </div>
            <div class="grid size-11 place-items-center rounded-xl bg-primary-50 text-primary-600">
              <Zap :size="21" />
            </div>
          </div>

          <div class="flex flex-col gap-4">
            <DashboardProgressRow
              v-for="item in maintenanceDistribution"
              :key="item.label"
              :label="item.label"
              :value="item.value"
              :total="maintenanceStats.total"
              :tone="item.tone"
            />
          </div>

          <RouterLink to="/mantenimiento" class="mt-6 inline-flex items-center gap-2 text-sm font-bold text-primary-600 hover:text-primary-700">
            Gestionar mantenimientos
            <ArrowRight :size="16" />
          </RouterLink>
        </article>
      </section>

      <section class="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <article class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm xl:col-span-2">
          <div class="flex items-center justify-between border-b border-slate-100 px-5 py-5 sm:px-6">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Seguimiento</p>
              <h2 class="mt-1 text-lg font-extrabold text-slate-950">Actividad de mantenimiento reciente</h2>
            </div>
            <Clock3 :size="20" class="text-slate-300" />
          </div>

          <div v-if="loading && !recentMaintenance.length" class="divide-y divide-slate-100">
            <div v-for="index in 4" :key="index" class="flex items-center gap-4 px-5 py-4 sm:px-6">
              <div class="size-10 animate-pulse rounded-xl bg-slate-100" />
              <div class="flex-1">
                <div class="h-4 w-1/3 animate-pulse rounded bg-slate-100" />
                <div class="mt-2 h-3 w-2/3 animate-pulse rounded bg-slate-100" />
              </div>
            </div>
          </div>

          <div v-else-if="recentMaintenance.length" class="divide-y divide-slate-100">
            <div
              v-for="ticket in recentMaintenance"
              :key="ticket.id"
              class="group flex flex-col gap-3 px-5 py-4 transition-colors hover:bg-slate-50/80 sm:flex-row sm:items-center sm:px-6"
            >
              <div class="grid size-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-xs font-extrabold text-slate-600 group-hover:bg-primary-50 group-hover:text-primary-600">
                {{ formatDate(ticket.fecha) }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-bold text-slate-900">{{ ticket.equipo?.codigo }}</p>
                  <span class="text-xs text-slate-400">{{ ticket.tipo_mantenimiento_display }}</span>
                </div>
                <p class="mt-1 truncate text-sm text-slate-500">{{ ticket.descripcion }}</p>
              </div>
              <div class="flex items-center justify-between gap-3 sm:flex-col sm:items-end">
                <span class="rounded-full px-2.5 py-1 text-[11px] font-bold ring-1 ring-inset" :class="maintenanceStateClasses[ticket.estado]">
                  {{ ticket.estado_display }}
                </span>
                <span class="text-[11px] text-slate-400">{{ ticket.tecnico_responsable }}</span>
              </div>
            </div>
          </div>

          <div v-else class="px-6 py-12 text-center">
            <CheckCircle2 :size="32" class="mx-auto text-success-400" />
            <p class="mt-3 text-sm font-semibold text-slate-600">No hay mantenimientos registrados.</p>
          </div>
        </article>

        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="mb-5 flex items-start justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Distribución</p>
              <h2 class="mt-1 text-lg font-extrabold text-slate-950">Equipos por espacio</h2>
            </div>
            <Building2 :size="20" class="text-slate-300" />
          </div>

          <div v-if="topSpaces.length" class="flex flex-col gap-3">
            <div v-for="(space, index) in topSpaces" :key="space.id" class="flex items-center gap-3 rounded-xl border border-slate-100 p-3">
              <div class="grid size-9 shrink-0 place-items-center rounded-lg bg-slate-50 text-xs font-extrabold text-slate-400">
                {{ index + 1 }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-bold text-slate-800">{{ space.codigo_espacio }}</p>
                <p class="truncate text-xs text-slate-400">{{ space.pabellon }} · {{ space.tipo_display }}</p>
              </div>
              <div class="text-right">
                <p class="text-lg font-extrabold text-slate-900">{{ space.cantidad_equipos }}</p>
                <p class="text-[10px] font-medium text-slate-400">equipos</p>
              </div>
            </div>
          </div>

          <div v-else-if="loading" class="flex flex-col gap-3">
            <div v-for="index in 5" :key="index" class="h-16 animate-pulse rounded-xl bg-slate-100" />
          </div>

          <p v-else class="py-8 text-center text-sm text-slate-400">No hay espacios disponibles.</p>

          <RouterLink to="/espacios" class="mt-5 inline-flex items-center gap-2 text-sm font-bold text-primary-600 hover:text-primary-700">
            Ver todos los espacios
            <ArrowRight :size="16" />
          </RouterLink>
        </article>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="mb-5">
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Accesos rápidos</p>
          <h2 class="mt-1 text-lg font-extrabold text-slate-950">Continuar trabajando</h2>
        </div>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <RouterLink to="/equipos" class="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 hover:border-primary-200 hover:bg-primary-50/50">
            <div class="grid size-10 place-items-center rounded-xl bg-primary-50 text-primary-600"><MonitorCog :size="19" /></div>
            <div class="min-w-0 flex-1"><p class="text-sm font-bold text-slate-800">Inventario</p><p class="text-xs text-slate-400">Consultar equipos</p></div>
            <ArrowRight :size="16" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-primary-500" />
          </RouterLink>
          <RouterLink to="/mantenimiento" class="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 hover:border-warning-200 hover:bg-warning-50/50">
            <div class="grid size-10 place-items-center rounded-xl bg-warning-50 text-warning-600"><Wrench :size="19" /></div>
            <div class="min-w-0 flex-1"><p class="text-sm font-bold text-slate-800">Mantenimiento</p><p class="text-xs text-slate-400">Atender tickets</p></div>
            <ArrowRight :size="16" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-warning-500" />
          </RouterLink>
          <RouterLink to="/espacios" class="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 hover:border-success-200 hover:bg-success-50/50">
            <div class="grid size-10 place-items-center rounded-xl bg-success-50 text-success-600"><Building2 :size="19" /></div>
            <div class="min-w-0 flex-1"><p class="text-sm font-bold text-slate-800">Espacios</p><p class="text-xs text-slate-400">Revisar ambientes</p></div>
            <ArrowRight :size="16" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-success-500" />
          </RouterLink>
          <RouterLink to="/usuarios" class="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 hover:border-violet-200 hover:bg-violet-50/50">
            <div class="grid size-10 place-items-center rounded-xl bg-violet-50 text-violet-600"><UsersRound :size="19" /></div>
            <div class="min-w-0 flex-1"><p class="text-sm font-bold text-slate-800">Usuarios</p><p class="text-xs text-slate-400">Administrar accesos</p></div>
            <ArrowRight :size="16" class="text-slate-300 group-hover:translate-x-0.5 group-hover:text-violet-500" />
          </RouterLink>
        </div>
      </section>
    </template>

    <section v-else class="grid min-h-80 place-items-center rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
      <div class="max-w-lg">
        <div class="mx-auto grid size-14 place-items-center rounded-2xl bg-primary-50 text-primary-600">
          <ShieldCheck :size="27" />
        </div>
        <h2 class="mt-5 text-2xl font-extrabold text-slate-950">Tu sesión está activa</h2>
        <p class="mt-2 text-sm leading-6 text-slate-500">
          Las métricas operativas están disponibles para administradores y técnicos. Tu acceso permanece protegido según el rol asignado.
        </p>
      </div>
    </section>
  </div>
</template>

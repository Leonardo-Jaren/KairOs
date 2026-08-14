import { computed, onMounted, reactive, ref } from 'vue';

import dashboardService from '@/services/dashboard.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const getResults = (response) => response?.results ?? response ?? [];
const getPercentage = (value, total) => (
  total > 0 ? Math.round((value / total) * 100) : 0
);

export function useDashboard(service = dashboardService) {
  const authStore = useAuthStore();
  const loading = ref(false);
  const error = ref('');
  const warning = ref('');
  const lastUpdated = ref(null);
  const recentMaintenance = ref([]);
  const spaces = ref([]);
  const equipmentStats = reactive({ total: 0, en_uso: 0, en_mantenimiento: 0, de_baja: 0 });
  const spaceStats = reactive({ total: 0, activos: 0, laboratorios: 0, equipos: 0 });
  const userStats = reactive({ total: 0, activos: 0, administradores: 0, tecnicos: 0, docentes: 0 });
  const maintenanceStats = reactive({
    total: 0,
    pendientes: 0,
    en_proceso: 0,
    resueltos: 0,
    cancelados: 0,
    total_tecnicos: 0,
    total_dispositivos: 0,
  });

  const user = computed(() => authStore.user);
  const canViewOperations = computed(() => ['admin', 'tecnico'].includes(user.value?.rol));
  const firstName = computed(() => {
    const name = user.value?.nombre?.trim().split(/\s+/)[0];
    return name ? `${name.charAt(0).toUpperCase()}${name.slice(1)}` : 'Usuario';
  });
  const roleLabel = computed(() => ({
    admin: 'Administrador',
    tecnico: 'Técnico',
    docente: 'Docente',
    usuario: 'Usuario',
  }[user.value?.rol] ?? 'Usuario'));
  const todayLabel = computed(() => new Intl.DateTimeFormat('es-PE', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date()));
  const lastUpdatedLabel = computed(() => (
    lastUpdated.value
      ? new Intl.DateTimeFormat('es-PE', { hour: '2-digit', minute: '2-digit' }).format(lastUpdated.value)
      : 'Sin actualizar'
  ));

  const damagedEquipment = computed(() => Math.max(
    0,
    equipmentStats.total
      - equipmentStats.en_uso
      - equipmentStats.en_mantenimiento
      - equipmentStats.de_baja,
  ));
  const equipmentOperationalRate = computed(() => getPercentage(
    equipmentStats.en_uso,
    equipmentStats.total,
  ));
  const activeSpacesRate = computed(() => getPercentage(spaceStats.activos, spaceStats.total));
  const activeUsersRate = computed(() => getPercentage(userStats.activos, userStats.total));
  const openMaintenance = computed(() => maintenanceStats.pendientes + maintenanceStats.en_proceso);
  const maintenanceResolutionRate = computed(() => getPercentage(
    maintenanceStats.resueltos,
    maintenanceStats.total,
  ));
  const equipmentDistribution = computed(() => [
    { label: 'En uso', value: equipmentStats.en_uso, tone: 'success' },
    { label: 'En mantenimiento', value: equipmentStats.en_mantenimiento, tone: 'warning' },
    { label: 'Dañados', value: damagedEquipment.value, tone: 'danger' },
    { label: 'De baja', value: equipmentStats.de_baja, tone: 'slate' },
  ]);
  const maintenanceDistribution = computed(() => [
    { label: 'Resueltos', value: maintenanceStats.resueltos, tone: 'success' },
    { label: 'En proceso', value: maintenanceStats.en_proceso, tone: 'blue' },
    { label: 'Pendientes', value: maintenanceStats.pendientes, tone: 'warning' },
    { label: 'Cancelados', value: maintenanceStats.cancelados, tone: 'slate' },
  ]);
  const topSpaces = computed(() => [...spaces.value]
    .sort((first, second) => second.cantidad_equipos - first.cantidad_equipos)
    .slice(0, 5));

  const formatDate = (value) => {
    if (!value) return 'Sin fecha';
    return new Intl.DateTimeFormat('es-PE', {
      day: '2-digit',
      month: 'short',
    }).format(new Date(`${value}T00:00:00`));
  };

  const loadDashboard = async () => {
    if (!canViewOperations.value) return;
    loading.value = true;
    error.value = '';
    warning.value = '';

    try {
      const response = await service.obtenerResumen();
      const data = response.data ?? {};
      Object.assign(equipmentStats, data.equipos ?? {});
      Object.assign(spaceStats, data.espacios ?? {});
      Object.assign(userStats, data.usuarios ?? {});
      Object.assign(maintenanceStats, data.mantenimiento ?? {});
      recentMaintenance.value = getResults(data.mantenimientosRecientes).slice(0, 5);
      spaces.value = getResults(data.espaciosDestacados);
      lastUpdated.value = new Date();

      if (response.failed?.length) {
        warning.value = 'Algunos indicadores no pudieron actualizarse. Los datos disponibles se muestran normalmente.';
      }
    } catch (requestError) {
      error.value = getApiErrorMessage(requestError, 'No se pudo cargar el resumen operativo.');
    } finally {
      loading.value = false;
    }
  };

  onMounted(loadDashboard);

  return {
    loading,
    error,
    warning,
    user,
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
  };
}

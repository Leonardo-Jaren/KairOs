import { computed, onMounted, ref, watch } from 'vue';

import espaciosService from '@/services/espacios.service';
import { getApiErrorMessage } from '@/utils/api-errors';
import { formatBuildingName } from '@/utils/formatters';

const naturalCompare = (left, right) => left.localeCompare(right, 'es', {
  numeric: true,
  sensitivity: 'base',
});

export function useCampusTecnologico(service = espaciosService) {
  const espacios = ref([]);
  const loading = ref(false);
  const error = ref('');
  const search = ref('');
  const selectedBuilding = ref('');

  const edificios = computed(() => {
    const groups = new Map();
    espacios.value.forEach((espacio) => {
      const name = formatBuildingName(espacio.pabellon);
      if (!groups.has(name)) groups.set(name, []);
      groups.get(name).push(espacio);
    });

    return [...groups.entries()]
      .map(([name, spaces]) => {
        const laboratorios = spaces.filter((space) => (
          space.tipo === 'laboratorio' || space.tipo === 'sala_computo'
        ));
        return {
          name,
          spaces,
          laboratorios,
          pisos: [...new Set(spaces.map((space) => space.piso))].sort(naturalCompare),
          equipos: spaces.reduce((total, space) => total + space.cantidad_equipos, 0),
          alertas: spaces.reduce((total, space) => (
            total
            + (space.resumen_equipos?.en_mantenimiento ?? 0)
            + (space.resumen_equipos?.dañado ?? 0)
          ), 0),
        };
      })
      .sort((left, right) => naturalCompare(left.name, right.name));
  });

  const edificioActivo = computed(() => (
    edificios.value.find((building) => building.name === selectedBuilding.value)
    ?? edificios.value[0]
    ?? null
  ));

  const laboratoriosVisibles = computed(() => {
    const query = search.value.trim().toLocaleLowerCase('es');
    const labs = edificioActivo.value?.laboratorios ?? [];
    if (!query) return labs;
    return labs.filter((space) => [
      space.codigo_espacio,
      space.tipo_display,
      space.piso,
      space.responsable?.nombre_completo,
    ].some((value) => String(value ?? '').toLocaleLowerCase('es').includes(query)));
  });

  const stats = computed(() => ({
    edificios: edificios.value.length,
    laboratorios: edificios.value.reduce((total, item) => total + item.laboratorios.length, 0),
    equipos: espacios.value.reduce((total, item) => total + item.cantidad_equipos, 0),
    alertas: edificios.value.reduce((total, item) => total + item.alertas, 0),
  }));

  const loadCampus = async () => {
    loading.value = true;
    error.value = '';
    try {
      const data = await service.listar({ activo: 'true', page_size: 100 });
      espacios.value = data.results ?? data;
    } catch (requestError) {
      error.value = getApiErrorMessage(requestError, 'No se pudo cargar el mapa tecnológico.');
    } finally {
      loading.value = false;
    }
  };

  watch(edificios, (items) => {
    if (!items.some((item) => item.name === selectedBuilding.value)) {
      selectedBuilding.value = items[0]?.name ?? '';
    }
  }, { immediate: true });

  onMounted(loadCampus);

  return {
    loading,
    error,
    search,
    edificios,
    selectedBuilding,
    edificioActivo,
    laboratoriosVisibles,
    stats,
    loadCampus,
  };
}

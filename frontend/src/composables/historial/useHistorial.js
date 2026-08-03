import { computed, onMounted, reactive, readonly, shallowRef } from 'vue';

import historialService from '@/services/historial.service';
import { getApiErrorMessage } from '@/utils/api-errors';

export function useHistorial(service = historialService) {
  const _historial = shallowRef([]);
  const _loading = shallowRef(false);

  const filters = reactive({
    modulo: '',
    tipo_evento: '',
    usuario_id: '',
    fecha_desde: '',
    fecha_hasta: '',
    page: 1,
    page_size: 15,
  });

  const _pagination = reactive({ total: 0, totalPages: 1 });

  const toast = reactive({ show: false, message: '', type: 'success' });

  const hasActiveFilters = computed(() =>
    Boolean(
      filters.modulo || filters.tipo_evento || filters.usuario_id
      || filters.fecha_desde || filters.fecha_hasta,
    ),
  );

  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });
  const closeToast = () => { toast.show = false; };

  const loadHistorial = async () => {
    _loading.value = true;
    try {
      const data = await service.listar(filters);
      _historial.value = data.results ?? data;
      _pagination.total = data.count ?? _historial.value.length;
      _pagination.totalPages = Math.max(1, Math.ceil(_pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo cargar el historial.'), 'error');
    } finally {
      _loading.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadHistorial();
  };

  const clearFilters = () => {
    Object.assign(filters, {
      modulo: '',
      tipo_evento: '',
      usuario_id: '',
      fecha_desde: '',
      fecha_hasta: '',
      page: 1,
    });
    return loadHistorial();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadHistorial();
  };

  onMounted(loadHistorial);

  return {
    historial: readonly(_historial),
    loading: readonly(_loading),
    pagination: readonly(_pagination),
    filters,
    toast,
    hasActiveFilters,
    loadHistorial,
    applyFilters,
    clearFilters,
    changePage,
    closeToast,
  };
}

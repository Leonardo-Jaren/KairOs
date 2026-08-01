import { computed, onMounted, ref } from 'vue';

import espaciosService from '@/services/espacios.service';
import { getApiErrorMessage } from '@/utils/api-errors';

export function useEspacioDetalle(id, service = espaciosService) {
  const espacio = ref(null);
  const loading = ref(false);
  const error = ref('');
  const equipos = computed(() => espacio.value?.equipos ?? []);

  const loadSpace = async () => {
    loading.value = true;
    error.value = '';
    try {
      espacio.value = await service.obtener(id);
    } catch (requestError) {
      error.value = getApiErrorMessage(requestError, 'No se pudo cargar el espacio.');
    } finally {
      loading.value = false;
    }
  };

  onMounted(loadSpace);

  return { espacio, equipos, loading, error, loadSpace };
}

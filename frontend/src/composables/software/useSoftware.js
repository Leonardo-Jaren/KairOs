import { computed, onMounted, reactive, ref } from 'vue';

import softwareService from '@/services/software.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  software: '',
  version: '',
  descripcion: '',
  tipo_licencia: 'perpetua',
  licencias_totales: 1,
  fecha_expiracion: '',
  costo_anual_total: 0,
});

export const TIPO_LICENCIA_OPTIONS = [
  { value: 'perpetua', label: 'Perpetua' },
  { value: 'suscripcion', label: 'Suscripción' },
  { value: 'oem', label: 'OEM' },
  { value: 'volumen', label: 'Volumen' },
  { value: 'libre', label: 'Libre / Open Source' },
];

export function useSoftware(service = softwareService) {
  const authStore = useAuthStore();
  const productos = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingProducto = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({ search: '', tipo_licencia: '', page: 1, page_size: 8 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total_productos: 0, licencias_por_expirar: 0, productos_sobre_uso: 0 });

  const isEditing = computed(() => Boolean(editingProducto.value));
  const canManageAll = computed(() => ['admin', 'tecnico'].includes(authStore.user?.rol));

  const loadProductos = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      productos.value = data.results ?? data;
      pagination.total = data.count ?? productos.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los productos de software.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const loadStats = async () => {
    try {
      Object.assign(stats, await service.obtenerEstadisticas());
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los indicadores.'), 'error');
    }
  };

  const loadData = () => Promise.all([loadProductos(), loadStats()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingProducto.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (producto) => {
    editingProducto.value = producto;
    resetForm();
    Object.assign(form, {
      software: producto.software,
      version: producto.version,
      descripcion: producto.descripcion ?? '',
      tipo_licencia: producto.tipo_licencia,
      licencias_totales: producto.licencias_totales,
      fecha_expiracion: producto.fecha_expiracion ?? '',
      costo_anual_total: producto.costo_anual_total,
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingProducto.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.software.trim()) formErrors.software = 'Ingresa el nombre del software.';
    if (!form.version.trim()) formErrors.version = 'Ingresa la versión.';
    if (!form.tipo_licencia) formErrors.tipo_licencia = 'Selecciona el tipo de licencia.';
    if (form.licencias_totales === '' || form.licencias_totales === null || Number(form.licencias_totales) < 0) {
      formErrors.licencias_totales = 'Ingresa una cantidad de licencias válida.';
    }
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;

    const payload = {
      ...form,
      licencias_totales: Number(form.licencias_totales),
      costo_anual_total: Number(form.costo_anual_total) || 0,
      fecha_expiracion: form.fecha_expiracion || null,
    };

    try {
      if (isEditing.value) {
        await service.actualizar(editingProducto.value.id, payload);
        showToast('Producto de software actualizado correctamente.');
      } else {
        await service.crear(payload);
        showToast('Producto de software registrado correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el producto de software.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (producto) => {
    pendingDelete.value = producto;
    deleteModalOpen.value = true;
  };

  const cancelDelete = () => {
    pendingDelete.value = null;
    deleteModalOpen.value = false;
  };

  const confirmDelete = async () => {
    if (!pendingDelete.value) return;
    saving.value = true;
    try {
      await service.eliminar(pendingDelete.value.id);
      showToast('Producto de software eliminado correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar el producto de software.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadProductos();
  };

  const clearFilters = () => {
    Object.assign(filters, { search: '', tipo_licencia: '', page: 1 });
    return loadProductos();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadProductos();
  };

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(loadData);

  return {
    productos,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canManageAll,
    tipoLicenciaOptions: TIPO_LICENCIA_OPTIONS,
    loadData,
    openCreate,
    openEdit,
    closeModal,
    submit,
    askDelete,
    cancelDelete,
    confirmDelete,
    applyFilters,
    clearFilters,
    changePage,
    closeToast,
  };
}

import { computed, reactive, ref } from 'vue';

import equiposService from '@/services/equipos.service';
import espaciosService from '@/services/espacios.service';
import softwareService from '@/services/software.service';
import softwareInstalacionesService from '@/services/software-instalaciones.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  equipo: '',
  producto_software: '',
  numero_licencia_usado: '',
  fecha_instalacion: '',
});

export function useInstalaciones(service = softwareInstalacionesService) {
  const authStore = useAuthStore();
  const instalaciones = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const formOpen = ref(false);
  const deleteOpen = ref(false);
  const editingItem = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({
    search: '', equipo_id: '', espacio_id: '', producto_software_id: '', page: 1, page_size: 10,
  });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const equipoOptions = ref([]);
  const productoOptions = ref([]);
  const espacioOptions = ref([]);

  const isEditing = computed(() => Boolean(editingItem.value));
  const canManageAll = computed(() => ['admin', 'tecnico'].includes(authStore.user?.rol));

  const equipoSelectOptions = computed(() => equipoOptions.value.map((equipo) => ({
    value: equipo.id,
    label: `${equipo.codigo} — ${equipo.marca} ${equipo.modelo}`,
  })));

  const productoSelectOptions = computed(() => productoOptions.value.map((producto) => ({
    value: producto.id,
    label: `${producto.software} v${producto.version}`,
  })));

  const espacioSelectOptions = computed(() => espacioOptions.value.map((espacio) => ({
    value: espacio.id,
    label: `${espacio.codigo_espacio} · ${espacio.pabellon}`,
  })));

  const cargar = async (overrideFilters = {}) => {
    Object.assign(filters, overrideFilters);
    loading.value = true;
    try {
      const data = await service.listar(filters);
      instalaciones.value = data.results ?? data;
      pagination.total = data.count ?? instalaciones.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar las instalaciones.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const cargarOpciones = async () => {
    try {
      const [equipos, productos, espacios] = await Promise.all([
        equiposService.obtenerOpciones(),
        softwareService.obtenerOpciones(),
        espaciosService.listar({ page_size: 100 }),
      ]);
      equipoOptions.value = equipos;
      productoOptions.value = productos;
      espacioOptions.value = espacios.results ?? espacios;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los datos de referencia.'), 'error');
    }
  };

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = (preset = {}) => {
    editingItem.value = null;
    resetForm();
    Object.assign(form, preset);
    formOpen.value = true;
  };

  const openEdit = (instalacion) => {
    editingItem.value = instalacion;
    resetForm();
    Object.assign(form, {
      equipo: instalacion.equipo,
      producto_software: instalacion.producto_software,
      numero_licencia_usado: instalacion.numero_licencia_usado ?? '',
      fecha_instalacion: instalacion.fecha_instalacion,
    });
    formOpen.value = true;
  };

  const closeForm = () => {
    formOpen.value = false;
    editingItem.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!isEditing.value) {
      if (!form.equipo) formErrors.equipo = 'Selecciona el equipo.';
      if (!form.producto_software) formErrors.producto_software = 'Selecciona el producto de software.';
    }
    if (!form.fecha_instalacion) formErrors.fecha_instalacion = 'Ingresa la fecha de instalación.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async (reloadFilters = {}) => {
    if (!validateForm()) return false;
    saving.value = true;

    try {
      if (isEditing.value) {
        await service.actualizar(editingItem.value.id, {
          numero_licencia_usado: form.numero_licencia_usado,
          fecha_instalacion: form.fecha_instalacion,
        });
        showToast('Instalación actualizada correctamente.');
      } else {
        await service.crear(form);
        showToast('Software instalado correctamente.');
      }
      closeForm();
      await cargar(reloadFilters);
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar la instalación.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (instalacion) => {
    pendingDelete.value = instalacion;
    deleteOpen.value = true;
  };

  const cancelDelete = () => {
    pendingDelete.value = null;
    deleteOpen.value = false;
  };

  const confirmDelete = async (reloadFilters = {}) => {
    if (!pendingDelete.value) return;
    saving.value = true;
    try {
      await service.eliminar(pendingDelete.value.id);
      showToast('Instalación eliminada correctamente.');
      cancelDelete();
      await cargar(reloadFilters);
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar la instalación.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return cargar();
  };

  const clearFilters = () => {
    Object.assign(filters, {
      search: '', equipo_id: '', espacio_id: '', producto_software_id: '', page: 1,
    });
    return cargar();
  };

  const changePage = (page) => {
    filters.page = page;
    return cargar();
  };

  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });
  const closeToast = () => { toast.show = false; };

  const reset = () => {
    instalaciones.value = [];
    closeForm();
    cancelDelete();
  };

  return {
    instalaciones, loading, saving, formOpen, deleteOpen, pendingDelete,
    form, formErrors, filters, pagination, toast, isEditing, canManageAll,
    equipoSelectOptions, productoSelectOptions, espacioSelectOptions,
    cargar, cargarOpciones, openCreate, openEdit, closeForm, submit,
    askDelete, cancelDelete, confirmDelete, applyFilters, clearFilters,
    changePage, closeToast, reset,
  };
}

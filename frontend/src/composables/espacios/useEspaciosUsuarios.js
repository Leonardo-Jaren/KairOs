import { computed, onMounted, reactive, ref } from 'vue';

import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import espaciosService from '@/services/espacios.service';
import usuariosService from '@/services/usuarios.service';
import { useAutoFilters } from '@/composables/shared/useAutoFilters';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  usuario_id: '',
  espacio_id: '',
  tipo_responsabilidad: 'responsable',
  activo: true,
});

const defaultOptionServices = {
  usuarios: usuariosService,
  espacios: espaciosService,
};

export function useEspaciosUsuarios(
  service = espaciosUsuariosService,
  optionServices = defaultOptionServices,
) {
  const authStore = useAuthStore();
  const asignaciones = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingAssignment = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const filters = reactive({ search: '', activo: '', page: 1, page_size: 10 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const toast = reactive({ show: false, message: '', type: 'success' });

  const canEdit = computed(() => authStore.user?.rol === 'admin');
  const isEditing = computed(() => Boolean(editingAssignment.value));
  const activeCount = computed(() => asignaciones.value.filter((item) => item.activo).length);
  const uniqueSpaces = computed(() => new Set(asignaciones.value.map((item) => item.espacio.id)).size);
  const uniqueUsers = computed(() => new Set(asignaciones.value.map((item) => item.usuario.id)).size);

  const responsibilityOptions = [
    { value: 'responsable', label: 'Responsable' },
    { value: 'tecnico', label: 'Soporte técnico' },
    { value: 'docente', label: 'Docente asignado' },
  ];

  const selectedUserOption = computed(() => {
    const user = editingAssignment.value?.usuario;
    return user ? {
      value: user.id,
      label: `${user.nombre_completo} · ${user.correo}`,
    } : null;
  });
  const selectedSpaceOption = computed(() => {
    const space = editingAssignment.value?.espacio;
    return space ? {
      value: space.id,
      label: `${space.codigo_espacio} · ${space.pabellon}`,
    } : null;
  });

  const mapPaginatedOptions = (data, mapper) => {
    const records = data.results ?? data;
    return {
      options: records.map(mapper),
      total: data.count ?? records.length,
    };
  };

  const loadUserOptions = async ({ page, pageSize, search }) => {
    const data = await optionServices.usuarios.listar({
      page,
      page_size: pageSize,
      search,
      activo: 'true',
    });
    return mapPaginatedOptions(data, (user) => ({
      value: user.id,
      label: `${user.nombre_completo} · ${user.correo}`,
    }));
  };

  const loadSpaceOptions = async ({ page, pageSize, search }) => {
    const data = await optionServices.espacios.listar({
      page,
      page_size: pageSize,
      search,
      activo: 'true',
    });
    return mapPaginatedOptions(data, (space) => ({
      value: space.id,
      label: `${space.codigo_espacio} · ${space.pabellon}`,
    }));
  };

  const loadAssignments = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      asignaciones.value = data.results ?? data;
      pagination.total = data.count ?? asignaciones.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar las asignaciones.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const loadData = () => loadAssignments();

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingAssignment.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (assignment) => {
    editingAssignment.value = assignment;
    resetForm();
    Object.assign(form, {
      usuario_id: assignment.usuario.id,
      espacio_id: assignment.espacio.id,
      tipo_responsabilidad: assignment.tipo_responsabilidad,
      activo: assignment.activo,
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingAssignment.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.usuario_id) formErrors.usuario_id = 'Selecciona un usuario.';
    if (!form.espacio_id) formErrors.espacio_id = 'Selecciona un espacio.';
    if (!form.tipo_responsabilidad) formErrors.tipo_responsabilidad = 'Selecciona una responsabilidad.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;
    const payload = {
      ...form,
      usuario_id: Number(form.usuario_id),
      espacio_id: Number(form.espacio_id),
    };
    try {
      if (isEditing.value) {
        await service.actualizar(editingAssignment.value.id, payload);
        showToast('Asignación actualizada correctamente.');
      } else {
        await service.crear(payload);
        showToast('Asignación creada correctamente.');
      }
      closeModal();
      await loadAssignments();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar la asignación.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (assignment) => {
    pendingDelete.value = assignment;
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
      showToast('Asignación eliminada correctamente.');
      cancelDelete();
      await loadAssignments();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar la asignación.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const { applyFilters, resetFilters } = useAutoFilters(filters, loadAssignments, {
    immediateKeys: ['activo'],
  });
  const clearFilters = () => resetFilters({ search: '', activo: '' });
  const changePage = (page) => {
    filters.page = page;
    return loadAssignments();
  };
  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });
  const closeToast = () => { toast.show = false; };

  onMounted(loadData);

  return {
    asignaciones,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    editingAssignment,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    toast,
    canEdit,
    isEditing,
    activeCount,
    uniqueSpaces,
    uniqueUsers,
    responsibilityOptions,
    selectedUserOption,
    selectedSpaceOption,
    loadUserOptions,
    loadSpaceOptions,
    loadAssignments,
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

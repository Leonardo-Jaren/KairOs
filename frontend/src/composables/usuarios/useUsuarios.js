import { computed, onMounted, reactive, ref } from 'vue';

import usuariosService from '@/services/usuarios.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({
  username: '',
  correo: '',
  nombre: '',
  apellido: '',
  dni: '',
  rol: 'docente',
  password: '',
  is_active: true,
});

export function useUsuarios(service = usuariosService) {
  const authStore = useAuthStore();
  const usuarios = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const modalOpen = ref(false);
  const deleteModalOpen = ref(false);
  const editingUser = ref(null);
  const pendingDelete = ref(null);
  const form = reactive(emptyForm());
  const formErrors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });
  const filters = reactive({ search: '', rol: '', activo: '', page: 1, page_size: 10 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, activos: 0, administradores: 0, tecnicos: 0, docentes: 0 });

  const isEditing = computed(() => Boolean(editingUser.value));
  const canManageAll = computed(() => authStore.user?.rol === 'admin');
  const canCreate = computed(() => ['admin', 'tecnico'].includes(authStore.user?.rol));

  const roleOptions = [
    { value: 'admin', label: 'Administrador' },
    { value: 'tecnico', label: 'Técnico' },
    { value: 'docente', label: 'Docente' },
    { value: 'usuario', label: 'Usuario' },
  ];
  const availableRoleOptions = computed(() => (
    canManageAll.value
      ? roleOptions
      : roleOptions.filter((option) => option.value === 'docente')
  ));

  const loadUsuarios = async () => {
    loading.value = true;
    try {
      const data = await service.listar(filters);
      usuarios.value = data.results ?? data;
      pagination.total = data.count ?? usuarios.value.length;
      pagination.totalPages = Math.max(1, Math.ceil(pagination.total / filters.page_size));
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los usuarios.'), 'error');
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

  const loadData = () => Promise.all([loadUsuarios(), loadStats()]);

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingUser.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (user) => {
    editingUser.value = user;
    resetForm();
    Object.assign(form, {
      username: user.username,
      correo: user.correo,
      nombre: user.nombre,
      apellido: user.apellido ?? '',
      dni: user.dni ?? '',
      rol: user.rol,
      password: '',
      is_active: user.is_active,
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingUser.value = null;
    resetForm();
  };

  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.nombre.trim()) formErrors.nombre = 'Ingresa el nombre.';
    if (!form.username.trim()) formErrors.username = 'Ingresa el nombre de usuario.';
    if (!/^\S+@\S+\.\S+$/.test(form.correo)) formErrors.correo = 'Ingresa un correo válido.';
    if (!form.rol) formErrors.rol = 'Selecciona un rol.';
    if (form.dni && !/^\d{8}$/.test(form.dni)) formErrors.dni = 'El DNI debe tener 8 dígitos.';
    if (!isEditing.value && form.password.length < 8) formErrors.password = 'Usa al menos 8 caracteres.';
    if (form.password && form.password.length < 8) formErrors.password = 'Usa al menos 8 caracteres.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;
    const payload = { ...form, dni: form.dni || null };
    if (!payload.password) delete payload.password;

    try {
      if (isEditing.value) {
        await service.actualizar(editingUser.value.id, payload);
        showToast('Usuario actualizado correctamente.');
      } else {
        await service.crear(payload);
        showToast('Usuario creado correctamente.');
      }
      closeModal();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el usuario.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (user) => {
    pendingDelete.value = user;
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
      await service.desactivar(pendingDelete.value.id);
      showToast('Usuario desactivado correctamente.');
      cancelDelete();
      await loadData();
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo desactivar el usuario.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const applyFilters = () => {
    filters.page = 1;
    return loadUsuarios();
  };

  const clearFilters = () => {
    Object.assign(filters, { search: '', rol: '', activo: '', page: 1 });
    return loadUsuarios();
  };

  const changePage = (page) => {
    filters.page = page;
    return loadUsuarios();
  };

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(loadData);

  return {
    usuarios,
    loading,
    saving,
    modalOpen,
    deleteModalOpen,
    editingUser,
    pendingDelete,
    form,
    formErrors,
    filters,
    pagination,
    stats,
    toast,
    isEditing,
    canManageAll,
    canCreate,
    roleOptions,
    availableRoleOptions,
    loadUsuarios,
    loadStats,
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

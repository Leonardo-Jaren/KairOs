import { computed, onMounted, reactive, ref, watch } from 'vue';

import localesService from '@/services/locales.service';
import usuariosService from '@/services/usuarios.service';
import { useAutoFilters } from '@/composables/shared/useAutoFilters';

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
  supervisor_id: null,
  sede_ids: [],
  sede_principal_id: null,
});

export function useUsuarios(service = usuariosService, sedesService = localesService) {
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
  const filters = reactive({ search: '', rol: '', activo: '', local_id: '', page: 1, page_size: 10 });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const stats = reactive({ total: 0, activos: 0, administradores: 0, tecnicos: 0, docentes: 0 });

  const isEditing = computed(() => Boolean(editingUser.value));
  const canManageAll = computed(() => ['admin', 'superadmin'].includes(authStore.user?.rol) || !!authStore.user?.is_superuser);
  const canCreate = computed(() => authStore.hasPermission('usuarios', 'crear'));
  const canEdit = computed(() => authStore.hasPermission('usuarios', 'editar'));
  const canDelete = computed(() => authStore.hasPermission('usuarios', 'eliminar'));

  const activeSedeIds = (user) => new Set((user?.sedes || []).map((sede) => Number(sede.id)));

  const sharesSede = (target) => {
    const actorSedes = activeSedeIds(authStore.user);
    if (!actorSedes.size) return true;
    const targetSedes = activeSedeIds(target);
    return !targetSedes.size || [...targetSedes].some((id) => actorSedes.has(id));
  };

  const canManageTarget = (target) => {
    const actor = authStore.user;
    if (!actor || !target) return false;
    if (actor.rol === 'superadmin' || actor.is_superuser) return true;

    if (actor.rol === 'admin') {
      return target.id === actor.id
        ? target.rol === 'admin'
        : ['responsable', 'tecnico', 'docente', 'usuario'].includes(target.rol) && sharesSede(target);
    }

    if (actor.rol === 'responsable') {
      return ['tecnico', 'docente', 'usuario'].includes(target.rol)
        && target.supervisor_id === actor.id
        && sharesSede(target);
    }

    return false;
  };

  const canEditUser = (target) => canEdit.value && canManageTarget(target);
  const canDeleteUser = (target) => canDelete.value && target?.id !== authStore.user?.id && canManageTarget(target);
  const canManagePermisos = (target) => canManageAll.value
    && canManageTarget(target)
    && target?.id !== authStore.user?.id;

  const roleOptions = [
    { value: 'superadmin', label: 'Superadministrador' },
    { value: 'admin', label: 'Administrador' },
    { value: 'responsable', label: 'Responsable de Sede / Área' },
    { value: 'tecnico', label: 'Técnico' },
    { value: 'docente', label: 'Docente' },
    { value: 'usuario', label: 'Usuario' },
  ];

  const filterRoleOptions = roleOptions;

  const availableRoleOptions = computed(() => {
    if (authStore.user?.rol === 'tecnico') {
      return [{ value: 'docente', label: 'Docente' }];
    }
    if (authStore.user?.rol === 'superadmin' || authStore.user?.is_superuser) {
      return roleOptions;
    }
    if (authStore.user?.rol === 'admin') {
      return roleOptions.filter((option) => option.value !== 'superadmin');
    }
    if (authStore.user?.rol === 'responsable') {
      return roleOptions.filter((option) => ['tecnico', 'docente', 'usuario'].includes(option.value));
    }
    return roleOptions.filter((option) => option.value === 'docente');
  });

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

  const locales = ref([]);
  const localesLoading = ref(false);
  const localesError = ref('');
  let activeLocalesPromise = null;

  const loadLocales = ({ notifyError = true } = {}) => {
    if (activeLocalesPromise) return activeLocalesPromise;

    localesLoading.value = true;
    localesError.value = '';
    activeLocalesPromise = (async () => {
      try {
        const data = await sedesService.listar({
          activo: 'true',
          asignables: 'true',
          page_size: 100,
        });
        const results = Array.isArray(data) ? data : data?.results;
        if (!Array.isArray(results)) {
          throw new Error('El servicio de sedes devolvió un formato inválido.');
        }
        locales.value = results;
        return true;
      } catch (error) {
        locales.value = [];
        localesError.value = getApiErrorMessage(error, 'No se pudieron cargar las sedes disponibles.');
        if (notifyError) showToast(localesError.value, 'error');
        return false;
      } finally {
        localesLoading.value = false;
        activeLocalesPromise = null;
      }
    })();

    return activeLocalesPromise;
  };

  const sedeOptions = computed(() => {
    return locales.value.map((loc) => ({
      value: loc.id,
      label: `${loc.codigo} - ${loc.nombre} (${loc.ciudad})`,
    }));
  });

  const supervisorOptions = computed(() => {
    const map = new Map();
    const currentUser = authStore.user;
    const isSuper = currentUser?.rol === 'superadmin' || currentUser?.is_superuser;
    const allowedSedeIds = new Set((currentUser?.sedes || []).map((s) => Number(s.id)));

    usuarios.value.forEach((u) => {
      if (u.id !== editingUser.value?.id && ['superadmin', 'admin', 'responsable'].includes(u.rol)) {
        if (!isSuper) {
          // Filtrar supervisores para que compartan sede con el usuario actual o sea el usuario mismo
          const uSedeIds = (u.sedes || []).map((s) => Number(s.id));
          const hasCommonSede = uSedeIds.some((id) => allowedSedeIds.has(id));
          if (!hasCommonSede && u.id !== currentUser?.id) {
            return;
          }
        }
        map.set(u.id, {
          value: u.id,
          label: `${u.nombre_completo || u.nombre} (${u.rol})`,
        });
      }
    });
    if (editingUser.value?.supervisor?.id && !map.has(editingUser.value.supervisor.id)) {
      const s = editingUser.value.supervisor;
      map.set(s.id, {
        value: s.id,
        label: `${s.nombre_completo || s.nombre} (${s.rol})`,
      });
    }
    return Array.from(map.values());
  });


  const loadData = () => Promise.all([loadUsuarios(), loadStats(), loadLocales()]);


  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  const openCreate = () => {
    editingUser.value = null;
    resetForm();
    const currentUser = authStore.user;
    if (currentUser && currentUser.rol !== 'superadmin' && !currentUser.is_superuser) {
      if (currentUser.sedes && currentUser.sedes.length > 0) {
        const primaryId = Number(currentUser.sedes[0].id);
        form.sede_ids = [primaryId];
        form.sede_principal_id = primaryId;
      }
      if (currentUser.rol === 'responsable') {
        form.supervisor_id = currentUser.id;
      }
    }
    modalOpen.value = true;
    // Refrescar al abrir evita conservar un catálogo vacío por un fallo inicial transitorio.
    void loadLocales();
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
      supervisor_id: user.rol === 'docente' ? null : (user.supervisor_id ?? user.supervisor?.id ?? null),
      sede_ids: user.sedes ? user.sedes.map((s) => s.id) : [],
      sede_principal_id: user.sedes?.find((s) => s.es_sede_principal)?.id ?? null,
    });
    modalOpen.value = true;
    void loadLocales();
  };

  watch(
    () => form.rol,
    (role) => {
      if (role === 'docente') form.supervisor_id = null;
    },
  );


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
    if (!form.sede_ids.length) formErrors.sede_ids = 'Selecciona la sede física del usuario.';
    if (form.dni && !/^\d{8}$/.test(form.dni)) formErrors.dni = 'El DNI debe tener 8 dígitos.';
    if (!isEditing.value && form.password.length < 8) formErrors.password = 'Usa al menos 8 caracteres.';
    if (form.password && form.password.length < 8) formErrors.password = 'Usa al menos 8 caracteres.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;
    const payload = { ...form, dni: form.dni || null };
    if (payload.rol === 'docente') payload.supervisor_id = null;
    if (!payload.password) delete payload.password;
    if (!payload.supervisor_id) payload.supervisor_id = null;
    // Enviar la lista vacía permite retirar una sede ya asignada al editar.
    payload.sede_ids = Array.isArray(form.sede_ids) ? [...form.sede_ids] : [];

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
    if (!pendingDelete.value) return false;
    saving.value = true;
    try {
      await service.desactivar(pendingDelete.value.id);
      showToast('Usuario desactivado correctamente.');
      cancelDelete();
      await loadData();
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo desactivar el usuario.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const { applyFilters, resetFilters } = useAutoFilters(filters, loadUsuarios, {
    immediateKeys: ['rol', 'activo', 'local_id'],
  });

  const clearFilters = () => resetFilters({ search: '', rol: '', activo: '', local_id: '' });

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
    canEditUser,
    canDeleteUser,
    canManagePermisos,
    canEdit,
    canDelete,
    roleOptions,
    filterRoleOptions,
    availableRoleOptions,
    locales,
    localesLoading,
    localesError,
    sedeOptions,
    supervisorOptions,
    loadLocales,
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

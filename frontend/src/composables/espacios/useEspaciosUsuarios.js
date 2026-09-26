import { computed, onMounted, reactive, ref } from 'vue';

import edificiosService from '@/services/edificios.service';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import espaciosService from '@/services/espacios.service';
import localesService from '@/services/locales.service';
import usuariosService from '@/services/usuarios.service';
import { useAutoFilters } from '@/composables/shared/useAutoFilters';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

// Estructura limpia del formulario con soporte para los cuatro ambitos territoriales
const emptyForm = () => ({
  tipo_ambito: 'espacio',
  ambito: 'espacio',
  local_id: '',
  edificio_id: '',
  piso: '',
  espacio_id: '',
  usuario_id: '',
  tipo_responsabilidad: 'responsable',
  activo: true,
});

const defaultOptionServices = {
  usuarios: usuariosService,
  espacios: espaciosService,
  locales: localesService,
  edificios: edificiosService,
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
  const filters = reactive({
    search: '',
    activo: '',
    local_id: '',
    edificio_id: '',
    ambito: '',
    page: 1,
    page_size: 10,
  });
  const pagination = reactive({ total: 0, totalPages: 1 });
  const toast = reactive({ show: false, message: '', type: 'success' });

  // Catalogos en memoria para selectores en cascada y filtros
  const localesList = ref([]);
  const edificiosList = ref([]);
  const espaciosList = ref([]);

  // Permiso de mutacion: superadmin, admin y responsable (con validacion de sede en backend)
  const canEdit = computed(() => {
    const rol = authStore.user?.rol;
    if (!rol && !authStore.user?.is_superuser) return false;
    return (
      ['superadmin', 'admin', 'responsable'].includes(rol)
      || Boolean(authStore.user?.is_superuser)
    );
  });

  const isEditing = computed(() => Boolean(editingAssignment.value));
  const activeCount = computed(() => asignaciones.value.filter((item) => item.activo).length);
  const uniqueSpaces = computed(() => (
    new Set(
      asignaciones.value
        .map((item) => item.espacio_id ?? item.espacio?.id ?? item.edificio_id ?? item.local_id)
        .filter(Boolean)
    ).size
  ));
  const uniqueUsers = computed(() => (
    new Set(
      asignaciones.value
        .map((item) => item.usuario_id ?? item.usuario?.id)
        .filter(Boolean)
    ).size
  ));

  const ambitoOptions = [
    { value: 'sede', label: 'Sede / Local' },
    { value: 'edificio', label: 'Pabellón / Edificio' },
    { value: 'piso', label: 'Piso de Pabellón' },
    { value: 'espacio', label: 'Espacio individual' },
  ];

  const responsibilityOptions = [
    { value: 'responsable', label: 'Responsable' },
    { value: 'tecnico', label: 'Soporte técnico' },
    { value: 'docente', label: 'Docente asignado' },
  ];

  // Opciones de sedes formateadas para componentes BaseSelect
  const localOptions = computed(() => localesList.value.map((loc) => ({
    id: loc.id,
    value: loc.id,
    label: loc.codigo ? `${loc.nombre} (${loc.codigo})` : loc.nombre,
    nombre: loc.nombre,
    codigo: loc.codigo,
  })));

  const localSelectOptions = localOptions;

  const localFilterOptions = computed(() => [
    { value: '', label: 'Todas las sedes' },
    ...localOptions.value,
  ]);

  // Filtra edificios segun la sede seleccionada en el formulario
  const filteredEdificios = computed(() => {
    if (!form.local_id) return [];
    return edificiosList.value
      .filter((edif) => String(edif.local_id) === String(form.local_id))
      .map((edif) => ({
        id: edif.id,
        value: edif.id,
        label: edif.codigo ? `${edif.codigo} · ${edif.nombre}` : edif.nombre,
        nombre: edif.nombre,
        codigo: edif.codigo,
        local_id: edif.local_id,
      }));
  });

  const filteredEdificioOptions = filteredEdificios;

  // Calcula pisos unicos disponibles para el edificio seleccionado
  const availablePisos = computed(() => {
    if (!form.edificio_id) return [];
    const pisosSet = new Set();

    const edif = edificiosList.value.find((e) => String(e.id) === String(form.edificio_id));
    if (edif && Array.isArray(edif.pisos)) {
      edif.pisos.forEach((p) => {
        if (p !== null && p !== undefined && String(p).trim() !== '') {
          pisosSet.add(String(p).trim());
        }
      });
    }

    espaciosList.value.forEach((espacio) => {
      const edId = espacio.edificio_id ?? espacio.edificio?.id;
      if (String(edId) === String(form.edificio_id) && espacio.piso) {
        pisosSet.add(String(espacio.piso).trim());
      }
    });

    return Array.from(pisosSet)
      .sort((a, b) => a.localeCompare(b, 'es', { numeric: true }))
      .map((piso) => ({
        id: piso,
        value: piso,
        label: `Piso ${piso}`,
        piso,
      }));
  });

  // Filtra espacios del formulario segun sede, edificio y piso
  const filteredEspacios = computed(() => {
    let list = espaciosList.value;

    if (form.local_id) {
      const edificiosDelLocal = new Set(
        edificiosList.value
          .filter((e) => String(e.local_id) === String(form.local_id))
          .map((e) => String(e.id))
      );
      list = list.filter((espacio) => {
        const edId = String(espacio.edificio_id ?? espacio.edificio?.id ?? '');
        return edificiosDelLocal.has(edId) || String(espacio.local_id) === String(form.local_id);
      });
    }

    if (form.edificio_id) {
      list = list.filter((espacio) => {
        const edId = String(espacio.edificio_id ?? espacio.edificio?.id ?? '');
        return edId === String(form.edificio_id);
      });
    }

    if (form.piso) {
      list = list.filter((espacio) => String(espacio.piso ?? '').trim() === String(form.piso).trim());
    }

    return list.map((espacio) => ({
      ...espacio,
      value: espacio.id,
      label: `${espacio.codigo_espacio} · ${espacio.pabellon || 'Pabellón'} (Piso ${espacio.piso || 'S/N'})`,
    }));
  });

  // Opciones de edificios para el filtro superior de la tabla
  const edificiosParaFiltro = computed(() => {
    let list = edificiosList.value;
    if (filters.local_id) {
      list = list.filter((edif) => String(edif.local_id) === String(filters.local_id));
    }
    return list.map((edif) => ({
      id: edif.id,
      value: edif.id,
      label: edif.codigo ? `${edif.codigo} · ${edif.nombre}` : edif.nombre,
      nombre: edif.nombre,
      codigo: edif.codigo,
      local_id: edif.local_id,
    }));
  });

  const edificioFilterOptions = computed(() => [
    { value: '', label: 'Todos los pabellones' },
    ...edificiosParaFiltro.value,
  ]);

  // Alias reactivos para los filtros de sede y pabellon
  const filtroLocal = computed({
    get: () => filters.local_id,
    set: (val) => {
      filters.local_id = val;
      filters.edificio_id = '';
      filters.page = 1;
    },
  });

  const filtroEdificio = computed({
    get: () => filters.edificio_id,
    set: (val) => {
      filters.edificio_id = val;
      filters.page = 1;
    },
  });

  // Opcion precargada para select paginado de usuario al editar
  const selectedUserOption = computed(() => {
    const user = editingAssignment.value?.usuario;
    return user ? {
      value: user.id,
      label: `${user.nombre_completo} · ${user.correo}`,
    } : null;
  });

  // Opcion precargada para select paginado de espacio al editar
  const selectedSpaceOption = computed(() => {
    const space = editingAssignment.value?.espacio;
    return space ? {
      value: space.id,
      label: `${space.codigo_espacio} · ${space.pabellon || ''}`.trim().replace(/\s·\s$/, ''),
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

  // Carga catalogos de sedes y edificios sin forzar descarga completa de espacios ni usuarios
  const loadCatalogs = async () => {
    if (typeof service.obtenerOpciones === 'function') {
      try {
        const data = await service.obtenerOpciones();
        if (data) {
          localesList.value = data.locales || [];
          edificiosList.value = data.edificios || [];
          espaciosList.value = data.espacios || [];
        }
      } catch {
        // En caso de fallo de red, se mantiene el estado previo sin interrumpir
      }
    } else {
      try {
        if (optionServices?.locales?.listar) {
          const lData = await optionServices.locales.listar({ activo: 'true', page_size: 100 });
          localesList.value = lData.results ?? lData;
        }
        if (optionServices?.edificios?.listar) {
          const eData = await optionServices.edificios.listar({ activo: 'true', page_size: 200 });
          edificiosList.value = eData.results ?? eData;
        }
      } catch {
        // Fallback silencioso
      }
    }
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

  const loadData = async () => {
    await Promise.all([loadAssignments(), loadCatalogs()]);
  };

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
  };

  // Handlers de cambio en cascada
  const onAmbitoChange = (nuevoAmbito) => {
    if (nuevoAmbito) {
      form.tipo_ambito = nuevoAmbito;
      form.ambito = nuevoAmbito;
    }
    delete formErrors.local_id;
    delete formErrors.edificio_id;
    delete formErrors.piso;
    delete formErrors.espacio_id;

    const currentScope = form.tipo_ambito || form.ambito;
    if (currentScope === 'sede') {
      form.edificio_id = '';
      form.piso = '';
      form.espacio_id = '';
    } else if (currentScope === 'edificio') {
      form.piso = '';
      form.espacio_id = '';
    } else if (currentScope === 'piso') {
      form.espacio_id = '';
    }
  };

  const onLocalChange = (localId) => {
    if (localId !== undefined) {
      form.local_id = localId;
    }
    form.edificio_id = '';
    form.piso = '';
    form.espacio_id = '';
    delete formErrors.edificio_id;
    delete formErrors.piso;
    delete formErrors.espacio_id;
  };

  const onEdificioChange = (edificioId) => {
    if (edificioId !== undefined) {
      form.edificio_id = edificioId;
    }
    form.piso = '';
    form.espacio_id = '';
    delete formErrors.piso;
    delete formErrors.espacio_id;
  };

  const onPisoChange = (piso) => {
    if (piso !== undefined) {
      form.piso = piso;
    }
    form.espacio_id = '';
    delete formErrors.espacio_id;
  };

  const openCreate = () => {
    editingAssignment.value = null;
    resetForm();
    modalOpen.value = true;
  };

  const openEdit = (assignment) => {
    editingAssignment.value = assignment;
    resetForm();

    const ambito = assignment.ambito || (assignment.espacio ? 'espacio' : 'sede');
    const localId = assignment.local_id ?? assignment.local?.id ?? assignment.edificio?.local_id ?? '';
    const edificioId = assignment.edificio_id ?? assignment.edificio?.id ?? '';
    const piso = assignment.piso ?? assignment.espacio?.piso ?? '';
    const espacioId = assignment.espacio_id ?? assignment.espacio?.id ?? '';
    const usuarioId = assignment.usuario?.id ?? assignment.usuario_id ?? '';

    Object.assign(form, {
      tipo_ambito: ambito,
      ambito,
      local_id: localId !== '' && localId !== null && localId !== undefined ? localId : '',
      edificio_id: edificioId !== '' && edificioId !== null && edificioId !== undefined ? edificioId : '',
      piso: piso !== '' && piso !== null && piso !== undefined ? String(piso) : '',
      espacio_id: espacioId !== '' && espacioId !== null && espacioId !== undefined ? espacioId : '',
      usuario_id: usuarioId !== '' && usuarioId !== null && usuarioId !== undefined ? usuarioId : '',
      tipo_responsabilidad: assignment.tipo_responsabilidad ?? 'responsable',
      activo: assignment.activo !== undefined ? Boolean(assignment.activo) : true,
    });
    modalOpen.value = true;
  };

  const closeModal = () => {
    modalOpen.value = false;
    editingAssignment.value = null;
    resetForm();
  };

  // Validacion por nivel territorial segun el ambito seleccionado
  const validateForm = () => {
    Object.keys(formErrors).forEach((key) => delete formErrors[key]);
    if (!form.usuario_id) formErrors.usuario_id = 'Selecciona un usuario.';
    if (!form.tipo_responsabilidad) formErrors.tipo_responsabilidad = 'Selecciona una responsabilidad.';

    const ambito = form.tipo_ambito || form.ambito || 'espacio';

    if (ambito === 'sede') {
      if (!form.local_id) formErrors.local_id = 'Selecciona una sede.';
    } else if (ambito === 'edificio') {
      if (!form.local_id) formErrors.local_id = 'Selecciona una sede.';
      if (!form.edificio_id) formErrors.edificio_id = 'Selecciona un pabellón o edificio.';
    } else if (ambito === 'piso') {
      if (!form.local_id) formErrors.local_id = 'Selecciona una sede.';
      if (!form.edificio_id) formErrors.edificio_id = 'Selecciona un pabellón o edificio.';
      if (!form.piso || String(form.piso).trim() === '') {
        formErrors.piso = 'Selecciona o ingresa un piso.';
      }
    } else if (ambito === 'espacio') {
      if (!form.espacio_id) formErrors.espacio_id = 'Selecciona un espacio.';
    }

    return Object.keys(formErrors).length === 0;
  };

  // Construye el payload limpio segun el contrato de API para cada ambito
  const buildPayload = () => {
    const ambito = form.tipo_ambito || form.ambito || 'espacio';
    const payload = {
      usuario_id: Number(form.usuario_id),
      tipo_responsabilidad: form.tipo_responsabilidad,
      activo: Boolean(form.activo),
      ambito,
    };

    if (ambito === 'sede') {
      payload.local_id = Number(form.local_id);
      payload.edificio_id = null;
      payload.piso = null;
      payload.espacio_id = null;
    } else if (ambito === 'edificio') {
      payload.local_id = Number(form.local_id);
      payload.edificio_id = Number(form.edificio_id);
      payload.piso = null;
      payload.espacio_id = null;
    } else if (ambito === 'piso') {
      payload.local_id = Number(form.local_id);
      payload.edificio_id = Number(form.edificio_id);
      payload.piso = String(form.piso).trim();
      payload.espacio_id = null;
    } else if (ambito === 'espacio') {
      payload.espacio_id = Number(form.espacio_id);
    }

    return payload;
  };

  const submit = async () => {
    if (!validateForm()) return false;
    saving.value = true;
    const payload = buildPayload();

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

  // Formateador defensivo de ubicacion para tablas y textos
  const getUbicacionDisplay = (item) => {
    if (!item) return '-';
    if (item.ubicacion_display) return item.ubicacion_display;
    if (item.ambito === 'sede') return item.local?.nombre || 'Sede institucional';
    if (item.ambito === 'edificio') return item.edificio?.nombre || 'Pabellón / Edificio';
    if (item.ambito === 'piso') {
      const edif = item.edificio?.nombre || 'Pabellón';
      return item.piso ? `${edif} · Piso ${item.piso}` : edif;
    }
    if (item.ambito === 'espacio' || item.espacio) {
      const sp = item.espacio;
      return sp ? `${sp.codigo_espacio} · ${sp.pabellon || ''}` : 'Espacio individual';
    }
    return '-';
  };

  const { applyFilters, resetFilters } = useAutoFilters(filters, loadAssignments, {
    immediateKeys: ['activo', 'local_id', 'edificio_id', 'ambito'],
  });

  const clearFilters = () => resetFilters({
    search: '',
    activo: '',
    local_id: '',
    edificio_id: '',
    ambito: '',
  });

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
    ambitoOptions,
    responsibilityOptions,
    localOptions,
    localSelectOptions,
    localFilterOptions,
    filteredEdificios,
    filteredEdificioOptions,
    availablePisos,
    filteredEspacios,
    edificiosParaFiltro,
    edificioFilterOptions,
    filtroLocal,
    filtroEdificio,
    selectedUserOption,
    selectedSpaceOption,
    loadUserOptions,
    loadSpaceOptions,
    loadAssignments,
    loadCatalogs,
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
    onAmbitoChange,
    onLocalChange,
    onEdificioChange,
    onPisoChange,
    getUbicacionDisplay,
  };
}

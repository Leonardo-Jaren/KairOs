import { computed, onMounted, reactive, ref, shallowRef, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import localesService from '@/services/locales.service';
import { normalizeFloorLayout } from '@/composables/espacios/useCroquisPiso';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';
import { formatFloor } from '@/utils/formatters';

const naturalCompare = (left, right) => String(left).localeCompare(String(right), 'es', {
  numeric: true,
  sensitivity: 'base',
});

const normalizeFloorValue = (value) => String(value ?? '')
  .trim()
  .replace(/^piso\s*/i, '')
  .trim();

export const getEspacioHealth = (space) => {
  const damaged = Number(space.resumen_equipos?.dañado ?? 0);
  const maintenance = Number(space.resumen_equipos?.en_mantenimiento ?? 0);
  const count = Number(space.cantidad_equipos ?? 0);

  if (damaged > 0) {
    return {
      status: 'incidencia',
      label: `Incidencia (${damaged})`,
      dotClass: 'bg-danger-500',
      badgeClass: 'bg-danger-50 text-danger-700 border-danger-200/80',
    };
  }
  if (maintenance > 0) {
    return {
      status: 'mantenimiento',
      label: `Mantenimiento (${maintenance})`,
      dotClass: 'bg-amber-500',
      badgeClass: 'bg-amber-50 text-amber-700 border-amber-200/80',
    };
  }
  if (count > 0) {
    return {
      status: 'optimo',
      label: 'Operativo',
      dotClass: 'bg-emerald-500',
      badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
    };
  }
  return {
    status: 'vacio',
    label: 'Sin equipos',
    dotClass: 'bg-slate-400',
    badgeClass: 'bg-slate-100 text-slate-600 border-slate-200',
  };
};

export const formatFloorTitle = (floorKey, totalFloors, index) => {
  const base = formatFloor(floorKey);
  if (totalFloors <= 1) return `${base} · Planta Única`;
  if (index === 0) return `${base} · Nivel Superior`;
  if (index === totalFloors - 1) return `${base} · Planta Baja`;
  return `${base} · Nivel Intermedio`;
};

const emptySede = () => ({
  codigo: '',
  nombre: '',
  ciudad: '',
  tipo: 'sede',
  descripcion: '',
  activo: true,
});

const emptyEdificio = () => ({
  codigo: '',
  nombre: '',
  descripcion: '',
  local_id: '',
  activo: true,
});

const emptyEspacio = () => ({
  codigo_espacio: '',
  tipo: 'laboratorio',
  local_id: '',
  edificio_id: '',
  piso: '',
  activo: true,
});

export function useEspaciosJerarquia(options = {}) {
  const {
    spaceService = espaciosService,
    buildingService = edificiosService,
    localService = localesService,
    assignService = espaciosUsuariosService,
    route: customRoute = null,
    router: customRouter = null,
  } = options;

  let router = customRouter;
  let route = customRoute;
  try {
    if (!router) router = useRouter();
    if (!route) route = useRoute();
  } catch {
    // Entorno de pruebas sin proveedor de router
  }

  const authStore = useAuthStore();
  const loading = ref(false);
  const saving = ref(false);
  const error = ref('');

  // Vista activa: 'jerarquia' | 'inventario'
  const currentView = ref('jerarquia');
  const searchQuery = ref('');
  const selectedCity = ref('');

  // Navegacion jerarquica
  const selectedSedeId = ref(null);
  const selectedEdificioId = ref(null);

  // Datos base
  const locales = ref([]);
  const edificios = ref([]);
  const espacios = ref([]);
  const stats = reactive({ total: 0, activos: 0, laboratorios: 0, equipos: 0 });
  const floorAssignments = ref([]);

  // Modales y formularios
  const sedeModalOpen = ref(false);
  const editingSede = ref(null);
  const sedeForm = reactive(emptySede());
  const sedeErrors = reactive({});
  const deleteSedeModalOpen = ref(false);
  const pendingDeleteSede = ref(null);

  const edificioModalOpen = ref(false);
  const editingEdificio = ref(null);
  const edificioForm = reactive(emptyEdificio());
  const edificioErrors = reactive({});
  const deleteEdificioModalOpen = ref(false);
  const pendingDeleteEdificio = ref(null);

  const espacioModalOpen = ref(false);
  const editingEspacio = ref(null);
  const espacioForm = reactive(emptyEspacio());
  const espacioErrors = reactive({});
  const deleteEspacioModalOpen = ref(false);
  const pendingDeleteEspacio = ref(null);

  const technicianModalOpen = ref(false);
  const technicianTarget = ref(null);
  const technicianForm = reactive({
    assignment_id: null,
    usuario_id: '',
    tipo_responsabilidad: 'tecnico',
  });
  const technicianOptions = ref([]);
  const technicianLoading = ref(false);
  const technicianSaving = ref(false);

  const croquisModalOpen = ref(false);
  const croquisTargetFloor = ref(null);

  const detailEspacio = shallowRef(null);
  const toast = reactive({ show: false, message: '', type: 'success' });

  // Filtros y paginacion de la vista inventario
  const inventoryFilters = reactive({ search: '', tipo: '', activo: '', page: 1, page_size: 10 });
  const inventoryPagination = reactive({ total: 0, totalPages: 1 });

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };
  const closeToast = () => { toast.show = false; };

  const canEdit = computed(() => (
    authStore.isSuperAdmin
    || authStore.isAdmin
    || authStore.hasPermission('espacios', 'editar')
  ));

  const typeOptions = [
    { value: 'laboratorio', label: 'Laboratorio' },
    { value: 'sala_computo', label: 'Sala de cómputo' },
    { value: 'aula', label: 'Aula' },
    { value: 'oficina', label: 'Oficina' },
    { value: 'otro', label: 'Otro' },
  ];

  const sedeTipoOptions = [
    { value: 'campus', label: 'Campus' },
    { value: 'sede', label: 'Sede' },
    { value: 'anexo', label: 'Anexo' },
    { value: 'otro', label: 'Otro' },
  ];

  // Sincronizacion bidireccional con parametros de URL
  const updateRouteQuery = (newQuery = {}, replace = true) => {
    if (!router || !route) return;
    const query = { ...route.query, ...newQuery };
    Object.keys(query).forEach((key) => {
      if (query[key] === undefined || query[key] === null || query[key] === '') {
        delete query[key];
      }
    });
    const method = replace ? 'replace' : 'push';
    router[method]({ query }).catch(() => {});
  };

  const syncStateFromRoute = () => {
    if (!route) return;
    if (route.query.vista === 'inventario') {
      currentView.value = 'inventario';
    } else {
      currentView.value = 'jerarquia';
    }

    if (route.query.sede) {
      const parsedSede = Number(route.query.sede);
      selectedSedeId.value = Number.isNaN(parsedSede) ? route.query.sede : parsedSede;
    } else {
      selectedSedeId.value = null;
    }

    if (route.query.edificio) {
      const parsedEdif = Number(route.query.edificio);
      selectedEdificioId.value = Number.isNaN(parsedEdif) ? route.query.edificio : parsedEdif;
    } else {
      selectedEdificioId.value = null;
    }
    selectedCity.value = String(route.query.ciudad || '');
  };

  const setVista = (vista) => {
    currentView.value = vista;
    updateRouteQuery({ vista: vista === 'inventario' ? 'inventario' : undefined }, false);
  };

  const selectSede = (sedeId) => {
    selectedCity.value = locales.value.find((local) => String(local.id) === String(sedeId))?.ciudad || selectedCity.value;
    selectedSedeId.value = sedeId;
    selectedEdificioId.value = null;
    updateRouteQuery({ ciudad: selectedCity.value, sede: sedeId, edificio: undefined, piso: undefined }, false);
  };

  const selectCity = (city) => {
    selectedCity.value = city;
    selectedSedeId.value = null;
    selectedEdificioId.value = null;
    searchQuery.value = '';
    updateRouteQuery({ ciudad: city, sede: undefined, edificio: undefined, piso: undefined }, false);
  };

  const selectEdificio = (edificioId) => {
    selectedEdificioId.value = edificioId;
    updateRouteQuery({ edificio: edificioId, piso: undefined }, false);
  };

  const resetToSedes = () => {
    selectedSedeId.value = null;
    selectedEdificioId.value = null;
    updateRouteQuery({ sede: undefined, edificio: undefined, piso: undefined }, false);
  };

  const resetToCities = () => selectCity('');

  const resetToEdificios = () => {
    selectedEdificioId.value = null;
    updateRouteQuery({ edificio: undefined, piso: undefined }, false);
  };

  // Carga de datos principales
  const loadLocales = async () => {
    try {
      const data = await localService.listar({ activo: true, page_size: 100 });
      locales.value = data.results ?? data ?? [];
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudieron cargar las sedes.'), 'error');
    }
  };

  const loadEdificios = async () => {
    try {
      const data = await buildingService.listar({ activo: true, page_size: 100 });
      edificios.value = data.results ?? data ?? [];
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudieron cargar los pabellones.'), 'error');
    }
  };

  const loadEspacios = async () => {
    try {
      const data = await spaceService.listar({ page_size: 500 });
      espacios.value = data.results ?? data ?? [];
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudieron cargar los ambientes.'), 'error');
    }
  };

  const loadEstadisticas = async () => {
    try {
      const data = await spaceService.obtenerEstadisticas();
      Object.assign(stats, data);
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudieron cargar las estadísticas.'), 'error');
    }
  };

  const loadFloorAssignments = async (buildingId) => {
    if (!buildingId) {
      floorAssignments.value = [];
      return;
    }
    try {
      const res = await assignService.listar({
        ambito: 'piso',
        edificio_id: buildingId,
        activo: 'true',
        page_size: 100,
      });
      floorAssignments.value = res.results ?? res ?? [];
    } catch {
      floorAssignments.value = [];
    }
  };

  const loadAllData = async () => {
    loading.value = true;
    error.value = '';
    try {
      await Promise.all([
        loadLocales(),
        loadEdificios(),
        loadEspacios(),
        loadEstadisticas(),
      ]);
      if (selectedEdificioId.value) {
        await loadFloorAssignments(selectedEdificioId.value);
      }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Error al sincronizar datos territoriales.');
    } finally {
      loading.value = false;
    }
  };

  // Reaccionar a cambios de edificio seleccionado para cargar encargados de piso
  watch(selectedEdificioId, (newId) => {
    if (newId) {
      loadFloorAssignments(newId);
    } else {
      floorAssignments.value = [];
    }
  });

  // Reaccionar a cambios en ruta URL (navegacion por historial o query params)
  if (route) {
    watch(() => route.query, () => {
      syncStateFromRoute();
    });
  }

  // Estructuras computadas de la jerarquia territorial

  // 1. Sedes con agregados de pabellones, ambientes y telemetria
  const sedesList = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();
    return locales.value
      .filter((sede) => {
        if (!query) return true;
        return (
          String(sede.nombre || '').toLowerCase().includes(query)
          || String(sede.codigo || '').toLowerCase().includes(query)
          || String(sede.ciudad || '').toLowerCase().includes(query)
        );
      })
      .map((sede) => {
        const sedeEdificios = edificios.value.filter(
          (e) => String(e.local_id ?? e.local?.id) === String(sede.id),
        );
        const edificioIds = new Set(sedeEdificios.map((e) => Number(e.id)));
        const sedeEspacios = espacios.value.filter((esp) => (
          edificioIds.has(Number(esp.edificio_id ?? esp.edificio?.id))
        ));

        const equiposCount = sedeEspacios.reduce(
          (total, esp) => total + Number(esp.cantidad_equipos ?? 0),
          0,
        );
        const enMantenimiento = sedeEspacios.reduce(
          (total, esp) => total + Number(esp.resumen_equipos?.en_mantenimiento ?? 0),
          0,
        );
        const incidencias = sedeEspacios.reduce(
          (total, esp) => total + Number(esp.resumen_equipos?.dañado ?? 0),
          0,
        );
        const operativos = Math.max(0, equiposCount - enMantenimiento - incidencias);

        let salud = 'optimo';
        if (incidencias > 0) salud = 'incidencia';
        else if (enMantenimiento > 0) salud = 'mantenimiento';
        else if (equiposCount === 0) salud = 'vacio';

        return {
          ...sede,
          edificios: sedeEdificios,
          edificiosCount: sedeEdificios.length,
          espacios: sedeEspacios,
          ambientesCount: sedeEspacios.length,
          equiposCount,
          telemetria: { operativos, mantenimiento: enMantenimiento, incidencias },
          salud,
        };
      });
  });

  const cityCards = computed(() => [...new Set(locales.value.map((local) => local.ciudad).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'es'))
    .map((city) => ({
      label: city,
      localCount: locales.value.filter((local) => local.ciudad === city).length,
      buildingCount: edificios.value.filter((building) => locales.value.some((local) => (
        local.ciudad === city && String(local.id) === String(building.local_id ?? building.local?.id)
      ))).length,
    })));

  const selectedSede = computed(() => (
    sedesList.value.find((s) => String(s.id) === String(selectedSedeId.value))
    || locales.value.find((s) => String(s.id) === String(selectedSedeId.value))
    || null
  ));

  // 2. Pabellones / Edificios pertenecientes a la sede seleccionada
  const edificiosDeSede = computed(() => {
    if (!selectedSedeId.value) return [];
    return edificios.value
      .filter((e) => String(e.local_id ?? e.local?.id) === String(selectedSedeId.value))
      .map((edificio) => {
        const buildingSpaces = espacios.value.filter(
          (esp) => Number(esp.edificio_id ?? esp.edificio?.id) === Number(edificio.id),
        );
        const floors = [...new Set(buildingSpaces.map((s) => normalizeFloorValue(s.piso)))].sort(naturalCompare);
        const equiposCount = buildingSpaces.reduce(
          (total, esp) => total + Number(esp.cantidad_equipos ?? 0),
          0,
        );
        const enMantenimiento = buildingSpaces.reduce(
          (total, esp) => total + Number(esp.resumen_equipos?.en_mantenimiento ?? 0),
          0,
        );
        const incidencias = buildingSpaces.reduce(
          (total, esp) => total + Number(esp.resumen_equipos?.dañado ?? 0),
          0,
        );
        const operativos = Math.max(0, equiposCount - enMantenimiento - incidencias);

        let salud = 'optimo';
        if (incidencias > 0) salud = 'incidencia';
        else if (enMantenimiento > 0) salud = 'mantenimiento';
        else if (equiposCount === 0) salud = 'vacio';

        return {
          ...edificio,
          spaces: buildingSpaces,
          pisos: floors,
          pisosCount: floors.length || (edificio.configuracion_croquis?.pisos ? Object.keys(edificio.configuracion_croquis.pisos).length : 0),
          ambientesCount: buildingSpaces.length,
          equiposCount,
          telemetria: { operativos, mantenimiento: enMantenimiento, incidencias },
          salud,
        };
      });
  });

  const selectedEdificio = computed(() => (
    edificiosDeSede.value.find((e) => String(e.id) === String(selectedEdificioId.value))
    || edificios.value.find((e) => String(e.id) === String(selectedEdificioId.value))
    || null
  ));

  // 3. Plantas Verticales / Pisos ordenados de arriba a abajo (Piso 3, Piso 2, Piso 1)
  const getFloorEncargado = (floorKey) => {
    const normalized = normalizeFloorValue(floorKey);
    const match = floorAssignments.value.find(
      (asig) => normalizeFloorValue(asig.piso) === normalized && asig.activo !== false,
    );
    if (!match) return null;
    return {
      id: match.id,
      usuario_id: match.usuario?.id ?? match.usuario_id,
      usuario_nombre: match.usuario?.nombre_completo ?? `${match.usuario?.nombre ?? ''} ${match.usuario?.apellido ?? ''}`.trim(),
      correo: match.usuario?.correo ?? '',
      tipo_responsabilidad: match.tipo_responsabilidad ?? 'tecnico',
      tipo_responsabilidad_display: match.tipo_responsabilidad_display ?? 'Técnico',
      badge_texto: match.badge_texto ?? `Encargado Piso ${match.piso}`,
    };
  };

  const pisosDeEdificio = computed(() => {
    if (!selectedEdificio.value) return [];
    const building = selectedEdificio.value;
    const buildingSpaces = espacios.value.filter(
      (esp) => Number(esp.edificio_id ?? esp.edificio?.id) === Number(building.id),
    );

    // Agrupar pisos existentes en los espacios y configuracion de croquis
    const floorSet = new Set(buildingSpaces.map((s) => normalizeFloorValue(s.piso)));
    if (building.configuracion_croquis?.pisos) {
      Object.keys(building.configuracion_croquis.pisos).forEach((p) => {
        floorSet.add(normalizeFloorValue(p));
      });
    }

    // Orden vertical descendente (de mayor piso a menor piso: 3, 2, 1)
    const sortedFloors = [...floorSet].filter(Boolean).sort((a, b) => naturalCompare(b, a));

    // Si no habia ningun piso registrado, proveer al menos el piso 1 por defecto
    if (sortedFloors.length === 0) {
      sortedFloors.push('1');
    }

    const totalFloors = sortedFloors.length;

    return sortedFloors.map((floorKey, index) => {
      const floorSpaces = buildingSpaces
        .filter((esp) => normalizeFloorValue(esp.piso) === floorKey)
        .sort((a, b) => naturalCompare(a.codigo_espacio, b.codigo_espacio))
        .map((space) => ({
          ...space,
          health: getEspacioHealth(space),
        }));

      const totalEquipos = floorSpaces.reduce(
        (sum, s) => sum + Number(s.cantidad_equipos ?? 0),
        0,
      );
      const enMantenimiento = floorSpaces.reduce(
        (sum, s) => sum + Number(s.resumen_equipos?.en_mantenimiento ?? 0),
        0,
      );
      const incidencias = floorSpaces.reduce(
        (sum, s) => sum + Number(s.resumen_equipos?.dañado ?? 0),
        0,
      );
      const operativos = Math.max(0, totalEquipos - enMantenimiento - incidencias);

      const storedFloors = building.configuracion_croquis?.pisos ?? {};
      const storedLayout = storedFloors[floorKey]
        ?? Object.entries(storedFloors).find(([k]) => normalizeFloorValue(k) === floorKey)?.[1];

      return {
        key: floorKey,
        piso: floorKey,
        label: formatFloorTitle(floorKey, totalFloors, index),
        edificio_id: Number(building.id),
        edificio_nombre: building.nombre,
        local_id: Number(building.local_id ?? building.local?.id ?? selectedSedeId.value ?? 0) || null,
        encargado: getFloorEncargado(floorKey),
        spaces: floorSpaces,
        allSpaces: floorSpaces,
        labs: floorSpaces.filter((space) => ['laboratorio', 'sala_computo'].includes(space.tipo)).length,
        aulas: floorSpaces.filter((space) => space.tipo === 'aula').length,
        layout: normalizeFloorLayout(storedLayout, floorSpaces),
        telemetria: {
          operativos,
          mantenimiento: enMantenimiento,
          incidencias,
          totalEquipos,
        },
      };
    });
  });

  // Opciones para formularios asistidos
  const allLocalesOptions = computed(() => locales.value.map((loc) => ({
    value: loc.id,
    label: `${loc.codigo} · ${loc.nombre} (${loc.ciudad})`,
  })));

  const edificiosOptionsForSede = computed(() => {
    let list = edificios.value;
    if (espacioForm.local_id) {
      list = list.filter((e) => String(e.local_id ?? e.local?.id) === String(espacioForm.local_id));
    }
    return list.map((b) => ({
      value: b.id,
      label: `${b.codigo} · ${b.nombre}`,
    }));
  });

  const pisosExistentesEnEdificio = computed(() => {
    if (!espacioForm.edificio_id) return [];
    const spaces = espacios.value.filter(
      (s) => Number(s.edificio_id ?? s.edificio?.id) === Number(espacioForm.edificio_id),
    );
    const floors = [...new Set(spaces.map((s) => normalizeFloorValue(s.piso)))].filter(Boolean);
    return floors.sort(naturalCompare);
  });

  // Acciones y Modales: Sedes
  const openCreateSede = () => {
    if (!canEdit.value) return;
    editingSede.value = null;
    Object.assign(sedeForm, emptySede());
    Object.keys(sedeErrors).forEach((k) => delete sedeErrors[k]);
    sedeModalOpen.value = true;
  };

  const openEditSede = (sede) => {
    if (!canEdit.value || !sede) return;
    editingSede.value = sede;
    Object.assign(sedeForm, {
      codigo: sede.codigo,
      nombre: sede.nombre,
      ciudad: sede.ciudad,
      tipo: sede.tipo || 'sede',
      descripcion: sede.descripcion || '',
      activo: sede.activo !== false,
    });
    Object.keys(sedeErrors).forEach((k) => delete sedeErrors[k]);
    sedeModalOpen.value = true;
  };

  const closeSedeModal = () => {
    sedeModalOpen.value = false;
    editingSede.value = null;
  };

  const submitSede = async () => {
    if (!canEdit.value) return false;
    Object.keys(sedeErrors).forEach((k) => delete sedeErrors[k]);
    if (!sedeForm.codigo.trim()) sedeErrors.codigo = 'Ingresa el código de la sede.';
    if (!sedeForm.nombre.trim()) sedeErrors.nombre = 'Ingresa el nombre de la sede.';
    if (!sedeForm.ciudad.trim()) sedeErrors.ciudad = 'Ingresa la ciudad de la sede.';
    if (Object.keys(sedeErrors).length) return false;

    saving.value = true;
    try {
      if (editingSede.value) {
        await localService.actualizar(editingSede.value.id, { ...sedeForm });
        showToast('Sede actualizada correctamente.');
      } else {
        await localService.crear({ ...sedeForm });
        showToast('Sede creada correctamente.');
      }
      closeSedeModal();
      await loadLocales();
      return true;
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo guardar la sede.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDeleteSede = (sede) => {
    if (!canEdit.value || !sede) return;
    pendingDeleteSede.value = sede;
    deleteSedeModalOpen.value = true;
  };

  const confirmDeleteSede = async () => {
    if (!pendingDeleteSede.value) return;
    saving.value = true;
    try {
      await localService.desactivar(pendingDeleteSede.value.id);
      showToast('Sede desactivada correctamente.');
      deleteSedeModalOpen.value = false;
      pendingDeleteSede.value = null;
      await loadLocales();
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo desactivar la sede.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  // Acciones y Modales: Edificios / Pabellones
  const openCreateEdificio = (preselectedSedeId = null) => {
    if (!canEdit.value) return;
    editingEdificio.value = null;
    Object.assign(edificioForm, emptyEdificio());
    edificioForm.local_id = preselectedSedeId ?? selectedSedeId.value ?? '';
    Object.keys(edificioErrors).forEach((k) => delete edificioErrors[k]);
    edificioModalOpen.value = true;
  };

  const openEditEdificio = (edificio) => {
    if (!canEdit.value || !edificio) return;
    editingEdificio.value = edificio;
    Object.assign(edificioForm, {
      codigo: edificio.codigo,
      nombre: edificio.nombre,
      descripcion: edificio.descripcion || '',
      local_id: edificio.local_id ?? edificio.local?.id ?? '',
      activo: edificio.activo !== false,
    });
    Object.keys(edificioErrors).forEach((k) => delete edificioErrors[k]);
    edificioModalOpen.value = true;
  };

  const closeEdificioModal = () => {
    edificioModalOpen.value = false;
    editingEdificio.value = null;
  };

  const submitEdificio = async () => {
    if (!canEdit.value) return false;
    Object.keys(edificioErrors).forEach((k) => delete edificioErrors[k]);
    if (!edificioForm.codigo.trim()) edificioErrors.codigo = 'Ingresa el código del pabellón.';
    if (!edificioForm.nombre.trim()) edificioErrors.nombre = 'Ingresa el nombre del pabellón.';
    if (!edificioForm.local_id) edificioErrors.local_id = 'Selecciona la sede correspondiente.';
    if (Object.keys(edificioErrors).length) return false;

    saving.value = true;
    try {
      const payload = {
        ...edificioForm,
        local_id: Number(edificioForm.local_id),
      };
      if (editingEdificio.value) {
        await buildingService.actualizar(editingEdificio.value.id, payload);
        showToast('Pabellón actualizado correctamente.');
      } else {
        await buildingService.crear(payload);
        showToast('Pabellón creado correctamente.');
      }
      closeEdificioModal();
      await loadEdificios();
      return true;
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo guardar el pabellón.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDeleteEdificio = (edificio) => {
    if (!canEdit.value || !edificio) return;
    pendingDeleteEdificio.value = edificio;
    deleteEdificioModalOpen.value = true;
  };

  const confirmDeleteEdificio = async () => {
    if (!pendingDeleteEdificio.value) return;
    saving.value = true;
    try {
      await buildingService.desactivar(pendingDeleteEdificio.value.id);
      showToast('Pabellón desactivado correctamente.');
      deleteEdificioModalOpen.value = false;
      pendingDeleteEdificio.value = null;
      await loadEdificios();
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo desactivar el pabellón.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  // Acciones y Modales: Espacios / Ambientes
  const openCreateEspacio = (context = {}) => {
    if (!canEdit.value) return;
    editingEspacio.value = null;
    Object.assign(espacioForm, emptyEspacio());
    espacioForm.local_id = context.sedeId ?? selectedSedeId.value ?? '';
    espacioForm.edificio_id = context.edificioId ?? selectedEdificioId.value ?? '';
    espacioForm.piso = context.piso !== undefined ? String(context.piso) : '';
    Object.keys(espacioErrors).forEach((k) => delete espacioErrors[k]);
    espacioModalOpen.value = true;
  };

  const openEditEspacio = (space) => {
    if (!canEdit.value || !space) return;
    editingEspacio.value = space;
    const building = edificios.value.find((b) => Number(b.id) === Number(space.edificio_id ?? space.edificio?.id));
    Object.assign(espacioForm, {
      codigo_espacio: space.codigo_espacio,
      tipo: space.tipo,
      local_id: building?.local_id ?? building?.local?.id ?? selectedSedeId.value ?? '',
      edificio_id: space.edificio_id ?? space.edificio?.id ?? '',
      piso: String(space.piso ?? '').trim(),
      activo: space.activo !== false,
    });
    Object.keys(espacioErrors).forEach((k) => delete espacioErrors[k]);
    espacioModalOpen.value = true;
  };

  const closeEspacioModal = () => {
    espacioModalOpen.value = false;
    editingEspacio.value = null;
  };

  const submitEspacio = async () => {
    if (!canEdit.value) return false;
    Object.keys(espacioErrors).forEach((k) => delete espacioErrors[k]);
    if (!espacioForm.codigo_espacio.trim()) espacioErrors.codigo_espacio = 'Ingresa el código del ambiente.';
    if (!espacioForm.tipo) espacioErrors.tipo = 'Selecciona el tipo de espacio.';
    if (!espacioForm.edificio_id) espacioErrors.edificio_id = 'Selecciona el pabellón.';
    if (!/^\d+$/.test(String(espacioForm.piso ?? '').trim())) {
      espacioErrors.piso = 'El piso debe contener únicamente números.';
    }
    if (Object.keys(espacioErrors).length) return false;

    saving.value = true;
    const payload = {
      codigo_espacio: espacioForm.codigo_espacio.trim(),
      tipo: espacioForm.tipo,
      edificio_id: Number(espacioForm.edificio_id),
      piso: String(espacioForm.piso).trim(),
      activo: espacioForm.activo,
    };

    try {
      if (editingEspacio.value) {
        await spaceService.actualizar(editingEspacio.value.id, payload);
        showToast('Ambiente actualizado correctamente.');
      } else {
        await spaceService.crear(payload);
        showToast('Ambiente creado correctamente.');
      }
      closeEspacioModal();
      await Promise.all([loadEspacios(), loadEstadisticas()]);
      return true;
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo guardar el ambiente.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDeleteEspacio = (space) => {
    if (!canEdit.value || !space) return;
    pendingDeleteEspacio.value = space;
    deleteEspacioModalOpen.value = true;
  };

  const confirmDeleteEspacio = async () => {
    if (!pendingDeleteEspacio.value) return;
    saving.value = true;
    try {
      await spaceService.desactivar(pendingDeleteEspacio.value.id);
      showToast('Ambiente desactivado correctamente.');
      deleteEspacioModalOpen.value = false;
      pendingDeleteEspacio.value = null;
      await Promise.all([loadEspacios(), loadEstadisticas()]);
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo desactivar el ambiente.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  // Acciones y Modal: Asignar Técnico de Piso
  const openAssignTechnicianModal = async (target) => {
    if (!canEdit.value) return;
    technicianTarget.value = target;
    technicianForm.assignment_id = target.encargado?.id ?? null;
    technicianForm.usuario_id = target.encargado?.usuario_id ?? '';
    technicianForm.tipo_responsabilidad = target.encargado?.tipo_responsabilidad ?? 'tecnico';
    technicianModalOpen.value = true;

    if (!technicianOptions.value.length) {
      technicianLoading.value = true;
      try {
        const data = await assignService.obtenerOpciones();
        const users = data?.usuarios ?? [];
        technicianOptions.value = users
          .filter((u) => ['tecnico', 'responsable', 'admin'].includes(u.rol))
          .map((u) => ({
            value: u.id,
            label: `${u.nombre} ${u.apellido} (${u.rol}) · ${u.correo}`,
          }));
      } catch {
        technicianOptions.value = [];
      } finally {
        technicianLoading.value = false;
      }
    }
  };

  const submitTechnicianAssignment = async () => {
    if (!technicianForm.usuario_id || !technicianTarget.value || technicianSaving.value) return;
    technicianSaving.value = true;
    const target = technicianTarget.value;
    const payload = {
      usuario_id: Number(technicianForm.usuario_id),
      tipo_responsabilidad: technicianForm.tipo_responsabilidad || 'tecnico',
      activo: true,
      ambito: 'piso',
      local_id: target.local_id ? Number(target.local_id) : undefined,
      edificio_id: Number(target.edificio_id),
      piso: String(target.piso).trim(),
      espacio_id: null,
    };

    try {
      if (technicianForm.assignment_id) {
        await assignService.actualizar(technicianForm.assignment_id, payload);
      } else {
        await assignService.crear(payload);
      }
      technicianModalOpen.value = false;
      showToast('Técnico encargado del piso asignado correctamente.');
      await loadFloorAssignments(target.edificio_id);
    } catch (err) {
      showToast(getApiErrorMessage(err, 'No se pudo asignar el técnico al piso.'), 'error');
    } finally {
      technicianSaving.value = false;
    }
  };

  // Modal: Croquis 2D de piso
  const openCroquisModal = (floor) => {
    croquisTargetFloor.value = floor;
    croquisModalOpen.value = true;
  };

  const closeCroquisModal = () => {
    croquisModalOpen.value = false;
    croquisTargetFloor.value = null;
  };

  // Paginacion y filtros para la tabla de inventario
  const inventoryFilteredEspacios = computed(() => {
    let list = espacios.value;
    const scopeCity = route?.query?.ciudad;
    const scopeLocal = route?.query?.sede || route?.query?.local;
    const scopeBuilding = route?.query?.edificio || route?.query?.pabellon;
    if (scopeCity) {
      const ids = new Set(locales.value.filter((local) => local.ciudad === scopeCity).map((local) => String(local.id)));
      const buildingIds = new Set(edificios.value.filter((building) => ids.has(String(building.local_id ?? building.local?.id))).map((building) => String(building.id)));
      list = list.filter((space) => buildingIds.has(String(space.edificio_id ?? space.edificio?.id)));
    }
    if (scopeLocal) {
      const buildingIds = new Set(edificios.value.filter((building) => String(building.local_id ?? building.local?.id) === String(scopeLocal)).map((building) => String(building.id)));
      list = list.filter((space) => buildingIds.has(String(space.edificio_id ?? space.edificio?.id)));
    }
    if (scopeBuilding) list = list.filter((space) => String(space.edificio_id ?? space.edificio?.id) === String(scopeBuilding));
    const search = inventoryFilters.search.trim().toLowerCase();
    if (search) {
      list = list.filter((s) => (
        String(s.codigo_espacio || '').toLowerCase().includes(search)
        || String(s.pabellon || '').toLowerCase().includes(search)
        || String(s.piso || '').toLowerCase().includes(search)
        || String(s.responsable?.nombre_completo || '').toLowerCase().includes(search)
      ));
    }
    if (inventoryFilters.tipo) {
      list = list.filter((s) => s.tipo === inventoryFilters.tipo);
    }
    if (inventoryFilters.activo !== '') {
      const boolVal = inventoryFilters.activo === 'true';
      list = list.filter((s) => Boolean(s.activo) === boolVal);
    }
    return list;
  });

  const paginatedInventoryEspacios = computed(() => {
    const start = (inventoryFilters.page - 1) * inventoryFilters.page_size;
    return inventoryFilteredEspacios.value.slice(start, start + inventoryFilters.page_size);
  });

  const changeInventoryPage = (page) => {
    inventoryFilters.page = page;
  };

  const clearInventoryFilters = () => {
    inventoryFilters.search = '';
    inventoryFilters.tipo = '';
    inventoryFilters.activo = '';
    inventoryFilters.page = 1;
  };

  const clearInventoryScope = () => {
    inventoryFilters.page = 1;
    updateRouteQuery({ ciudad: undefined, sede: undefined, edificio: undefined, local: undefined, pabellon: undefined, piso: undefined });
  };

  onMounted(() => {
    syncStateFromRoute();
    loadAllData();
  });

  return {
    // Estado y navegacion
    loading, saving, error, currentView, searchQuery,
    selectedCity, selectedSedeId, selectedEdificioId, selectedSede, selectedEdificio,
    cityCards, sedesList, edificiosDeSede, pisosDeEdificio, stats,
    canEdit, typeOptions, sedeTipoOptions, allLocalesOptions,
    edificiosOptionsForSede, pisosExistentesEnEdificio,
    toast, detailEspacio,

    // Acciones de navegacion
    setVista, selectCity, selectSede, selectEdificio, resetToCities, resetToSedes, resetToEdificios,
    loadAllData, showToast, closeToast,

    // Formularios contextuales
    sedeModalOpen, editingSede, isEditingSede: computed(() => Boolean(editingSede.value)),
    sedeForm, sedeErrors, deleteSedeModalOpen, pendingDeleteSede,
    openCreateSede, openEditSede, closeSedeModal, submitSede, askDeleteSede, confirmDeleteSede,

    edificioModalOpen, editingEdificio, isEditingEdificio: computed(() => Boolean(editingEdificio.value)),
    edificioForm, edificioErrors, deleteEdificioModalOpen, pendingDeleteEdificio,
    openCreateEdificio, openEditEdificio, closeEdificioModal, submitEdificio, askDeleteEdificio, confirmDeleteEdificio,

    espacioModalOpen, editingEspacio, isEditingEspacio: computed(() => Boolean(editingEspacio.value)),
    espacioForm, espacioErrors, deleteEspacioModalOpen, pendingDeleteEspacio,
    openCreateEspacio, openEditEspacio, closeEspacioModal, submitEspacio, askDeleteEspacio, confirmDeleteEspacio,

    // Tecnico de piso
    technicianModalOpen, technicianTarget, technicianForm, technicianOptions,
    technicianLoading, technicianSaving, openAssignTechnicianModal, submitTechnicianAssignment,

    // Croquis 2D
    croquisModalOpen, croquisTargetFloor, openCroquisModal, closeCroquisModal,

    // Inventario
    inventoryFilters, inventoryFilteredEspacios, paginatedInventoryEspacios,
    inventoryPagination: computed(() => ({
      total: inventoryFilteredEspacios.value.length,
      totalPages: Math.max(1, Math.ceil(inventoryFilteredEspacios.value.length / inventoryFilters.page_size)),
    })),
    changeInventoryPage, clearInventoryFilters, clearInventoryScope,
  };
}

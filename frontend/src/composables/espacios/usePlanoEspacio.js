import { computed, onMounted, reactive, ref } from 'vue';

import equiposService from '@/services/equipos.service';
import espaciosService from '@/services/espacios.service';
import mantenimientoService from '@/services/mantenimiento.service';
import usuariosService from '@/services/usuarios.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const clamp = (value, min, max) => Math.min(max, Math.max(min, Number(value)));
const positionKey = (row, column) => `${row}-${column}`;
const today = () => new Date().toISOString().slice(0, 10);

const emptyReport = () => ({
  descripcion: '',
  tecnico_id: '',
  reportado_por_id: '',
  atencion: 'en_proceso',
});

const emptyEquipment = () => ({
  espacio: '',
  codigo: '',
  numero_serie: '',
  numero_mac: '',
  tipo_equipo: 'desktop',
  marca: '',
  modelo: '',
  modo_adquisicion: 'comprado',
  fecha_adquisicion: today(),
  fecha_renovacion: '',
  estado: 'en_uso',
  responsable_usuario: '',
});

export function usePlanoEspacio(
  id,
  spaceService = espaciosService,
  maintenanceService = mantenimientoService,
) {
  const authStore = useAuthStore();
  const espacio = ref(null);
  const loading = ref(false);
  const saving = ref(false);
  const error = ref('');
  const editing = ref(false);
  const columns = ref(6);
  const rows = ref(3);
  const positions = ref([]);
  const layoutBackup = ref(null);
  const selectedPositionId = ref(null);
  const selectedEquipo = ref(null);
  const equipmentDetailOpen = ref(false);
  const equipmentModalOpen = ref(false);
  const equipmentDeleteOpen = ref(false);
  const editingEquipment = ref(null);
  const pendingEquipmentDelete = ref(null);
  const equipmentSaving = ref(false);
  const equipmentForm = reactive(emptyEquipment());
  const equipmentErrors = reactive({});
  const activeMaintenances = ref([]);
  const maintenanceLoading = ref(false);
  const reportOpen = ref(false);
  const reportSaving = ref(false);
  const reportForm = reactive(emptyReport());
  const reportErrors = reactive({});
  const technicians = ref([]);
  const users = ref([]);
  const toast = reactive({ show: false, message: '', type: 'success' });

  const equipos = computed(() => espacio.value?.equipos ?? []);
  const canEdit = computed(() => authStore.user?.rol === 'admin');
  const isEditingEquipment = computed(() => Boolean(editingEquipment.value));
  const selectedPosition = computed(() => (
    positions.value.find((item) => item.equipo_id === selectedPositionId.value) ?? null
  ));
  const positionMap = computed(() => new Map(
    positions.value.map((position) => [positionKey(position.fila, position.columna), position]),
  ));
  const equipmentMap = computed(() => new Map(
    equipos.value.map((equipment) => [equipment.id, equipment]),
  ));
  const selectedLayoutEquipment = computed(() => (
    equipmentMap.value.get(selectedPositionId.value) ?? null
  ));
  const aisleColumns = computed(() => {
    const occupied = [...new Set(positions.value.map((position) => position.columna))];
    if (occupied.length < 2) return new Set();
    const firstOccupied = Math.min(...occupied);
    const lastOccupied = Math.max(...occupied);
    return new Set(Array.from({ length: columns.value }, (_, index) => index + 1)
      .filter((column) => (
        column > firstOccupied && column < lastOccupied && !occupied.includes(column)
      )));
  });
  const cells = computed(() => {
    const result = [];
    for (let row = 1; row <= rows.value; row += 1) {
      for (let column = 1; column <= columns.value; column += 1) {
        const position = positionMap.value.get(positionKey(row, column));
        result.push({
          row,
          column,
          position,
          equipment: position ? equipmentMap.value.get(position.equipo_id) : null,
          isAisle: !position && aisleColumns.value.has(column),
        });
      }
    }
    return result;
  });
  const statusSummary = computed(() => equipos.value.reduce((summary, equipment) => {
    if (equipment.estado in summary) summary[equipment.estado] += 1;
    return summary;
  }, { en_uso: 0, en_mantenimiento: 0, dañado: 0, de_baja: 0 }));
  const teacherEquipment = computed(() => {
    const teacher = positions.value.find((position) => position.es_docente);
    return teacher ? equipmentMap.value.get(teacher.equipo_id) : null;
  });
  const technicianOptions = computed(() => technicians.value.map((technician) => ({
    value: technician.id,
    label: `${technician.nombre_completo} · ${technician.area}`,
  })));
  const reporterOptions = computed(() => users.value.map((user) => ({
    value: user.id,
    label: `${user.nombre} ${user.apellido} · ${user.correo}`,
  })));

  const equipmentTypeOptions = [
    { value: 'desktop', label: 'Desktop' },
    { value: 'laptop', label: 'Laptop' },
    { value: 'servidor', label: 'Servidor' },
    { value: 'impresora', label: 'Impresora' },
    { value: 'proyector', label: 'Proyector' },
    { value: 'monitor', label: 'Monitor' },
    { value: 'otro', label: 'Otro' },
  ];
  const acquisitionModeOptions = [
    { value: 'comprado', label: 'Comprado' },
    { value: 'arrendado', label: 'Arrendado' },
    { value: 'donado', label: 'Donado' },
  ];
  const equipmentStatusOptions = [
    { value: 'en_uso', label: 'En uso' },
    { value: 'en_mantenimiento', label: 'En mantenimiento' },
    { value: 'dañado', label: 'Dañado' },
    { value: 'de_baja', label: 'De baja' },
  ];

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const nextFreePosition = (occupied, maxRows, maxColumns, preserveAisle = false) => {
    const blockedColumn = preserveAisle && maxColumns >= 6 ? Math.ceil(maxColumns / 2) : null;
    for (let row = 1; row <= maxRows; row += 1) {
      for (let column = 1; column <= maxColumns; column += 1) {
        if (column === blockedColumn) continue;
        if (!occupied.has(positionKey(row, column))) return { fila: row, columna: column };
      }
    }
    return null;
  };

  const hydrateLayout = () => {
    const saved = espacio.value?.configuracion_plano ?? {};
    const initialColumns = clamp(saved.columnas || (equipos.value.length > 30 ? 8 : 6), 2, 10);
    const hasSavedLayout = Array.isArray(saved.puestos) && saved.puestos.length > 0;
    const centralColumn = initialColumns >= 6 ? Math.ceil(initialColumns / 2) : null;
    const preservesCentralAisle = Boolean(centralColumn) && !(saved.puestos ?? []).some((position) => (
      position.columna === centralColumn
    ));
    const usableColumns = preservesCentralAisle ? initialColumns - 1 : initialColumns;
    const minimumRows = Math.max(2, Math.ceil(equipos.value.length / usableColumns));
    let initialRows = clamp(saved.filas || (minimumRows + 1), minimumRows, 20);
    const validIds = new Set(equipos.value.map((equipment) => equipment.id));
    const occupied = new Set();
    const placedIds = new Set();
    const normalized = [];

    (saved.puestos ?? []).forEach((position) => {
      const key = positionKey(position.fila, position.columna);
      const isValid = validIds.has(position.equipo_id)
        && position.fila >= 1
        && position.fila <= initialRows
        && position.columna >= 1
        && position.columna <= initialColumns
        && !occupied.has(key)
        && !placedIds.has(position.equipo_id);
      if (!isValid) return;
      normalized.push({ ...position, es_docente: Boolean(position.es_docente) });
      occupied.add(key);
      placedIds.add(position.equipo_id);
    });

    equipos.value.forEach((equipment) => {
      if (placedIds.has(equipment.id)) return;
      let free = nextFreePosition(
        occupied,
        initialRows,
        initialColumns,
        !hasSavedLayout || preservesCentralAisle,
      );
      if (!free && initialRows < 20) {
        initialRows += 1;
        free = nextFreePosition(
          occupied,
          initialRows,
          initialColumns,
          !hasSavedLayout || preservesCentralAisle,
        );
      }
      if (!free) return;
      normalized.push({ equipo_id: equipment.id, ...free, es_docente: false });
      occupied.add(positionKey(free.fila, free.columna));
    });

    columns.value = initialColumns;
    rows.value = initialRows;
    positions.value = normalized;
  };

  const loadSpace = async ({ silent = false } = {}) => {
    const showInitialLoader = !silent || !espacio.value;
    if (showInitialLoader) loading.value = true;
    if (!silent) error.value = '';
    try {
      espacio.value = await spaceService.obtener(id);
      hydrateLayout();
    } catch (requestError) {
      const message = getApiErrorMessage(requestError, 'No se pudo cargar el plano del espacio.');
      if (silent) showToast(message, 'error');
      else error.value = message;
    } finally {
      if (showInitialLoader) loading.value = false;
    }
  };

  const loadTechnicians = async () => {
    try {
      technicians.value = await maintenanceService.obtenerTecnicosDisponibles();
    } catch {
      technicians.value = [];
    }
  };

  const loadUsers = async () => {
    try {
      const data = await usuariosService.listar({ activo: true, page_size: 100 });
      users.value = data.results ?? data;
    } catch {
      users.value = [];
    }
  };

  const loadEquipmentMaintenance = async (equipmentId) => {
    maintenanceLoading.value = true;
    activeMaintenances.value = [];
    try {
      const data = await maintenanceService.listar({ equipo_id: equipmentId, page_size: 20 });
      const records = data.results ?? data;
      activeMaintenances.value = records.filter((record) => (
        record.estado === 'pendiente' || record.estado === 'en_proceso'
      ));
    } catch {
      activeMaintenances.value = [];
    } finally {
      maintenanceLoading.value = false;
    }
  };

  const selectEquipment = (equipment) => {
    selectedEquipo.value = equipment;
    equipmentDetailOpen.value = false;
    if (equipment) loadEquipmentMaintenance(equipment.id);
  };

  const manageSelectedEquipment = () => {
    if (!selectedLayoutEquipment.value) return;
    selectEquipment(selectedLayoutEquipment.value);
    equipmentDetailOpen.value = true;
  };

  const startEditing = () => {
    layoutBackup.value = JSON.stringify({
      columns: columns.value,
      rows: rows.value,
      positions: positions.value,
    });
    selectedEquipo.value = null;
    selectedPositionId.value = null;
    editing.value = true;
  };

  const cancelEditing = () => {
    if (layoutBackup.value) {
      const backup = JSON.parse(layoutBackup.value);
      columns.value = backup.columns;
      rows.value = backup.rows;
      positions.value = backup.positions;
    }
    selectedPositionId.value = null;
    editing.value = false;
  };

  const reflowPositions = (nextColumns) => {
    const ordered = [...positions.value].sort((left, right) => (
      left.fila - right.fila || left.columna - right.columna
    ));
    columns.value = clamp(nextColumns, 2, 10);
    const usableColumns = columns.value >= 6 ? columns.value - 1 : columns.value;
    rows.value = clamp(
      Math.max(rows.value, Math.ceil(ordered.length / usableColumns) + 1),
      1,
      20,
    );
    const occupied = new Set();
    positions.value = ordered.map((position) => {
      const free = nextFreePosition(occupied, rows.value, columns.value, true);
      occupied.add(positionKey(free.fila, free.columna));
      return { ...position, ...free };
    });
  };

  const addRow = () => {
    rows.value = clamp(rows.value + 1, 1, 20);
  };

  const removeRow = () => {
    if (rows.value <= 1) return;
    if (positions.value.some((position) => position.fila === rows.value)) {
      showToast('Mueve los equipos de la última fila antes de eliminarla.', 'error');
      return;
    }
    rows.value -= 1;
  };

  const moveEquipment = (equipmentId, targetRow, targetColumn) => {
    const moving = positions.value.find((position) => position.equipo_id === equipmentId);
    if (!moving) return;
    const target = positions.value.find((position) => (
      position.fila === targetRow && position.columna === targetColumn
    ));
    const origin = { fila: moving.fila, columna: moving.columna };
    moving.fila = targetRow;
    moving.columna = targetColumn;
    if (target && target.equipo_id !== equipmentId) {
      target.fila = origin.fila;
      target.columna = origin.columna;
    }
    positions.value = [...positions.value];
  };

  const handleCellClick = (cell) => {
    if (!editing.value) {
      if (cell.equipment) selectEquipment(cell.equipment);
      return;
    }
    if (cell.equipment) {
      selectedPositionId.value = cell.equipment.id;
      return;
    }
    if (selectedPositionId.value) {
      moveEquipment(selectedPositionId.value, cell.row, cell.column);
    }
  };

  const handleDrop = (event, cell) => {
    if (!editing.value) return;
    const equipmentId = Number(event.dataTransfer?.getData('text/plain'));
    if (!equipmentId) return;
    selectedPositionId.value = equipmentId;
    moveEquipment(equipmentId, cell.row, cell.column);
  };

  const toggleTeacher = () => {
    if (!selectedPositionId.value) return;
    const selected = positions.value.find((position) => (
      position.equipo_id === selectedPositionId.value
    ));
    const nextValue = !selected?.es_docente;
    positions.value = positions.value.map((position) => ({
      ...position,
      es_docente: position.equipo_id === selectedPositionId.value ? nextValue : false,
    }));
  };

  const saveLayout = async () => {
    saving.value = true;
    try {
      espacio.value = await spaceService.guardarDisposicion(id, {
        columnas: columns.value,
        filas: rows.value,
        puestos: positions.value,
      });
      hydrateLayout();
      editing.value = false;
      selectedPositionId.value = null;
      showToast('Distribución guardada correctamente.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar la distribución.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const openReport = (equipment = selectedEquipo.value) => {
    if (!equipment) return;
    selectedEquipo.value = equipment;
    Object.assign(reportForm, emptyReport());
    reportForm.reportado_por_id = authStore.user?.id ?? '';
    const currentTechnician = technicians.value.find((technician) => (
      technician.usuario_id === authStore.user?.id
    ));
    reportForm.tecnico_id = currentTechnician?.id ?? '';
    Object.keys(reportErrors).forEach((key) => delete reportErrors[key]);
    reportOpen.value = true;
  };

  const closeReport = () => {
    reportOpen.value = false;
    Object.assign(reportForm, emptyReport());
    Object.keys(reportErrors).forEach((key) => delete reportErrors[key]);
  };

  const validateReport = () => {
    Object.keys(reportErrors).forEach((key) => delete reportErrors[key]);
    if (!reportForm.descripcion.trim()) {
      reportErrors.descripcion = 'Describe la falla observada.';
    }
    return Object.keys(reportErrors).length === 0;
  };

  const submitReport = async () => {
    if (!selectedEquipo.value || !validateReport()) return;
    reportSaving.value = true;
    const equipmentId = selectedEquipo.value.id;
    const attentionMode = reportForm.atencion;
    try {
      await maintenanceService.crear({
        equipo_id: equipmentId,
        fecha: today(),
        tipo_mantenimiento: 'correctivo',
        estado: reportForm.atencion,
        descripcion: reportForm.descripcion.trim(),
        reportado_por_id: reportForm.reportado_por_id ? Number(reportForm.reportado_por_id) : null,
        tecnicos_ids: reportForm.tecnico_id ? [Number(reportForm.tecnico_id)] : [],
      });

      if (reportForm.atencion === 'en_proceso') {
        espacio.value.equipos = equipos.value.map((equipment) => (
          equipment.id === equipmentId
            ? {
                ...equipment,
                estado: 'en_mantenimiento',
                estado_display: 'En mantenimiento',
              }
            : equipment
        ));
        selectedEquipo.value = espacio.value.equipos.find((item) => item.id === equipmentId);
      }

      closeReport();
      await loadEquipmentMaintenance(equipmentId);
      showToast(
        attentionMode === 'en_proceso'
          ? 'Falla registrada y equipo enviado a mantenimiento.'
          : 'Falla registrada como pendiente de atención.',
      );
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo registrar la falla.'), 'error');
    } finally {
      reportSaving.value = false;
    }
  };

  const resetEquipmentForm = () => {
    Object.assign(equipmentForm, emptyEquipment(), { espacio: Number(id) });
    Object.keys(equipmentErrors).forEach((key) => delete equipmentErrors[key]);
  };

  const suggestEquipmentCode = () => {
    const prefix = espacio.value?.codigo_espacio?.replace(/\s+/g, '-') || 'PC';
    const sequence = String(equipos.value.length + 1).padStart(2, '0');
    return `${prefix}-PC${sequence}`;
  };

  const openCreateEquipment = () => {
    editingEquipment.value = null;
    resetEquipmentForm();
    equipmentForm.codigo = suggestEquipmentCode();
    equipmentModalOpen.value = true;
  };

  const openEditEquipment = (equipment = selectedEquipo.value) => {
    if (!equipment) return;
    editingEquipment.value = equipment;
    resetEquipmentForm();
    Object.assign(equipmentForm, {
      espacio: Number(id),
      codigo: equipment.codigo,
      numero_serie: equipment.numero_serie,
      numero_mac: equipment.numero_mac ?? '',
      tipo_equipo: equipment.tipo_equipo,
      marca: equipment.marca,
      modelo: equipment.modelo,
      modo_adquisicion: equipment.modo_adquisicion,
      fecha_adquisicion: equipment.fecha_adquisicion,
      fecha_renovacion: equipment.fecha_renovacion ?? '',
      estado: equipment.estado,
      responsable_usuario: equipment.responsable_usuario ?? '',
    });
    equipmentModalOpen.value = true;
  };

  const closeEquipmentModal = () => {
    equipmentModalOpen.value = false;
    editingEquipment.value = null;
    resetEquipmentForm();
  };

  const validateEquipment = () => {
    Object.keys(equipmentErrors).forEach((key) => delete equipmentErrors[key]);
    if (!equipmentForm.codigo.trim()) equipmentErrors.codigo = 'Ingresa el código interno.';
    if (!equipmentForm.numero_serie.trim()) equipmentErrors.numero_serie = 'Ingresa el número de serie.';
    if (!equipmentForm.marca.trim()) equipmentErrors.marca = 'Ingresa la marca.';
    if (!equipmentForm.modelo.trim()) equipmentErrors.modelo = 'Ingresa el modelo.';
    if (!equipmentForm.fecha_adquisicion) equipmentErrors.fecha_adquisicion = 'Ingresa la fecha.';
    return Object.keys(equipmentErrors).length === 0;
  };

  const submitEquipment = async () => {
    if (!validateEquipment()) return;
    equipmentSaving.value = true;
    const payload = {
      ...equipmentForm,
      espacio: Number(id),
      fecha_renovacion: equipmentForm.fecha_renovacion || null,
    };
    try {
      const savedEquipment = isEditingEquipment.value
        ? await equiposService.actualizar(editingEquipment.value.id, payload)
        : await equiposService.crear(payload);
      const wasCreating = !isEditingEquipment.value;
      closeEquipmentModal();
      await loadSpace({ silent: true });
      const refreshed = equipos.value.find((equipment) => equipment.id === savedEquipment.id);
      selectEquipment(refreshed ?? savedEquipment);
      equipmentDetailOpen.value = wasCreating;
      showToast(wasCreating ? 'PC creada y ubicada en el primer puesto libre.' : 'Equipo actualizado correctamente.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo guardar el equipo.'), 'error');
    } finally {
      equipmentSaving.value = false;
    }
  };

  const askDeleteEquipment = (equipment = selectedEquipo.value) => {
    if (!equipment) return;
    pendingEquipmentDelete.value = equipment;
    equipmentDeleteOpen.value = true;
  };

  const cancelDeleteEquipment = () => {
    pendingEquipmentDelete.value = null;
    equipmentDeleteOpen.value = false;
  };

  const confirmDeleteEquipment = async () => {
    if (!pendingEquipmentDelete.value) return;
    equipmentSaving.value = true;
    try {
      await equiposService.eliminar(pendingEquipmentDelete.value.id);
      cancelDeleteEquipment();
      selectedEquipo.value = null;
      equipmentDetailOpen.value = false;
      await loadSpace({ silent: true });
      showToast('Equipo retirado del espacio correctamente.');
    } catch (requestError) {
      showToast(getApiErrorMessage(requestError, 'No se pudo retirar el equipo.'), 'error');
    } finally {
      equipmentSaving.value = false;
    }
  };

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(() => Promise.all([loadSpace(), loadTechnicians(), loadUsers()]));

  return {
    espacio,
    equipos,
    loading,
    saving,
    error,
    editing,
    canEdit,
    columns,
    rows,
    cells,
    statusSummary,
    teacherEquipment,
    selectedPosition,
    selectedLayoutEquipment,
    selectedPositionId,
    selectedEquipo,
    equipmentDetailOpen,
    equipmentModalOpen,
    equipmentDeleteOpen,
    pendingEquipmentDelete,
    equipmentSaving,
    equipmentForm,
    equipmentErrors,
    isEditingEquipment,
    activeMaintenances,
    maintenanceLoading,
    reportOpen,
    reportSaving,
    reportForm,
    reportErrors,
    technicianOptions,
    reporterOptions,
    equipmentTypeOptions,
    acquisitionModeOptions,
    equipmentStatusOptions,
    toast,
    loadSpace,
    startEditing,
    cancelEditing,
    reflowPositions,
    addRow,
    removeRow,
    handleCellClick,
    handleDrop,
    toggleTeacher,
    saveLayout,
    openReport,
    closeReport,
    submitReport,
    selectEquipment,
    manageSelectedEquipment,
    openCreateEquipment,
    openEditEquipment,
    closeEquipmentModal,
    submitEquipment,
    askDeleteEquipment,
    cancelDeleteEquipment,
    confirmDeleteEquipment,
    closeToast,
  };
}

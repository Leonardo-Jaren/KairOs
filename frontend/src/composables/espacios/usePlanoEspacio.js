import { computed, onMounted, reactive, ref } from 'vue';

import espaciosService from '@/services/espacios.service';
import mantenimientoService from '@/services/mantenimiento.service';
import { useAuthStore } from '@/stores/auth';
import { getApiErrorMessage } from '@/utils/api-errors';

const clamp = (value, min, max) => Math.min(max, Math.max(min, Number(value)));
const positionKey = (row, column) => `${row}-${column}`;
const today = () => new Date().toISOString().slice(0, 10);

const emptyReport = () => ({
  descripcion: '',
  tecnico_id: '',
  atencion: 'en_proceso',
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
  const reportOpen = ref(false);
  const reportSaving = ref(false);
  const reportForm = reactive(emptyReport());
  const reportErrors = reactive({});
  const technicians = ref([]);
  const toast = reactive({ show: false, message: '', type: 'success' });

  const equipos = computed(() => espacio.value?.equipos ?? []);
  const canEdit = computed(() => authStore.user?.rol === 'admin');
  const selectedPosition = computed(() => (
    positions.value.find((item) => item.equipo_id === selectedPositionId.value) ?? null
  ));
  const positionMap = computed(() => new Map(
    positions.value.map((position) => [positionKey(position.fila, position.columna), position]),
  ));
  const equipmentMap = computed(() => new Map(
    equipos.value.map((equipment) => [equipment.id, equipment]),
  ));
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

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const nextFreePosition = (occupied, maxRows, maxColumns) => {
    for (let row = 1; row <= maxRows; row += 1) {
      for (let column = 1; column <= maxColumns; column += 1) {
        if (!occupied.has(positionKey(row, column))) return { fila: row, columna: column };
      }
    }
    return null;
  };

  const hydrateLayout = () => {
    const saved = espacio.value?.configuracion_plano ?? {};
    const initialColumns = clamp(saved.columnas || (equipos.value.length > 30 ? 8 : 6), 2, 10);
    const minimumRows = Math.max(2, Math.ceil(equipos.value.length / initialColumns));
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
      let free = nextFreePosition(occupied, initialRows, initialColumns);
      if (!free && initialRows < 20) {
        initialRows += 1;
        free = nextFreePosition(occupied, initialRows, initialColumns);
      }
      if (!free) return;
      normalized.push({ equipo_id: equipment.id, ...free, es_docente: false });
      occupied.add(positionKey(free.fila, free.columna));
    });

    columns.value = initialColumns;
    rows.value = initialRows;
    positions.value = normalized;
  };

  const loadSpace = async () => {
    loading.value = true;
    error.value = '';
    try {
      espacio.value = await spaceService.obtener(id);
      hydrateLayout();
    } catch (requestError) {
      error.value = getApiErrorMessage(requestError, 'No se pudo cargar el plano del espacio.');
    } finally {
      loading.value = false;
    }
  };

  const loadTechnicians = async () => {
    try {
      technicians.value = await maintenanceService.obtenerTecnicosDisponibles();
    } catch {
      technicians.value = [];
    }
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
    rows.value = clamp(
      Math.max(rows.value, Math.ceil(ordered.length / columns.value) + 1),
      1,
      20,
    );
    positions.value = ordered.map((position, index) => ({
      ...position,
      fila: Math.floor(index / columns.value) + 1,
      columna: (index % columns.value) + 1,
    }));
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
      if (cell.equipment) selectedEquipo.value = cell.equipment;
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

  const closeToast = () => {
    toast.show = false;
  };

  onMounted(() => Promise.all([loadSpace(), loadTechnicians()]));

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
    selectedPositionId,
    selectedEquipo,
    reportOpen,
    reportSaving,
    reportForm,
    reportErrors,
    technicianOptions,
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
    closeToast,
  };
}

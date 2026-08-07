import { computed, reactive, ref } from 'vue';
import {
  CircuitBoard, Cpu, Database, HardDrive, Network, Package, Server, Tv2, Zap,
} from '@lucide/vue';

import componentesService from '@/services/componentes.service';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyForm = () => ({ equipo_id: '', tipo: '', modelo: '', descripcion: '' });

export const TIPO_OPTIONS = [
  { value: 'cpu',         label: 'CPU',            icon: Cpu },
  { value: 'ram',         label: 'RAM',            icon: Server },
  { value: 'ssd',         label: 'SSD',            icon: HardDrive },
  { value: 'hdd',         label: 'HDD',            icon: Database },
  { value: 'gpu',         label: 'GPU',            icon: Tv2 },
  { value: 'motherboard', label: 'Motherboard',    icon: CircuitBoard },
  { value: 'fuente',      label: 'Fuente de Poder', icon: Zap },
  { value: 'nic',         label: 'Tarjeta de Red', icon: Network },
  { value: 'otro',        label: 'Otro',           icon: Package },
];

export function getTipoIcon(tipo) {
  return TIPO_OPTIONS.find((o) => o.value === tipo)?.icon ?? Package;
}

export function useComponentes(service = componentesService) {
  const componentes   = ref([]);
  const loading       = ref(false);
  const saving        = ref(false);
  const formOpen      = ref(false);
  const deleteOpen    = ref(false);
  const editingItem   = ref(null);
  const pendingDelete = ref(null);
  const form          = reactive(emptyForm());
  const formErrors    = reactive({});
  const toast         = reactive({ show: false, message: '', type: 'success' });

  const isEditing = computed(() => Boolean(editingItem.value));

  const cargar = async (equipoId = null) => {
    loading.value = true;
    try {
      const params = equipoId ? { equipo_id: equipoId } : {};
      const data = await service.listar(params);
      componentes.value = data.results ?? data;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudieron cargar los componentes.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  };

  const openCreate = () => {
    editingItem.value = null;
    resetForm();
    formOpen.value = true;
  };

  const openEdit = (comp) => {
    editingItem.value = comp;
    resetForm();
    Object.assign(form, { tipo: comp.tipo, modelo: comp.modelo, descripcion: comp.descripcion });
    formOpen.value = true;
  };

  const closeForm = () => {
    formOpen.value = false;
    editingItem.value = null;
    resetForm();
  };

  const validate = (requireEquipo = false) => {
    Object.keys(formErrors).forEach((k) => delete formErrors[k]);
    if (requireEquipo && !form.equipo_id) formErrors.equipo_id = 'Selecciona el equipo.';
    if (!form.tipo) formErrors.tipo = 'Selecciona el tipo.';
    if (!form.modelo.trim()) formErrors.modelo = 'Ingresa el modelo.';
    return Object.keys(formErrors).length === 0;
  };

  const submit = async (equipoId = null) => {
    const resolvedId = equipoId || form.equipo_id || null;
    if (!validate(!equipoId && !isEditing.value)) return false;
    saving.value = true;
    try {
      if (isEditing.value) {
        await service.actualizar(editingItem.value.id, { tipo: form.tipo, modelo: form.modelo, descripcion: form.descripcion });
        showToast('Componente actualizado correctamente.');
      } else {
        await service.crear({ tipo: form.tipo, modelo: form.modelo, descripcion: form.descripcion, equipo_id: resolvedId });
        showToast('Componente agregado correctamente.');
      }
      closeForm();
      await cargar(equipoId);
      return true;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo guardar el componente.'), 'error');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (comp) => {
    pendingDelete.value = comp;
    deleteOpen.value = true;
  };

  const cancelDelete = () => {
    pendingDelete.value = null;
    deleteOpen.value = false;
  };

  const confirmDelete = async (equipoId) => {
    if (!pendingDelete.value) return;
    saving.value = true;
    try {
      await service.eliminar(pendingDelete.value.id);
      showToast('Componente eliminado correctamente.');
      cancelDelete();
      await cargar(equipoId);
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo eliminar el componente.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const showToast = (message, type = 'success') => Object.assign(toast, { show: true, message, type });
  const closeToast = () => { toast.show = false; };

  const reset = () => {
    componentes.value = [];
    closeForm();
    cancelDelete();
  };

  return {
    componentes, loading, saving, formOpen, deleteOpen, pendingDelete,
    form, formErrors, toast, isEditing,
    cargar, openCreate, openEdit, closeForm, submit,
    askDelete, cancelDelete, confirmDelete, closeToast, reset,
  };
}

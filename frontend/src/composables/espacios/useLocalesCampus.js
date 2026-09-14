import { computed, reactive, ref } from 'vue';
import { getApiErrorMessage } from '@/utils/api-errors';

const emptyLocal = () => ({ codigo: '', nombre: '', ciudad: '', descripcion: '', activo: true });

export function useLocalesCampus({ service, saving, canEdit, selectionBlocked, loadCampus, selectLocal, showToast }) {
  const localModalOpen = ref(false);
  const localDeleteOpen = ref(false);
  const editingLocal = ref(null);
  const pendingLocalDelete = ref(null);
  const localForm = reactive(emptyLocal());
  const localErrors = reactive({});
  const isEditingLocal = computed(() => Boolean(editingLocal.value));
  const resetForm = () => {
    Object.assign(localForm, emptyLocal());
    Object.keys(localErrors).forEach((key) => delete localErrors[key]);
  };
  const openCreateLocal = () => {
    if (!canEdit.value || selectionBlocked()) return;
    editingLocal.value = null;
    resetForm();
    localModalOpen.value = true;
  };
  const openEditLocal = (local) => {
    if (!local || !canEdit.value || selectionBlocked()) return;
    resetForm();
    editingLocal.value = local;
    for (const key of Object.keys(emptyLocal())) localForm[key] = local[key] ?? emptyLocal()[key];
    localModalOpen.value = true;
  };
  const closeLocalModal = () => {
    localModalOpen.value = false;
    editingLocal.value = null;
    resetForm();
  };
  const submitLocal = async () => {
    if (!canEdit.value || saving.value || selectionBlocked()) return;
    Object.keys(localErrors).forEach((key) => delete localErrors[key]);
    for (const [field, label] of [['codigo', 'código'], ['nombre', 'nombre'], ['ciudad', 'ciudad']]) {
      if (!localForm[field].trim()) localErrors[field] = `Ingresa ${field === 'ciudad' ? 'la' : 'el'} ${label}.`;
    }
    if (Object.keys(localErrors).length) return;
    saving.value = true;
    try {
      const creating = !isEditingLocal.value;
      const saved = creating ? await service.crear({ ...localForm })
        : await service.actualizar(editingLocal.value.id, { ...localForm });
      closeLocalModal();
      if (!await loadCampus({ silent: true })) return;
      if (saved.activo) selectLocal(saved.id);
      showToast(creating ? 'Local agregado.' : 'Local actualizado.');
    } catch (error) {
      const errors = error.response?.data?.errores ?? {};
      for (const field of Object.keys(emptyLocal())) {
        if (errors[field]) localErrors[field] = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
      }
      showToast(getApiErrorMessage(error, 'No se pudo guardar el local.'), 'error');
    } finally {
      saving.value = false;
    }
  };
  const askDeleteLocal = (local) => {
    if (!local || !canEdit.value || selectionBlocked()) return;
    pendingLocalDelete.value = local;
    localDeleteOpen.value = true;
  };
  const cancelDeleteLocal = () => {
    pendingLocalDelete.value = null;
    localDeleteOpen.value = false;
  };
  const confirmDeleteLocal = async () => {
    if (!pendingLocalDelete.value || !canEdit.value || saving.value || selectionBlocked()) return;
    saving.value = true;
    try {
      await service.desactivar(pendingLocalDelete.value.id);
      cancelDeleteLocal();
      if (await loadCampus({ silent: true })) showToast('Local desactivado.');
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo desactivar el local.'), 'error');
    } finally {
      saving.value = false;
    }
  };
  return {
    localModalOpen, localDeleteOpen, editingLocal, pendingLocalDelete, localForm,
    localErrors, isEditingLocal, openCreateLocal, openEditLocal, closeLocalModal,
    submitLocal, askDeleteLocal, cancelDeleteLocal, confirmDeleteLocal,
  };
}

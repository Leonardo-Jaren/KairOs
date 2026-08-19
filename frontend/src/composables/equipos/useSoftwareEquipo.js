import { computed, reactive, ref } from 'vue';

import softwareService from '@/services/software.service';
import { getApiErrorMessage } from '@/utils/api-errors';

const today = () => new Date().toISOString().slice(0, 10);
const emptyForm = () => ({
  producto_software_id: '',
  numero_licencia_usado: '',
  fecha_instalacion: today(),
});

export function useSoftwareEquipo(service = softwareService) {
  const installations = ref([]);
  const products = ref([]);
  const loading = ref(false);
  const saving = ref(false);
  const formOpen = ref(false);
  const deleteOpen = ref(false);
  const pendingDelete = ref(null);
  const currentEquipmentId = ref(null);
  const form = reactive(emptyForm());
  const errors = reactive({});
  const toast = reactive({ show: false, message: '', type: 'success' });

  const productOptions = computed(() => {
    const installedIds = new Set(installations.value.map((item) => item.producto_software));
    return products.value
      .filter((product) => !installedIds.has(product.id))
      .filter((product) => !product.fecha_expiracion || product.fecha_expiracion >= today())
      .filter((product) => product.tipo_licencia === 'libre' || product.licencias_disponibles > 0)
      .map((product) => ({
        value: product.id,
        label: `${product.software} ${product.version} · ${product.tipo_licencia_display}`,
      }));
  });

  const showToast = (message, type = 'success') => {
    Object.assign(toast, { show: true, message, type });
  };

  const resetForm = () => {
    Object.assign(form, emptyForm());
    Object.keys(errors).forEach((key) => delete errors[key]);
  };

  const load = async (equipmentId) => {
    if (!equipmentId) return;
    currentEquipmentId.value = equipmentId;
    loading.value = true;
    try {
      const [installationData, productData] = await Promise.all([
        service.listarInstalaciones({ equipo_id: equipmentId, page_size: 100 }),
        service.listarProductos({ page_size: 100 }),
      ]);
      installations.value = installationData.results ?? installationData;
      products.value = productData.results ?? productData;
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo cargar el software del equipo.'), 'error');
    } finally {
      loading.value = false;
    }
  };

  const openCreate = () => {
    resetForm();
    formOpen.value = true;
  };

  const closeForm = () => {
    formOpen.value = false;
    resetForm();
  };

  const submit = async () => {
    Object.keys(errors).forEach((key) => delete errors[key]);
    if (!form.producto_software_id) errors.producto_software_id = 'Selecciona un producto.';
    if (!form.fecha_instalacion) errors.fecha_instalacion = 'Ingresa la fecha de instalación.';
    if (Object.keys(errors).length) return;
    saving.value = true;
    try {
      await service.instalar({
        equipo_id: currentEquipmentId.value,
        producto_software_id: Number(form.producto_software_id),
        numero_licencia_usado: form.numero_licencia_usado.trim(),
        fecha_instalacion: form.fecha_instalacion,
      });
      closeForm();
      await load(currentEquipmentId.value);
      showToast('Software instalado correctamente.');
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo instalar el software.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const askDelete = (installation) => {
    pendingDelete.value = installation;
    deleteOpen.value = true;
  };

  const cancelDelete = () => {
    pendingDelete.value = null;
    deleteOpen.value = false;
  };

  const confirmDelete = async () => {
    if (!pendingDelete.value) return;
    saving.value = true;
    try {
      await service.retirar(pendingDelete.value.id);
      cancelDelete();
      await load(currentEquipmentId.value);
      showToast('Software retirado del equipo.');
    } catch (error) {
      showToast(getApiErrorMessage(error, 'No se pudo retirar el software.'), 'error');
    } finally {
      saving.value = false;
    }
  };

  const reset = () => {
    installations.value = [];
    products.value = [];
    currentEquipmentId.value = null;
    formOpen.value = false;
    deleteOpen.value = false;
    pendingDelete.value = null;
    resetForm();
  };

  return {
    installations,
    loading,
    saving,
    formOpen,
    deleteOpen,
    pendingDelete,
    form,
    errors,
    toast,
    productOptions,
    load,
    openCreate,
    closeForm,
    submit,
    askDelete,
    cancelDelete,
    confirmDelete,
    reset,
    closeToast: () => { toast.show = false; },
  };
}

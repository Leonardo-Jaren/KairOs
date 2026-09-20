import { computed, reactive, ref } from 'vue';

import permisosService from '@/services/permisos.service';
import { getApiErrorMessage } from '@/utils/api-errors';

export function usePermisos(service = permisosService) {
  const loading = ref(false);
  const saving = ref(false);
  const error = ref(null);
  const successMessage = ref(null);

  const usuarioId = ref(null);
  const usuarioNombre = ref('');
  const usuarioRol = ref('');

  const modulos = ref([
    'espacios',
    'equipos',
    'mantenimiento',
    'incidencias',
    'software',
    'usuarios',
    'auditoria',
  ]);

  const modulosEtiquetas = {
    espacios: 'Espacios y Ambientes',
    equipos: 'Equipos y Hardware',
    mantenimiento: 'Mantenimiento Preventivo / Correctivo',
    incidencias: 'Reporte y Gestión de Incidencias',
    software: 'Software y Licencias',
    usuarios: 'Administración de Usuarios',
    auditoria: 'Auditoría y Trazabilidad',
  };

  const modulosDescripciones = {
    espacios: 'Pabellones, aulas, laboratorios y planos.',
    equipos: 'Computadoras, periféricos y componentes.',
    mantenimiento: 'Órdenes, diagnósticos y tareas técnicas.',
    incidencias: 'Reportes de fallas y seguimiento.',
    software: 'Programas instalados y licencias.',
    usuarios: 'Cuentas institucionales y jerarquías.',
    auditoria: 'Registro inmutable de actividades.',
  };

  const acciones = ['ver', 'crear', 'editar', 'eliminar'];

  const permisosBase = ref({});
  const permisosEfectivos = reactive({});

  const cargarPermisos = async (targetUsuarioId) => {
    usuarioId.value = targetUsuarioId;
    loading.value = true;
    error.value = null;
    successMessage.value = null;
    try {
      const data = await service.obtenerPermisos(targetUsuarioId);
      usuarioNombre.value = data.nombre_completo || '';
      usuarioRol.value = data.rol || '';
      permisosBase.value = data.permisos_base || {};

      // Limpiar y poblar permisosEfectivos reactivamente
      Object.keys(permisosEfectivos).forEach((k) => delete permisosEfectivos[k]);
      for (const mod of modulos.value) {
        permisosEfectivos[mod] = {};
        for (const acc of acciones) {
          permisosEfectivos[mod][acc] = Boolean(data.permisos_efectivos?.[mod]?.[acc]);
        }
      }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'No se pudieron cargar los permisos del usuario.');
    } finally {
      loading.value = false;
    }
  };

  const togglePermiso = (modulo, accion) => {
    if (!permisosEfectivos[modulo]) {
      permisosEfectivos[modulo] = {};
    }
    permisosEfectivos[modulo][accion] = !permisosEfectivos[modulo][accion];
  };

  // Verifica si un permiso específico difiere de la plantilla base del rol
  const isCustomized = (modulo, accion) => {
    const base = Boolean(permisosBase.value?.[modulo]?.[accion]);
    const actual = Boolean(permisosEfectivos[modulo]?.[accion]);
    return base !== actual;
  };


  // Cuenta total de permisos personalizados
  const totalPersonalizados = computed(() => {
    let count = 0;
    for (const mod of modulos.value) {
      for (const acc of acciones) {
        const base = Boolean(permisosBase.value?.[mod]?.[acc]);
        const actual = Boolean(permisosEfectivos[mod]?.[acc]);
        if (base !== actual) count += 1;
      }
    }
    return count;
  });

  const guardar = async () => {
    if (!usuarioId.value) return false;
    saving.value = true;
    error.value = null;
    successMessage.value = null;

    try {
      const listaPermisos = [];
      for (const mod of modulos.value) {
        for (const acc of acciones) {
          listaPermisos.push({
            modulo: mod,
            accion: acc,
            permitido: Boolean(permisosEfectivos[mod]?.[acc]),
          });
        }
      }

      const res = await service.guardarPermisos(usuarioId.value, listaPermisos);
      successMessage.value = 'Permisos actualizados correctamente.';
      // Actualizar mapa efectivo devuelto
      for (const mod of modulos.value) {
        for (const acc of acciones) {
          permisosEfectivos[mod][acc] = Boolean(res.permisos_efectivos?.[mod]?.[acc]);
        }
      }
      return true;
    } catch (err) {
      error.value = getApiErrorMessage(err, 'No se pudieron guardar los permisos.');
      return false;
    } finally {
      saving.value = false;
    }
  };

  const restablecer = async () => {
    if (!usuarioId.value) return false;
    saving.value = true;
    error.value = null;
    successMessage.value = null;

    try {
      const res = await service.restablecerPermisos(usuarioId.value);
      successMessage.value = 'Permisos restablecidos a los valores por defecto del rol.';
      for (const mod of modulos.value) {
        for (const acc of acciones) {
          permisosEfectivos[mod][acc] = Boolean(res.permisos_efectivos?.[mod]?.[acc]);
        }
      }
      return true;
    } catch (err) {
      error.value = getApiErrorMessage(err, 'No se pudieron restablecer los permisos.');
      return false;
    } finally {
      saving.value = false;
    }
  };

  return {
    loading,
    saving,
    error,
    successMessage,
    usuarioId,
    usuarioNombre,
    usuarioRol,
    modulos,
    modulosEtiquetas,
    modulosDescripciones,
    acciones,
    permisosBase,
    permisosEfectivos,
    totalPersonalizados,
    cargarPermisos,
    togglePermiso,
    isCustomized,
    guardar,
    restablecer,
  };
}

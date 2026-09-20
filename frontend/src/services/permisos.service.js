import api from '@/services/api';

const permisosService = {
  // Obtiene la estructura jerárquica del organigrama (árbol de nodos)
  async obtenerOrganigrama(params = {}) {
    const { data } = await api.get('/api/v1/usuarios/organigrama/', { params });
    return data;
  },

  // Consulta la configuración de permisos (base, personalizados y efectivos) de un usuario
  async obtenerPermisos(usuarioId) {
    const { data } = await api.get(`/api/v1/usuarios/${usuarioId}/permisos/`);
    return data;
  },

  // Guarda o actualiza los permisos personalizados para un usuario
  async guardarPermisos(usuarioId, permisos) {
    const { data } = await api.post(`/api/v1/usuarios/${usuarioId}/permisos/`, { permisos });
    return data;
  },

  // Restablece los permisos del usuario a los predeterminados de su rol
  async restablecerPermisos(usuarioId) {
    const { data } = await api.post(`/api/v1/usuarios/${usuarioId}/permisos/`, { reset_to_default: true });
    return data;
  },

  // Obtiene los eventos recientes de auditoría generados por el usuario
  async obtenerActividad(usuarioId, params = {}) {
    const { data } = await api.get(`/api/v1/usuarios/${usuarioId}/actividad/`, { params });
    return data;
  },

  // Obtiene los subordinados directos de un usuario
  async obtenerSubordinados(usuarioId) {
    const { data } = await api.get(`/api/v1/usuarios/${usuarioId}/subordinados/`);
    return data;
  },
};

export default permisosService;

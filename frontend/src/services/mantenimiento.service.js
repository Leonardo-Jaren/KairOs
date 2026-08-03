import api from '@/services/api';

const mantenimientoService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/mantenimiento/', { params });
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/mantenimiento/estadisticas/');
    return data;
  },

  async obtenerTecnicosDisponibles() {
    const { data } = await api.get('/api/v1/mantenimiento/tecnicos-disponibles/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/mantenimiento/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/mantenimiento/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/mantenimiento/${id}/`);
  },
};

export default mantenimientoService;

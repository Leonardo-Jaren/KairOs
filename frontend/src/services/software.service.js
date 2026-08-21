import api from '@/services/api';

const softwareService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/software/productos/', { params });
    return data;
  },

  async obtenerOpciones() {
    const { data } = await api.get('/api/v1/software/productos/opciones/');
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/software/productos/estadisticas/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/software/productos/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/software/productos/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/software/productos/${id}/`);
  },
};

export default softwareService;

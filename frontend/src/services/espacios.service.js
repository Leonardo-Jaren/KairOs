import api from '@/services/api';

const espaciosService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/espacios/', { params });
    return data;
  },

  async obtener(id) {
    const { data } = await api.get(`/api/v1/espacios/${id}/`);
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/espacios/estadisticas/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/espacios/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/espacios/${id}/`, payload);
    return data;
  },

  async guardarDisposicion(id, payload) {
    const { data } = await api.patch(`/api/v1/espacios/${id}/disposicion/`, payload);
    return data;
  },

  async desactivar(id) {
    await api.delete(`/api/v1/espacios/${id}/`);
  },
};

export default espaciosService;

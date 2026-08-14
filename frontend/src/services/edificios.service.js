import api from '@/services/api';

const edificiosService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/espacios/edificios/', { params });
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/espacios/edificios/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/espacios/edificios/${id}/`, payload);
    return data;
  },

  async desactivar(id) {
    await api.delete(`/api/v1/espacios/edificios/${id}/`);
  },
};

export default edificiosService;

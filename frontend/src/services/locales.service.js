import api from '@/services/api';

const localesService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/espacios/locales/', { params });
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/espacios/locales/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/espacios/locales/${id}/`, payload);
    return data;
  },

  async desactivar(id) {
    await api.delete(`/api/v1/espacios/locales/${id}/`);
  },
};

export default localesService;

import api from '@/services/api';

const softwareInstalacionesService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/software/instalaciones/', { params });
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/software/instalaciones/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/software/instalaciones/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/software/instalaciones/${id}/`);
  },
};

export default softwareInstalacionesService;

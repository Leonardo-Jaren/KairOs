import api from '@/services/api';

const componentesService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/equipos/componentes/', { params });
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/equipos/componentes/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/equipos/componentes/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/equipos/componentes/${id}/`);
  },
};

export default componentesService;

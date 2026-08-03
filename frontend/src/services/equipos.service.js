import api from '@/services/api';

const equiposService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/equipos/', { params });
    return data;
  },

  async obtenerOpciones() {
    const { data } = await api.get('/api/v1/equipos/opciones/');
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/equipos/estadisticas/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/equipos/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/equipos/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/equipos/${id}/`);
  },
};

export default equiposService;

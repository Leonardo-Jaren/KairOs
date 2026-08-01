import api from '@/services/api';

const usuariosService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/usuarios/', { params });
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/usuarios/estadisticas/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/usuarios/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/usuarios/${id}/`, payload);
    return data;
  },

  async desactivar(id) {
    await api.delete(`/api/v1/usuarios/${id}/`);
  },
};

export default usuariosService;

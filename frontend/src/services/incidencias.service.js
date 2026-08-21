import api from '@/services/api';

const incidenciasService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/incidencias/', { params });
    return data;
  },

  async obtenerEstadisticas() {
    const { data } = await api.get('/api/v1/incidencias/estadisticas/');
    return data;
  },

  async obtenerEspaciosOpciones() {
    const { data } = await api.get('/api/v1/incidencias/espacios-opciones/');
    return data;
  },

  async obtenerEquiposOpciones() {
    const { data } = await api.get('/api/v1/incidencias/equipos-opciones/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/incidencias/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/incidencias/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/incidencias/${id}/`);
  },
};

export default incidenciasService;

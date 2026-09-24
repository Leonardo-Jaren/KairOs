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

  async obtenerEquiposOpciones(espacioId = null) {
    const { data } = await api.get('/api/v1/incidencias/equipos-opciones/', {
      params: espacioId ? { espacio_id: espacioId } : {},
    });
    return data;
  },

  async obtenerTecnicosDisponibles() {
    const { data } = await api.get('/api/v1/incidencias/tecnicos-disponibles/');
    return data;
  },

  async obtenerMantenimientos(id) {
    const { data } = await api.get(`/api/v1/incidencias/${id}/mantenimientos/`);
    return data;
  },

  async crearMantenimiento(id, payload = {}) {
    const { data } = await api.post(`/api/v1/incidencias/${id}/crear-mantenimiento/`, payload);
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

  async atender(id) {
    const { data } = await api.patch(`/api/v1/incidencias/${id}/`, {
      estado: 'en_proceso',
    });
    return data;
  },

  async cerrar(id) {
    const { data } = await api.patch(`/api/v1/incidencias/${id}/`, {
      estado: 'cerrado',
    });
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/incidencias/${id}/`);
  },
};

export default incidenciasService;

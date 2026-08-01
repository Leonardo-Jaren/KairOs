import api from '@/services/api';

const espaciosUsuariosService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/espacios/usuarios/', { params });
    return data;
  },

  async obtenerOpciones() {
    const { data } = await api.get('/api/v1/espacios/usuarios/opciones/');
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/espacios/usuarios/', payload);
    return data;
  },

  async actualizar(id, payload) {
    const { data } = await api.patch(`/api/v1/espacios/usuarios/${id}/`, payload);
    return data;
  },

  async eliminar(id) {
    await api.delete(`/api/v1/espacios/usuarios/${id}/`);
  },
};

export default espaciosUsuariosService;

import api from '@/services/api';

const softwareService = {
  async listarProductos(params = {}) {
    const { data } = await api.get('/api/v1/software/productos/', { params });
    return data;
  },

  async listarInstalaciones(params = {}) {
    const { data } = await api.get('/api/v1/software/instalaciones/', { params });
    return data;
  },

  async instalar(payload) {
    const { data } = await api.post('/api/v1/software/instalaciones/', payload);
    return data;
  },

  async retirar(id) {
    await api.delete(`/api/v1/software/instalaciones/${id}/`);
  },
};

export default softwareService;

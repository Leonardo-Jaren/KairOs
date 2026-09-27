import api from '@/services/api';

const ciudadesService = {
  async listar(params = {}) {
    const { data } = await api.get('/api/v1/espacios/ciudades/', { params });
    return data;
  },

  async crear(payload) {
    const { data } = await api.post('/api/v1/espacios/ciudades/', payload);
    return data;
  },
};

export default ciudadesService;

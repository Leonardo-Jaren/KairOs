import api from '@/services/api';

const historialService = {
  async listar(params = {}) {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== '' && v != null),
    );
    const { data } = await api.get('/api/v1/historial/', { params: cleanParams });
    return data;
  },

  async obtener(id) {
    const { data } = await api.get(`/api/v1/historial/${id}/`);
    return data;
  },

  async exportarExcel(params = {}) {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== '' && v != null),
    );
    return api.get('/api/v1/historial/exportar-excel/', {
      params: cleanParams,
      responseType: 'blob',
    });
  },
};

export default historialService;

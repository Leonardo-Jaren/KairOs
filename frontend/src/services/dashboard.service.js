import equiposService from '@/services/equipos.service';
import espaciosService from '@/services/espacios.service';
import mantenimientoService from '@/services/mantenimiento.service';
import usuariosService from '@/services/usuarios.service';

const dashboardService = {
  async obtenerResumen() {
    const requests = [
      ['equipos', () => equiposService.obtenerEstadisticas()],
      ['espacios', () => espaciosService.obtenerEstadisticas()],
      ['usuarios', () => usuariosService.obtenerEstadisticas()],
      ['mantenimiento', () => mantenimientoService.obtenerEstadisticas()],
      ['mantenimientosRecientes', () => mantenimientoService.listar({ page_size: 5 })],
      ['espaciosDestacados', () => espaciosService.listar({ page_size: 100 })],
    ];

    const results = await Promise.allSettled(
      requests.map(async ([key, load]) => [key, await load()]),
    );
    const data = {};
    const failed = [];

    results.forEach((result, index) => {
      const key = requests[index][0];
      if (result.status === 'fulfilled') {
        data[key] = result.value[1];
      } else {
        failed.push(key);
      }
    });

    return { data, failed };
  },
};

export default dashboardService;

import { describe, expect, it } from 'vitest';
import { viewLocation } from '@/composables/espacios/espaciosNavigation';

describe('cambio entre vistas territoriales', () => {
  it('mantiene ciudad, local, pabellón y piso al pasar del mapa a Tradicional', () => {
    expect(viewLocation('jerarquia', {
      ciudad: 'Huánuco', local: '1', pabellon: '10', piso: '2',
    })).toEqual({
      path: '/espacios',
      query: { ciudad: 'Huánuco', sede: '1', edificio: '10', piso: '2', vista: undefined },
    });
  });

  it('mantiene la ubicación al volver al mapa desde Tradicional o Lista', () => {
    expect(viewLocation('mapa', {
      sede: '1', edificio: '10', piso: '2', vista: 'inventario',
    }, 'Huánuco')).toEqual({
      path: '/espacios/mapa',
      query: { ciudad: 'Huánuco', local: '1', pabellon: '10', piso: '2' },
    });
  });

  it('permite abrir Lista sin contexto de ubicación', () => {
    expect(viewLocation('inventario')).toEqual({
      path: '/espacios',
      query: { ciudad: undefined, sede: undefined, edificio: undefined, piso: undefined, vista: 'inventario' },
    });
  });
});

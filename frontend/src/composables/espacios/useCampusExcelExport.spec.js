import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ref } from 'vue';

const mocks = vi.hoisted(() => ({ exportExcel: vi.fn() }));

vi.mock('@/composables/shared/useExcelExport', () => ({
  useExcelExport: () => ({ isExporting: { value: false }, exportExcel: mocks.exportExcel }),
}));

import { useCampusExcelExport } from './useCampusExcelExport';

describe('useCampusExcelExport', () => {
  const edificiosService = {
    exportarPisoExcel: vi.fn(),
    exportarExcel: vi.fn(),
  };
  const localesService = { exportarExcel: vi.fn() };

  beforeEach(() => {
    vi.clearAllMocks();
    mocks.exportExcel.mockImplementation((exportFn) => exportFn());
  });

  it('exporta los datos del piso seleccionado', async () => {
    const state = useCampusExcelExport({
      edificiosService,
      localesService,
      explorerLevel: ref('floors'),
      edificioActivo: ref({ id: 9, codigo: 'P-1' }),
      activeFloorKey: ref('2'),
      localActivo: ref(null),
      territorySearch: ref(''),
    });

    await state.exportCampusExcel();

    expect(mocks.exportExcel).toHaveBeenCalledWith(
      expect.any(Function),
      expect.stringMatching(/^croquis_piso_P-1_p2_.*\.xlsx$/),
    );
    expect(edificiosService.exportarPisoExcel).toHaveBeenCalledWith(9, '2');
    expect(state.exportLabel.value).toBe('Exportar Piso 2');
  });

  it('exporta pabellones filtrados por local', async () => {
    const state = useCampusExcelExport({
      edificiosService,
      localesService,
      explorerLevel: ref('buildings'),
      edificioActivo: ref(null),
      activeFloorKey: ref(''),
      localActivo: ref({ id: 4, codigo: 'LOC-4' }),
      territorySearch: ref(''),
    });

    await state.exportCampusExcel();

    expect(mocks.exportExcel).toHaveBeenCalledWith(
      expect.any(Function),
      expect.stringMatching(/^pabellones_LOC-4_.*\.xlsx$/),
    );
    expect(edificiosService.exportarExcel).toHaveBeenCalledWith({ local_id: 4 });
    expect(state.exportLabel.value).toBe('Exportar Pabellones');
  });

  it('exporta el territorio respetando la búsqueda', async () => {
    const state = useCampusExcelExport({
      edificiosService,
      localesService,
      explorerLevel: ref('cities'),
      edificioActivo: ref(null),
      activeFloorKey: ref(''),
      localActivo: ref(null),
      territorySearch: ref('Lima'),
    });

    await state.exportCampusExcel();

    expect(mocks.exportExcel).toHaveBeenCalledWith(
      expect.any(Function),
      expect.stringMatching(/^reporte_territorio_.*\.xlsx$/),
    );
    expect(localesService.exportarExcel).toHaveBeenCalledWith({ search: 'Lima' });
    expect(state.exportLabel.value).toBe('Exportar Territorio');
  });
});

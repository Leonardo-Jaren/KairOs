import { describe, expect, it, vi } from 'vitest';
import { useExcelExport } from './useExcelExport';

describe('useExcelExport composable', () => {
  it('inicializa con isExporting en false', () => {
    const { isExporting } = useExcelExport();
    expect(isExporting.value).toBe(false);
  });

  it('descarga el blob y maneja el estado de carga correctamente', async () => {
    const { isExporting, exportExcel } = useExcelExport();

    const mockResponse = {
      data: new Uint8Array([1, 2, 3]),
      headers: {
        'content-disposition': 'attachment; filename="reporte_test.xlsx"',
      },
    };

    const mockExportFn = vi.fn().mockResolvedValue(mockResponse);

    // Mock DOM elements
    const linkMock = {
      href: '',
      setAttribute: vi.fn(),
      click: vi.fn(),
    };
    const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(linkMock);
    const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});

    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();

    const promise = exportExcel(mockExportFn, 'default.xlsx');
    expect(isExporting.value).toBe(true);

    const result = await promise;

    expect(isExporting.value).toBe(false);
    expect(result.success).toBe(true);
    expect(result.filename).toBe('reporte_test.xlsx');
    expect(linkMock.setAttribute).toHaveBeenCalledWith('download', 'reporte_test.xlsx');
    expect(linkMock.click).toHaveBeenCalled();

    createElementSpy.mockRestore();
    appendChildSpy.mockRestore();
    removeChildSpy.mockRestore();
  });
});

import { ref } from 'vue';

import {
  createExcelBlob,
  getExcelFilename,
  triggerExcelDownload,
} from '@/utils/excel-download';

export function useExcelExport() {
  const isExporting = ref(false);

  const exportExcel = async (exportFn, defaultFilename = 'reporte.xlsx') => {
    isExporting.value = true;
    try {
      const response = await exportFn();
      const blob = createExcelBlob(response);
      const filename = getExcelFilename(response, defaultFilename);
      triggerExcelDownload(blob, filename);
      return { success: true, filename };
    } catch (error) {
      console.error('Error durante la descarga del reporte Excel:', error);
      throw error;
    } finally {
      isExporting.value = false;
    }
  };

  return { isExporting, exportExcel };
}

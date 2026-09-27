import { computed } from 'vue';

import { useExcelExport } from '@/composables/shared/useExcelExport';

export function useCampusExcelExport({
  edificiosService,
  localesService,
  explorerLevel,
  edificioActivo,
  activeFloorKey,
  localActivo,
  territorySearch,
}) {
  const { isExporting, exportExcel } = useExcelExport();

  const exportLabel = computed(() => {
    if (explorerLevel.value === 'floors' && edificioActivo.value) {
      const floor = activeFloorKey.value ? ` Piso ${activeFloorKey.value}` : '';
      return `Exportar${floor}`;
    }
    if (explorerLevel.value === 'buildings' && localActivo.value) {
      return 'Exportar Pabellones';
    }
    return 'Exportar Territorio';
  });

  const exportCampusExcel = async () => {
    const dateSuffix = new Date().toISOString().slice(0, 10);

    if (explorerLevel.value === 'floors' && edificioActivo.value) {
      const floor = activeFloorKey.value || '1';
      return exportExcel(
        () => edificiosService.exportarPisoExcel(edificioActivo.value.id, floor),
        `croquis_piso_${edificioActivo.value.codigo}_p${floor}_${dateSuffix}.xlsx`,
      );
    }

    if (explorerLevel.value === 'buildings' && localActivo.value) {
      return exportExcel(
        () => edificiosService.exportarExcel({ local_id: localActivo.value.id }),
        `pabellones_${localActivo.value.codigo}_${dateSuffix}.xlsx`,
      );
    }

    return exportExcel(
      () => localesService.exportarExcel({ search: territorySearch.value }),
      `reporte_territorio_${dateSuffix}.xlsx`,
    );
  };

  return { isExporting, exportLabel, exportCampusExcel };
}

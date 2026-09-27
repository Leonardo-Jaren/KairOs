const EXCEL_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

export function createExcelBlob(response) {
  const data = response?.data !== undefined ? response.data : response;
  return data instanceof Blob ? data : new Blob([data], { type: EXCEL_MIME_TYPE });
}

export function getExcelFilename(response, fallback = 'reporte.xlsx') {
  const disposition = response?.headers?.['content-disposition'];
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1]?.trim() || fallback;
}

export function triggerExcelDownload(blob, filename) {
  if (typeof window === 'undefined' || !window.URL || typeof document === 'undefined') return;

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export const getApiErrorMessage = (error, fallback) => {
  const data = error?.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return data;

  // DRF default format: { detail: "..." }
  if (data.detail) {
    return Array.isArray(data.detail) ? data.detail[0] : data.detail;
  }

  // Custom handler auth/permission/404 format: { error: "..." }
  if (typeof data.error === 'string') return data.error;

  // Custom handler validation format: { errores: { campo: ["..."] } }
  if (data.errores && typeof data.errores === 'object') {
    const firstField = Object.values(data.errores)[0];
    if (Array.isArray(firstField)) return firstField[0];
    if (typeof firstField === 'string') return firstField;
  }

  const firstValue = Object.values(data)[0];
  if (Array.isArray(firstValue)) return firstValue[0];
  if (typeof firstValue === 'string') return firstValue;
  return fallback;
};

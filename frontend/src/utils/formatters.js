export function formatDateTime(value) {
  return new Date(value).toLocaleString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

export function formatDate(value) {
  return new Date(value).toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function formatFloor(value) {
  const floor = String(value ?? '').trim().replace(/^piso\s*/i, '');
  return floor ? `Piso ${floor}` : 'Piso sin registrar';
}

export function formatBuildingName(value) {
  return String(value ?? '').trim().replace(/\s+piso$/i, '') || 'Sin edificio';
}

export const mapLocationQuery = (query = {}, localCity = '') => ({
  ciudad: localCity || query.ciudad || undefined,
  local: query.local || query.sede || undefined,
  pabellon: query.pabellon || query.edificio || undefined,
  piso: query.piso || undefined,
});

export const traditionalLocationQuery = (query = {}, localCity = '') => ({
  ciudad: localCity || query.ciudad || undefined,
  sede: query.sede || query.local || undefined,
  edificio: query.edificio || query.pabellon || undefined,
  piso: query.piso || undefined,
});

export const viewLocation = (view, query = {}, localCity = '') => {
  if (view === 'mapa') return { path: '/espacios/mapa', query: mapLocationQuery(query, localCity) };
  return {
    path: '/espacios',
    query: {
      ...traditionalLocationQuery(query, localCity),
      vista: view === 'inventario' ? 'inventario' : undefined,
    },
  };
};

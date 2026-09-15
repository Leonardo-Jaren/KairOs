import { computed, onBeforeUnmount, ref, watch } from 'vue';

export const LEGACY_LOCAL = '__legacy__';
const sameId = (left, right) => String(left ?? '') === String(right ?? '');
const localIdOf = (building) => building.local_id ?? building.local?.id ?? null;
const compare = (left, right) => String(left).localeCompare(String(right), 'es', {
  numeric: true,
  sensitivity: 'base',
});

export async function listarTodas(service, params = {}) {
  const rows = [];
  const visited = new Set();
  let page = 1;
  while (true) {
    if (visited.has(page)) throw new Error('La API repitió una página del listado.');
    visited.add(page);
    const data = await service.listar({ ...params, page_size: 100, page });
    const batch = Array.isArray(data) ? data : data?.results;
    if (!Array.isArray(batch)) throw new Error('La API devolvió un listado no válido.');
    rows.push(...batch);
    if (Array.isArray(data)) return rows;
    if (!data.next) {
      if (Number(data.count) > rows.length) {
        throw new Error('No se pudo recuperar el listado completo. Intenta de nuevo.');
      }
      return rows;
    }
    if (!batch.length) throw new Error('La API devolvió una página vacía antes de terminar.');
    const nextPage = Number(new URL(data.next, 'http://localhost').searchParams.get('page'));
    if (!Number.isInteger(nextPage) || nextPage < 1) {
      throw new Error('La API devolvió una página siguiente no válida.');
    }
    page = nextPage;
  }
}

export function useCampusTerritorio({ buildingRecords, localRecords, navigation, isEditing, showToast }) {
  const selectedCity = ref('');
  const selectedLocalId = ref('');
  const selectedBuildingId = ref('');
  let ready = false;

  const orderedLocals = computed(() => [...localRecords.value].sort((a, b) => (
    compare(a.ciudad, b.ciudad) || compare(a.nombre, b.nombre) || compare(a.codigo, b.codigo)
  )));
  const ciudades = computed(() => [...new Set(orderedLocals.value.map((local) => local.ciudad))]);
  const hasLegacy = computed(() => buildingRecords.value.some((building) => localIdOf(building) == null));
  const cityOptions = computed(() => [
    ...ciudades.value.map((city) => ({ value: city, label: city })),
    ...(hasLegacy.value ? [{ value: LEGACY_LOCAL, label: 'Sin ciudad asignada' }] : []),
  ]);
  const localOptions = computed(() => selectedCity.value === LEGACY_LOCAL
    ? [{ value: LEGACY_LOCAL, label: 'Sin local asignado' }]
    : orderedLocals.value.filter((local) => local.ciudad === selectedCity.value)
      .map((local) => ({ value: local.id, label: `${local.codigo} · ${local.nombre}` })));
  const allLocalOptions = computed(() => [
    { value: '', label: 'Sin local asignado' },
    ...orderedLocals.value.map((local) => ({
      value: local.id,
      label: `${local.ciudad} · ${local.nombre} (${local.codigo})`,
    })),
  ]);
  const localActivo = computed(() => localRecords.value.find((local) => sameId(local.id, selectedLocalId.value)) ?? null);
  const selectedLocalName = computed(() => selectedLocalId.value === LEGACY_LOCAL
    ? 'Sin local asignado' : localActivo.value?.nombre ?? '');
  const currentBuildingRecords = computed(() => buildingRecords.value.filter((building) => (
    selectedLocalId.value === LEGACY_LOCAL
      ? localIdOf(building) == null
      : selectedLocalId.value !== '' && sameId(localIdOf(building), selectedLocalId.value)
  )));

  const selectionBlocked = () => {
    if (!isEditing()) return false;
    showToast('Guarda o cancela la edición del croquis antes de cambiar de ubicación.', 'error');
    return true;
  };

  const writeQuery = (method = 'replace') => {
    if (!ready || !navigation.router) return;
    const previous = navigation.route?.query ?? {};
    const query = { ...previous };
    for (const [key, value] of Object.entries({
      ciudad: selectedCity.value, local: selectedLocalId.value, pabellon: selectedBuildingId.value,
    })) {
      if (value !== '') query[key] = String(value);
      else delete query[key];
    }
    const keys = new Set([...Object.keys(previous), ...Object.keys(query)]);
    if ([...keys].every((key) => sameId(previous[key], query[key]))) return;
    navigation.router[method]({ query }).catch(() => {
      showToast('No se pudo actualizar la ubicación en la navegación.', 'error');
    });
  };

  const resolveSelection = (requested = {}) => {
    const requestedLocal = orderedLocals.value.find((local) => sameId(local.id, requested.local));
    const legacy = requested.local === LEGACY_LOCAL && hasLegacy.value;
    const city = requestedLocal?.ciudad ?? (legacy ? LEGACY_LOCAL
      : cityOptions.value.find((option) => sameId(option.value, requested.ciudad))?.value
        ?? cityOptions.value[0]?.value ?? '');
    const local = requestedLocal?.id ?? (city === LEGACY_LOCAL ? LEGACY_LOCAL
      : orderedLocals.value.find((item) => item.ciudad === city)?.id ?? '');
    const candidates = buildingRecords.value.filter((building) => local === LEGACY_LOCAL
      ? localIdOf(building) == null : local !== '' && sameId(localIdOf(building), local));
    return {
      city,
      local,
      building: candidates.find((building) => sameId(building.id, requested.pabellon))?.id
        ?? candidates[0]?.id ?? '',
    };
  };

  const applySelection = (requested, method = 'replace') => {
    const result = resolveSelection(requested);
    selectedCity.value = result.city;
    selectedLocalId.value = result.local;
    selectedBuildingId.value = result.building;
    writeQuery(method);
  };
  const refreshSelection = () => {
    const requested = ready ? {
      ciudad: selectedCity.value, local: selectedLocalId.value, pabellon: selectedBuildingId.value,
    } : navigation.route?.query ?? {};
    ready = true;
    applySelection(requested);
  };
  const selectCity = (city) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: city, local: city === LEGACY_LOCAL ? LEGACY_LOCAL : '' }, 'push');
    return true;
  };
  const selectLocal = (local) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: selectedCity.value, local }, 'push');
    return true;
  };
  const selectBuilding = (building) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: selectedCity.value, local: selectedLocalId.value, pabellon: building }, 'push');
    return true;
  };
  const selectSavedBuilding = (building) => applySelection({
    local: localIdOf(building) ?? LEGACY_LOCAL, pabellon: building.id,
  }, 'push');

  if (navigation.route) {
    watch(() => navigation.route.query, (query) => {
      if (ready) applySelection(query);
    });
  }
  if (navigation.router?.beforeEach) {
    const removeGuard = navigation.router.beforeEach((to, from) => (
      to.fullPath !== from.fullPath && selectionBlocked() ? false : true
    ));
    onBeforeUnmount(removeGuard);
  }

  return {
    selectedCity, selectedLocalId, selectedBuildingId, ciudades, cityOptions,
    localOptions, allLocalOptions, localActivo, selectedLocalName, currentBuildingRecords,
    selectionBlocked, refreshSelection, selectCity, selectLocal, selectBuilding, selectSavedBuilding,
  };
}

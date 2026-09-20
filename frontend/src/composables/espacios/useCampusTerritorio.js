import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';

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

export function useCampusTerritorio({
  buildingRecords,
  localRecords,
  navigation,
  isEditing,
  showToast,
}) {
  const authStore = useAuthStore();
  const selectedCity = ref('');
  const selectedCampusType = ref('');
  const selectedLocalId = ref('');
  const selectedBuildingId = ref('');
  let ready = false;
  let latestWrittenQuery = '';
  let navigationPending = Promise.resolve();

  const querySignature = (query) => JSON.stringify(
    Object.entries(query).sort(([left], [right]) => left.localeCompare(right)),
  );

  const typeLabels = {
    campus: 'Campus',
    sede: 'Sede',
    anexo: 'Anexo',
    otro: 'Otro tipo',
  };
  const normalizeLegacy = (value) => (
    ['legacy', '**legacy**', '__legacy__'].includes(String(value ?? '').toLowerCase())
      ? LEGACY_LOCAL
      : value
  );

  const orderedLocals = computed(() => {
    let list = [...localRecords.value];
    // Si el usuario no es superadministrador y tiene sedes asignadas, restringir a su ámbito
    if (authStore?.user && !authStore.isSuperAdmin && Array.isArray(authStore.user.sedes)) {
      const allowedSedeIds = new Set(authStore.user.sedes.map((s) => String(s.id)));
      list = list.filter((local) => allowedSedeIds.has(String(local.id)));
    }
    return list.sort((a, b) => (
      compare(a.ciudad, b.ciudad) || compare(a.nombre, b.nombre) || compare(a.codigo, b.codigo)
    ));
  });
  const ciudades = computed(() => [...new Set(orderedLocals.value.map((local) => local.ciudad))]);
  const hasLegacy = computed(() => (
    (authStore?.isSuperAdmin || authStore?.isAdmin)
    && buildingRecords.value.some((building) => localIdOf(building) == null)
  ));
  const cityOptions = computed(() => [
    ...ciudades.value.map((city) => ({ value: city, label: city })),
    ...(hasLegacy.value ? [{ value: LEGACY_LOCAL, label: 'Sin ciudad asignada' }] : []),
  ]);
  const cityCards = computed(() => cityOptions.value.map((option) => {
    if (option.value === LEGACY_LOCAL) {
      const buildings = buildingRecords.value.filter((building) => localIdOf(building) == null);
      return {
        ...option,
        localCount: 0,
        buildingCount: buildings.length,
        legacy: true,
      };
    }
    const locals = orderedLocals.value.filter((local) => local.ciudad === option.value);
    const localIds = new Set(locals.map((local) => String(local.id)));
    return {
      ...option,
      localCount: locals.length,
      buildingCount: buildingRecords.value.filter(
        (building) => localIds.has(String(localIdOf(building))),
      ).length,
      legacy: false,
    };
  }).sort((left, right) => right.buildingCount - left.buildingCount || compare(left.label, right.label)));
  const campusTypeOptions = computed(() => {
    const counts = new Map();
    orderedLocals.value
      .filter((local) => local.ciudad === selectedCity.value)
      .forEach((local) => {
        const type = local.tipo ?? 'sede';
        counts.set(type, (counts.get(type) ?? 0) + 1);
    });
    if (selectedCity.value === LEGACY_LOCAL && hasLegacy.value) {
      return [{ value: LEGACY_LOCAL, label: 'Sin tipo asignado', count: 1 }];
    }
    return Object.entries(typeLabels)
      .filter(([value]) => counts.has(value))
      .map(([value, label]) => ({
        value,
        label,
        count: counts.get(value),
      }));
  });
  const localOptions = computed(() => {
    if (selectedCity.value === LEGACY_LOCAL) {
      return hasLegacy.value ? [{ value: LEGACY_LOCAL, label: 'Registros sin local asignado' }] : [];
    }
    return orderedLocals.value
      .filter((local) => local.ciudad === selectedCity.value)
      .filter((local) => (local.tipo ?? 'sede') === selectedCampusType.value)
      .map((local) => ({ value: local.id, label: `${local.codigo} · ${local.nombre}` }));
  });
  const cityLocalCards = computed(() => {
    if (selectedCity.value === LEGACY_LOCAL) {
      const buildings = buildingRecords.value.filter((building) => localIdOf(building) == null);
      return hasLegacy.value ? [{
        id: LEGACY_LOCAL,
        codigo: 'PENDIENTE',
        nombre: 'Registros sin local asignado',
        tipo: LEGACY_LOCAL,
        tipoLabel: 'Pendiente de clasificación',
        descripcion: 'Pabellones anteriores que todavía necesitan una ubicación.',
        buildingCount: buildings.length,
      }] : [];
    }
    return orderedLocals.value
      .filter((local) => local.ciudad === selectedCity.value)
      .map((local) => ({
        ...local,
        tipoLabel: typeLabels[local.tipo ?? 'sede'] ?? typeLabels.otro,
        buildingCount: buildingRecords.value.filter(
          (building) => sameId(localIdOf(building), local.id),
        ).length,
      }));
  });
  const allLocalOptions = computed(() => [
    { value: '', label: 'Sin local asignado' },
    ...orderedLocals.value.map((local) => ({
      value: local.id,
      label: `${local.ciudad} · ${local.nombre} (${local.codigo})`,
    })),
  ]);
  const localActivo = computed(() => orderedLocals.value.find((local) => sameId(local.id, selectedLocalId.value)) ?? null);
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
    const locationChanged = !sameId(previous.ciudad, selectedCity.value)
      || !sameId(previous.tipo, selectedCampusType.value)
      || !sameId(previous.local, selectedLocalId.value)
      || !sameId(previous.pabellon, selectedBuildingId.value);
    for (const [key, value] of Object.entries({
      ciudad: selectedCity.value,
      tipo: selectedCampusType.value,
      local: selectedLocalId.value,
      pabellon: selectedBuildingId.value,
    })) {
      if (value !== '') query[key] = String(value);
      else delete query[key];
    }
    if (locationChanged) delete query.piso;
    const keys = new Set([...Object.keys(previous), ...Object.keys(query)]);
    if ([...keys].every((key) => sameId(previous[key], query[key]))) return;
    const writtenSignature = querySignature(query);
    latestWrittenQuery = writtenSignature;
    navigationPending = navigation.router[method]({ query })
      .catch(() => {
        showToast('No se pudo actualizar la ubicación en la navegación.', 'error');
      })
      .finally(() => {
        if (latestWrittenQuery === writtenSignature) {
          latestWrittenQuery = '';
        }
      });
  };
  const afterNavigation = (callback) => navigationPending.finally(callback);

  const resolveSelection = (requested = {}) => {
    const requestedCity = normalizeLegacy(requested.ciudad);
    const requestedLocalValue = normalizeLegacy(requested.local);
    const requestedType = normalizeLegacy(requested.tipo);
    const requestedLocal = orderedLocals.value.find((local) => sameId(local.id, requestedLocalValue));
    const legacy = [requestedCity, requestedType, requestedLocalValue].includes(LEGACY_LOCAL)
      && hasLegacy.value;
    const hasRequestedPath = [requested.ciudad, requested.tipo, requested.local, requested.pabellon]
      .some((value) => value !== undefined && value !== '');
    if (!hasRequestedPath && navigation.route) {
      return { city: '', type: '', local: '', building: '' };
    }
    const city = requestedLocal?.ciudad ?? (legacy ? LEGACY_LOCAL
      : cityOptions.value.find((option) => sameId(option.value, requestedCity))?.value
        ?? (!navigation.route ? cityOptions.value[0]?.value : '') ?? '');
    const cityLocals = orderedLocals.value.filter((local) => local.ciudad === city);
    const availableTypes = new Set(cityLocals.map((local) => local.tipo ?? 'sede'));
    const type = city === LEGACY_LOCAL
      ? LEGACY_LOCAL
      : availableTypes.has(requestedType)
        ? requestedType
        : requestedLocal
          ? requestedLocal.tipo ?? 'sede'
          : !navigation.route
            ? cityLocals[0]?.tipo ?? (cityLocals.length ? 'sede' : '')
            : '';
    const matchingLocals = cityLocals.filter((local) => (local.tipo ?? 'sede') === type);
    const local = requestedLocal && requestedLocal.ciudad === city
      && (requestedLocal.tipo ?? 'sede') === type
      ? requestedLocal.id
      : city === LEGACY_LOCAL
        ? (requestedLocalValue === LEGACY_LOCAL || !navigation.route ? LEGACY_LOCAL : '')
        : !navigation.route
          ? matchingLocals[0]?.id ?? ''
          : '';
    const candidates = buildingRecords.value.filter((building) => local === LEGACY_LOCAL
      ? localIdOf(building) == null : local !== '' && sameId(localIdOf(building), local));
    return {
      city,
      type,
      local,
      building: candidates.find((building) => sameId(building.id, requested.pabellon))?.id
        ?? (!navigation.route ? candidates[0]?.id : '') ?? '',
    };
  };

  const applySelection = (requested, method = 'replace') => {
    const result = resolveSelection(requested);
    selectedCity.value = result.city;
    selectedCampusType.value = result.type;
    selectedLocalId.value = result.local;
    selectedBuildingId.value = result.building;
    writeQuery(method);
  };
  const refreshSelection = () => {
    const requested = ready ? {
      ciudad: selectedCity.value,
      tipo: selectedCampusType.value,
      local: selectedLocalId.value,
      pabellon: selectedBuildingId.value,
    } : navigation.route?.query ?? {};
    ready = true;
    applySelection(requested);
  };
  const selectCity = (city) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: city }, 'push');
    return true;
  };
  const selectCampusType = (type) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: selectedCity.value, tipo: type }, 'push');
    return true;
  };
  const selectLocal = (local) => {
    if (selectionBlocked()) return false;
    applySelection({ ciudad: selectedCity.value, tipo: selectedCampusType.value, local }, 'push');
    return true;
  };
  const selectLocalCard = (local) => {
    if (selectionBlocked()) return false;
    applySelection({ local }, 'push');
    return true;
  };
  const selectSavedLocal = (local) => applySelection({ local: local.id }, 'push');
  const selectBuilding = (building) => {
    if (selectionBlocked()) return false;
    applySelection({
      ciudad: selectedCity.value,
      tipo: selectedCampusType.value,
      local: selectedLocalId.value,
      pabellon: building,
    }, 'push');
    return true;
  };
  const selectSavedBuilding = (building) => applySelection({
    local: localIdOf(building) ?? LEGACY_LOCAL, pabellon: building.id,
  }, 'push');

  if (navigation.route) {
    watch(() => navigation.route.query, (query) => {
      if (!ready) return;
      const signature = querySignature(query);
      if (latestWrittenQuery && signature !== latestWrittenQuery) return;
      applySelection(query);
    });
  }
  if (navigation.router?.beforeEach) {
    const removeGuard = navigation.router.beforeEach((to, from) => (
      to.fullPath !== from.fullPath && selectionBlocked() ? false : true
    ));
    onBeforeUnmount(removeGuard);
  }

  return {
    selectedCity, selectedCampusType, selectedLocalId, selectedBuildingId, ciudades, cityOptions,
    cityCards, cityLocalCards,
    campusTypeOptions,
    localOptions, allLocalOptions, localActivo, selectedLocalName, currentBuildingRecords,
    selectionBlocked, refreshSelection, selectCity, selectCampusType, selectLocal, selectLocalCard,
    selectSavedLocal, selectBuilding, selectSavedBuilding, afterNavigation,
  };
}

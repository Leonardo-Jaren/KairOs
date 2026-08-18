import { ref } from 'vue';

import { getApiErrorMessage } from '@/utils/api-errors';
import { formatFloor } from '@/utils/formatters';

const clone = (value) => JSON.parse(JSON.stringify(value));

const roomSize = (space) => {
  if (['laboratorio', 'sala_computo'].includes(space.tipo)) {
    if (space.cantidad_equipos >= 20) return { ancho: 4, alto: 2 };
    if (space.cantidad_equipos >= 8) return { ancho: 3, alto: 2 };
    return { ancho: 2, alto: 2 };
  }
  return { ancho: space.cantidad_equipos > 3 ? 2 : 1, alto: 1 };
};

const createDefaultFloorLayout = (floorSpaces) => {
  const columnas = 12;
  const ambientes = [];
  const pasillos = [];
  const roomDefinitions = floorSpaces.map((space) => ({ space, ...roomSize(space) }));
  const groupCount = roomDefinitions.length > 1 ? 2 : 1;
  const groups = Array.from({ length: groupCount }, () => ({ width: 0, rooms: [] }));

  roomDefinitions.forEach((room) => {
    let group = groups
      .filter((candidate) => candidate.width + room.ancho <= columnas)
      .sort((left, right) => left.width - right.width)[0];
    if (!group && groups.length < 4) {
      group = { width: 0, rooms: [] };
      groups.push(group);
    }
    if (!group) group = groups[groups.length - 1];
    group.rooms.push(room);
    group.width += room.ancho;
  });

  groups.forEach((group, groupIndex) => {
    const fila = groupIndex * 3 + 1;
    let columna = 1;
    group.rooms.forEach((room) => {
      ambientes.push({
        espacio_id: room.space.id,
        fila,
        columna,
        ancho: room.ancho,
        alto: room.alto,
      });
      columna += room.ancho;
    });
    if (groupIndex < groups.length - 1 || groups.length === 1) {
      for (let corridorColumn = 1; corridorColumn <= columnas; corridorColumn += 1) {
        pasillos.push({ fila: fila + 2, columna: corridorColumn });
      }
    }
  });

  const filas = Math.max(3, Math.min(12, groups.length * 2 + groups.length - 1));
  return { filas, columnas, ambientes, pasillos };
};

const cellsForRoom = (room) => {
  const cells = [];
  for (let row = room.fila; row < room.fila + room.alto; row += 1) {
    for (let column = room.columna; column < room.columna + room.ancho; column += 1) {
      cells.push(`${row}-${column}`);
    }
  }
  return cells;
};

const findFreeRoomPosition = (layout, size) => {
  const occupied = new Set(layout.ambientes.flatMap(cellsForRoom));
  const corridors = new Set(layout.pasillos.map((cell) => `${cell.fila}-${cell.columna}`));

  for (let row = 1; row <= layout.filas - size.alto + 1; row += 1) {
    for (let column = 1; column <= layout.columnas - size.ancho + 1; column += 1) {
      const candidate = { fila: row, columna: column, ...size };
      const cells = cellsForRoom(candidate);
      if (cells.every((cell) => !occupied.has(cell) && !corridors.has(cell))) return candidate;
    }
  }
  return null;
};

const appendMissingRooms = (layout, missingSpaces) => {
  missingSpaces.forEach((space) => {
    const size = roomSize(space);
    let position = findFreeRoomPosition(layout, size);

    while (!position && layout.filas < 12) {
      layout.filas += 1;
      position = findFreeRoomPosition(layout, size);
    }
    while (!position && layout.columnas < 16) {
      layout.columnas += 1;
      position = findFreeRoomPosition(layout, size);
    }

    if (position) layout.ambientes.push({ espacio_id: Number(space.id), ...position });
  });
};

export const normalizeFloorLayout = (storedLayout, floorSpaces) => {
  if (!storedLayout?.ambientes?.length) return createDefaultFloorLayout(floorSpaces);
  const activeIds = new Set(floorSpaces.map((space) => Number(space.id)));
  const ambientes = storedLayout.ambientes
    .filter((room) => activeIds.has(Number(room.espacio_id)))
    .map((room) => ({ ...room, espacio_id: Number(room.espacio_id) }));
  const layout = {
    filas: Number(storedLayout.filas) || 3,
    columnas: Number(storedLayout.columnas) || 12,
    ambientes,
    pasillos: (storedLayout.pasillos ?? []).map((cell) => ({ ...cell })),
  };
  const placedIds = new Set(ambientes.map((room) => room.espacio_id));
  const missingSpaces = floorSpaces.filter((space) => !placedIds.has(Number(space.id)));
  appendMissingRooms(layout, missingSpaces);
  return layout;
};

export function useCroquisPiso({
  buildingRecords,
  activeBuilding,
  buildingService,
  showToast,
}) {
  const editingFloor = ref('');
  const floorDraft = ref(null);
  const floorTool = ref('move');
  const selectedFloorSpaceId = ref(null);
  const floorSaving = ref(false);

  const roomCells = (room) => {
    const result = [];
    for (let row = room.fila; row < room.fila + room.alto; row += 1) {
      for (let column = room.columna; column < room.columna + room.ancho; column += 1) {
        result.push(`${row}-${column}`);
      }
    }
    return result;
  };

  const canPlaceRoom = (candidate, ignoredSpaceId = null) => {
    if (!floorDraft.value) return false;
    if (
      candidate.fila < 1
      || candidate.columna < 1
      || candidate.fila + candidate.alto - 1 > floorDraft.value.filas
      || candidate.columna + candidate.ancho - 1 > floorDraft.value.columnas
    ) return false;
    const candidateCells = new Set(roomCells(candidate));
    const corridorCells = new Set(
      floorDraft.value.pasillos.map((cell) => `${cell.fila}-${cell.columna}`),
    );
    if ([...candidateCells].some((cell) => corridorCells.has(cell))) return false;
    return !floorDraft.value.ambientes.some((room) => (
      Number(room.espacio_id) !== Number(ignoredSpaceId)
      && roomCells(room).some((cell) => candidateCells.has(cell))
    ));
  };

  const startFloorEditing = (floor) => {
    editingFloor.value = floor.key;
    floorDraft.value = clone(floor.layout);
    floorTool.value = 'move';
    selectedFloorSpaceId.value = floor.allSpaces[0]?.id ?? null;
  };

  const cancelFloorEditing = () => {
    editingFloor.value = '';
    floorDraft.value = null;
    selectedFloorSpaceId.value = null;
    floorTool.value = 'move';
  };

  const selectFloorSpace = (spaceId) => {
    selectedFloorSpaceId.value = Number(spaceId);
    floorTool.value = 'move';
  };

  const setFloorTool = (tool) => {
    if (['move', 'corridor'].includes(tool)) floorTool.value = tool;
  };

  const handleFloorCell = ({ row, column }) => {
    if (!floorDraft.value) return;
    const key = `${row}-${column}`;
    if (floorTool.value === 'corridor') {
      const occupied = floorDraft.value.ambientes.some((room) => roomCells(room).includes(key));
      if (occupied) {
        showToast('El pasillo no puede atravesar un ambiente.', 'error');
        return;
      }
      const index = floorDraft.value.pasillos.findIndex((cell) => (
        `${cell.fila}-${cell.columna}` === key
      ));
      if (index >= 0) floorDraft.value.pasillos.splice(index, 1);
      else floorDraft.value.pasillos.push({ fila: row, columna: column });
      return;
    }

    const room = floorDraft.value.ambientes.find((item) => (
      Number(item.espacio_id) === Number(selectedFloorSpaceId.value)
    ));
    if (!room) return;
    const candidate = { ...room, fila: row, columna: column };
    if (!canPlaceRoom(candidate, room.espacio_id)) {
      showToast('Ese espacio no tiene área libre suficiente.', 'error');
      return;
    }
    Object.assign(room, { fila: row, columna: column });
  };

  const resizeSelectedFloorSpace = (field, delta) => {
    const room = floorDraft.value?.ambientes.find((item) => (
      Number(item.espacio_id) === Number(selectedFloorSpaceId.value)
    ));
    if (!room || !['ancho', 'alto'].includes(field)) return;
    const limit = field === 'ancho' ? 6 : 4;
    const candidate = {
      ...room,
      [field]: Math.max(1, Math.min(limit, room[field] + delta)),
    };
    if (!canPlaceRoom(candidate, room.espacio_id)) {
      showToast('No hay espacio para ampliar el ambiente en esa dirección.', 'error');
      return;
    }
    room[field] = candidate[field];
  };

  const updateFloorColumns = (value) => {
    const nextColumns = Number(value);
    if (floorDraft.value.ambientes.some((room) => room.columna + room.ancho - 1 > nextColumns)) {
      showToast('Mueve primero los ambientes que quedarían fuera del croquis.', 'error');
      return;
    }
    floorDraft.value.columnas = nextColumns;
    floorDraft.value.pasillos = floorDraft.value.pasillos.filter(
      (cell) => cell.columna <= nextColumns,
    );
  };

  const addFloorRow = () => {
    if (floorDraft.value?.filas < 12) floorDraft.value.filas += 1;
  };

  const removeFloorRow = () => {
    if (!floorDraft.value || floorDraft.value.filas <= 3) return;
    const lastRow = floorDraft.value.filas;
    const occupied = floorDraft.value.ambientes.some(
      (room) => room.fila + room.alto - 1 >= lastRow,
    );
    if (occupied) {
      showToast('Mueve los ambientes de la última fila antes de retirarla.', 'error');
      return;
    }
    floorDraft.value.pasillos = floorDraft.value.pasillos.filter(
      (cell) => cell.fila < lastRow,
    );
    floorDraft.value.filas -= 1;
  };

  const saveFloorLayout = async () => {
    if (!editingFloor.value || !floorDraft.value || !activeBuilding.value) return;
    const floor = editingFloor.value;
    floorSaving.value = true;
    try {
      const saved = await buildingService.guardarCroquisPiso(activeBuilding.value.id, {
        piso: floor,
        ...clone(floorDraft.value),
      });
      buildingRecords.value = buildingRecords.value.map((building) => (
        building.id === saved.id ? saved : building
      ));
      cancelFloorEditing();
      showToast(`Croquis de ${formatFloor(floor)} actualizado.`);
    } catch (requestError) {
      showToast(
        getApiErrorMessage(requestError, 'No se pudo guardar el croquis del piso.'),
        'error',
      );
    } finally {
      floorSaving.value = false;
    }
  };

  return {
    editingFloor,
    floorDraft,
    floorTool,
    selectedFloorSpaceId,
    floorSaving,
    startFloorEditing,
    cancelFloorEditing,
    selectFloorSpace,
    setFloorTool,
    handleFloorCell,
    resizeSelectedFloorSpace,
    updateFloorColumns,
    addFloorRow,
    removeFloorRow,
    saveFloorLayout,
  };
}

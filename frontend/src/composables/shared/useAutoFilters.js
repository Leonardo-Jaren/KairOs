import { nextTick, onBeforeUnmount, watch } from 'vue';

export function useAutoFilters(
  filters,
  load,
  { searchKey = 'search', immediateKeys = [], delay = 350 } = {},
) {
  let searchTimer = null;
  let paused = false;

  const cancelPendingSearch = () => {
    if (searchTimer !== null) {
      clearTimeout(searchTimer);
      searchTimer = null;
    }
  };

  const reloadFirstPage = () => {
    filters.page = 1;
    return load();
  };

  watch(() => filters[searchKey], () => {
    if (paused) return;
    cancelPendingSearch();
    searchTimer = setTimeout(() => {
      searchTimer = null;
      reloadFirstPage();
    }, delay);
  });

  if (immediateKeys.length) {
    watch(
      () => immediateKeys.map((key) => filters[key]),
      () => {
        if (paused) return;
        cancelPendingSearch();
        reloadFirstPage();
      },
    );
  }

  const applyFilters = () => {
    cancelPendingSearch();
    return reloadFirstPage();
  };

  const resetFilters = async (values) => {
    paused = true;
    cancelPendingSearch();
    Object.assign(filters, values, { page: 1 });
    await nextTick();
    paused = false;
    return load();
  };

  onBeforeUnmount(cancelPendingSearch);

  return { applyFilters, resetFilters };
}

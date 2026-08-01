<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Check, ChevronDown, ChevronLeft, ChevronRight, LoaderCircle, Search } from '@lucide/vue';

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: '' },
  id: { type: String, required: true },
  label: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Seleccionar' },
  searchPlaceholder: { type: String, default: 'Buscar opciones' },
  emptyMessage: { type: String, default: 'No hay opciones disponibles.' },
  pageSize: { type: Number, default: 10 },
  initialOption: { type: Object, default: null },
  loadOptions: { type: Function, required: true },
});

const emit = defineEmits(['update:modelValue', 'load-error']);
const isOpen = ref(false);
const loading = ref(false);
const loaded = ref(false);
const options = ref([]);
const selectedCache = ref(props.initialOption);
const highlightedIndex = ref(-1);
const search = ref('');
const page = ref(1);
const total = ref(0);
const loadError = ref('');
const container = ref(null);
const trigger = ref(null);
const dropdown = ref(null);
const dropdownStyle = ref({});
let searchTimer;
let requestSequence = 0;

const sameValue = (left, right) => (
  Object.is(left, right) || String(left) === String(right)
);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / props.pageSize)));
const selectedOption = computed(() => (
  options.value.find((option) => sameValue(option.value, props.modelValue))
  || (selectedCache.value && sameValue(selectedCache.value.value, props.modelValue)
    ? selectedCache.value
    : null)
));

const optionId = (index) => `${props.id}-option-${index}`;

watch(() => props.initialOption, (option) => {
  if (option) selectedCache.value = option;
}, { immediate: true });

watch(() => props.modelValue, (value) => {
  if (value === '' || value === null || value === undefined) selectedCache.value = null;
  const matchingOption = options.value.find((option) => sameValue(option.value, value));
  if (matchingOption) selectedCache.value = matchingOption;
});

const updateDropdownPosition = () => {
  if (!trigger.value || !dropdown.value) return;

  const gap = 8;
  const rect = trigger.value.getBoundingClientRect();
  const menuHeight = Math.min(dropdown.value.scrollHeight || 320, 320);
  const spaceBelow = window.innerHeight - rect.bottom - gap;
  const spaceAbove = rect.top - gap;
  const opensUpward = spaceBelow < Math.min(menuHeight, 200) && spaceAbove > spaceBelow;
  const availableHeight = Math.max(160, Math.min(320, opensUpward ? spaceAbove - gap : spaceBelow - gap));
  const visibleHeight = Math.min(menuHeight, availableHeight);

  dropdownStyle.value = {
    left: `${rect.left}px`,
    top: opensUpward
      ? `${Math.max(gap, rect.top - visibleHeight - gap)}px`
      : `${rect.bottom + gap}px`,
    width: `${rect.width}px`,
    maxHeight: `${availableHeight}px`,
  };
};

const loadPage = async (requestedPage = 1) => {
  const currentRequest = ++requestSequence;
  loading.value = true;
  loadError.value = '';

  try {
    const response = await props.loadOptions({
      page: requestedPage,
      pageSize: props.pageSize,
      search: search.value.trim(),
    });
    if (currentRequest !== requestSequence) return;

    options.value = response.options ?? response.results ?? [];
    total.value = response.total ?? response.count ?? options.value.length;
    page.value = requestedPage;
    loaded.value = true;
    highlightedIndex.value = options.value.length ? 0 : -1;

    const matchingOption = options.value.find((option) => sameValue(option.value, props.modelValue));
    if (matchingOption) selectedCache.value = matchingOption;
  } catch (error) {
    if (currentRequest !== requestSequence) return;
    options.value = [];
    total.value = 0;
    loadError.value = 'No se pudieron cargar las opciones.';
    emit('load-error', error);
  } finally {
    if (currentRequest === requestSequence) {
      loading.value = false;
      await nextTick();
      updateDropdownPosition();
    }
  }
};

const close = () => {
  isOpen.value = false;
  highlightedIndex.value = -1;
};

const open = async () => {
  if (props.disabled) return;
  isOpen.value = true;
  await nextTick();
  updateDropdownPosition();
  if (!loaded.value) await loadPage(1);
};

const toggle = () => {
  if (isOpen.value) close();
  else open();
};

const selectOption = (option) => {
  selectedCache.value = option;
  emit('update:modelValue', option.value);
  close();
  trigger.value?.focus();
};

const changePage = (nextPage) => {
  if (loading.value || nextPage < 1 || nextPage > totalPages.value) return;
  loadPage(nextPage);
};

const handleSearch = (event) => {
  search.value = event.target.value;
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadPage(1), 300);
};

const moveHighlight = (direction) => {
  if (!isOpen.value) {
    open();
    return;
  }
  if (!options.value.length) return;
  const nextIndex = highlightedIndex.value + direction;
  highlightedIndex.value = (nextIndex + options.value.length) % options.value.length;
};

const handleKeydown = (event) => {
  if ((event.key === 'Enter' || event.key === ' ') && !isOpen.value) {
    event.preventDefault();
    open();
  } else if (event.key === 'ArrowDown') {
    event.preventDefault();
    moveHighlight(1);
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    moveHighlight(-1);
  } else if ((event.key === 'Enter' || event.key === ' ') && isOpen.value) {
    event.preventDefault();
    const option = options.value[highlightedIndex.value];
    if (option) selectOption(option);
  } else if (event.key === 'Escape') {
    event.preventDefault();
    close();
  }
};

const handleOutsideClick = (event) => {
  const clickedTrigger = container.value?.contains(event.target);
  const clickedDropdown = dropdown.value?.contains(event.target);
  if (!clickedTrigger && !clickedDropdown) close();
};

const handleViewportChange = () => {
  if (isOpen.value) updateDropdownPosition();
};

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
  window.addEventListener('resize', handleViewportChange);
  window.addEventListener('scroll', handleViewportChange, true);
});

onBeforeUnmount(() => {
  clearTimeout(searchTimer);
  requestSequence += 1;
  document.removeEventListener('click', handleOutsideClick);
  window.removeEventListener('resize', handleViewportChange);
  window.removeEventListener('scroll', handleViewportChange, true);
});
</script>

<template>
  <div ref="container" class="relative flex w-full flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-xs font-semibold text-slate-600">
      {{ label }}
    </label>

    <button
      :id="id"
      ref="trigger"
      type="button"
      role="combobox"
      aria-autocomplete="none"
      aria-haspopup="listbox"
      :aria-expanded="isOpen"
      :aria-controls="`${id}-options`"
      :aria-activedescendant="isOpen && highlightedIndex >= 0 ? optionId(highlightedIndex) : undefined"
      :disabled="disabled"
      class="flex min-h-11 w-full items-center justify-between gap-3 rounded-xl border bg-white px-3.5 text-left text-sm outline-none transition-all duration-200"
      :class="[
        error
          ? 'border-danger-300 focus:border-danger-400 focus:ring-4 focus:ring-danger-100'
          : isOpen
            ? 'border-primary-500 ring-4 ring-primary-100'
            : 'border-slate-200 hover:border-slate-300 focus:border-primary-500 focus:ring-4 focus:ring-primary-100',
        disabled ? 'cursor-not-allowed bg-slate-100 text-slate-400' : 'cursor-pointer',
      ]"
      @click.stop="toggle"
      @keydown="handleKeydown"
    >
      <span class="truncate" :class="selectedOption ? 'text-slate-800' : 'text-slate-400'">
        {{ selectedOption?.label ?? placeholder }}
      </span>
      <LoaderCircle v-if="loading && !isOpen" :size="17" class="shrink-0 animate-spin text-primary-500" />
      <ChevronDown
        v-else
        :size="18"
        class="shrink-0 text-slate-400 transition-transform duration-200"
        :class="isOpen ? 'rotate-180 text-primary-600' : ''"
        aria-hidden="true"
      />
    </button>

    <p v-if="error" role="alert" class="text-xs text-danger-600">{{ error }}</p>

    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="translate-y-1 opacity-0"
        leave-active-class="transition duration-100 ease-in"
        leave-to-class="translate-y-1 opacity-0"
      >
        <section
          v-if="isOpen"
          ref="dropdown"
          :style="dropdownStyle"
          class="fixed z-[70] flex overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10"
          aria-label="Opciones paginadas"
        >
          <div class="flex min-h-0 w-full flex-col">
            <div class="border-b border-slate-100 p-2">
              <label :for="`${id}-search`" class="sr-only">{{ searchPlaceholder }}</label>
              <div class="relative">
                <Search :size="16" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  :id="`${id}-search`"
                  :value="search"
                  type="search"
                  :placeholder="searchPlaceholder"
                  autocomplete="off"
                  class="min-h-10 w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-800 outline-none placeholder:text-slate-400 focus:border-primary-400 focus:bg-white focus:ring-3 focus:ring-primary-100"
                  @input="handleSearch"
                />
              </div>
            </div>

            <div :id="`${id}-options`" role="listbox" class="min-h-16 flex-1 overflow-y-auto p-1.5">
              <div v-if="loading" class="flex items-center justify-center gap-2 px-3 py-8 text-sm text-slate-500">
                <LoaderCircle :size="18" class="animate-spin text-primary-500" />
                Cargando opciones...
              </div>
              <p v-else-if="loadError" class="px-3 py-6 text-center text-sm text-danger-600">{{ loadError }}</p>
              <template v-else>
                <button
                  v-for="(option, index) in options"
                  :id="optionId(index)"
                  :key="option.value"
                  type="button"
                  role="option"
                  :aria-selected="selectedOption?.value === option.value"
                  class="flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors duration-150"
                  :class="[
                    highlightedIndex === index
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-slate-700 hover:bg-slate-50 hover:text-slate-950',
                    selectedOption?.value === option.value ? 'font-semibold' : 'font-medium',
                  ]"
                  @mouseenter="highlightedIndex = index"
                  @click="selectOption(option)"
                >
                  <span class="truncate">{{ option.label }}</span>
                  <Check v-if="selectedOption?.value === option.value" :size="16" class="shrink-0 text-primary-600" />
                </button>
                <p v-if="!options.length" class="px-3 py-6 text-center text-sm text-slate-400">{{ emptyMessage }}</p>
              </template>
            </div>

            <footer class="flex items-center justify-between gap-2 border-t border-slate-100 bg-slate-50/80 px-3 py-2">
              <span class="text-xs font-medium text-slate-500">{{ total }} registros</span>
              <div class="flex items-center gap-1.5">
                <button
                  type="button"
                  aria-label="Página anterior de opciones"
                  :disabled="page <= 1 || loading"
                  class="rounded-md p-1.5 text-slate-500 hover:bg-white hover:text-slate-900 disabled:pointer-events-none disabled:opacity-35"
                  @click="changePage(page - 1)"
                >
                  <ChevronLeft :size="16" />
                </button>
                <span class="min-w-16 text-center text-xs font-semibold text-slate-600">{{ page }} / {{ totalPages }}</span>
                <button
                  type="button"
                  aria-label="Página siguiente de opciones"
                  :disabled="page >= totalPages || loading"
                  class="rounded-md p-1.5 text-slate-500 hover:bg-white hover:text-slate-900 disabled:pointer-events-none disabled:opacity-35"
                  @click="changePage(page + 1)"
                >
                  <ChevronRight :size="16" />
                </button>
              </div>
            </footer>
          </div>
        </section>
      </Transition>
    </Teleport>
  </div>
</template>

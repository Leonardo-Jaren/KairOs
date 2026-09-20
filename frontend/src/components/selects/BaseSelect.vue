<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { Check, ChevronDown } from '@lucide/vue';

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: '' },
  id: { type: String, required: true },
  label: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Seleccionar' },
  size: { type: String, default: 'md' }, // 'sm' | 'md'
});

const emit = defineEmits(['update:modelValue']);
const isOpen = ref(false);
const highlightedIndex = ref(-1);
const container = ref(null);
const trigger = ref(null);
const dropdown = ref(null);
const dropdownStyle = ref({});

const selectedOption = computed(() => props.options.find((option) => (
  Object.is(option.value, props.modelValue)
  || String(option.value) === String(props.modelValue)
)));

const optionId = (index) => `${props.id}-option-${index}`;

const close = () => {
  isOpen.value = false;
  highlightedIndex.value = -1;
};

const updateDropdownPosition = () => {
  if (!trigger.value || !dropdown.value) return;

  const gap = 8;
  const rect = trigger.value.getBoundingClientRect();
  const menuHeight = Math.min(dropdown.value.scrollHeight || 240, 240);
  const spaceBelow = window.innerHeight - rect.bottom - gap;
  const spaceAbove = rect.top - gap;
  const opensUpward = spaceBelow < Math.min(menuHeight, 160) && spaceAbove > spaceBelow;
  const availableHeight = Math.max(96, Math.min(240, opensUpward ? spaceAbove - gap : spaceBelow - gap));
  const visibleHeight = Math.min(menuHeight, availableHeight);

  // Mantener el menu alineado con su campo sin desbordar la ventana
  const maxAllowedWidth = window.innerWidth - gap * 2;
  const widthToUse = Math.min(Math.max(rect.width, 160), maxAllowedWidth);
  const leftPosition = Math.max(gap, Math.min(rect.left, window.innerWidth - widthToUse - gap));

  dropdownStyle.value = {
    left: `${leftPosition}px`,
    top: opensUpward
      ? `${Math.max(gap, rect.top - visibleHeight - gap)}px`
      : `${rect.bottom + gap}px`,
    width: `${widthToUse}px`,
    maxHeight: `${availableHeight}px`,
  };
};

const open = async () => {
  if (props.disabled) return;
  isOpen.value = true;
  const selectedIndex = props.options.findIndex((option) => option === selectedOption.value);
  highlightedIndex.value = selectedIndex >= 0 ? selectedIndex : (props.options.length ? 0 : -1);
  await nextTick();
  updateDropdownPosition();
};

const toggle = () => {
  if (isOpen.value) close();
  else open();
};

const selectOption = (option) => {
  emit('update:modelValue', option.value);
  close();
  trigger.value?.focus();
};

const moveHighlight = (direction) => {
  if (!isOpen.value) {
    open();
    return;
  }

  if (!props.options.length) return;
  const nextIndex = highlightedIndex.value + direction;
  highlightedIndex.value = (nextIndex + props.options.length) % props.options.length;
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
  } else if (event.key === 'Home' && isOpen.value) {
    event.preventDefault();
    highlightedIndex.value = 0;
  } else if (event.key === 'End' && isOpen.value) {
    event.preventDefault();
    highlightedIndex.value = props.options.length - 1;
  } else if ((event.key === 'Enter' || event.key === ' ') && isOpen.value) {
    event.preventDefault();
    const option = props.options[highlightedIndex.value];
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
      class="flex w-full items-center justify-between border bg-white text-left outline-none transition-all duration-200 min-w-0 overflow-hidden"
      :class="[
        size === 'sm'
          ? 'h-8.5 rounded-xl px-2.5 text-xs gap-1.5'
          : 'h-11 rounded-xl px-3.5 text-sm gap-2.5',
        error
          ? 'border-danger-300 focus:border-danger-400 focus:ring-4 focus:ring-danger-100'
          : isOpen
            ? 'border-primary-500 ring-4 ring-primary-100'
            : 'border-slate-200 hover:border-slate-300 focus:border-primary-500 focus:ring-4 focus:ring-primary-100',
        disabled ? 'cursor-not-allowed bg-slate-100 text-slate-400' : 'cursor-pointer',
      ]"
      :disabled="disabled"
      role="combobox"
      aria-autocomplete="none"
      aria-haspopup="listbox"
      :aria-expanded="isOpen"
      :aria-controls="`${id}-options`"
      :aria-activedescendant="isOpen && highlightedIndex >= 0 ? optionId(highlightedIndex) : undefined"
      @click.stop="toggle"
      @keydown="handleKeydown"
    >
      <span
        class="truncate min-w-0 flex-1"
        :title="selectedOption?.label ?? placeholder"
        :class="selectedOption ? 'text-slate-800' : 'text-slate-400'"
      >
        {{ selectedOption?.label ?? placeholder }}
      </span>
      <ChevronDown
        :size="size === 'sm' ? 14 : 18"
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
        <div
          v-if="isOpen"
          :id="`${id}-options`"
          ref="dropdown"
          role="listbox"
          :aria-labelledby="label ? id : undefined"
          :style="dropdownStyle"
          class="surface-scrollbar fixed z-[70] overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-xl shadow-slate-900/10"
          :class="size === 'sm' ? 'p-1' : 'p-1.5'"
        >
          <button
            v-for="(option, index) in options"
            :id="optionId(index)"
            :key="option.value"
            type="button"
            role="option"
            :title="option.label"
            :aria-selected="selectedOption === option"
            class="flex w-full items-center justify-between gap-2 text-left transition-colors duration-150 min-w-0"
            :class="[
              size === 'sm' ? 'rounded-lg px-2.5 py-1.5 text-xs' : 'rounded-lg px-3 py-2.5 text-sm',
              highlightedIndex === index
                ? 'bg-primary-50 text-primary-700'
                : 'text-slate-700 hover:bg-slate-50 hover:text-slate-950',
              selectedOption === option ? 'font-semibold' : 'font-medium',
            ]"
            @mouseenter="highlightedIndex = index"
            @click="selectOption(option)"
          >
            <span class="truncate min-w-0 flex-1">{{ option.label }}</span>
            <Check v-if="selectedOption === option" :size="size === 'sm' ? 13 : 16" class="shrink-0 text-primary-600" aria-hidden="true" />
          </button>
          <p v-if="!options.length" :class="size === 'sm' ? 'px-2.5 py-1.5 text-xs' : 'px-3 py-2.5 text-sm'" class="text-slate-400">No hay opciones disponibles.</p>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

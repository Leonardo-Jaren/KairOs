<script setup>
import { ChevronLeft, ChevronRight } from '@lucide/vue';
import { ref, useId, watch } from 'vue';

const props = defineProps({
  page: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  total: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(['change']);
const errorId = useId();
const pageInput = ref(String(props.page));
const pageError = ref('');

watch(() => props.page, (page) => {
  pageInput.value = String(page);
  pageError.value = '';
});

const handlePageInput = (event) => {
  pageInput.value = event.target.value.replace(/\D/g, '');
  pageError.value = '';
};

const requestPage = (page) => {
  if (props.loading) return;
  pageError.value = '';
  pageInput.value = String(page);
  if (page === props.page) return;
  emit('change', page);
};

const applyPageInput = () => {
  if (!pageInput.value) {
    pageError.value = 'Ingresa un número de página.';
    return;
  }

  const requestedPage = Number(pageInput.value);
  if (requestedPage < 1 || requestedPage > props.totalPages) {
    pageError.value = `La página debe estar entre 1 y ${props.totalPages}.`;
    return;
  }

  requestPage(requestedPage);
};
</script>

<template>
  <div class="flex flex-col items-center justify-between gap-3 sm:flex-row sm:items-start">
    <p class="text-sm text-slate-500">
      {{ total }} {{ total === 1 ? 'registro' : 'registros' }}
    </p>

    <div class="flex flex-col items-center gap-1 sm:items-end">
      <form class="flex items-center gap-2" @submit.prevent="applyPageInput">
        <button
          type="button"
          class="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 transition-colors duration-150 hover:border-slate-300 hover:text-slate-900 disabled:pointer-events-none disabled:opacity-40"
          :disabled="loading || page <= 1"
          aria-label="Página anterior"
          @click="requestPage(page - 1)"
        >
          <ChevronLeft :size="18" />
        </button>

        <label class="flex items-center gap-1.5 text-sm font-semibold text-slate-700">
          <span>Página</span>
          <input
            :value="pageInput"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            autocomplete="off"
            class="h-9 w-12 rounded-lg border bg-white px-1.5 text-center text-sm font-semibold outline-none transition-colors duration-150 focus:ring-2 disabled:cursor-wait disabled:bg-slate-50"
            :class="pageError
              ? 'border-danger-400 text-danger-700 focus:border-danger-500 focus:ring-danger-100'
              : 'border-slate-200 text-slate-700 focus:border-primary-500 focus:ring-primary-100'"
            :disabled="loading"
            :aria-invalid="Boolean(pageError)"
            :aria-describedby="pageError ? errorId : undefined"
            aria-label="Número de página"
            @input="handlePageInput"
          />
          <span>de {{ totalPages }}</span>
        </label>

        <button
          type="submit"
          class="h-9 rounded-lg bg-primary-500 px-3 text-sm font-semibold text-white transition-colors duration-150 hover:bg-primary-600 disabled:pointer-events-none disabled:opacity-40"
          :disabled="loading"
        >
          Ir
        </button>

        <button
          type="button"
          class="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 transition-colors duration-150 hover:border-slate-300 hover:text-slate-900 disabled:pointer-events-none disabled:opacity-40"
          :disabled="loading || page >= totalPages"
          aria-label="Página siguiente"
          @click="requestPage(page + 1)"
        >
          <ChevronRight :size="18" />
        </button>
      </form>

      <p
        v-if="pageError"
        :id="errorId"
        class="text-xs font-medium text-danger-600"
        role="alert"
      >
        {{ pageError }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { X } from '@lucide/vue';

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  size: { type: String, default: 'md' },
});

defineEmits(['close']);

const sizes = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-3xl',
  xl: 'max-w-4xl',
};
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-2.5 backdrop-blur-sm sm:p-4"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        tabindex="-1"
        @keydown.esc="$emit('close')"
        @click.self="$emit('close')"
      >
        <section
          class="flex max-h-[min(640px,calc(100dvh-1.5rem))] w-full flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-2xl sm:max-h-[min(640px,calc(100dvh-3rem))]"
          :class="sizes[size]"
        >
          <header class="flex shrink-0 items-start justify-between gap-3 border-b border-slate-100 px-4 py-3 sm:px-6 sm:py-3.5">
            <div>
              <h2 class="text-base font-bold text-slate-900 sm:text-lg">{{ title }}</h2>
              <p v-if="description" class="mt-0.5 text-xs text-slate-500">{{ description }}</p>
            </div>
            <button
              type="button"
              class="grid size-8 shrink-0 place-items-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 sm:size-9 sm:rounded-xl"
              aria-label="Cerrar"
              @click="$emit('close')"
            >
              <X :size="17" />
            </button>
          </header>
          <div class="dock-scrollbar min-h-0 flex-1 overflow-y-auto px-4 py-3.5 sm:px-6 sm:py-4">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="flex shrink-0 justify-end gap-2 border-t border-slate-100 bg-slate-50/80 px-4 py-2.5 sm:gap-3 sm:px-6 sm:py-3">
            <slot name="footer" />
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

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
  md: 'max-w-2xl',
  lg: 'max-w-4xl',
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
        class="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-slate-950/50 p-4 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        @click.self="$emit('close')"
      >
        <section
          class="my-auto w-full overflow-hidden rounded-2xl border border-white/70 bg-white shadow-2xl"
          :class="sizes[size]"
        >
          <header class="flex items-start justify-between border-b border-slate-100 px-6 py-5">
            <div>
              <h2 class="text-lg font-bold text-slate-900">{{ title }}</h2>
              <p v-if="description" class="mt-1 text-sm text-slate-500">{{ description }}</p>
            </div>
            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
              aria-label="Cerrar"
              @click="$emit('close')"
            >
              <X :size="19" />
            </button>
          </header>
          <div class="max-h-[72vh] overflow-y-auto px-6 py-5">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="flex justify-end gap-3 border-t border-slate-100 bg-slate-50/80 px-6 py-4">
            <slot name="footer" />
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { CircleCheck, CircleX, X } from '@lucide/vue';

defineProps({
  show: { type: Boolean, default: false },
  message: { type: String, default: '' },
  type: { type: String, default: 'success' },
});

defineEmits(['close']);
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-y-3 opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="translate-y-3 opacity-0"
    >
      <div
        v-if="show"
        class="fixed bottom-5 right-5 z-[60] flex max-w-sm items-center gap-3 rounded-xl border bg-white px-4 py-3 shadow-xl"
        :class="type === 'error' ? 'border-danger-200' : 'border-success-200'"
        role="status"
      >
        <CircleX v-if="type === 'error'" :size="20" class="shrink-0 text-danger-500" />
        <CircleCheck v-else :size="20" class="shrink-0 text-success-500" />
        <p class="text-sm font-medium text-slate-700">{{ message }}</p>
        <button type="button" class="ml-2 text-slate-400 hover:text-slate-700" aria-label="Cerrar notificación" @click="$emit('close')">
          <X :size="17" />
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

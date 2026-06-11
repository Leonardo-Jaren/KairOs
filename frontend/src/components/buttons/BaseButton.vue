<script setup>
const props = defineProps({
  type:    { type: String,  default: 'button' },
  loading: { type: Boolean, default: false },
  variant: { type: String,  default: 'primary' },
  id:      { type: String,  required: true },
});

const variants = {
  primary:   'bg-white text-kairos-navy hover:bg-white/95 hover:shadow-lg focus:ring-4 focus:ring-white/20',
  secondary: 'bg-transparent text-white border border-white/30 hover:border-white/80 hover:bg-white/5 focus:ring-4 focus:ring-white/10',
  google:    'bg-kairos-navy-light text-white border border-white/10 hover:bg-kairos-navy hover:shadow-md focus:ring-4 focus:ring-kairos-blue/20',
};
</script>

<template>
  <button
    :id="id"
    :type="type"
    :disabled="loading"
    class="w-full flex items-center justify-center gap-2.5 font-semibold text-base py-2.5 px-6 rounded-lg shadow transition-all duration-200 cursor-pointer select-none outline-none active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed disabled:pointer-events-none"
    :class="variants[variant]"
  >
    <svg
      v-if="loading"
      class="animate-spin size-5 shrink-0"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25" />
      <path fill="currentColor" class="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>

    <span class="tracking-wide"><slot /></span>
  </button>
</template>
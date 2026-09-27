<script setup>
import { computed } from 'vue';

const props = defineProps({
  count: { type: Number, default: 0 },
});

const buildingPositions = computed(() => {
  const count = Math.min(4, Math.max(0, Number(props.count) || 0));
  const positionsByCount = {
    0: [],
    1: [88],
    2: [60, 116],
    3: [39, 88, 137],
    4: [18, 66, 116, 164],
  };

  return positionsByCount[count];
});
</script>

<template>
  <svg
    class="massing-art h-auto w-full max-w-64 overflow-visible"
    viewBox="0 0 220 125"
    aria-hidden="true"
    focusable="false"
  >
    <path
      d="M18 72 110 30l92 42-92 43L18 72Z"
      class="fill-slate-100 stroke-slate-300 transition-colors duration-200 group-hover:fill-primary-50 group-hover:stroke-primary-300"
      stroke-width="1.2"
    />
    <path d="m18 72 92 43v7L18 79v-7Z" class="fill-slate-200" />
    <path d="m110 115 92-43v7l-92 43v-7Z" class="fill-slate-300/80" />

    <g
      v-for="(position, index) in buildingPositions"
      :key="`${position}-${index}`"
      :transform="`translate(${position} ${index % 2 === 0 ? 19 : 10})`"
      class="transition-transform duration-200 group-hover:-translate-y-1"
    >
      <path
        d="m0 22 20-11 20 11-20 11L0 22Z"
        class="fill-white stroke-slate-400 transition-colors duration-200 group-hover:fill-primary-100 group-hover:stroke-primary-500"
        stroke-width="1.1"
      />
      <path
        d="m0 22 20 11v30L0 52V22Z"
        class="fill-slate-200 stroke-slate-400 transition-colors duration-200 group-hover:fill-primary-200 group-hover:stroke-primary-500"
        stroke-width="1.1"
      />
      <path
        d="m20 33 20-11v30L20 63V33Z"
        class="fill-slate-300 stroke-slate-400 transition-colors duration-200 group-hover:fill-primary-300 group-hover:stroke-primary-500"
        stroke-width="1.1"
      />
      <path d="m6 28 8 4v15l-8-4V28Zm17 7 7-4v14l-7 4V35Z" class="fill-white/80" />
    </g>

    <path
      v-if="!buildingPositions.length"
      d="m77 69 33-15 33 15-33 16-33-16Z"
      class="fill-white/60 stroke-slate-400"
      stroke-dasharray="4 3"
    />
  </svg>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  .massing-art,
  .massing-art * {
    transition-duration: 0.01ms !important;
  }
}
</style>

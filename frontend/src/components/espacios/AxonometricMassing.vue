<script setup>
import { computed } from 'vue';

const props = defineProps({ count: { type: Number, default: 0 } });

const buildings = computed(() => {
  const count = Math.min(4, Math.max(0, Number(props.count) || 0));
  const layouts = {
    0: [],
    1: [[44, 24]],
    2: [[18, 38], [90, 8]],
    3: [[18, 65], [18, 0], [100, 30]],
    4: [[12, 66], [12, 0], [98, 66], [98, 0]],
  };
  return layouts[count]
    .map(([x, y], index) => ({ x, y, height: index % 2 ? 44 : 35 }))
    .sort((a, b) => b.y - a.y || a.x - b.x);
});

// Una proyección común conserva el volumen de cada bloque y de su plataforma.
function point(x, y, z = 0) {
  return [35 + x * 1.12 + y * 0.7, 100 + x * 0.34 - y * 0.5 - z];
}

function face(vertices) {
  return vertices.map((vertex) => point(...vertex).join(',')).join(' ');
}
</script>

<template>
  <svg class="massing-art h-auto w-full max-w-72" viewBox="0 0 320 185" aria-hidden="true" focusable="false">
    <polygon :points="face([[-12, -12, -4], [170, -12, -4], [170, 119, -4], [-12, 119, -4]])" fill="#edf2f8" stroke="#cad7e7" stroke-width="1.2" />
    <polygon :points="face([[-12, -12, -4], [170, -12, -4], [170, -12, -11], [-12, -12, -11]])" fill="#dfe7f1" />
    <polygon :points="face([[170, -12, -4], [170, 119, -4], [170, 119, -11], [170, -12, -11]])" fill="#cfdbe9" />

    <g v-for="(building, index) in buildings" :key="index" class="campus-block">
      <polygon :points="face([[building.x + 4, building.y - 4, -3], [building.x + 66, building.y - 4, -3], [building.x + 66, building.y + 35, -3], [building.x + 4, building.y + 35, -3]])" fill="#b8c8da" opacity="0.35" />
      <polygon :points="face([[building.x, building.y, 0], [building.x + 60, building.y, 0], [building.x + 60, building.y, building.height], [building.x, building.y, building.height]])" fill="#f8fafc" stroke="#92a8c0" stroke-width="0.8" />
      <polygon :points="face([[building.x + 60, building.y, 0], [building.x + 60, building.y + 30, 0], [building.x + 60, building.y + 30, building.height], [building.x + 60, building.y, building.height]])" fill="#d4deeb" stroke="#92a8c0" stroke-width="0.8" />

      <g v-for="row in 3" :key="row">
        <polygon v-for="column in 4" :key="column" :points="face([[building.x + 5 + (column - 1) * 13, building.y, row * building.height / 3 - 9], [building.x + 15 + (column - 1) * 13, building.y, row * building.height / 3 - 9], [building.x + 15 + (column - 1) * 13, building.y, row * building.height / 3 - 3], [building.x + 5 + (column - 1) * 13, building.y, row * building.height / 3 - 3]])" fill="#8fa4bc" />
        <polygon :points="face([[building.x + 60, building.y + 6, row * building.height / 3 - 9], [building.x + 60, building.y + 24, row * building.height / 3 - 9], [building.x + 60, building.y + 24, row * building.height / 3 - 3], [building.x + 60, building.y + 6, row * building.height / 3 - 3]])" fill="#92a8bf" />
      </g>

      <polygon :points="face([[building.x - 1, building.y - 1, building.height], [building.x + 61, building.y - 1, building.height], [building.x + 61, building.y + 31, building.height], [building.x - 1, building.y + 31, building.height]])" class="campus-roof" fill="#fff" stroke="#91a7c0" stroke-width="1" />
      <polygon :points="face([[building.x + 4, building.y + 4, building.height], [building.x + 56, building.y + 4, building.height], [building.x + 56, building.y + 26, building.height], [building.x + 4, building.y + 26, building.height]])" fill="#edf2f8" />
    </g>

    <polygon v-if="!buildings.length" :points="face([[46, 25, 0], [110, 25, 0], [110, 67, 0], [46, 67, 0]])" fill="#fff" stroke="#9aadc3" stroke-dasharray="4 3" />
  </svg>
</template>

<style scoped>
.campus-roof { transition: stroke 180ms ease; }
:global(.group:hover) .campus-roof { stroke: #729ac7; }
@media (prefers-reduced-motion: reduce) {
  .campus-roof { transition: none; }
}
</style>

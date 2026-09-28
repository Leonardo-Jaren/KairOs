<script setup>
import { computed, useId } from 'vue';

const props = defineProps({
  name: { type: String, default: 'Pabellón' },
  floors: { type: Number, default: 0 },
  selected: { type: Boolean, default: false },
});

const titleId = `pavilion-${useId()}`;
const floorCount = computed(() => Math.max(0, Math.floor(Number(props.floors) || 0)));
const levelHeight = computed(() => Math.min(38, 176 / Math.max(1, floorCount.value)));
const height = computed(() => Math.max(1, floorCount.value) * levelHeight.value);
const rows = computed(() => Array.from({ length: floorCount.value }, (_, index) => index));
const bays = [66, 105, 144, 183, 222];

// Proyección compartida por todos los planos para conservar aristas y profundidad.
function point(x, y, z = 0) {
  return [78 + x * 1.38 + y * 0.85, 252 + x * 0.24 - y * 0.48 - z];
}

function plane(vertices) {
  return vertices.map(([x, y, z]) => point(x, y, z).join(',')).join(' ');
}

function front(x, width, bottom, top, depth = 0) {
  return plane([[x, depth, bottom], [x + width, depth, bottom], [x + width, depth, top], [x, depth, top]]);
}

function side(x, bottom, top) {
  return plane([[x, 0, bottom], [x, 77, bottom], [x, 77, top], [x, 0, top]]);
}

function slab(x, width, z, depth = 77) {
  return plane([[x, 0, z], [x + width, 0, z], [x + width, depth, z], [x, depth, z]]);
}
</script>

<template>
  <svg
    class="pavilion-art block h-auto w-full"
    :class="{ 'is-selected': selected }"
    viewBox="0 0 560 370"
    role="img"
    :aria-labelledby="titleId"
    focusable="false"
  >
    <title :id="titleId">
      {{ floorCount ? `${name}, edificio de ${floorCount} ${floorCount === 1 ? 'piso' : 'pisos'}` : `${name}, sin pisos registrados` }}
    </title>

    <!-- Base de la maqueta con la misma perspectiva del edificio. -->
    <polygon :points="plane([[-25, -24, -6], [282, -24, -6], [282, 105, -6], [-25, 105, -6]])" class="base-top" />
    <polygon :points="plane([[-25, -24, -6], [282, -24, -6], [282, -24, -14], [-25, -24, -14]])" class="base-front" />
    <polygon :points="plane([[282, -24, -6], [282, 105, -6], [282, 105, -14], [282, -24, -14]])" class="base-side" />
    <polygon :points="slab(7, 259, -4, 87)" fill="#cad5e2" opacity="0.65" />

    <!-- Fachada principal y testero lateral con iluminación diferenciada. -->
    <polygon :points="side(264, 0, height)" class="wall-side outlined" />
    <polygon :points="front(58, 206, 0, height)" class="wall-front outlined" />
    <polygon :points="front(0, 58, 0, height - 3, 17)" class="wall-recess outlined" />

    <g v-if="floorCount">
      <g v-for="row in rows" :key="row" :data-floor-level="row + 1">
        <!-- Las ventanas representan franjas de fachada, no ambientes registrados. -->
        <g v-for="x in bays" :key="x" data-window>
          <polygon :points="front(x, 32, (row + 0.47) * levelHeight, (row + 0.92) * levelHeight)" class="glass" />
          <polygon :points="front(x, 32, (row + 0.87) * levelHeight, (row + 0.92) * levelHeight)" fill="#45576e" />
          <polygon :points="front(x + 15, 0.8, (row + 0.47) * levelHeight, (row + 0.92) * levelHeight)" fill="#b7c8d8" />
          <polygon :points="front(x + 2, 11, (row + 0.81) * levelHeight, (row + 0.83) * levelHeight)" fill="#b7cadb" opacity="0.7" />
        </g>
        <g data-window>
          <polygon :points="front(7, 44, (row + 0.3) * levelHeight, (row + 0.94) * levelHeight, 17)" fill="#53667b" />
          <polygon :points="plane([[264, 16, (row + 0.5) * levelHeight], [264, 59, (row + 0.5) * levelHeight], [264, 59, (row + 0.84) * levelHeight], [264, 16, (row + 0.84) * levelHeight]])" fill="#60758c" />
        </g>

        <!-- Los balcones sobresalen del núcleo de circulación retranqueado. -->
        <polygon :points="slab(0, 58, row * levelHeight + 2, 20)" class="roof" />
        <polygon :points="front(0, 58, row * levelHeight - 1, row * levelHeight + 2)" class="frame" />
        <polygon :points="front(2, 54, (row + 0.1) * levelHeight, (row + 0.29) * levelHeight)" class="wall-front" />
        <polygon :points="front(2, 54, (row + 0.36) * levelHeight, (row + 0.4) * levelHeight)" fill="#f9fbff" />
        <polygon v-for="post in [4, 27, 52]" :key="post" :points="front(post, 1.2, (row + 0.25) * levelHeight, (row + 0.4) * levelHeight)" class="frame" />

        <polygon :points="front(58, 206, row * levelHeight, row * levelHeight + 3)" class="frame" />
        <polygon :points="side(264, row * levelHeight, row * levelHeight + 3)" class="frame-side" />
      </g>

      <polygon v-for="x in [58, 101, 140, 179, 218, 258]" :key="x" :points="front(x, 4, 0, height)" class="frame" />
      <polygon :points="front(0, 4, 0, height)" class="frame" />
      <polygon :points="front(54, 4, 0, height)" class="frame" />
      <polygon :points="front(4, 1, 0, height)" fill="#fff" />
    </g>

    <g v-else>
      <polygon :points="front(70, 181, 6, height - 6)" fill="#eef3f8" stroke="#97aac0" stroke-dasharray="4 3" />
      <text x="287" y="223" text-anchor="middle" fill="#61748c" font-size="12" font-weight="600">Sin pisos registrados</text>
    </g>

    <!-- Cubierta y voladizo con espesor, evitando la silueta plana. -->
    <polygon :points="slab(-3, 270, height + 3, 81)" class="roof outlined" />
    <polygon :points="plane([[5, 7, height + 3], [259, 7, height + 3], [259, 72, height + 3], [5, 72, height + 3]])" fill="#edf2f8" />
    <polygon :points="front(-3, 270, height - 1, height + 3)" class="frame" />
    <polygon :points="plane([[267, 0, height - 1], [267, 81, height - 1], [267, 81, height + 3], [267, 0, height + 3]])" class="frame-side" />
    <polygon :points="front(0, 264, -3, 0)" fill="#95a9bf" />
    <polygon :points="side(264, -3, 0)" fill="#8198b1" />
  </svg>
</template>

<style scoped>
.pavilion-art { --frame: #a5bad1; --frame-side: #91a8c1; }
.pavilion-art.is-selected { --frame: #8daaca; --frame-side: #7898bb; }
.base-top { fill: #edf2f8; stroke: #cad6e5; stroke-width: 1; }
.base-front { fill: #dbe4ef; }
.base-side { fill: #cedae8; }
.wall-front { fill: #f4f7fb; }
.wall-side { fill: #d5dfea; }
.wall-recess { fill: #b7c7d8; }
.glass { fill: #74899f; }
.roof { fill: #fff; }
.outlined { stroke: #93a8bf; stroke-width: 0.9; stroke-linejoin: round; }
.frame { fill: var(--frame); transition: fill 180ms ease; }
.frame-side { fill: var(--frame-side); transition: fill 180ms ease; }
@media (prefers-reduced-motion: reduce) {
  .pavilion-art * { transition: none !important; }
}
</style>

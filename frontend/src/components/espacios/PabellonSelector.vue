<script setup>
import { Building2, ChevronRight, Pencil, Trash2 } from "@lucide/vue";

defineProps({
  buildings: { type: Array, default: () => [] },
  selectedId: { type: [String, Number], default: "" },
  canEdit: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
});
const emit = defineEmits(["select", "edit", "delete"]);
</script>

<template>
  <section
    class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5"
  >
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <p
          class="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400"
        >
          Pabellones
        </p>
        <h2 class="mt-1 text-lg font-extrabold text-slate-950">
          Elige un pabellón
        </h2>
      </div>
      <p class="text-xs text-slate-400">
        {{ buildings.length }}
        {{
          buildings.length === 1
            ? "pabellón disponible"
            : "pabellones disponibles"
        }}
      </p>
    </div>
    <div
      v-if="buildings.length === 1"
      class="mt-4 flex items-center gap-3 rounded-xl border border-primary-200 bg-primary-50/60 px-4 py-3"
    >
      <button
        type="button"
        class="flex min-h-11 min-w-0 flex-1 items-center gap-3 text-left focus:outline-none focus:ring-2 focus:ring-primary-200"
        :disabled="disabled"
        :aria-pressed="String(selectedId) === String(buildings[0].id)"
        @click="emit('select', buildings[0].id)"
      >
        <span
          class="grid size-10 place-items-center rounded-xl bg-primary-500 text-white"
          ><Building2 :size="19" /></span
        ><span class="min-w-0"
          ><p class="truncate text-sm font-extrabold text-slate-900">
            {{ buildings[0].nombre }}
          </p>
          <p
            class="font-mono text-[10px] font-bold uppercase tracking-wide text-primary-700"
          >
            {{ buildings[0].codigo }}
          </p></span
        ></button
      ><button
        v-if="canEdit"
        type="button"
        class="grid size-11 shrink-0 place-items-center rounded-lg text-slate-500 transition hover:bg-white hover:text-primary-600 disabled:opacity-40"
        :disabled="disabled"
        aria-label="Editar pabellón"
        @click="emit('edit', buildings[0])"
      >
        <Pencil :size="16" /></button
      ><button
        v-if="canEdit"
        type="button"
        class="grid size-11 shrink-0 place-items-center rounded-lg text-slate-500 transition hover:bg-danger-50 hover:text-danger-600 disabled:opacity-40"
        :disabled="disabled"
        aria-label="Desactivar pabellón"
        @click="emit('delete', buildings[0])"
      >
        <Trash2 :size="16" />
      </button>
    </div>
    <div
      v-else-if="buildings.length"
      class="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-3"
    >
      <div
        v-for="building in buildings"
        :key="building.id"
        class="flex min-h-16 items-center gap-2 rounded-xl border px-3 text-left transition hover:border-primary-300 hover:shadow-sm"
        :class="
          String(selectedId) === String(building.id)
            ? 'border-primary-400 bg-primary-50'
            : 'border-slate-200 bg-slate-50/60'
        "
      >
        <button
          type="button"
          class="flex min-h-11 min-w-0 flex-1 items-center gap-3 text-left focus:outline-none focus:ring-2 focus:ring-primary-200"
          :disabled="disabled"
          :aria-pressed="String(selectedId) === String(building.id)"
          @click="emit('select', building.id)"
        >
          <span
            class="grid size-9 shrink-0 place-items-center rounded-lg"
            :class="
              String(selectedId) === String(building.id)
                ? 'bg-primary-500 text-white'
                : 'bg-secondary-950 text-primary-300'
            "
            ><Building2 :size="17" /></span
          ><span class="min-w-0 flex-1"
            ><strong
              class="block truncate text-sm font-extrabold text-slate-900"
              >{{ building.nombre }}</strong
            ><span
              class="font-mono text-[10px] font-bold uppercase tracking-wide text-slate-400"
              >{{ building.codigo }} · {{ building.spaces.length }} amb.</span
            ></span
          ><ChevronRight :size="16" class="shrink-0 text-slate-400" /></button
        ><button
          v-if="canEdit"
          type="button"
          class="grid size-11 shrink-0 place-items-center rounded-lg text-slate-500 transition hover:bg-white hover:text-primary-600 disabled:opacity-40"
          :disabled="disabled"
          aria-label="Editar pabellón"
          @click="emit('edit', building)"
        >
          <Pencil :size="15" /></button
        ><button
          v-if="canEdit"
          type="button"
          class="grid size-11 shrink-0 place-items-center rounded-lg text-slate-500 transition hover:bg-danger-50 hover:text-danger-600 disabled:opacity-40"
          :disabled="disabled"
          aria-label="Desactivar pabellón"
          @click="emit('delete', building)"
        >
          <Trash2 :size="15" />
        </button>
      </div>
    </div>
    <div
      v-else
      class="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center"
    >
      <Building2 :size="28" class="mx-auto text-slate-300" />
      <p class="mt-2 text-sm font-semibold text-slate-600">
        Este local aún no tiene pabellones.
      </p>
    </div>
  </section>
</template>

<script setup>
import { Search } from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

defineProps({
  hasActiveFilters: { type: Boolean, default: false },
});

const emit = defineEmits(['apply', 'clear']);

const modulo = defineModel('modulo', { type: String, default: '' });
const tipoEvento = defineModel('tipoEvento', { type: String, default: '' });
const fechaDesde = defineModel('fechaDesde', { type: String, default: '' });
const fechaHasta = defineModel('fechaHasta', { type: String, default: '' });

const MODULO_OPTIONS = [
  { value: 'usuario', label: 'Usuarios' },
  { value: 'espacio', label: 'Espacios' },
  { value: 'espaciousuario', label: 'Asignaciones' },
  { value: 'equipo', label: 'Equipos' },
  { value: 'software', label: 'Software' },
  { value: 'mantenimiento', label: 'Mantenimiento' },
  { value: 'incidencia', label: 'Incidencias' },
];
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
    <form class="flex flex-wrap items-end gap-3" @submit.prevent="emit('apply')">
      <div class="w-48">
        <BaseSelect
          id="historial-modulo"
          v-model="modulo"
          :options="MODULO_OPTIONS"
          placeholder="Todos los módulos"
        />
      </div>
      <div class="min-w-52 flex-1">
        <BaseInput
          id="historial-evento"
          v-model="tipoEvento"
          appearance="light"
          placeholder="Tipo de evento (ej. usuario.alta)"
        >
          <template #icon>
            <Search :size="17" />
          </template>
        </BaseInput>
      </div>
      <div class="w-40">
        <BaseInput
          id="historial-desde"
          v-model="fechaDesde"
          type="date"
          appearance="light"
          placeholder=""
        />
      </div>
      <div class="w-40">
        <BaseInput
          id="historial-hasta"
          v-model="fechaHasta"
          type="date"
          appearance="light"
          placeholder=""
        />
      </div>
      <BaseButton type="submit" variant="accent" :full-width="false">Buscar</BaseButton>
      <BaseButton
        v-if="hasActiveFilters"
        type="button"
        variant="ghost"
        :full-width="false"
        @click="emit('clear')"
      >
        Limpiar
      </BaseButton>
    </form>
  </section>
</template>

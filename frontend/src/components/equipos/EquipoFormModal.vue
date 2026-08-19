<script setup>
import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';

defineProps({
  open: { type: Boolean, default: false },
  form: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
  editing: { type: Boolean, default: false },
  typeOptions: { type: Array, default: () => [] },
  acquisitionOptions: { type: Array, default: () => [] },
  statusOptions: { type: Array, default: () => [] },
  spaceOptions: { type: Array, default: () => [] },
  lockSpace: { type: Boolean, default: false },
  spaceName: { type: String, default: '' },
});

defineEmits(['close', 'submit']);
</script>

<template>
  <BaseModal
    :open="open"
    :title="editing ? 'Editar equipo' : 'Nueva PC'"
    :description="lockSpace ? `Se asignará a ${spaceName}.` : 'Registra los datos técnicos y de adquisición del equipo.'"
    size="lg"
    @close="$emit('close')"
  >
    <form id="shared-equipment-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="$emit('submit')">
      <BaseInput id="equipment-code" v-model="form.codigo" appearance="light" label="Código interno" placeholder="LAB203-PC01" :error="errors.codigo" />
      <BaseInput id="equipment-serial" v-model="form.numero_serie" appearance="light" label="Número de serie" placeholder="SN-000123" :error="errors.numero_serie" />
      <BaseSelect id="equipment-type" v-model="form.tipo_equipo" label="Tipo de equipo" :options="typeOptions" :error="errors.tipo_equipo" />
      <div v-if="lockSpace" class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5">
        <p class="text-xs font-semibold text-slate-500">Espacio asignado</p>
        <p class="mt-1 truncate text-sm font-bold text-slate-800">{{ spaceName }}</p>
      </div>
      <BaseSelect v-else id="equipment-space" v-model="form.espacio" label="Espacio asignado" :options="spaceOptions" placeholder="Sin asignar" />
      <BaseInput id="equipment-brand" v-model="form.marca" appearance="light" label="Marca" placeholder="HP" :error="errors.marca" />
      <BaseInput id="equipment-model" v-model="form.modelo" appearance="light" label="Modelo" placeholder="ProDesk 400" :error="errors.modelo" />
      <BaseInput id="equipment-mac" v-model="form.numero_mac" appearance="light" label="Dirección MAC" placeholder="AA:BB:CC:DD:EE:FF" />
      <BaseSelect id="equipment-acquisition" v-model="form.modo_adquisicion" label="Modo de adquisición" :options="acquisitionOptions" :error="errors.modo_adquisicion" />
      <BaseInput id="equipment-acquisition-date" v-model="form.fecha_adquisicion" type="date" appearance="light" label="Fecha de adquisición" :error="errors.fecha_adquisicion" />
      <BaseInput id="equipment-renewal-date" v-model="form.fecha_renovacion" type="date" appearance="light" label="Fecha de renovación (opcional)" />
      <BaseSelect id="equipment-status" v-model="form.estado" label="Estado" :options="statusOptions" :error="errors.estado" />
      <BaseInput id="equipment-owner" v-model="form.responsable_usuario" appearance="light" label="Usuario responsable (opcional)" placeholder="Nombre del responsable" />
    </form>

    <template #footer>
      <BaseButton variant="ghost" :full-width="false" @click="$emit('close')">Cancelar</BaseButton>
      <BaseButton type="submit" form="shared-equipment-form" variant="accent" :loading="saving" :full-width="false">
        {{ editing ? 'Guardar cambios' : 'Crear y continuar' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

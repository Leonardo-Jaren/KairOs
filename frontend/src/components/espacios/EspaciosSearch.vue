<script setup>
import { Search } from '@lucide/vue';
import BaseInput from '@/components/inputs/BaseInput.vue';

defineProps({
  id: { type: String, required: true },
  modelValue: { type: String, default: '' },
  placeholder: { type: String, required: true },
});
const emit = defineEmits(['update:modelValue']);
</script>

<template>
  <BaseInput :id="id" :model-value="modelValue" :placeholder="placeholder" appearance="light" @update:model-value="emit('update:modelValue', $event)">
    <template #icon><Search :size="17" /></template>
  </BaseInput>
</template>

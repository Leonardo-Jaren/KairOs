<script setup>
import { shallowRef, watch } from 'vue';

import AuditTimelineList from '@/components/historial/AuditTimelineList.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import historialService from '@/services/historial.service';

const props = defineProps({
  open:        { type: Boolean,           default: false },
  title:       { type: String,            required: true },
  description: { type: String,            default: '' },
  modulo:      { type: String,            required: true },
  objectId:    { type: [Number, String],  default: null },
});

defineEmits(['close']);

const activeTab       = shallowRef('info');
const timelineEvents  = shallowRef([]);
const timelineLoading = shallowRef(false);
const timelineLoaded  = shallowRef(false);

watch(() => props.objectId, () => {
  activeTab.value      = 'info';
  timelineEvents.value = [];
  timelineLoaded.value = false;
});

async function switchToTimeline() {
  activeTab.value = 'timeline';
  if (timelineLoaded.value || !props.objectId) return;
  timelineLoading.value = true;
  try {
    const data = await historialService.listar({
      modulo: props.modulo,
      object_id: props.objectId,
      page_size: 50,
    });
    timelineEvents.value = data.results ?? data;
    timelineLoaded.value = true;
  } finally {
    timelineLoading.value = false;
  }
}
</script>

<template>
  <BaseModal
    :open="open"
    :title="title"
    :description="description"
    size="lg"
    @close="$emit('close')"
  >
    <div class="flex flex-col">

      <div class="mb-5 flex border-b border-slate-200">
        <button
          type="button"
          class="-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === 'info'
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="activeTab = 'info'"
        >
          Información
        </button>
        <button
          type="button"
          class="-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
          :class="activeTab === 'timeline'
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-slate-500 hover:text-slate-700'"
          @click="switchToTimeline"
        >
          Línea de Tiempo
        </button>
      </div>

      <div v-if="activeTab === 'info'">
        <slot name="info" />
      </div>

      <div v-else>
        <AuditTimelineList
          :events="timelineEvents"
          :loading="timelineLoading"
          :inline="true"
        />
      </div>

    </div>
  </BaseModal>
</template>

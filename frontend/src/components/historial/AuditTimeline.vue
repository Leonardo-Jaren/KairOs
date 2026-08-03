<script setup>
import { shallowRef } from 'vue';

import AuditDetailModal from './AuditDetailModal.vue';
import AuditTimelineList from './AuditTimelineList.vue';

defineProps({
  events:  { type: Array,   required: true },
  loading: { type: Boolean, default: false },
});

const selectedEvent = shallowRef(null);
</script>

<template>
  <div class="flex flex-col">
    <AuditTimelineList
      :events="events"
      :loading="loading"
      @show-detail="selectedEvent = $event"
    />
    <AuditDetailModal
      :open="selectedEvent !== null"
      :event="selectedEvent"
      @close="selectedEvent = null"
    />
  </div>
</template>

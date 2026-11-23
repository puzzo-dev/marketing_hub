<template>
  <ListScreen
    title="Placements" doctype="Placement"
    :columns="[
      { label: 'Content', field: 'content_item', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Channel', field: 'channel', width: '140px' },
      { label: 'Scheduled for', field: 'scheduled_for', width: '170px' },
      { label: 'Approval', field: 'approval_state', width: '140px', badge: true },
      { label: 'Status', field: 'status', width: '120px', badge: true },
    ]"
    order-by="scheduled_for asc"
    status-field="status" :statuses="['Scheduled', 'Posted', 'Failed']"
    empty-title="Nothing scheduled" empty-text="Placements you schedule go to the exercise's Brand Manager for approval before they send."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
</script>

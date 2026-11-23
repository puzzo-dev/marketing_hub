<template>
  <ListScreen
    title="Content" doctype="Content Item" row-route="ContentDetail"
    :columns="[
      { label: 'Title', field: 'title', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Exercise', field: 'campaign' },
      { label: 'Type', field: 'type', width: '120px' },
      { label: 'Due', field: 'due_date', width: '120px' },
      { label: 'Status', field: 'status', width: '130px', badge: true },
    ]"
    status-field="status" :statuses="['Draft', 'In review', 'Approved', 'Posted']"
    empty-title="No content yet" empty-text="Content you create for an exercise appears here with its review status."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
</script>

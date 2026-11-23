<template>
  <ListScreen
    title="Leads" doctype="Lead" row-route="Lead"
    :columns="[
      { label: 'Lead', field: 'lead_name', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Source', field: 'source', width: '160px' },
      { label: 'Exercise', field: 'mkt_campaign' },
      { label: 'Status', field: 'status', width: '130px', badge: true },
    ]"
    status-field="status" :statuses="['Open', 'Replied', 'Converted']"
    empty-title="No leads yet" empty-text="Leads captured by an exercise's tracking links and forms appear here."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
</script>

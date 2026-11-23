<template>
  <ListScreen
    title="Out of home" doctype="OOH Booking" row-route="OOHBooking" :secondary="{ label: 'Map', to: { name: 'OOHMap' } }"
    :columns="[
      { label: 'Site', field: 'site', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Exercise', field: 'campaign', sub: true },
      { label: 'Starts', field: 'start_date', width: '120px' },
      { label: 'Ends', field: 'end_date', width: '120px' },
      { label: 'Status', field: 'status', width: '130px', badge: true },
    ]"
    status-field="status" :statuses="['Proposed', 'Production', 'Live', 'Ended']"
    :action="canBook ? { label: 'New booking', to: { name: 'NewOOHBooking' } } : null"
    empty-title="No bookings" empty-text="A booking reserves a site for an exercise. It needs the Brand Manager's approval."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
import { hasRole, ROLES } from "@/lib/session"
const canBook = hasRole(ROLES.ooh, ROLES.manager)
</script>

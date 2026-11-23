<template>
  <ListScreen
    title="Exercises" doctype="Marketing Campaign" row-route="Exercise"
    :columns="[
      { label: 'Exercise', field: 'campaign_name', width: 'minmax(0, 1.6fr)', strong: true },
      { label: 'Brand', field: 'brand', sub: true },
      { label: 'Brand Manager', field: 'brand_manager' },
      { label: 'Dates', field: 'start_date', width: '120px' },
      { label: 'Budget', field: 'budget', width: '120px', currency: 'NGN' },
      { label: 'Status', field: 'status', width: '120px', badge: true },
    ]"
    status-field="status" :statuses="['Draft', 'Active', 'Completed']"
    :action="canCreate ? { label: 'New exercise', to: { name: 'NewExercise' } } : null"
    empty-title="No exercises yet" empty-text="An exercise is one marketing push, with its own plan, content, placements and budget."
  />
</template>

<script setup>
import ListScreen from "@/components/ListScreen.vue"
import { hasRole, ROLES } from "@/lib/session"
// Only the Brand Manager creates an exercise; everyone else raises a change request.
const canCreate = hasRole(ROLES.manager)
</script>
